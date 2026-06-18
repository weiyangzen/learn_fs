# subset-b-007645 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd-idl.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd-idl.h

## Purpose
Defines the on-wire socklnd protocol structures shared by the TCP socket LNet driver and any peer that must parse socklnd handshakes or messages. It is intentionally compact and packed, because the structures are serialized directly across sockets.

## Important APIs, types, and constants
`struct ksock_hello_msg` is the current large-NID hello frame. It carries magic, protocol version, source/destination NIDs and PIDs, incarnation counters, connection type, and deprecated IP-vector fields. `struct ksock_hello_msg_nid4` is the legacy NID4-compatible form used by protocol v2/v3. `struct ksock_msg_hdr` prefixes v2+ data messages with message type, checksum, and two zero-copy cookies. `struct ksock_msg` unions NID4 and NID16 LNet headers after that socklnd header. `KSOCK_MSG_NOOP`, `KSOCK_MSG_LNET`, and `KSOCK_PROTO_V2/V3/V4` define the message and protocol discriminators.

## Control flow and integration
This header has no executable control flow. `socklnd_proto.c` fills and parses these structures in per-version hello, pack, unpack, zero-copy ACK, and matching routines. `socklnd_cb.c` receives `struct ksock_msg_hdr` before deciding whether to consume an LNet header, a NOOP, a zero-copy ACK, or slop bytes. `socklnd.c` uses the hello fields to validate peer identity, connection type, protocol compatibility, and incarnation changes.

## State and persistence
The file defines transient wire state only. The incarnation fields let runtime code distinguish a live peer from a rebooted peer and force protocol renegotiation when necessary. Zero-copy cookies are persisted only in memory by `ksnp_zc_req_list` while a sender waits for a matching ACK.

## Dependencies
Depends on UAPI LNet types and socklnd connection type constants. Packed layout and integer widths are part of the protocol contract.

## Risks and test signals
Risks concentrate in ABI drift: changing field order, packing, widths, or protocol constants breaks interoperability. NID4/NID16 conversion paths should be tested with IPv4, IPv6 or large-NID peers, byte-swapped peers, zero-copy ACK traffic, and mixed protocol-version negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd-idl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.c

## Purpose
Implements the main socklnd LNet driver lifecycle: module registration, NI startup and shutdown, interface binding, peer and connection-control-block management, active/passive connection creation, close paths, LNet control operations, and netdevice/address notifier handling.

## Important APIs and functions
Exports the `struct lnet_lnd` callbacks through `the_ksocklnd`: `ksocknal_startup`, `ksocknal_shutdown`, `ksocknal_ctl`, `ksocknal_send`, `ksocknal_recv`, `ksocknal_accept`, and tunable/netlink helpers. Peer APIs include `ksocknal_add_peer`, `ksocknal_find_peer_locked`, `ksocknal_close_matching_conns`, and `ksocknal_peer_failed`. Connection lifecycle APIs include `ksocknal_create_conn`, `ksocknal_close_conn_locked`, `ksocknal_terminate_conn`, `ksocknal_queue_zombie_conn`, and `ksocknal_destroy_conn`.

## Control flow
`ksocklnd_init` initializes tunables, libcfs, and registers the LND. `ksocknal_startup` performs global base startup if needed, allocates `ksock_net`, selects an IP interface from `lnet_inet_enumerate`, initializes NI NID/interface state, starts scheduler threads for configured CPTs, checks link state, and registers acceptor sockets. `ksocknal_add_peer` creates or finds a peer and attaches a single route/control block. `ksocknal_create_conn` is the central handshake path: allocate `ksock_conn`, save socket callbacks, exchange hello messages, resolve protocol version and identity, create or find the peer for passive accepts, reject duplicate or racing connections, bind a scheduler, queue pending TXs, set socket options, install callbacks, and kick RX/TX readiness. Close paths remove connections from peers, move blocked TXs for completion or drain, enqueue deathrow/zombie work to the reaper, and notify LNet when kernel peers appear down.

