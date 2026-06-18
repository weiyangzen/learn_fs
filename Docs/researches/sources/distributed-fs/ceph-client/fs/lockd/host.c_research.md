# sources/distributed-fs/ceph-client/fs/lockd/host.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/host.c` manages cached `nlm_host` objects shared by lockd client and server personalities. It handles host lookup, allocation, RPC client binding/rebinding, reference release, reboot notification fanout, per-net shutdown, and garbage collection. The source was read as a complete 723-line file.

## Important APIs, Types, and Functions

Important APIs are `nlmclnt_lookup_host`, `nlmclnt_release_host`, `nlmclnt_shutdown_rpc_clnt`, `nlmsvc_lookup_host`, `nlmsvc_release_host`, `nlm_bind_host`, `nlm_rebind_host`, `nlm_get_host`, `nlm_host_rebooted`, `nlm_shutdown_hosts_net`, and `nlm_shutdown_hosts`. Internal state includes client/server host hash tables, `nlm_host_mutex`, and the `nlm_lookup_host_info` construction record.

## Control Flow

Client lookup searches the client table by network namespace, peer address, protocol, and NLM version, sharing an existing NSM handle for the same address when possible; otherwise it allocates and inserts a new host. Server lookup adds source-address matching and runs GC periodically. `nlm_bind_host` lazily creates an SUNRPC client, configuring hard retry for client-side calls, soft behavior for server-side block callbacks, UDP autobind/rebind, optional nonprivileged source ports, and optional source address. Reboot notification maps NSM private data to handles, marks matching hosts with new NSM state, frees server resources, and starts client recovery.

## State and Persistence Behavior

Host state is in-memory, refcounted, and separated into client and server hash tables. Each host owns credentials, NSM handle reference, optional RPC client, lockowner/granted/reclaim lists, rebinding/expiry timestamps, and net namespace pointer. Server hosts are destroyed by mark-and-sweep GC after resources and references clear; client hosts are destroyed when their refcount reaches zero.

## Dependencies and Integration Points

This file integrates with `mon.c` for NSM handles, `clntlock.c` for recovery, server resource cleanup in `svcsubs.c`/related files, `clntxdr.c` via `nlm_program`, SUNRPC client creation, portmapper autobind, per-net `lockd_net`, and service request source/destination addresses.

## Risks and Edge Cases

Host identity must include net namespace, transport, version, and server source address where applicable. UDP rebind throttling must avoid stale portmapper data without excessive rebinding. Shutdown must cancel tasks before host destruction. GC must not destroy hosts with locks, blocks, shares, or live refs. NSM reuse by address can couple host lifetime unexpectedly if names differ.

## Test Signals

Tests should cover host cache hit/miss identity, per-net isolation, UDP rebind after connection errors, RPC client shutdown races, server-host GC with and without resources, NSM reboot notifications affecting multiple host entries, and lockdep around `nlm_host_mutex` plus host mutex nesting.
