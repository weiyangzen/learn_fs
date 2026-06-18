# Research: subset-b-007104

Grouped research for GlusterD management, handshake, hooks, locks, log rotation, memory-type, and message-id source files. Each section preserves the source path in its title and is bounded for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-handshake.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-handshake.c

## Purpose
`glusterd-handshake.c` implements the server-side Gluster handshake RPC program and the GlusterD management handshake used between peers. It serves client volfile requests, event notifications, volume and snapshot metadata queries, and peer operating-version negotiation. It also contains the older dump-version discovery path used before switching to the management handshake program.

## Important APIs, Types, And Functions
Key exported entry points include `server_getspec`, `server_event_notify`, `server_get_volume_info`, `server_get_snap_info`, `glusterd_mgmt_hndsk_versions`, `glusterd_mgmt_hndsk_versions_ack`, `glusterd_mgmt_handshake`, `glusterd_peer_dump_version`, and `glusterd_set_clnt_mgmt_program`. The file defines the local management handshake procedure enum `GD_MGMT_HNDSK_*`, the random management handshake program number/version, RPC service program tables for `gluster_handshake_prog`, `gluster_cli_getspec_prog`, and `glusterd_mgmt_hndsk_prog`, and client program descriptors for dump and management handshake callbacks.

`build_volfile_path()` is central to client mounting. It maps requested volume identifiers into volfile paths for regular volumes, trusted internal volfiles, snapshots, snapd, glusterd-managed services, self-heal daemon, rebalance, gfproxy, and client-per-brick volfiles. `glusterd_get_args_from_dict()` parses getspec xdata and records client min/max op versions plus an optional brick name. `_client_supports_volume()` rejects client volfile requests whose version range cannot support the target volume's `client_op_version`.

Snapshot support is embedded in `get_snap_volname_and_volinfo()`, `glusterd_create_missed_snap()`, and `glusterd_take_missing_brick_snapshots()`. These functions parse `/snaps/...` paths, resolve snapshot volume information, create missed brick snapshots, mount/start snap bricks, and persist updated missed-snapshot state.

## Control Flow
`__server_getspec()` decodes a `gf_getspec_req`, normalizes the requested volume key into `req->trans->peerinfo.volname`, parses xdata, checks client/volume op-version compatibility, chooses trusted or untrusted volfile path based on local address detection, builds a connected peer host list in response xdata, stats and reads the volfile, optionally creates missed snapshots for the requested brick, and replies with `gf_getspec_rsp`.

`__server_event_notify()` handles event notifications, currently dispatching `GF_EN_DEFRAG_STATUS` into `glusterd_defrag_event_notify_handle()` and suppressing a response for that asynchronous update. Unknown events are logged and surfaced through `gf_event()`.

The management handshake flow starts with `glusterd_peer_dump_version()`, which sends `GF_DUMP_DUMP` to a peer. `__glusterd_peer_dump_version_cbk()` inspects the returned program list. If the management handshake program is present, it calls `glusterd_mgmt_handshake()`. Otherwise, it falls back to program assignment only when the local op-version is compatible with old peers. `glusterd_mgmt_handshake()` sends `GD_MGMT_HNDSK_VERSIONS` with the local peer UUID. `__glusterd_mgmt_hndsk_version_cbk()` validates the peer's min/max/current op-version and sends a `GD_MGMT_HNDSK_VERSIONS_ACK` containing the local op-version. `__glusterd_mgmt_hndsk_version_ack_cbk()` installs peer RPC program pointers, emits child-up notification, and injects `GD_FRIEND_EVENT_CONNECTED` where appropriate.

On the server side, `__glusterd_mgmt_hndsk_versions()` authenticates the requester with `gd_validate_mgmt_hndsk_req()`, then replies with current, min, and max op-version. `__glusterd_mgmt_hndsk_versions_ack()` accepts the selected cluster op-version, validates that it is not beyond local support and does not reduce an existing-volume cluster, stores it in `conf->op_version`, and persists it with `glusterd_store_global_info()`.

