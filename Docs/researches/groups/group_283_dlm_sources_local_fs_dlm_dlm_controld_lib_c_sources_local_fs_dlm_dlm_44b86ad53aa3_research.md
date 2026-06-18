# Group Research: group_283_dlm_sources_local_fs_dlm_dlm_controld_lib_c_sources_local_fs_dlm_dlm_44b86ad53aa3

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/local-fs/dlm`, which is included in subset A. I read each listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/lib.c -->
# File Research: sources/local-fs/dlm/dlm_controld/lib.c

This file implements the user-facing `libdlmcontrol` client library for talking to `dlm_controld` over abstract AF_UNIX sockets. It wraps control and query commands into `struct dlmc_header` messages, sends them to `DLMC_SOCK_PATH` or `DLMC_QUERY_SOCK_PATH`, and decodes fixed-size or dump-style replies.

Key behavior:
- `do_read()` and `do_write()` perform full-buffer blocking I/O with EINTR retry. `do_write()` handles short writes by advancing an offset.
- `do_connect()` opens an abstract UNIX socket by writing the path into `sun_path[1]`, so no filesystem socket node is used.
- `init_header()` stamps `DLMC_MAGIC`, `DLMC_VERSION`, total length, command, optional name, flags/data/option fields as needed by each call.
- Dump APIs use `do_dump()` and a static 1 MiB `copy_buf`: `dlmc_dump_debug`, `dlmc_dump_config`, `dlmc_dump_log_plock`, `dlmc_dump_plocks`, and `dlmc_dump_run`.
- Control APIs send one-shot commands: `dlmc_reload_config`, `dlmc_set_config`, `dlmc_deadlock_check`, `dlmc_fence_ack`.
- Query APIs fetch structured data: `dlmc_lockspace_info`, `dlmc_node_info`, `dlmc_lockspaces`, `dlmc_lockspace_nodes`.
- Filesystem integration APIs keep a persistent fd: `dlmc_fs_connect`, `dlmc_fs_register`, `dlmc_fs_unregister`, `dlmc_fs_notified`, `dlmc_fs_result`.
- Cluster command execution APIs are `dlmc_run_start()` and `dlmc_run_check()`, using fixed `DLMC_RUN_COMMAND_LEN` command buffers and UUID strings returned through the header name field.
- `dlmc_print_status()` is more than a raw client call: it consumes streamed daemon state records, parses key/value strings with `kv()` and `ks()`, sorts node ids, and prints human-readable cluster/fence/startup status.

Important dependencies:
- Protocol constants and `struct dlmc_header` come from `dlm_controld.h`.
- Public structs and flags come from `libdlmcontrol.h`.
- `DLM_LOCKSPACE_LEN` comes from Linux DLM constants.
- The query/status format is tightly coupled to `main.c` query handlers and daemon state emitters elsewhere in `dlm_controld`.

Notable implementation details:
- Status parsing is simple substring/key scanning, not a structured parser.
- `dlmc_lockspace_nodes()` intentionally reads a maximum-sized reply even though the daemon may return fewer bytes; it uses `rh->data` and supports `-E2BIG`.
- `dlmc_run_check()` may reuse a single connection and retry once per second until `wait_sec` expires while status remains `DLMC_RUN_STATUS_WAITING`.
- `dlmc_set_config()` and `dlmc_run_start()` copy input into fixed 1024-byte buffers, truncating at `DLMC_RUN_COMMAND_LEN - 1`.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/lib.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/libdlmcontrol.h -->
# File Research: sources/local-fs/dlm/dlm_controld/libdlmcontrol.h

This header is the public API contract for `libdlmcontrol`. It exposes dump, status, lockspace/node query, filesystem notification, fencing acknowledgement, and distributed run-command interfaces.

Key declarations:
- `DLMC_DUMP_SIZE` defines 1 MiB client dump buffers.
- Node flags include membership/start/disallowed/fencing/check-fs state bits.
- `struct dlmc_node` reports node id, flags, add/remove sequence numbers, fail reason, and fail timestamps.
- `struct dlmc_change` captures lockspace change state: member/join/remove/fail counts, wait condition/message state, sequence, and combined sequence.
- `struct dlmc_lockspace` exposes previous and next changes, lockspace flags, global id, and name.
- `DLMC_NODES_ALL`, `DLMC_NODES_MEMBERS`, and `DLMC_NODES_NEXT` define `dlmc_lockspace_nodes()` views.
- `DLMC_STATUS_VERBOSE` selects verbose status formatting.
- Filesystem result types are `DLMC_RESULT_REGISTER` and `DLMC_RESULT_NOTIFIED`.
- Run-command constants define UUID/command lengths, start behavior flags, check behavior flags, and status bits.

Important dependencies:
- The header uses `uint32_t`, `uint64_t`, and `DLM_LOCKSPACE_LEN`, so consumers need integer typedefs and DLM constants available through include ordering or surrounding package headers.
- Function implementations live in `lib.c`; daemon-side protocol handling lives in `main.c`.

Notable details:
- The comments document lockspace node views carefully, especially the difference between completed and in-progress change groups.
- Run-command semantics are cluster-wide: one node requests command execution, each daemon helper executes locally when selected, and the originator collects replies.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/libdlmcontrol.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/libdlmcontrol.pc.in -->
# File Research: sources/local-fs/dlm/dlm_controld/libdlmcontrol.pc.in

This is the pkg-config template for the `libdlmcontrol` development package.

It defines:
- `prefix=@PREFIX@`
- `includedir=${prefix}/include`
- `libdir=@LIBDIR@`
- Package name `libdlmcontrol`
- Description `The dlmcontrol library`
- Version `4.0.0`
- Compile flags `-I${includedir}`
- Link flags `-L${libdir} -ldlmcontrol`

The build system substitutes `@PREFIX@` and `@LIBDIR@`. There is no conditional logic in this file.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/libdlmcontrol.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/linux_endian.h -->
# File Research: sources/local-fs/dlm/dlm_controld/linux_endian.h

This header provides Linux-style endian conversion macros in userspace using glibc `<endian.h>` and `<byteswap.h>`.

Key behavior:
- On big-endian systems, big-endian conversions are identity and little-endian conversions byte-swap.
- On little-endian systems, little-endian conversions are identity and big-endian conversions byte-swap.
- It defines `be16_to_cpu`, `be32_to_cpu`, `be64_to_cpu`, `cpu_to_be16`, `cpu_to_be32`, `cpu_to_be64`, `le16_to_cpu`, `le32_to_cpu`, `le64_to_cpu`, `cpu_to_le16`, `cpu_to_le32`, and `cpu_to_le64`.
- It includes an Alpha-specific replacement for `bswap_64`.

Used by:
- `plock.c` for marshaling `struct dlm_plock_info`, plock checkpoint data, and resource metadata into little-endian wire/storage format.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/linux_endian.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/linux_helpers.h -->
# File Research: sources/local-fs/dlm/dlm_controld/linux_helpers.h

This header is a small userspace copy of Linux helper macros needed by local kernel-derived headers.

It defines:
- `static_assert()` wrapper around C11 `_Static_assert`.
- `__same_type()` using GCC `__builtin_types_compatible_p`.
- Poison pointers `LIST_POISON1` and `LIST_POISON2`.
- `container_of()` with type checking.
- `READ_ONCE()` and `WRITE_ONCE()` volatile access helpers.

Used by:
- `list.h`
- `rbtree.h`
- `rbtree_augmented.h`

Important detail:
- This file assumes GCC/Clang extensions: `typeof`, statement expressions, and `__builtin_types_compatible_p`.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/linux_helpers.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/list.h -->
# File Research: sources/local-fs/dlm/dlm_controld/list.h

This is a userspace copy of Linux `include/linux/list.h`, backed by helpers from `linux_helpers.h`. It provides intrusive circular doubly linked list primitives used throughout `dlm_controld`.

Covered functionality:
- List declaration and initialization: `struct list_head`, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`.
- Add/delete/move/replace/swap operations: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_move`, `list_move_tail`, `list_replace`, `list_replace_init`, `list_swap`.
- Bulk and splice operations: `list_bulk_move_tail`, `list_cut_position`, `list_cut_before`, `list_splice`, `list_splice_tail`, `list_splice_init`, `list_splice_tail_init`.
- State predicates: `list_empty`, `list_is_first`, `list_is_last`, `list_is_head`, `list_is_singular`.
- Entry helpers: `list_entry`, first/last/or-null helpers, next/prev helpers, circular next/prev helpers.
- Iteration macros: raw list iteration, reverse iteration, safe iteration, typed entry iteration, continuation/from/reverse variants, and safe variants.
- `list_count_nodes()` counts entries in a list.

Used heavily by:
- Lockspace lists and run-operation lists in `main.c`.
- Cluster node tracking in `member.c`.
- Plock resource, lock, waiter, pending, and saved-message lists in `plock.c`.
- Other daemon modules outside this group.

Notable details:
- Debug list validation hooks are stubbed out unless `CONFIG_DEBUG_LIST` is defined.
- Deleted entries are poisoned, which helps catch accidental reuse.
- Because it is intrusive, lifetime management is entirely the caller’s responsibility.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/logging.c -->
# File Research: sources/local-fs/dlm/dlm_controld/logging.c

This file implements synchronous logging for `dlm_controld`: syslog, optional logfile, stderr in debug mode, and in-memory circular dump buffers.

Key behavior:
- `init_logging()` sets default syslog/logfile priorities, creates log directories with restrictive permissions, opens the logfile, marks it close-on-exec, and calls `openlog()`.
- `close_logging()` closes syslog and logfile state.
- `set_logfile_priority()` raises logfile verbosity to `LOG_DEBUG` when `debug_logfile` is enabled.
- `log_level()` formats messages with monotonic timestamp and optional lockspace/name prefix.
- General messages are saved into `log_dump`; plock-tagged messages are also saved into `log_dump_plock`.
- `copy_log_dump()` and `copy_log_dump_plock()` copy circular-buffer contents for daemon query replies.

Important dependencies:
- Uses daemon options through `opt()` and `dlm_options`.
- Uses constants from daemon headers: `DEFAULT_SYSLOG_FACILITY`, `DEFAULT_SYSLOG_PRIORITY`, `DEFAULT_LOGFILE_PRIORITY`, `DEFAULT_LOGFILE`, `LOG_DUMP_SIZE`, `LOG_PLOCK`, `LOG_NONE`.
- Query serving in `main.c` exposes these buffers through `DLMC_CMD_DUMP_DEBUG` and `DLMC_CMD_DUMP_LOG_PLOCK`.

Notable details:
- Logging is not internally mutex-protected here; `main.c` serializes daemon/query access with `query_mutex` for many paths, but general signal/thread interactions should be understood in that context.
- The logfile timestamp uses wall clock, while message body starts with monotonic time.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/logging.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/main.c -->
# File Research: sources/local-fs/dlm/dlm_controld/main.c

This is the main executable entry point and event loop for `dlm_controld`. It initializes options, logging, Corosync, configfs, kernel DLM monitoring, uevent handling, client sockets, query sockets, plocks, and optional helper-process command execution.

Major areas:
- Client/poll management: dynamic arrays of `struct client` and `struct pollfd`, with `client_add`, `client_dead`, `client_ignore`, and `client_back`.
- I/O helpers: daemon-local `do_read()` and `do_write()`.
- Helper process: `setup_helper()` forks `run_helper()`, uses nonblocking pipes, receives `DLM_MSG_RUN_REPLY`, sends run requests/cancels, and tracks helper heartbeats.
- Run operations: `start_run_operation()`, `find_run()`, `check_run_operation()`, and `clear_run()` maintain cluster-wide helper command state and result counts.
- Lockspace creation and lookup: `create_ls()`, `find_ls()`, and `find_ls_id()`.
- Filesystem registration: tracks fs-controlled lockspaces via an internal `fs_register_list`.
- Kernel uevents: `setup_uevent()` opens `NETLINK_KOBJECT_UEVENT`; `process_uevent()` handles DLM `online` and `offline` events by joining/leaving lockspaces.
- Query thread: `process_queries()` listens on `DLMC_QUERY_SOCK_PATH`, validates headers, locks `query_mutex`, and serves dump/status/lockspace/node requests.
- Control socket: `process_listener()` and `process_connection()` handle `DLMC_SOCK_PATH` commands such as fs register/notified, run start/check, reload config, and dynamic set config.
- Main loop: `loop()` initializes subsystems in order, enters `poll()`, dispatches fds, processes deferred fencing/lockspace/plock work, and tears down on exit.
- Option handling: `set_opt_defaults()`, `set_opt_cli()`, `get_ind_name()`, `get_ind_letter()`, `get_dlm_option()`, and `print_usage()`.
- Process singleton: `lockfile()` creates runtime dirs, takes an fcntl write lock, writes pid, and `unlink_lockfile()` cleans up.

Startup order in `loop()`:
1. Start query thread and control listener.
2. Connect Corosync cfg.
3. Check uncontrolled kernel lockspaces.
4. Unfence local node.
5. Load node config and quorum cluster service.
6. Discover misc devices and configure configfs.
7. Set up monitor fd, configfs members, uevent socket, daemon CPG, protocol, plocks, and optional helper fd.
8. Notify systemd if enabled.
9. Allow fencing only after protocol setup.

Important interactions:
- `member.c` supplies Corosync cfg/quorum setup and cluster membership callbacks.
- `plock.c` supplies `/dev/misc/dlm_plock` handling and state dump.
- `logging.c` supplies debug/config/plock dump buffers.
- `action.c`/other daemon modules outside this group supply configfs/kernel operations, CPG, fencing, and lockspace transition logic.
- `lib.c` is coupled to command handling and query reply layouts here.

Notable details:
- Query serving is moved to a separate thread because the main thread may block on sysfs writes.
- `query_mutex` serializes query snapshots against main-loop state changes.
- Shutdown is ignored if active lockspaces remain after SIGTERM/SIGINT.
- `process_connection()` validates magic and major protocol version, but command-specific extra payload sizes rely on command logic.
- The option parser supports long options, short options, boolean shorthand, bundled boolean letters, `--name=value`, and environment override `DLM_CONTROLD_DEBUG`.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/member.c -->
# File Research: sources/local-fs/dlm/dlm_controld/member.c

This file connects `dlm_controld` to Corosync quorum/cfg/cmap APIs and translates cluster membership into DLM configfs node state.

Key state:
- Corosync cfg handle `ch` and quorum handle `qh`.
- Old and current quorum node arrays.
- A list of `struct node_cluster` records containing node id, cluster add time, and remove time.
- A `leavejoin_nodes` array for nodes that appear in both joined and left lists in one ring transition.

Key behavior:
- `quorum_nodelist_callback()` logs joined/left nodes and records leave-join nodes.
- `quorum_callback()` updates quorate/ring state, tracks add/remove times, removes configfs nodes for departed members, handles leave-join as remove-plus-add, and creates configfs comms nodes for new members using Corosync node addresses.
- `cluster_add_time()` exposes a node’s add timestamp.
- `is_cluster_member()` checks current quorum list.
- `process_cluster()` and `update_cluster()` dispatch quorum callbacks.
- `setup_cluster()` initializes quorum model v1 tracking and returns its fd for the main poll loop.
- `setup_cluster_cfg()` initializes cfg, retries transient startup failures, gets cfg fd and local node id, and rejects negative node ids.
- `kick_node_from_cluster()` asks Corosync to shut down locally or kill a remote node.
- `shutdown_callback()` allows Corosync shutdown only when no lockspaces are active.
- `setup_node_config()` reads Corosync cmap nodelist entries, adds startup-fencing nodes when enabled, and detects two-node quorum mode.

Important dependencies:
- Calls `add_configfs_node()` and `del_configfs_node()` to mirror membership into kernel DLM configfs.
- Uses `node_config_get()` to apply per-node marks.
- Uses global daemon state: `our_nodeid`, `cluster_quorate`, `cluster_ringid_seq`, `cluster_two_node`, `cluster_joined_*`, `fence_delay_begin`, and lockspace list.
- Uses fencing startup hooks such as `add_startup_node()`.

Notable details:
- The code copies old quorum membership before replacing it, then computes removals/additions by array scans.
- The address pointer `addrptr` points to the stack `addrs` array and is indexed for every address returned by Corosync.
- `setup_node_config()` treats cmap failure to read `quorum.two_node` as non-fatal.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/member.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/node_config.c -->
# File Research: sources/local-fs/dlm/dlm_controld/node_config.c

This file parses optional per-node DLM configuration from a text file, currently only `mark` values.

Key behavior:
- Static `nc[MAX_NODES]` stores per-node `struct node_config`.
- `nc_default` has `.mark = 0`.
- `node_config_init(path)` opens the config file; if missing, it logs and uses default zero marks.
- It skips comments and blank lines.
- It parses lines of the form `node id=<nodeid> mark=<value>`.
- Invalid line syntax returns `-EINVAL`; invalid node ids are skipped.
- `node_config_get(nodeid)` returns `nc_default` for out-of-range ids, otherwise the array entry.

Important dependencies:
- Included through `dlm_daemon.h`, with `MAX_NODES`, logging, and integer format macros.
- Consumed by `member.c` when creating configfs comms nodes.

Notable details:
- Static storage starts zeroed, so unconfigured in-range nodes effectively get mark 0.
- `strtoul()` is used with base 0 for decimal/hex-style input.
- The overflow/error check compares to `ULONG_MAX` but does not inspect `errno`.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/node_config.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/node_config.h -->
# File Research: sources/local-fs/dlm/dlm_controld/node_config.h

This header declares the per-node configuration interface.

It defines:
- `struct node_config { uint32_t mark; }`
- `node_config_init(const char *path)`
- `node_config_get(int nodeid)`

The comments define return semantics for configuration lookup/parsing:
- `-ENOENT` means the path or node config is absent.
- Other negative errors indicate config problems.
- `0` means config was found with no problems.

The implementation in `node_config.c` currently treats a missing file as non-fatal default configuration and returns `0`.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/node_config.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/plock.c -->
# File Research: sources/local-fs/dlm/dlm_controld/plock.c

This file implements user-space coordination of DLM POSIX locks (`plocks`) through `/dev/misc/dlm_plock` and cluster messages. It tracks byte-range locks per resource, waiters, optional resource ownership, saved messages during joins, checkpoint-style state transfer, and purge/drop behavior.

Core data structures:
- `struct resource`: one lock resource by number, with owner state, flags, last access time, lists of locks/waiters/pending ops, and an rb-tree node.
- `struct posix_lock`: byte range, owner, pid, nodeid, exclusive/shared mode, and flags.
- `struct lock_waiter`: waiting plock request.
- `struct save_msg`: deferred cluster plock messages saved while a joining node synchronizes state.
- `struct resource_data` and `struct plock_data`: little-endian packed data used for plock state transfer.

Major behavior:
- `setup_plocks()` opens `/dev/misc/dlm_plock` and initializes rate counters.
- `process_plocks()` reads kernel plock requests, identifies the lockspace by fsid, applies rate limiting, and either broadcasts replicated plocks or routes through ownership logic.
- Non-ownership mode replicates each plock to all nodes and frees empty resources eagerly.
- Ownership mode lets a resource have owner `-1` unknown, `0` unowned/replicated, or a nodeid owner. Pending local ops wait until ownership is established.
- `receive_plock()`, `receive_own()`, `receive_sync()`, and `receive_drop()` handle cluster messages, with save-and-replay if `ls->save_plocks` is active.
- Range operations are handled by `lock_internal()` and `unlock_internal()`, using `ranges_overlap()` and `overlap_type()` to split, shrink, convert, or remove locks.
- Waiters are queued on conflicts, canceled through `DLM_PLOCK_OP_CANCEL`, and retried by `do_waiters()` after unlocks/purges.
- `send_all_plocks_data()` serializes local plock state into bounded messages for a joining node; `receive_plocks_data()` reconstructs it.
- `clear_plocks_data()` frees synchronized state.
- `purge_plocks()` removes locks/waiters for a failed node or all locks on unmount, resets owner state when needed, and wakes waiters.
- `copy_plock_state()` formats a human-readable plock dump for query clients.
- `drop_resources_all()` periodically drops unused owned/unowned resources according to `drop_resources_*` options.
- `limit_plocks()` throttles kernel plock reads based on `plock_rate_limit`.

Important dependencies:
- Uses Linux DLM plock ABI from `<linux/dlm_plock.h>`.
- Uses local rb-tree code for fast resource lookup by number.
- Uses local list primitives for resources, locks, waiters, pending ops, and saved messages.
- Uses `linux_endian.h` conversions for cross-node state.
- Uses daemon messaging functions such as `dlm_send_message()` and message types `DLM_MSG_PLOCK*`.
- Uses global daemon options: `enable_plock`, `plock_ownership`, `plock_rate_limit`, and drop-resource tuning.

Notable details:
- GETLK operations from remote nodes are ignored; only local GET replies are written back to the kernel.
- CLOSE unlocks skip result replies and clear waiters for the same owner.
- Ownership transitions are carefully documented with race scenarios around drop, own, and plock messages.
- Locks marked `P_SYNCING` are excluded from checkpoint data because they will be delivered by sync messages.
- `MAX_SEND_SIZE` is 1024 bytes, so large resource state is split into continuation chunks.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/plock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree.c -->
# File Research: sources/local-fs/dlm/dlm_controld/rbtree.c

This is a userspace copy of Linux `lib/rbtree.c`. It implements red-black tree insertion, deletion/rebalancing, replacement, and traversal.

Provided functions:
- `rb_insert_color()`
- `rb_erase()`
- `__rb_insert_augmented()`
- `__rb_erase_color()`
- `rb_first()`, `rb_last()`
- `rb_next()`, `rb_prev()`
- `rb_replace_node()`
- `rb_first_postorder()`, `rb_next_postorder()`

Implementation characteristics:
- Parent pointer and color are stored together in `__rb_parent_color`.
- Rotations use `WRITE_ONCE()` for child pointer updates.
- Non-augmented erase/insert use dummy callbacks so augmented logic is optimized out.
- Augmented operation support delegates propagation/copy/rotate work through callbacks declared in `rbtree_augmented.h`.

Used by:
- `plock.c`, which stores plock resources in `ls->plock_resources_root` keyed by resource number.

Notable details:
- Comments include Linux’s lockless lookup caveats: traversals may miss subtrees during concurrent rotations, but should not loop or return invalid elements if pointer stores obey the constraints.
- In `dlm_controld`, tree use appears single-threaded/serialized by daemon state locks rather than relying on lockless lookup semantics.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree.h -->
# File Research: sources/local-fs/dlm/dlm_controld/rbtree.h

This is a userspace copy of Linux `include/linux/rbtree.h`. It declares rb-tree APIs and provides inline helper algorithms.

Key contents:
- Includes `linux_helpers.h` and `rbtree_types.h`.
- Defines `rb_parent`, `rb_entry`, `RB_EMPTY_ROOT`, `RB_EMPTY_NODE`, and `RB_CLEAR_NODE`.
- Declares core exported functions from `rbtree.c`.
- Defines `rb_link_node()`.
- Provides cached-root helpers: `rb_first_cached`, `rb_insert_color_cached`, `rb_erase_cached`, `rb_replace_node_cached`.
- Provides generic inline helpers: `rb_add_cached`, `rb_add`, `rb_find_add`, `rb_find`, `rb_find_first`, `rb_next_match`, and `rb_for_each`.
- Provides postorder safe iteration macro `rbtree_postorder_for_each_entry_safe`.

Used by:
- `plock.c` resource indexing.
- `rbtree_augmented.h` and `rbtree.c`.

Important constraints:
- Users provide their own comparison/search logic for performance and type control.
- Like the Linux original, the generic helper functions expect callback operators defining ordering.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree_augmented.h -->
# File Research: sources/local-fs/dlm/dlm_controld/rbtree_augmented.h

This is a userspace copy of Linux `include/linux/rbtree_augmented.h`. It supports rb-trees with per-subtree augmented metadata.

Key contents:
- `struct rb_augment_callbacks` with `propagate`, `copy`, and `rotate` callbacks.
- `rb_insert_augmented()` and `rb_insert_augmented_cached()`.
- Macro templates `RB_DECLARE_CALLBACKS` and `RB_DECLARE_CALLBACKS_MAX`.
- Color and parent helpers: `RB_RED`, `RB_BLACK`, `rb_color`, `rb_is_red`, `rb_is_black`, `rb_set_parent`, `rb_set_parent_color`.
- `__rb_change_child()` and `__rb_erase_augmented()`.
- `rb_erase_augmented()` and cached variant.

Used by:
- `rbtree.c`, which includes this header for both augmented and non-augmented erase/insert internals.

Notable details:
- The comments explicitly say most of the header is implementation detail; public consumers should generally depend only on callbacks and augmented insert/erase APIs.
- The current plock resource tree does not use augmented metadata, but the full support is present.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree_augmented.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree_types.h -->
# File Research: sources/local-fs/dlm/dlm_controld/rbtree_types.h

This header defines the rb-tree storage types copied from Linux.

It provides:
- `struct rb_node` with packed parent/color field and left/right child pointers.
- `struct rb_root`.
- `struct rb_root_cached` with an O(1) leftmost pointer.
- Initializers `RB_ROOT` and `RB_ROOT_CACHED`.

Used by:
- `rbtree.h`, `rbtree_augmented.h`, `rbtree.c`, and `plock.c`.

Notable detail:
- `struct rb_node` is aligned to `sizeof(long)`, matching the Linux implementation’s assumptions for storing color bits in low pointer bits.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_controld/rbtree_types.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/Makefile -->
# File Research: sources/local-fs/dlm/dlm_sand/Makefile

This Makefile builds the `dlm_sand` executable.

Key settings:
- Default install-style variables: `PREFIX=/usr`, `LIBNUM=/lib64`, `BINDIR=$(PREFIX)/sbin`.
- `USE_SD_NOTIFY ?= yes` is defined but not directly used in this file fragment.
- Binary target: `dlm_sand`.
- Sources: `action.c`, `config.c`, `crc32c.c`, `log.c`, `main.c`, and `ondisk.c`.
- Includes: `../include` and `../dlm_controld`.
- Compiler flags emphasize hardening and warnings: `_FORTIFY_SOURCE=2`, stack protector, stack clash protection, PIE, relro/now.
- Libraries: `pthread`, `rt`, `uuid`, and `sanlock`.

Targets:
- `all` builds `dlm_sand`.
- `clean` removes objects, shared libraries, and the binary.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/action.c -->
# File Research: sources/local-fs/dlm/dlm_sand/action.c

This file manages kernel DLM sysfs/configfs state for `dlm_sand`. It creates and removes cluster communication nodes, lockspaces, lockspace members, kernel control attributes, and related runtime kernel settings.

Major paths:
- Sysfs DLM lockspaces: `/sys/kernel/dlm`.
- Configfs cluster root: `/sys/kernel/config/dlm/cluster`.
- Spaces: `/sys/kernel/config/dlm/cluster/spaces`.
- Comms: `/sys/kernel/config/dlm/cluster/comms`.

Key behavior:
- `check_uncontrolled_lockspaces()` detects abandoned kernel lockspaces and fails if any exist.
- `stop_kernel()`, `start_kernel()`, `stop_kernel_leave()`, and `start_kernel_join()` write DLM sysfs control/event/id/nodir attributes.
- `read_configfs_space_members()` loads current configfs membership for a lockspace.
- `add_configfs_lockspace()` creates a lockspace directory.
- `add_configfs_node()` creates a comms node, writes nodeid, binary socket address, optional mark, and local flag.
- `del_configfs_node()` removes a comms node directory.
- `add_configfs_member()` creates a lockspace node directory, writes nodeid, and writes weight from `get_weight()`.
- `del_configfs_member()` removes a lockspace member directory.
- `clear_configfs_comms()`, `clear_configfs_space_nodes()`, and `clear_configfs_spaces()` remove stale configfs state.
- `add_configfs_base()` verifies configfs and DLM configfs are mounted/loaded and creates cluster root if needed.
- `set_configfs_opt()` writes cluster-level options.
- `setup_configfs_options()` clears old state, sets selected DLM options, sets protocol and mark, raises SCTP receive buffers, enables recover callbacks, and sets cluster name `dlm_sand`.
- `setup_misc_devices()` discovers `/proc/misc` minors and waits for `/dev/misc/dlm-control` and `/dev/misc/dlm-monitor`.

Important dependencies:
- Uses `sand_internal.h` for globals, constants, options, lockspace structure, and `do_write()`.
- Uses `config.c` for `get_weight()`.
- Uses logging helpers from `log.c`.
- Kernel ABI assumptions are embedded in sysfs/configfs filenames and binary address write format.

Notable details:
- `add_configfs_node()` treats missing `mark` attribute as non-fatal because older kernels may not support it.
- `set_proc_rmem()` raises `/proc/sys/net/core/rmem_default` and `rmem_max` to 4 MiB for SCTP.
- `find_minors()` has a `found == 3` break condition despite tracking two named devices; harmless but inconsistent.
- Directory member discovery currently trusts directory names as node ids and comments that reading each nodeid attribute would be better.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/action.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/config.c -->
# File Research: sources/local-fs/dlm/dlm_sand/config.c

This file parses `dlm_sand` configuration from `dlm.conf` and supports runtime option changes through socket commands.

Lockspace/master config:
- `get_weight()` returns lockspace member weight. If no masters are configured, all nodes default to weight 1; if masters exist, non-masters default to 0.
- `setup_lockspace_config()` scans `lockspace <name> ...` lines, applies `nodir=`, and then reads following `master <name> node=<id> [weight=<w>]` lines through `read_master_config()`.
- Master entries populate arrays on the lockspace: node ids and weights.

Option-file config:
- `set_opt_file(update)` parses `DLM_CONF_PATH`, looks up known option names, applies values by type, respects CLI precedence, and optionally reloads only reloadable options.
- It tracks scanned options during update so removed/commented reloadable file options can be reset.
- Parsing helpers handle int, uint, and string `key=value` forms.

Dynamic config:
- `set_opt_online(cmd_str, cmd_len)` tokenizes a command string into at most `MAX_AV_COUNT` arguments with limited escaping.
- `restore_all` clears all dynamic settings.
- `name=restore` clears one dynamic setting.
- Reloadable options can be changed dynamically and `reload_setting()` applies side effects.
- `reset_dynamic()` and `reset_opt_value()` restore effective values according to priority: CLI, file, default.

Reload side effects:
- `log_debug` writes configfs `log_debug`.
- `debug_logfile` changes logfile priority.

Important dependencies:
- Uses option metadata and helpers from `sand_internal.h`: `dlm_options`, `opt()`, `optu()`, `opts()`, option indexes, request argument types.
- Uses `path_exists()` and `set_configfs_opt()` from `action.c`.
- Uses logging from `log.c`.

Notable details:
- File option precedence is conservative: explicit CLI values are never overridden by file reloads.
- Dynamic settings have top priority while set.
- `get_val_str()` uses `strcpy()` into caller-provided fixed buffers; current callers pass `MAX_LINE` buffers.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/config.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/crc32c.c -->
# File Research: sources/local-fs/dlm/dlm_sand/crc32c.c

This file implements table-driven CRC-32C.

Key contents:
- A static 256-entry CRC-32C table for reflected input/output using polynomial `0x1EDC6F41`.
- Public function `uint32_t crc32c(uint32_t crc, uint8_t *data, size_t length)`.

Behavior:
- Iterates byte by byte.
- Updates `crc` as `crc32c_table[(crc ^ *data++) & 0xFF] ^ (crc >> 8)`.
- Returns the final crc accumulator.

Origin:
- Comments say it was copied from btrfs-progs, which copied from the kernel `lib/libcrc32c.c`.

Likely use:
- Included in the `dlm_sand` binary and presumably used by `ondisk.c` or related sanlock/on-disk metadata code outside this group.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/crc32c.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/dlm_sand_sock.h -->
# File Research: sources/local-fs/dlm/dlm_sand/dlm_sand_sock.h

This header defines the local socket protocol for `dlm_sand`.

Key constants:
- Control socket path: `DLM_SD_SOCK_PATH` = `dlm_sd_sock`.
- Query socket path: `DLM_SDQ_SOCK_PATH` = `dlm_sd_query_sock`.
- Magic: `DLM_SD_MAGIC` = `0x20240307`.
- Version: `DLM_SD_VERSION` = `0x00010001`.
- Control commands: reload config and set config.
- Query commands: dump status, dump config, dump debug.
- Dump size: `DLM_SD_DUMP_SIZE` = 1 MiB.

Main structure:
- `struct dlm_sd_header` contains magic, version, command, option, length, flags, integer data, padding field named `unsued`, and a name buffer sized `DLM_LOCKSPACE_LEN + 8`.

Important dependencies:
- Requires `DLM_LOCKSPACE_LEN` from DLM constants through include context.
- Consumed by `dlm_sand` main/query/control code outside this file list.

Notable detail:
- The field name `unsued` is misspelled but part of the C struct layout; changing it is source-visible even though layout would remain identical.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/dlm_sand_sock.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/list.h -->
# File Research: sources/local-fs/dlm/dlm_sand/list.h

This is an older/smaller userspace copy of Linux intrusive doubly linked list helpers for `dlm_sand`.

Provided functionality:
- `container_of`, poison pointers, and `struct list_head`.
- Initialization and declaration macros.
- Add/delete/move operations: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_move`, `list_move_tail`.
- Empty checks: `list_empty`, `list_empty_careful`.
- Splice helpers: `list_splice`, `list_splice_init`.
- Entry and iteration macros: `list_entry`, `list_first_entry`, raw iteration, reverse iteration, safe iteration, typed entry iteration, typed reverse iteration, continuation, and typed safe iteration.