## State and persistence
Global state lives in `ksocknal_data`: peer hash, net list, scheduler array, connd/reaper lists, TX freelist, and shutdown flags. Per-NI state is `struct ksock_net`, including incarnation, selected interface, and peer count. Peer state records NID/PID, protocol, incarnation, connection list, pending TX queue, zero-copy requests, and keepalive timestamps. All state is volatile kernel memory. Shutdown applies `SOCKNAL_SHUTDOWN_BIAS` to prevent new peers, deletes peers, removes acceptor sockets, waits for refs to drain, then tears down global threads when the last net exits.

## Dependencies and integration points
Integrates with LNet NI registration, acceptor socket management, libcfs allocation/CPT APIs, Linux netdevice and inet address notifiers, kernel sockets, SunRPC sockaddr helpers, netlink tunable export/import, and socklnd protocol/lib/callback helpers.

## Risks and test signals
High-risk areas are lock ordering around `ksnd_global_lock`, scheduler locks, and reaper/connd locks; passive/active race resolution; duplicate connection limits; peer reboot incarnation handling; IPv6/large-NID protocol selection; and shutdown refcount drainage. Test signals include multi-peer startup/shutdown, interface down/up and address removal events, mixed v3/v4 peers, connection-race tests, duplicate `conns_per_peer` scenarios, ioctl/netlink tunable checks, and leak/refcount assertions during module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.h

## Purpose
Central private header for the socklnd implementation. It defines all in-memory driver objects, tunable pointers, scheduler state, connection and peer models, protocol operations, refcount helpers, constants, and cross-file function prototypes.

## Important APIs and types
`struct ksock_sched` owns per-CPT RX/TX work queues and scheduler thread accounting. `struct ksock_interface`, `struct ksock_net`, and `struct ksock_nal_data` model selected network interfaces, per-NI state, and global driver state. `struct ksock_tx` wraps an LNet message or NOOP, including header iov, page payloads, zero-copy cookies, deadlines, and health status. `struct ksock_conn` tracks one socket, callback replacements, refcounts, RX state machine, TX queue, deadlines, and scheduler assignment. `struct ksock_conn_cb` is the route/reconnect controller. `struct ksock_peer_ni` aggregates all connections and pending work for a peer. `struct ksock_proto` provides per-wire-version operations.

## Control flow and integration
The header binds together `socklnd.c` lifecycle, `socklnd_cb.c` data path, `socklnd_lib.c` socket primitives, `socklnd_proto.c` protocol variants, and `socklnd_modparams.c` tunables. Inline helpers manage reference transitions for conns, sockets, TXs, conn control blocks, and peers. The public LND callback prototypes are here so the module registration table can bind to them.

## State and persistence
All declared structures are runtime kernel memory with explicit list ownership and refcounting. RX state constants define the receive parser stages: socklnd header, LNet header, parse handoff, payload, and slop skipping. Timeout helpers read mutable module tunables or LNet defaults.

## Dependencies
Depends on Linux kernel networking, TCP, kthreads, crypto CRC32, libcfs, LNet internals, and the wire IDL header. `SOCKNAL_RISK_KMAP_DEADLOCK` changes behavior by build configuration.

## Risks and test signals
Layout and bitfield widths affect concurrency and connection-count correctness. Refcount helper misuse can leak sockets or free live peers. Test coverage should stress lifecycle transitions, callback replacement/reset, RX parser state changes, zero-copy completion, typed vs untyped connections, and conns-per-peer bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_cb.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_cb.c

## Purpose
Implements socklnd's active data path and worker threads: TX allocation/free, LNet send entry, packet launch, RX state machine, scheduler loop, socket-read/write callbacks, hello negotiation wrappers, connection daemon loop, reconnect/backoff logic, keepalive, timeout scanning, ENOMEM retry, and reaper destruction.

## Important APIs and functions
TX functions include `ksocknal_alloc_tx`, `ksocknal_alloc_tx_noop`, `ksocknal_free_tx`, `ksocknal_tx_done`, `ksocknal_txlist_done`, `ksocknal_send`, `ksocknal_launch_packet`, `ksocknal_queue_tx_locked`, and `ksocknal_tx_prep`. RX functions include `ksocknal_new_packet`, `ksocknal_process_receive`, and `ksocknal_recv`. Worker entry points are `ksocknal_scheduler`, `ksocknal_connd`, and `ksocknal_reaper`. Connection setup helpers include `ksocknal_send_hello`, `ksocknal_recv_hello`, and `ksocknal_connect`.