## State And Persistence Behavior
The file mutates `req->trans->peerinfo` with volname and client op-version data, writes `conf->op_version`, updates peer program pointers (`mgmt`, `peer`, `mgmt_v3`), and can transition peer state through the friend state machine. It persists op-version changes through `glusterd_store_global_info()`, snapshot volinfo changes through `glusterd_store_volinfo()`, and missed snapshot lists through `glusterd_store_update_missed_snaps()`. Volfile serving reads generated volfiles from the GlusterD workdir and adds response xdata such as peer brick servers or service pidfiles.

## Dependencies And Integration Points
This file integrates with RPC/XDR (`xdr_to_generic`, `glusterd_submit_reply`, `glusterd_submit_request`), GlusterD volume and snapshot stores, service-volfile builders, peer management (`glusterd_peerinfo_find*` under RCU), the friend/op state machines, and transport address utilities. Its RPC program structs are registered by GlusterD initialization and consumed by clients, peers, CLI getspec, and internal daemons.

## Risks
Volfile path construction accepts many string formats and must avoid truncation, bad tokenization, and stale snapshot paths. Trusted volfile selection depends on local-address detection; mistakes can bypass auth policy for external clients or block internal services. Peer handshake validation mixes UUID and hostname matching for compatibility with older peers, so reinstall/reused hostname cases are sensitive. `conf->op_version` reduction is blocked when volumes exist, but any missed validation can create cluster incompatibility. The missed-snapshot creation path performs storage and brick-start side effects during mount/volfile serving, so failures need careful persistence and retry handling.

## Test Signals
Useful tests include getspec requests for normal, trusted, snapshot, service, rebalance, gfproxy, and client-per-brick volfile IDs; version-range rejection for incompatible clients; management handshake between compatible peers, incompatible peers, unknown peers, and peers with changed UUIDs; op-version ACK persistence and downgrade rejection when volumes exist; `GF_EN_DEFRAG_STATUS` event handling; volume UUID and snapshot-info queries; and missed-snapshot creation on brick reconnect with store updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-handshake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.c

## Purpose
`glusterd-hooks.c` implements GlusterD's commit hook framework. It creates the hook directory hierarchy, maps volume-management operations to hook subdirectories, executes enabled hook scripts with operation-specific command-line arguments, and runs post-commit hooks asynchronously through a worker thread.

## Important APIs, Types, And Functions
The operation-to-directory table `glusterd_hook_dirnames[GD_OP_MAX]` maps selected operations such as create, delete, start, stop, add-brick, remove-brick, set, reset, and gsync-create to hook directory names. `glusterd_hooks_create_hooks_directory()` builds `<workdir>/hooks/1/<op>/{pre,post}` for every operation with a hook directory. `glusterd_hooks_get_hooks_cmd_subdir()` returns the mapped directory name.

Script argument helpers include `glusterd_hooks_add_working_dir()`, `glusterd_hooks_add_op()`, `glusterd_hooks_add_hooks_version()`, `glusterd_hooks_add_custom_args()`, `glusterd_hooks_set_volume_args()`, and the switch-based `glusterd_hooks_add_op_args()`. `glusterd_hooks_run_hooks()` discovers enabled hook scripts, sorts them, builds runner commands, and executes them. Queue/worker APIs are `glusterd_hooks_post_stub_enqueue()`, `glusterd_hooks_stub_init()`, `glusterd_hooks_stub_cleanup()`, `glusterd_hooks_priv_init()`, and `glusterd_hooks_spawn_worker()`.

## Control Flow
Hook setup runs during GlusterD startup: the base hooks directory and versioned pre/post subdirectories are created for every mapped operation. A hook script is enabled only when its filename starts with `S` and does not match rpm backup suffixes such as `*.rpmsave` or `*.rpmnew`.