Differences from `dlm_controld/list.h`:
- It does not use `READ_ONCE`/`WRITE_ONCE`.
- It has fewer helper macros and no debug validation stubs.
- It defines its own `container_of` without the stronger static type assertion used by `linux_helpers.h`.

Used by:
- `dlm_sand` structures via `sand_internal.h` and related source files.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/log.c -->
# File Research: sources/local-fs/dlm/dlm_sand/log.c

This file implements asynchronous logging for `dlm_sand`.

Key state:
- `log_dump`: in-memory circular dump buffer for query responses.
- `log_ents`: circular array of pending entries for file/syslog output.
- Mutex and condition variable protect logging state.
- A background thread drains entries and writes to logfile/syslog.
- `log_dropped` counts messages dropped when the pending-entry ring is full.

Key behavior:
- `setup_logging()` initializes priorities, stderr behavior, opens `LOG_FILE_PATH`, allocates the entry ring, calls `openlog()`, and starts the log thread.
- `log_level()` formats timestamped messages, stores every message in the dump ring, queues messages meeting logfile/syslog thresholds, optionally writes to stderr, and signals the logging thread.
- `copy_log_dump()` copies the circular dump buffer under the log mutex.
- `log_thread_fn()` waits for pending entries, writes dropped-entry notices, and calls `write_entry()`.
- `close_logging()` signals shutdown, joins the thread, closes syslog and logfile.
- `set_logfile_priority()` raises logfile verbosity to debug when `debug_logfile` is enabled.