## Control flow
`ksocknal_send` converts an LNet message into a `ksock_tx`, extracts page fragments, marks zero-copy eligibility, and calls `ksocknal_launch_packet`. Launch finds an existing matching connection, creates an on-demand peer when possible, starts connection attempts, or queues the TX on the peer until a connection arrives. Socket callbacks only mark readiness and queue the conn on the scheduler. The scheduler alternates RX and TX work: RX reads headers/payload fragments, calls `lnet_parse`, waits for `ksocknal_recv` to provide payload buffers, verifies checksums, handles zero-copy requests, and finalizes LNet messages. TX packs headers, sends nonblocking header/page fragments, handles partial sends, ENOMEM retry, zero-copy request tracking, health status, and connection closure on hard errors.

## State and persistence
State is volatile and list based. TX descriptors carry residual bytes, deadlines, connection refs, and health status until completion. Connections carry readiness/scheduled flags for each direction. `ksnd_connd_routes` and `ksnd_connd_connreqs` feed connection daemons. The reaper owns deathrow, zombie, and ENOMEM lists and periodically scans peer hash buckets for socket errors, RX/TX deadlines, stale queued TXs, stale zero-copy requests, and keepalive needs.

## Dependencies and integration points
Calls `socklnd.c` for peer/connection lifecycle, `socklnd_proto.c` through `ksock_proto`, `socklnd_lib.c` for socket I/O, LNet parse/finalize/notify APIs, acceptor connect helpers, and libcfs scheduler/CPT utilities.

## Risks and test signals
Most risks are race related: callbacks racing termination, `lnet_parse` racing `ksocknal_recv`, scheduler refs, ENOMEM reschedule, zero-copy ACK loss, and connection attempts racing passive accepts. Tests should exercise partial reads/writes, socket EOF mid-message, checksum injection, send error simulation, zero-copy request/ACK ranges, keepalive NOOPs, peer timeout detection, connd dynamic grow/shrink, and orderly unload with active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_lib.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_lib.c

## Purpose
Provides Linux socket-facing primitives used by the higher-level socklnd state machines: address discovery, capability checks, nonblocking send/receive, checksum calculation, socket option setup, callback install/reset, push/nodelay behavior, tunable inspection, and memory-pressure detection.

## Important APIs and functions
`ksocknal_lib_get_conn_addrs` snapshots peer/local socket addresses. `ksocknal_lib_zc_capable` checks route capabilities for scatter/gather and checksum offload. `ksocknal_lib_send_hdr`, `ksocknal_lib_send_kiov`, and `ksocknal_lib_recv` perform nonblocking I/O. `ksocknal_lib_csum_tx` computes v2 checksums. `ksocknal_lib_setup_sock` configures GFP_NOFS, linger, Nagle, buffers, keepalive, and TOS. Callback helpers save, set, and restore `sk_data_ready` and `sk_write_space`. `ksocknal_lib_memory_pressure` distinguishes retryable full-socket cases from ENOMEM-like stalls.

## Control flow
The scheduler calls send helpers without letting socket code mutate the driver's iov state. Header sends optionally compute checksum on first v2 send and use `MSG_MORE` when queued data remains. Payload sends use sendpage or `MSG_SPLICE_PAGES` for zero-copy-marked transfers, otherwise bvec iterators. Receive uses `sock_recvmsg` into the current iterator and accumulates checksum only for the protocol/data combinations that require it. Socket callbacks acquire global read locks, retrieve `sk_user_data`, and enqueue scheduler work or delegate to saved callbacks if termination already detached the conn.

## State and persistence
No standalone persistent state. It mutates connection address fields, RX checksum accumulator, socket callbacks, socket flags/options, and TCP Nagle/keepalive/TOS settings. Callback restoration is essential because sockets may outlive module code.