For synchronous hook execution, callers pass a hook path, operation, op context dict, and pre/post type to `glusterd_hooks_run_hooks()`. It requires `volname` in the op context, opens the directory, collects enabled entries into a growable array, sorts them with `glusterd_compare_lines()`, then runs each script as `<hooks_path>/<script> --volname=<volname> ...`. Operation-specific arguments add flags such as `--first=yes/no` for start-volume, `--last=yes/no` for stop-volume, `-o key=value` for set-volume, hook version, volume operation name, GlusterD workdir, custom `hooks_args`, and special transport address-family data when shared storage is enabled.

For asynchronous post hooks, `glusterd_hooks_post_stub_enqueue()` copies the script directory and op context into a `glusterd_hooks_stub_t`, pushes it to `hooks_priv->list` under a mutex, increments `waitcount`, and signals the worker condition variable. `hooks_worker()` waits indefinitely, removes one stub at a time, decrements `waitcount`, executes post hooks with `GD_COMMIT_HOOK_POST`, and frees the stub.

## State And Persistence Behavior
Persistent filesystem state is the hook directory tree under GlusterD's workdir. Runtime state is held in `glusterd_hooks_private_t`: a linked-list queue, mutex, condition variable, worker thread, and debug wait count. Each queued stub owns a duplicated script path and a referenced copy of the operation context dict. The file does not store durable hook execution history; success and failures are emitted to Gluster logs through `runner_log()`.

## Dependencies And Integration Points
The hooks layer uses Gluster's `runner_t` execution API, dict APIs, `mkdir_p`, syscall wrappers, GlusterD volume lists, and memory types from `glusterd-mem-types.h`. `glusterd.c` creates directories and spawns the worker. `glusterd-mgmt.c` invokes pre and post commit hooks around volume transactions. `glusterd-store.c` uses the header helper for hook-friendly user namespace keys.

## Risks
Hook scripts are external executables and run with GlusterD-supplied arguments, so argument construction and dict contents matter. `glusterd_hooks_add_custom_args()` appends a single `hooks_args` string via runner formatting; callers must ensure this value is safe and expected. The worker thread has no shutdown path in this file and loops forever. Queue growth is unbounded apart from memory availability. Post-hook failures are logged but do not retry or roll back committed operations. Directory creation or path formatting failures at startup can disable hooks for all operations.

## Test Signals
Test coverage should verify hook directory creation for every mapped op, skipping operations with empty directory names; enabled script filtering and deterministic sort order; argument sets for start/stop first/last volume transitions, set-volume key/value pairs, shared-storage transport family injection, add-brick, reset, and gsync-create; failed script logging without aborting later scripts; asynchronous enqueue/dequeue behavior with dict reference cleanup; and behavior when `volname`, `count`, or script directories are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.h

## Purpose
`glusterd-hooks.h` declares the public interface and private data structures for GlusterD's hook subsystem. It is the contract between hook execution code, GlusterD startup, operation commit code, and store code that filters hook-friendly keys.

## Important APIs, Types, And Functions
`GLUSTERD_GET_HOOKS_DIR(path, version, priv)` formats the versioned hooks directory as `<workdir>/hooks/<version>`. `GLUSTERD_HOOK_VER` is currently `1`. `GD_HOOKS_SPECIFIC_KEY` is `user.*`, used by `is_key_glusterd_hooks_friendly()` to identify user-namespace keys that hooks may preserve or expose.

`glusterd_commit_hook_type_t` defines hook phases: none, pre, post, and max. `glusterd_hooks_private_t` owns the asynchronous post-hook queue, mutex, condition variable, worker thread, and wait counter. `glusterd_hooks_stub_t` stores one queued hook run: list node, script directory, operation context dict, and operation id.

Declared functions cover directory creation, command-subdirectory lookup, hook execution, worker spawning, stub allocation/cleanup, post-stub enqueue, and private-state initialization.

## Control Flow
Callers use this header in three main paths. Startup calls `glusterd_hooks_create_hooks_directory()` and `glusterd_hooks_spawn_worker()`. Transaction commit code calls `glusterd_hooks_run_hooks()` for immediate pre hooks and enqueues post hooks through `glusterd_hooks_post_stub_enqueue()`. Store code calls `is_key_glusterd_hooks_friendly()` to permit only `user.*` keys under hook-specific behavior.

