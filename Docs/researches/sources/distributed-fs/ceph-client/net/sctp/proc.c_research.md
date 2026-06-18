# sources/distributed-fs/ceph-client/net/sctp/proc.c

## Purpose
`proc.c` exposes SCTP observability under `/proc/net/sctp`. It publishes MIB counters, endpoint tables, association tables, and remote-address/transport information for each network namespace.

## Important APIs, Types, And Functions
The initialization API is `sctp_proc_init(struct net *net)`. Proc entries are `snmp`, `eps`, `assocs`, and `remaddr`. Key functions include `sctp_snmp_seq_show()`, `sctp_seq_dump_local_addrs()`, `sctp_seq_dump_remote_addrs()`, endpoint seq operations (`sctp_eps_seq_start/next/stop/show()`), transport rhashtable iterator operations (`sctp_transport_seq_start/next/stop()`), `sctp_assocs_seq_show()`, and `sctp_remaddr_seq_show()`. `struct sctp_ht_iter` embeds `seq_net_private` plus `rhashtable_iter`.

## Control Flow
`sctp_proc_init()` creates the namespace SCTP proc directory and then registers the four read-only files, removing the subtree if any creation fails. `snmp` folds per-CPU SCTP MIB fields into a local buffer and prints name/value rows from `sctp_snmp_list`.

`eps` iterates endpoint hash buckets by position, locks each bucket, filters sockets by seq file net namespace, and prints endpoint pointer, socket pointer, style, state, hash bucket, local port, UID, inode, and local addresses. `assocs` and `remaddr` iterate the transport rhashtable with hold/put discipline; associations are printed once per transport iterator entry, while `remaddr` prints every peer transport for the association visible from the current iterator transport.

Address dumping is AF-polymorphic: local and remote address printers use `sctp_get_af_specific()` and `af->seq_dump_addr()`, marking primary addresses with `*`.

## State And Persistence
Proc output is a live snapshot of in-memory SCTP counters, endpoint hash state, association state, transport lists, timers, socket buffers, and address lists. It does not store history. The proc directory exists per net namespace and is removed during SCTP per-net cleanup.

## Dependencies And Integration Points
This file depends on procfs, seq_file, SCTP MIB allocation, endpoint hash tables from `input.c`/`protocol.c`, transport rhashtable iterators, AF address dump callbacks, socket UID/inode helpers, and net namespace filtering.

## Risks
Iterator lifetime and locking are central. Endpoint iteration uses bucket read locks, while transport iteration must hold and release transports correctly around seq transitions. Association and transport lists are live and RCU-protected in places, so output can be approximate under concurrent changes. Pointer printing uses `%pK`, respecting kernel pointer exposure policy, but still exposes diagnostic topology.

## Test Signals
Check proc files in initial, active, and teardown states; verify per-net namespace filtering; compare SNMP counters with traffic; create multihomed associations and verify local/remote primary markers; read while associations are closing; test failure cleanup by forcing one proc entry creation to fail; and validate `remaddr` timer/state fields after heartbeat and path failure events.