Important dependencies:
- Uses options from `sand_internal.h`: `daemon_debug`, `debug_logfile`, and logging priority globals.
- Uses macros from `log.h` for callers.
- Query handling outside this group can expose the dump buffer.

Notable details:
- This logger is more thread-friendly than `dlm_controld/logging.c`: formatting and queueing are mutex-protected, while file/syslog writes happen in a worker thread.
- If the log entry ring fills, messages are dropped but a later “dropped N entries” notice is written.
- `write_dropped()` formats without a newline, unlike normal log entries.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/log.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/dlm/dlm_sand/log.h -->
# File Research: sources/local-fs/dlm/dlm_sand/log.h

This header declares `dlm_sand` logging macros and the printf-checked `log_level()` function.

Key contents:
- `log_level(char *ls_name, int level, const char *fmt, ...)` with GCC printf format checking.
- Convenience macros:
  - `log_debug`
  - `log_space`
  - `log_warn`
  - `log_warns`
  - `log_error`
  - `log_erros`
  - `log_info`
  - `log_print`

Intended severity destinations:
- Errors go to syslog and the `dlm_sand` logfile.
- Warnings/info go to the logfile.
- Debug goes to the in-core dump buffer unless debug output is enabled.

Notable detail:
- `log_erros(space, ...)` expands to `log_level(ls->name, ...)` but the macro parameter is named `space`; this appears inconsistent and would only compile correctly where an `ls` identifier is in scope. It may be unused or a typo.

<!-- END FILE RESEARCH: sources/local-fs/dlm/dlm_sand/log.h -->