## State And Persistence Behavior
The header itself stores no state, but it defines the queue structures that become `glusterd_conf_t.hooks_priv` at runtime. The directory macro encodes the persistent on-disk hook layout and ties it directly to `glusterd_conf_t.workdir`.

## Dependencies And Integration Points
It depends on `fnmatch.h`, Gluster's `gf_boolean_t`, `dict_t`, list primitives, pthreads, `xlator_t`, and `glusterd_op_t` from surrounding headers. Its memory type usage is coordinated with `glusterd-mem-types.h`.

## Risks
The directory macro writes into a caller-provided buffer and sets `path[0] = 0` only if `snprintf()` returns a negative value; truncation is not explicitly handled in the macro. `is_key_glusterd_hooks_friendly()` relies on `THIS->name` for debug logging and assumes a non-null key. Any new hook phase requires updating both enum consumers and directory creation logic.

## Test Signals
Tests should exercise the hooks directory macro with normal and long workdirs, `user.*` matching and nonmatching keys, phase enum assumptions in directory creation, stub lifecycle behavior, and compile-time inclusion from both hook implementation and store/management code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.c

## Purpose
`glusterd-locks.c` implements GlusterD management v3 local lock ownership. It tracks transaction locks for volumes, snapshots, and global entities, provides single and multi-entity lock/unlock operations, and attaches timers that eventually clear stale locks.

## Important APIs, Types, And Functions
`valid_types[]` defines lockable entity classes: `vol` defaults to locked, while `snap` and `global` default to not held unless the transaction dict requests them. Public lifecycle functions are `glusterd_mgmt_v3_lock_init()`, `glusterd_mgmt_v3_lock_fini()`, `glusterd_mgmt_v3_lock_timer_init()`, and `glusterd_mgmt_v3_lock_timer_fini()`. Public lock APIs are `glusterd_mgmt_v3_lock()`, `glusterd_mgmt_v3_unlock()`, `glusterd_multiple_mgmt_v3_lock()`, and `glusterd_multiple_mgmt_v3_unlock()`. `gd_mgmt_v3_unlock_timer_cbk()` is the stale-lock timeout callback.

Static helpers include `glusterd_mgmt_v3_is_type_valid()`, `glusterd_get_mgmt_v3_lock_owner()`, `glusterd_release_multiple_locks_per_entity()`, `glusterd_acquire_multiple_locks_per_entity()`, `glusterd_mgmt_v3_lock_entity()`, and `glusterd_mgmt_v3_unlock_entity()`.

## Control Flow
Startup initializes two dicts in `glusterd_conf_t`: `mgmt_v3_lock` for `glusterd_mgmt_v3_lock_obj` entries and `mgmt_v3_lock_timer` for associated `gf_timer_t *` pointers. A single lock call validates `name` and `type`, constructs the key `<name>_<type>`, checks whether an owner UUID already exists, allocates a lock object with the requester UUID, stores it in `mgmt_v3_lock`, duplicates the key for timer data, schedules `gd_mgmt_v3_unlock_timer_cbk()` after `priv->mgmt_v3_lock_timeout`, resets the timeout to `GF_LOCK_TIMER`, and stores the timer pointer in `mgmt_v3_lock_timer`.

Unlock validates the key and owner UUID, deletes the owner from `mgmt_v3_lock`, retrieves and cancels the timer, removes the timer dict entry, and resets `volinfo->stage_deleted` if a delete transaction failed after staging the volume. Owner mismatch and missing-lock cases are rejected.

Multi-lock acquisition walks `valid_types[]`. For each type, it evaluates `hold_<type>_locks` from the transaction dict, then locks either `<type>name` or numbered `<type>nameN` entries based on `<type>count`. If any lock fails, it releases the locks already acquired for that entity and then releases all previously acquired entity types. Multi-unlock mirrors this process but attempts all entity types and records the last failure.

