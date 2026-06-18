# sources/distributed-fs/ceph-client/net/rds/connection.c

## Purpose
`connection.c` owns RDS connection object allocation, lookup, state reset/shutdown/destroy, reconnect triggering, and connection-related info exports. Connections persist across underlying transport reconnects to preserve retransmission and sequencing state.

## Important APIs, Types, And Functions
Key APIs are `rds_conn_create()`, `rds_conn_create_outgoing()`, `rds_conn_shutdown()`, `rds_conn_destroy()`, `rds_for_each_conn_info()`, `rds_conn_init()`, `rds_conn_exit()`, `rds_conn_path_drop()`, `rds_conn_drop()`, `rds_conn_path_connect_if_down()`, `rds_check_all_paths()`, `rds_conn_connect_if_down()`, and `__rds_conn_path_error()`. Important helpers include `rds_conn_bucket()`, `rds_conn_lookup()`, `rds_conn_path_reset()`, and `__rds_conn_create()`.

## Control Flow
Connection creation hashes local/foreign address pairs and looks up an existing connection under RCU. If none exists, it allocates `struct rds_connection` and one or more `struct rds_conn_path` entries depending on transport multipath capability, initializes congestion maps, detects loopback preference, initializes per-path workqueues and delayed works, calls the transport `conn_alloc()`, then inserts under `rds_conn_lock` unless a racing creator won.

Shutdown transitions a path to disconnecting, waits for transmit/refill flags to clear, calls the transport shutdown hook, resets send path state without clearing `next_rx_seq`, transitions to down, cancels pending reconnect work, and requeues reconnect for still-hashed live connections. Destroy removes from the hash under RCU, destroys each path, drops queued messages and retransmits, removes congestion map linkage, frees path memory and slab object, and decrements the global count.

Info export walks connection hash buckets under RCU, optionally walks send/retrans queues under path locks, zeroes per-item buffers before copying to userspace, and reports IPv4/IPv6 connection state.

## State And Persistence
Global state includes `rds_conn_hash`, `rds_conn_lock`, `rds_conn_count`, and `rds_conn_slab`. Each connection stores local/foreign addresses, net, transport, TOS, device index, loopback/passive status, generation numbers, congestion maps, and per-path state including send/retrans queues, sequence numbers, delayed works, waitqueues, flags, and transport private data.

## Dependencies And Integration Points
The file integrates with RDS transports, loopback, congestion maps, send/recv workers, reconnect scheduling, info getsockopt, IPv6 hashing, and RCU hash traversal. Transport hooks include `conn_alloc`, `conn_free`, `conn_path_shutdown`, `conn_slots_available`, and multipath flags.

## Risks
Creation handles races by allocating outside the global lock then rolling back if another connection appears; rollback must free all per-path transport data and workqueues. Passive loopback IB connections are special and not hashed like normal connections. Reset intentionally preserves receive sequence state for reliability. Shutdown waits can hang if transport flags or fast-reg completions never drain. Info APIs currently report only the first multipath path for some records.

## Test Signals
Tests should cover duplicate creation races, passive loopback creation, transport allocation failure rollback, multipath path allocation, shutdown from UP/ERROR/RESETTING states, reconnect scheduling suppression after destroy, queued message cleanup, info export buffer zeroing, IPv4/IPv6 filtering, and module exit with empty hash.
