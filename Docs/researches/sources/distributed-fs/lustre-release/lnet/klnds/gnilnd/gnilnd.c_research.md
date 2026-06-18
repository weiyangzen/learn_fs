# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd.c

## Purpose

`gnilnd.c` is the core module and lifecycle implementation for Lustre's Cray GNI LNet network driver. It registers `the_kgnilnd` with LNet, owns the global `kgnilnd_data` runtime object, creates and tears down GNI devices, nets, peers, connections, scheduler/dgram/reaper threads, and handles administrative peer/connection control paths. Message send/receive mechanics live in sibling files, but this file is the control-plane spine that makes those paths possible.

## Important APIs, Types, And Functions

- `the_kgnilnd`: the `struct lnet_lnd` exported to LNet with startup, shutdown, ctl, send, recv, eager recv, tunable, netlink, and timeout hooks.
- `kgnilnd_tun_defaults()`, `kgnilnd_nl_get()`, `kgnilnd_nl_set()`: bridge module tunables into LNet common and netlink-visible settings.
- `kgnilnd_thread_start()` and `kgnilnd_start_sd_threads()`: spawn worker threads and optionally bind scheduler threads to nonzero CPUs.
- Connection lifecycle: `kgnilnd_create_conn()`, `kgnilnd_find_conn_locked()`, `kgnilnd_find_or_create_conn_locked()`, `kgnilnd_destroy_conn_ep()`, `kgnilnd_destroy_conn()`.
- Connection ordering and cleanup: `kgnilnd_conn_isdup_locked()`, `kgnilnd_close_stale_conns_locked()`, `kgnilnd_close_conn_locked()`, `kgnilnd_close_conn()`, `kgnilnd_complete_closed_conn()`.
- Peer lifecycle and admin control: `kgnilnd_create_peer_safe()`, `kgnilnd_add_peer_locked()`, `kgnilnd_add_peer()`, `kgnilnd_del_conn_or_peer()`, `kgnilnd_del_peer_locked()`, `kgnilnd_cancel_peer_connect_locked()`, `kgnilnd_report_node_state()`, `kgnilnd_ctl()`.
- Purgatory handling: `kgnilnd_add_purgatory_locked()`, `kgnilnd_mark_for_detach_purgatory_all_locked()`, `kgnilnd_detach_purgatory_locked()`, `kgnilnd_release_purgatory_list()`.
- Device and module lifecycle: `kgnilnd_dev_init()`, `kgnilnd_dev_fini()`, `kgnilnd_base_startup()`, `kgnilnd_base_shutdown()`, `kgnilnd_startup()`, `kgnilnd_shutdown()`, `kgnilnd_init()`, `kgnilnd_exit()`.

## Control Flow

Module initialization runs via `late_initcall_sync(kgnilnd_init)`. Initialization sets tunables, sysctl/proc entries, `libcfs_setup()`, then registers `the_kgnilnd` with LNet. LNet calls `kgnilnd_startup()` for a network interface; the first interface triggers `kgnilnd_base_startup()`, which zeroes `kgnilnd_data`, initializes lock/list/table/cache state, creates GNI devices and completion queues, allocates FMA mailbox blocks, starts reaper/RCA/ruhroh/scheduler/dgram threads, and posts wildcard datagrams. `kgnilnd_startup()` then allocates a `kgn_net_t`, configures per-NI tunables, selects a GNI device, rewrites the NI address to the GNI device NID, and links the net into the global net hash.

Connection establishment is coordinated through peers and datagrams. `kgnilnd_find_or_create_conn_locked()` returns an established connection when one exists; otherwise it observes reconnect backoff and in-flight endpoint shutdown, marks the peer `GNILND_PEER_CONNECT`, queues it on the device connd list, and wakes datagram processing. `kgnilnd_set_conn_params()` binds the endpoint when needed, sets local/remote event data, initializes SMSG, records peer stamps, and updates timeout/reaper state.