The timer callback receives the duplicated key, deletes the lock object, optionally deletes DEBUG backtrace metadata, retrieves its timer pointer, frees timer data, cancels the timer, and logs cleanup.

## State And Persistence Behavior
Lock state is in-memory only under `glusterd_conf_t`. It is not persisted across GlusterD restarts. Timer timeout state uses `conf->mgmt_v3_lock_timeout`, which can be temporarily overridden by management handlers using a request dict `timeout`, then reset after scheduling. DEBUG builds also store a `debug.last-success-bt-<key>` string in the lock dict. Unlock may mutate volume runtime metadata by clearing `stage_deleted` if the volume still exists.

## Dependencies And Integration Points
The file depends on Gluster dicts, UUID utilities, timers, volume lookup, logging message IDs, and the management v3 RPC handlers in `glusterd-mgmt-handler.c`. Management initiation code and syncop code call these APIs locally and remotely. Statedump code inspects `priv->mgmt_v3_lock`. The lock key contract is dictated by transaction dictionaries produced by volume, snapshot, and global operation paths.

## Risks
There is a fragile constant relationship between `GF_MAX_LOCKING_ENTITIES` and the length of `valid_types[]`; adding a type without updating the constant can make successful multi-locks look failed. The dicts are global process state, so callers rely on the big GlusterD lock or external serialization rather than internal per-dict locking. Error paths around timer storage can leave an owner lock without a valid timer if partial setup changes are not fully undone. The timer callback clears locks without checking transaction liveness, so very long operations need correct timeout extension. Lock key formatting with `PATH_MAX` rejects truncation but still depends on names fitting within that bound.

## Test Signals
Tests should cover valid and invalid entity types, single lock/unlock success, already-held lock returning `EG_ANOTRANS`, owner mismatch rejection, timer cancellation on unlock, stale timer unlock, timeout override reset, single and counted multi-lock dict layouts, rollback on partial multi-lock failure, global/snap `hold_*_locks` toggles, `stage_deleted` reset on unlock, and DEBUG backtrace key cleanup where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.h

## Purpose
`glusterd-locks.h` declares the management v3 lock object, valid lock entity descriptor, lifecycle hooks, lock/unlock APIs, multi-lock helpers, and stale-lock timer callback used across GlusterD management code.

## Important APIs, Types, And Functions
`glusterd_mgmt_v3_lock_obj` stores the UUID of the lock owner. `glusterd_valid_entities` describes each entity type name and whether locks should be held by default for that type. The public API initializes and tears down the lock and timer dicts, acquires/releases single locks by key and type, acquires/releases multiple entity locks from a transaction dict, and exposes `gd_mgmt_v3_unlock_timer_cbk()` for timer registration.

## Control Flow
Management handlers and syncop code include this header to acquire local locks before transaction phases and release them after completion. The multi-lock functions interpret transaction dictionaries containing keys such as `volname`, `volcount`, `volname1`, `hold_snap_locks`, and similar snap/global variants.

## State And Persistence Behavior
The header defines state shape only. Runtime instances live in `glusterd_conf_t.mgmt_v3_lock` and `glusterd_conf_t.mgmt_v3_lock_timer`; they are in-memory dictionaries and are not persisted by this interface.

## Dependencies And Integration Points
Consumers must provide Gluster types such as `dict_t`, `uuid_t`, `gf_boolean_t`, and `uint32_t` through surrounding includes. The header is consumed by management RPC handlers, syncop transaction code, startup/shutdown initialization, and statedump diagnostics.

## Risks
The API accepts raw `char *type` values and only validates them in the C implementation. Callers must pass stable transaction dicts with the exact key naming convention expected by multi-lock functions. Adding a new lock entity requires coordinated updates to the implementation's valid type table, max entity constant, transaction dict builders, RPC handlers, and tests.

