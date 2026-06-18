# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_conn.c

## Purpose

`ip_vs_conn.c` owns IPVS connection table management. It creates, hashes, looks up, rehashes, expires, flushes, lists, and frees `struct ip_vs_conn` objects. It also binds connections to destinations, transmit methods, application helpers, persistence engines, conntrack behavior, sync behavior, and per-netns resize/cleanup state.

## Important APIs, types, and functions

Hashing and lookup are built around `struct ip_vs_rht`, bucket bit locks, seqcounts, and dual hash nodes `hn0`/`hn1`. `ip_vs_conn_hashkey()`, `ip_vs_conn_hashkey_param()`, and `ip_vs_conn_hashkey_conn()` compute siphash keys. `ip_vs_conn_hash()` inserts new connections into the current table and schedules resizing. `ip_vs_conn_unlink()` removes only when the reference count shows no other users. Lookup APIs include `ip_vs_conn_in_get()`, `ip_vs_conn_in_get_proto()`, `ip_vs_ct_in_get()`, `ip_vs_conn_out_get()`, and `ip_vs_conn_out_get_proto()`. `ip_vs_conn_fill_cport()` safely rehashes no-client-port entries after the real client port is learned. `ip_vs_conn_new()` constructs and hashes new connections. Lifecycle functions include `ip_vs_conn_put()`, `ip_vs_conn_expire()`, `ip_vs_conn_expire_now()`, `ip_vs_conn_del()`, `ip_vs_conn_del_put()`, `ip_vs_conn_flush()`, and `ip_vs_conn_cleanup()`.

## Control flow

Initialization clamps `conn_tab_bits` to memory and architecture limits, computes `ip_vs_conn_tab_size`, and creates the connection slab cache. Per-netns init initializes counters, delayed resize work, conn table pointer, proc files, and default load factor. A new connection is allocated from the slab, initialized with client/virtual/destination tuple, flags, optional persistence data, timer, locks, destination binding, transmit function, app binding, conntrack flag, and finally inserted into the hash table. Incoming and outgoing packet lookup compute the appropriate tuple hash, walk current and transitional resize tables under RCU, compare tuple fields, and take a reference before returning.

Hash table resizing runs from `conn_resize_work_handler()`: it allocates a new table at the desired size/load factor, links it as `new_tbl`, waits for readers, migrates bucket chains under seqcount and bucket locks, publishes the new table, increments `conn_tab_changes`, waits for RCU readers, frees the old table, and reschedules shrink monitoring. No-client-port rehashing uses a similar seqcount-protected move so early fragments or protocols without initial client ports can later become normally keyed.

Expiration starts from timers or forced deletes. `ip_vs_conn_expire()` refuses to unlink while the connection controls children, otherwise unhashes when the refcount permits, handles control-chain release, drops conntrack if enabled and namespace is still active, unbinds app and destination, updates no-client-port counters, RCU-frees or directly frees one-packet connections, and decrements `conn_count`. If busy, it extends timeout and may sync the connection from master state. Flush loops over all buckets under RCU, expires un-controlled entries, waits until `conn_count` reaches zero, then unregisters and RCU-frees all resize-chain tables.

## State and persistence behavior

Per-connection state includes address/port tuples, protocol, forwarding flags, destination pointer, app pointer/data, persistence engine data, timer, refcount, control-chain counters, packet counters, sequence adjustment state, sync end time, and hash keys. Per-netns state includes the resizeable hash table, connection count, no-client-port counters, resize work item, table generation counter, dropentry counters, sysctls, and proc entries. State is in-memory only; synchronization code can mirror connection state to peer IPVS nodes, but this file does not persist it to disk.

## Dependencies and integration points

The file depends on IPVS core headers, RCU, hlist_bl locks, timers, delayed work, siphash/jhash/randomness, procfs, slab caches, protocol modules, destination/service lookup, transmit functions, app helpers, persistence engines, netfilter conntrack integration, sync, sysctl, and net namespace lifecycle. It exports lookup functions used by packet handling and flush/drop functions used by control/sysctl paths.

## Risks

Concurrency is the main risk. Resizing, no-client-port rehashing, lookup, and deletion rely on correct hash-key generation, table-id checks, seqcount retry, bucket lock ordering, RCU grace periods, and refcount transitions. Any mismatch can cause missed lookups, stale pointers, or double unlink. Destination counter updates must stay paired with bind/unbind, including templates and sync-created connections. Timer expiration cannot access conntrack after namespace cleanup disables IPVS. Random drop and flush paths must avoid deleting controlled connections prematurely.

## Test signals

Tests should cover incoming/outgoing lookup for NAT, DR, tunnel, localnode, bypass, IPv4 and IPv6, templates and persistence engines, no-client-port fill and rehash, resize growth/shrink under concurrent lookups, timer expiration of normal/template/controlled/one-packet connections, destination overload counter transitions, app binding/unbinding, conntrack drop behavior during namespace cleanup, proc listing across resize generations, random drop sysctl behavior, and full per-netns cleanup with active connections.