Connection close is staged. `kgnilnd_close_conn_locked()` removes the connection from the CQ hash, marks it closing or closed depending on reset state, optionally puts it in purgatory, resets receive timeout state, and schedules the connection so a CLOSE can be sent. `kgnilnd_complete_closed_conn()` runs after the close message phase, cancels any remaining TX references from `gnc_tx_ref_table`, completes them with the connection error, destroys the endpoint, moves the connection to `GNILND_CONN_DONE`, unlinks it from peer lists when eligible, and notifies LNet. Purgatory is used when a peer may still have stale access to mailbox/MDD resources; the reaper later detaches and releases these resources.

Shutdown mirrors startup but must drain asynchronous state. `kgnilnd_shutdown()` marks the net shutting down, cancels datagrams, deletes peers/connections for that net, wakes quiesced threads if needed, waits for net references, unlinks the net, and calls `kgnilnd_base_shutdown()` when it was the last net. Base shutdown cancels wildcard datagrams, deletes all peers, waits for connections, stops ruhroh and worker threads, unmaps FMA blocks, destroys caches, frees hash tables, finalizes devices, and drops the module reference.

## State And Persistence Behavior

All durable state is in-kernel runtime state; this file writes no persistent on-disk data. The central state object is `kgnilnd_data`, which tracks init/shutdown/reset/quiesce flags, device array, net/peer/connection hash tables, thread counts, cache pointers, connection stamp generators, pending admin counters, and timeout data. LNet interface state is attached through `ni->ni_data` as `kgn_net_t`. Peers and connections are list/refcount managed, with ownership split across peer lists, CQ hash lists, scheduler lists, datagram queues, endpoint references, and TX descriptors. Correctness depends on `kgn_peer_conn_lock`, `kgn_net_rw_sem`, per-device locks, per-connection locks, atomics, and memory barriers such as `set_mb()`.

## Dependencies And Integration Points

The file integrates with LNet through `struct lnet_lnd`, `lnet_register_lnd()`, `lnet_unregister_lnd()`, `lnet_notify()`, NI tunables, and libcfs ioctls. It integrates with Cray GNI through wrapper functions from `gnilnd_api_wrap.h` for CDM, CQ, endpoint, SMSG, memory, error, and quiesce operations. It calls many sibling gnilnd modules through prototypes in `gnilnd.h`: datagram movement, scheduler/reaper/RCA, mailbox/FMA memory handling, transmit/receive logic, sysctl/proc, HSS/RCA node-state translation, and quiesce/reset handling.

## Risks And Edge Cases

- The code is highly sensitive to lock ordering and reference ownership. Many helpers require `kgn_peer_conn_lock` or `kgn_net_rw_sem`; violating those preconditions can create stale peer/connection lookups or premature frees.
- `kgnilnd_base_startup()` reuses loop variable `i` inside the per-device `gnd_dgrams` initialization loop, and `kgnilnd_base_shutdown()` similarly reuses `i` while freeing per-device dgram lists. That pattern can perturb the outer device loop and should be treated as a review hotspot.
- Connection stamp and CQID reuse are central safety boundaries. `kgnilnd_create_conn()` starts `gnc_next_tx` near wrap and asserts `GNILND_MAX_MSG_ID < GNILND_MSGID_CLOSE`, which shows wrap behavior is intentionally stress-prone.
- Purgatory is a correctness mechanism for stale remote mailbox/MDD access. Premature detach or missed `gnp_dirty_eps` accounting could corrupt reused mailbox memory.
- Shutdown paths contain long waits for pending refs, connections, threads, and net references. Missed decrefs can hang module unload or LNet shutdown.
- Loopback handling is special-cased in duplicate/stale connection logic and purgatory checks; it is easy to regress while changing connection-stamp comparisons.

## Test Signals

Useful signals are successful module registration/unregistration, LNet NI startup/shutdown, lctl peer/connection ioctls, peer health notifications, clean unload with zero peers/connections/threads/MDDs, and exercised fail locations from `gnilnd_api_wrap.h` such as CDM/CQ/EP/SMSG/RDMA/memory failures. High-value tests should cover duplicate connection negotiation, stale connection pruning, peer down/up events, admin `del_peer`/`disconnect`/`push`, reset/quiesce shutdown, purgatory release, and `kgn_npending_*` drain behavior.