## Test Signals
Compile and integration tests should ensure all declared functions match implementation signatures, lock object UUID storage is statedump-readable, multi-lock key conventions remain stable, and timer callback linkage remains valid for `gf_timer_call_after()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-log-ops.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-log-ops.c

## Purpose
`glusterd-log-ops.c` implements the CLI-facing and operation-state-machine pieces of volume log rotation. It decodes log-rotate requests, validates target volume/brick state, and performs local brick logfile rename plus `SIGHUP` to trigger log reopening.

## Important APIs, Types, And Functions
`glusterd_handle_log_rotate()` wraps `__glusterd_handle_log_rotate()` in the GlusterD big lock. `glusterd_op_stage_log_rotate()` validates the operation during the op-sm stage phase. `glusterd_op_log_rotate()` performs the commit work on local bricks. The operation uses dict keys `volname`, optional `brick`, and internally added `rotate-key`.

## Control Flow
The request handler decodes `gf_cli_req`, unserializes the dict, extracts `volname`, logs the request, writes `rotate-key` with the current time, and starts the transaction through `glusterd_op_begin_synctask(req, GD_OP_LOG_ROTATE, dict)`. On early failure it sends a CLI response with an explanatory message.

The stage function requires `volname`, verifies the volume exists, rejects stopped volumes, and optionally validates a specific `brick` against the volume. Absence of a brick is treated as "all bricks" and is not an error.

The commit function retrieves the volume and rotate key, optionally parses a specific brick into temporary brickinfo, iterates local bricks for the volume, skips remote bricks, filters to the requested brick if present, reads the brick pidfile, renames the current logfile to `<logfile>.<rotate-key>`, and sends `SIGHUP` to the brick process. If the request named one brick, it stops after that brick. If no local matching brick exists, it treats the operation as successful for this node.

## State And Persistence Behavior
The handler mutates the operation dict by adding a timestamp rotate key so every node uses the same suffix. The commit path changes filesystem state by renaming brick logfiles and signals running brick processes. It does not update persistent GlusterD store metadata. Temporary brickinfo allocated for requested brick parsing is deleted before return.

## Dependencies And Integration Points
The file integrates with CLI XDR, GlusterD op-sm/synctask execution, volume and brick lookup utilities, pidfile path macros, syscall wrappers, and process signaling. It relies on brick processes honoring `SIGHUP` by reopening logs after the old file has been renamed.

## Risks
The implementation reads pidfiles and sends signals directly; stale pidfiles can signal the wrong process if process reuse is possible. Rename failure is logged as a warning but does not immediately abort before `SIGHUP`, which may still rotate from the brick process's perspective depending on logger behavior. Missing pidfiles or unreadable pidfiles fail the operation for local matching bricks. Requested brick parsing must match hostname/path formatting exactly.

## Test Signals
Tests should cover request decode/unserialize failures, missing `volname`, stopped volume rejection, unknown brick rejection, all-bricks rotation across only local bricks, single-brick filtering, missing local brick success, pidfile open/read failures, logfile rename failure logging, `SIGHUP` failure, and use of a consistent `rotate-key` across staged/commit execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-log-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mem-types.h

## Purpose
`glusterd-mem-types.h` assigns GlusterD-specific memory accounting type IDs. These IDs are passed to `GF_MALLOC`, `GF_CALLOC`, and related allocation helpers so memory usage can be attributed to management subsystem structures.

## Important APIs, Types, And Functions
The file defines `gf_gld_mem_types_t`, starting at `gf_common_mt_end + 1` and ending at `gf_gld_mt_end`. Entries cover GlusterD configuration, peers, friend/op state machine contexts, lock/stage/commit contexts, probe contexts, volume and brick info, defrag info, pending node lists, brick response contexts, line buffers, mount specs, geo-replication specs, hooks stubs/private state, snapshot structures, service and brick process structures, pmap registry entries, and generic char/int/hostname helpers.

## Control Flow
There is no runtime control flow. The enum is included by GlusterD source files and referenced at allocation sites. For this subset, `glusterd-hooks.c` uses `gf_gld_mt_hooks_stub_t`, `gf_gld_mt_hooks_priv_t`, and `gf_gld_mt_charptr`, while management handlers use context memory types such as `gf_gld_mt_op_lock_ctx_t`.

## State And Persistence Behavior
The enum contributes to process memory accounting and diagnostics only. It does not persist state. Numeric stability matters because IDs are consumed by allocator/accounting code after compilation.

## Dependencies And Integration Points
It depends on `<glusterfs/mem-types.h>` for the common memory type range and is integrated throughout GlusterD's allocation paths. Adding a new memory type should happen before `gf_gld_mt_end` and must not collide with common types.

## Risks
Removing or reordering enum values can confuse diagnostics and any code assuming stable allocation categories. Using an overly generic type for new allocations makes leak accounting less useful. Forgetting to add a GlusterD-specific type for a long-lived allocation can obscure subsystem memory growth.

## Test Signals
Build tests catch missing enum names. Runtime leak/accounting tests should verify high-volume paths, especially hook queue and mgmt lock contexts, are attributed to meaningful GlusterD memory types. Review allocation changes for correct type selection and no use beyond `gf_gld_mt_end`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-messages.h -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-messages.h

## Purpose
`glusterd-messages.h` defines the append-only structured logging message IDs and selected message strings for the GlusterD component. It lets GlusterD code log with stable identifiers through `gf_msg()` and `gf_smsg()`.

## Important APIs, Types, And Functions
The core macro invocation `GLFS_MSGID(GLUSTERD, ...)` declares a long ordered list of `GD_MSG_*` identifiers covering quorum, peer/brick disconnects, store failures, snapshot operations, management v3 phases, lock errors, handshake/version negotiation, georeplication, rebalance, volume operations, service management, brick validation, bitrot/scrub, NFS-Ganesha, tiering, transport, and many other GlusterD domains. The comments explicitly require new IDs to be appended, never removed, to prevent ID reuse.

The latter part of the file defines string macros such as `GD_MSG_INVALID_ENTRY_STR`, `GD_MSG_DICT_GET_FAILED_STR`, `GD_MSG_BRICK_NOT_FOUND_STR`, `GD_MSG_VOL_NOT_STARTED_STR`, `GD_MSG_CREATE_DIR_FAILED_STR`, `GD_MSG_FILE_OP_FAILED_STR`, and `GD_MSG_DICT_ALLOC_AND_SERL_LENGTH_GET_FAIL_STR`.

## Control Flow
There is no executable control flow. Including this header makes the generated message IDs available to C files. In this subset, hooks, locks, log ops, handshake, and management handlers all use these IDs to identify error, warning, info, debug, and trace messages.

## State And Persistence Behavior
The file influences log compatibility rather than runtime state. Message IDs are effectively part of GlusterD's external observability contract; log parsers, documentation, and support tooling can depend on them being stable.

## Dependencies And Integration Points
It depends on `<glusterfs/glfs-message-id.h>` and must use the `GLUSTERD` component name known by that infrastructure. Every GlusterD C file that emits structured logs includes this header. Message string macros are consumed where a reusable human-readable error phrase is needed.

## Risks
The largest risk is changing ID order or deleting IDs, which can cause the same numeric ID to refer to a different condition across releases. Typographical mistakes in identifiers can become permanent once shipped. Adding a log call with a poorly matched message ID reduces diagnostic value. The file is large and manually maintained, so merge conflicts and duplicate semantic entries are possible.

## Test Signals
Build tests should catch missing or duplicated identifiers at compile time. Review and static checks should enforce append-only changes and component-name correctness. Runtime tests can assert that high-risk paths, such as management v3 lock failures, handshake rejections, hook failures, and log rotation errors, emit the expected structured IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt-handler.c -->
# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt-handler.c

## Purpose
`glusterd-mgmt-handler.c` implements the server-side RPC actor table for GlusterD management v3 transactions. It receives peer requests for lock, pre-validate, brick-op, commit, post-commit, post-validate, and unlock phases, validates peer identity, decodes serialized dictionaries, invokes the matching management v3 phase function, and returns XDR responses.

## Important APIs, Types, And Functions
The file exposes `glusterd_handle_mgmt_v3_lock()` and `glusterd_handle_mgmt_v3_unlock()` as public big-locked handlers. Static handlers cover the remaining phase actors: pre-validate, brick-op, commit, post-commit, and post-validate. Each phase has a send-response helper, such as `glusterd_mgmt_v3_pre_validate_send_resp()`, `glusterd_mgmt_v3_commit_send_resp()`, and `glusterd_mgmt_v3_post_commit_send_resp()`.

Lock/unlock paths have two modes. If request dict key `is_synctasked` is true, `glusterd_synctasked_mgmt_v3_lock()` or `glusterd_syctasked_mgmt_v3_unlock()` directly calls `glusterd_multiple_mgmt_v3_lock()` or `glusterd_multiple_mgmt_v3_unlock()` and sends a response. Otherwise, `glusterd_op_state_machine_mgmt_v3_lock()` or unlock injects `GD_OP_EVENT_LOCK`/`GD_OP_EVENT_UNLOCK` into the op state machine using a `glusterd_op_lock_ctx_t`.

The file defines `gd_svc_mgmt_v3_actors[]` and exports `gd_svc_mgmt_v3_prog`, with `.synctask = _gf_true`.

## Control Flow
Every handler follows a common pattern: decode the XDR request from `req->msg[0]`; reject garbage args; verify `uuid` belongs to a known peer with `glusterd_peerinfo_find_by_uuid()`; allocate and unserialize input dicts where needed; allocate response dicts for phase functions; call the relevant `gd_mgmt_v3_*_fn()` operation implementation; serialize response dict and error string into the matching XDR response; free XDR-allocated dict buffers and unref Gluster dicts; return `0` after response submission to avoid double deletion of the RPC request.

For lock requests, the handler also reads a `timeout` value from the dict and sets `conf->mgmt_v3_lock_timeout` to `timeout + 120` before taking locks. Ownership of the lock context differs by path: direct synctasked handling frees it in the handler; state-machine injection transfers ownership unless injection fails.

Wrapper functions run all actors under `glusterd_big_locked_handler()`, serializing access to global GlusterD management state.

## State And Persistence Behavior
The file itself does not persist store data, but it drives operations that do. It mutates in-memory transaction/op-state by storing transaction opinfo for non-synctasked locks, injecting op-sm events, and invoking phase functions that may stage or commit persistent volume/snapshot changes. It can temporarily adjust `conf->mgmt_v3_lock_timeout`. Response dictionaries carry peer-local results back to the transaction coordinator.

## Dependencies And Integration Points
It integrates with management v3 phase functions declared in `glusterd-mgmt.h`, lock APIs from `glusterd-locks.h`, op-sm transaction info helpers, peer identity lookup, XDR types for `gd1_mgmt_v3_*`, Gluster dict serialization, and the RPC service registration path in GlusterD startup. It is the inbound peer counterpart to outbound mgmt v3 calls in syncop and rpc-ops code.

## Risks
The handlers trust only known peer UUIDs, so peer-list correctness is a security and consistency boundary. Several allocation failures return `-1` before the usual cleanup in the immediate branch, so memory ownership must be reviewed when modifying. Returning nonzero from a handler can cause RPC request lifetime issues; existing code often sends a response and then forces `0`. The typo in `glusterd_syctasked_mgmt_v3_unlock` is harmless but easy to repeat. Timeout changes are global in `conf` until the lock layer resets them after scheduling, so concurrent lock requests rely on the big lock for correctness.

## Test Signals
Tests should cover each actor's XDR decode failure, unknown peer rejection, dict unserialize failure, phase function failure with error string, response dict serialization failure, direct synctasked lock/unlock behavior, state-machine lock/unlock injection behavior, timeout override, cleanup of `op_errstr` and dict buffers, actor table procedure mapping, and no double-free/double-reply behavior under failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt-handler.c -->