## Dependencies and integration points
Depends on Linux socket, TCP, bvec/iov iterator, page mapping, route capability, and compatibility macros. It is called by `socklnd.c` during connection creation/termination and by `socklnd_cb.c` during runtime I/O.

## Risks and test signals
Risks include callback lifetime races, checksum coverage mismatch across protocol versions, highmem mapping issues, kernel-version sendpage behavior, keepalive/TOS option failures, and false ENOMEM detection. Test with v2 checksums, v3/v4 checksum-off cases, zero-copy and non-zero-copy sends, callback reset under simultaneous socket readiness, configured buffer/keepalive/nagle/tos values, and kernels with and without `MSG_SPLICE_PAGES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_modparams.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_modparams.c

## Purpose
Declares socklnd module parameters, validates selected parameter values, exposes global tunable pointer tables, computes default `conns_per_peer`, and copies module/net defaults into per-NI LND tunables.

## Important APIs and functions
Parameters cover timeout, TX credits, peer credits, scheduler/connd counts, reconnect intervals, eager ACK, typed connections, bulk threshold, socket buffers, Nagle, round-robin, keepalive, checksum and checksum-error injection, zero-copy thresholds, IRQ affinity compatibility, `conns_per_peer`, route setup, optional TCP backoff, debug protocol override, and TOS. `ksocknal_tunables_init` populates `ksocknal_tunables` and `ksock_default_tunables`. `ksocknal_tunables_setup` merges module defaults with common LNet network tunables. `ksocklnd_lookup_conns_per_peer` estimates connections per peer from interface speed.

## Control flow
Module load registers parameters through `module_param*`. TOS uses a custom setter to allow -1 through 255 only. Interface speed lookup scans the NI namespace for the configured interface, supports IPv4 labels and IPv6 device-name matching, asks ethtool for speed, and maps Mbps to a small heuristic connection count. Init also caps zero-copy minimum payload and warns on removed IRQ affinity behavior.

## State and persistence
The file owns static module parameter storage for the module lifetime. `ksocknal_tunables` stores pointers to those variables, so runtime code observes current writable parameter values. `ksock_default_tunables` is copied into NIs that have not explicitly set LND tunables.

## Dependencies and integration points
Uses Linux module parameter APIs, ethtool, rtnl-protected netdevice enumeration, IPv4/IPv6 address lists, LNet NI/common tunable structs, and constants from `socklnd.h`.

## Risks and test signals
Risk areas include writable parameters changing while connections are active, speed lookup returning driver errors, IPv6 temporary-address selection, unit conversion for reconnect milliseconds, and `conns_per_peer` exceeding bitfield capacity. Tests should validate parameter bounds, TOS rejection, default merging, ethtool-failure fallback, IPv4 and IPv6 interface lookup, and that per-NI tunables are stable enough for active connection setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_modparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_proto.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_proto.c

## Purpose
Implements socklnd wire protocol variants v1, v2, v3, and v4. It owns hello serialization/deserialization, LNet header packing/unpacking, connection-type TX matching, zero-copy request/ACK handling, NOOP ACK piggybacking, and the exported `ksock_proto` operation tables.

## Important APIs and functions
Protocol tables `ksocknal_protocol_v1x`, `v2x`, `v3x`, and `v4x` provide callbacks consumed by the rest of socklnd. Queueing helpers include `ksocknal_queue_tx_msg_v1`, `ksocknal_queue_tx_msg_v2`, `ksocknal_queue_tx_zcack_v2`, `ksocknal_queue_tx_zcack_v3`, and `ksocknal_next_tx_carrier`. Matching functions are `ksocknal_match_tx`, `ksocknal_match_tx_v3`, and `ksocknal_match_tx_v4`. Handshake helpers are versioned send/receive functions. Pack/unpack helpers convert between LNet header forms and socklnd message layout.

## Control flow
V1 sends bare legacy LNet headers and has no NOOP or zero-copy support. V2/V3 use NID4 hello and `ksock_msg_hdr`; V4 uses the large-NID hello and NID16 LNet header. Normal TX queueing tries to replace queued NOOP zero-copy ACKs by piggybacking their cookie onto an LNet message. Zero-copy ACK queueing tries to piggyback on a carrier TX; v3/v4 can compact ACK cookies or ranges on ACK connections and ignore keepalive PING cookies. Incoming zero-copy requests find a matching ACK-capable connection or allocate a NOOP. Incoming ACKs remove matching TXs from the peer pending zero-copy request list.

## State and persistence
The file does not own global state but mutates connection TX queues, `ksnc_tx_carrier`, message cookie fields, peer zero-copy request lists, connection byte-order flip flags, and TX refs. Protocol tables are static read-only dispatch state.

## Dependencies and integration points
Depends on `socklnd-idl.h`, LNet NID4/NID16 conversion helpers, `lnet_sock_read/write`, `the_lnet.ln_testprotocompat`, and peer/connection helpers from `socklnd_cb.c`.

## Risks and test signals
Compatibility risk is high: v1/v2/v3/v4 peers must parse each other's hello and message formats correctly, including byte-swapped peers and protocol mismatch replies. Zero-copy cookie compaction must not lose or duplicate ACKs. Test mixed protocol negotiation, large-NID v4 peers, checksum-enabled v2 traffic, nonblocking ACK routes, keepalive PINGs, duplicate cookie detection, protocol compatibility injection bits, and typed-connection matching around the bulk threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/Makefile -->
# sources/distributed-fs/lustre-release/lnet/lnet/Makefile

## Purpose
Build definition for the LNet kernel module object. It declares `lnet.o` as a module and lists the object files linked into it, including socket acceptor and Adler checksum support.

## Important build entries
`obj-m += lnet.o` builds LNet as a module. `lnet-objs` aggregates core API/config/NID/string/RDMA/locking/message/memory descriptor/portal/socket/move/module/loopback/router/debugfs/acceptor/peer/fault/UDSP/crypto objects. `lnet-objs-$(CONFIG_SMP) = lib-cpt.o` adds CPT support when SMP is enabled. `lnet-objs += $(lnet-objs-y)` appends conditional objects. `CFLAGS_lnet_rdma.o` injects GDS/CUDA include paths. `CONFIG_GCOV_PROFILE_LNET` enables GCOV profiling.

## Control flow and integration
There is no runtime control flow. The file controls which compilation units participate in `lnet.o`, so changes directly affect symbol availability for socklnd and other LNDs. `acceptor.o` provides exported socket connection helpers used by socklnd. `adler.o` participates in LNet crypto checksum registration.

## State and persistence
Build-only state. It influences module composition and coverage instrumentation but stores no runtime state.

## Dependencies
Depends on kernel kbuild variables, optional `CONFIG_SMP`, optional `CONFIG_GCOV_PROFILE_LNET`, and environment variables for CUDA/GDS include directories.

## Risks and test signals
Removing or renaming objects can break unresolved symbols or omit required networking/crypto behavior. Test signals are successful kernel-module build, modpost symbol resolution, SMP and non-SMP builds, GCOV-profiled builds, and RDMA builds with valid/invalid CUDA or GDS include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/acceptor.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/acceptor.c

## Purpose
Implements LNet's TCP acceptor and outbound connect helper used by IP-based LNDs such as socklnd. It manages listen sockets per interface/port, accepts inbound socket requests, validates acceptor protocol headers, maps requested NIDs to local NIs, delegates accepted sockets to the selected LND, and creates outbound sockets from reserved ports.

## Important APIs and functions
Exports `lnet_acceptor_port`, `lnet_acceptor_port_bulk`, `lnet_acceptor_timeout`, `lnet_connect_console_error`, `lnet_acceptor_add_sockets`, `lnet_acceptor_remove_sockets`, `lnet_connect`, `lnet_acceptor_start`, and `lnet_acceptor_stop`. Internal objects include `struct listening_socket`, global `socket_list`, and `lnet_acceptor_state` with readiness, shutdown, completion, and original socket callback state.

## Control flow
`lnet_acceptor_add_sockets` binds listen sockets for control and optionally bulk ports and installs a data-ready callback that wakes the acceptor thread. `lnet_connect` chooses the correct destination port, iterates privileged local ports, connects, writes an acceptor request containing either NID4 or large-NID form, and returns the connected socket. The acceptor thread waits for readiness, snapshots active listen sockets, accepts nonblocking sockets, optionally enforces secure reserved-port sources, reads magic/version/NID, calls `lnet_accept`, and delegates to `ni->ni_net->net_lnd->lnd_accept`.

## State and persistence
Runtime state includes the listen socket list, per-listen refcounts, active socket count, original data-ready callback, acceptor shutdown flag, waitqueue, and completion. No disk persistence. Socket refs are deliberately dropped outside spinlocks.

## Dependencies and integration points
Depends on Linux sockets, network namespaces, LNet protocol structs/constants, NI lookup/refcounting, module parameters, and LND `lnd_accept` callbacks. Socklnd calls the exported add/remove/connect/timeout/port helpers.

## Risks and test signals
Risks include listen-socket callback restoration races, leaks on `lnet_acceptor_add_socket` error paths, secure-port policy surprises, acceptor protocol compatibility, NID4 vs NID16 parsing, and start/stop decisions tied to `lnet_count_acceptor_nets`. Tests should cover secure/all/none modes, multiple interfaces, bulk port distinct from control port, IPv4 and IPv6/large-NID connect requests, malformed magic/version, no matching NI, concurrent socket removal during accept, and stop while refs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/acceptor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/adler.c -->
# sources/distributed-fs/lustre-release/lnet/lnet/adler.c

## Purpose
Registers an LNet crypto API synchronous hash implementation named `adler32` backed by `zlib_adler32`. It lets LNet checksum code access Adler-32 through the kernel shash interface.

## Important APIs and functions
`adler32_cra_init` initializes the transform context seed to 1. `adler32_setkey` accepts a 32-bit seed. `adler32_init`, `adler32_update`, `adler32_final`, `adler32_finup`, and `adler32_digest` implement the shash lifecycle. Static `struct shash_alg alg` declares names, priority, optional-key flag, block size, digest size, context sizes, and callbacks. Public `cfs_crypto_adler32_register` and `cfs_crypto_adler32_unregister` register/unregister the algorithm.

## Control flow
Registration passes `alg` to `crypto_register_shash`. A digest operation initializes descriptor state from the transform seed, updates it with one or more buffers through `zlib_adler32`, and writes the resulting 32-bit value to the caller output. `digest` and `finup` share `__adler32_finup`.

## State and persistence
State is limited to per-transform seed (`cra_ctxsize`) and per-descriptor running checksum (`descsize`). There is no persistent storage.

## Dependencies and integration points
Depends on Linux crypto internal hash APIs and zlib. Built into `lnet.o` by the LNet Makefile and exposed through `adler.h` for LNet crypto registration paths.

## Risks and test signals
Risks include unaligned `u32` stores/loads through `u8 *`, host-endian digest interpretation, incorrect seed size, and registration name conflicts. Tests should cover register/unregister, default seed digest against known Adler-32 vectors, keyed seed behavior, update-vs-digest equivalence, zero-length input, and repeated module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/adler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/adler.h -->
# sources/distributed-fs/lustre-release/lnet/lnet/adler.h

## Purpose
Declares the Adler-32 crypto registration entry points implemented by `adler.c`.

## Important APIs
`cfs_crypto_adler32_register(void)` registers the shash algorithm. `cfs_crypto_adler32_unregister(void)` unregisters it.

## Control flow and integration
No executable control flow. Inclusion by LNet crypto/module code allows startup to install the algorithm and shutdown to remove it. The Makefile ensures `adler.o` is linked into the same module.

## State and persistence
No state is declared here. Runtime state lives inside the crypto registration object in `adler.c`.

## Dependencies
Relies on callers including appropriate kernel declarations for `int`/`void`; no include guard is present.

## Risks and test signals
The main risks are duplicate declarations if the header grows without guards and mismatches with `adler.c`. Test signals are clean compilation with warnings enabled and successful LNet crypto register/unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/lnet/adler.h -->
