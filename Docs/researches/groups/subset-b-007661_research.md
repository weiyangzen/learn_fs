# Research: subset-b-007661

This grouped report covers three Lustre MDT source files. Each file section is bounded with the reconciliation markers required by the research cron so it can be split into the source-tree-aligned per-file artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_batch.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_batch.c

## Purpose

`mdt_batch.c` implements the MDT-side handler for Lustre batch metadata update RPCs, currently with a very narrow supported operation set. The registered top-level MDT handler is `mdt_batch(struct tgt_session_info *tsi)`, wired from the normal MDT target handler table as `MDS_BATCH`. It parses a `BUT_HEADER_MAGIC` batch update request, optionally receives large request buffers through PTLRPC bulk GET, creates a batched reply capsule, iterates embedded Lustre messages, and dispatches each subrequest through a local `struct tgt_handler` table.

The only concrete batch suboperation in this file is `BUT_GETATTR`, implemented as an LDLM enqueue/getattr-style lock operation through `ldlm_handle_enqueue()`. The file is therefore a batch framing and dispatch layer more than a metadata mutation engine.

## Important APIs, Types, And Functions

`mdt_batch()` is the exported entry point. It uses `struct but_update_header`, `struct but_update_buffer`, `struct batch_update_request`, and `struct batch_update_reply` request/reply formats, together with `req_capsule` subrequest machinery.

`mdt_batch_unpack()` extracts opcode-specific fields from the subrequest capsule. For `BUT_GETATTR`, it fetches `RMF_DLM_REQ` into `info->mti_dlm_req`; any other opcode returns `-EOPNOTSUPP`.

`mdt_batch_getattr()` is the concrete handler. It passes the MDT export namespace, subrequest capsule, DLM request, and MDT LDLM callback suite (`ldlm_server_completion_ast`, `tgt_blocking_ast`, `ldlm_server_glimpse_ast`) to `ldlm_handle_enqueue()`.

`mdt_batch_handler_find()` maps `BUT_FIRST_OPC <= opc < BUT_LAST_OPC` onto `mdt_batch_handlers[]` and asserts that the table entry opcode matches the request opcode. The handler macro `TGT_BUT_HDL()` initializes `struct tgt_handler` with `HAS_KEY | HAS_REPLY`, `LUSTRE_MDS_VERSION`, and an `RQF_<opcode>` capsule format.

`mdt_batch_reconstruct()` is a replay/reconstruction hook for mutable batched subrequests. The current handler table has only read-only `BUT_GETATTR`, so the reconstructor array is structurally present but not exercised by the current operation set.

## Control Flow

`mdt_batch()` first validates that the client capsule has an MDT batch header, checks the magic, and rejects zero update-buffer counts. It allocates an array of update buffer pointers sized by `buh_count`.

The request payload arrives either inline or by bulk transfer. If `buh_inline_length > 0`, the first update buffer points directly into `buh_inline_data`. Otherwise the server reads an array of `but_update_buffer` descriptors from `RMF_BUT_BUF`, estimates a page-fragment count, prepares a bulk sink descriptor on `MDS_BULK_PORTAL`, allocates one large buffer per update descriptor, wires those buffers into the bulk descriptor, prepares secure bulk state with `sptlrpc_svc_prep_bulk()`, and receives the payload with `target_bulk_io()`.

After payload acquisition, the function sizes `RMF_BUT_REPLY` from `buh_reply_size`, packs the server reply capsule, initializes `batch_update_reply`, switches the MDT thread/session into batch mode (`mti_batch_env`, `mti_pill`, `tsi_batch_env`), allocates `tg_reply_data`, and checks whether the RPC is resent.

The nested loop walks each `batch_update_request` buffer and every embedded Lustre message inside it using `batch_update_reqmsg_next()` and `batch_update_repmsg_next()`. For each submessage it validates message magic, finds a handler, initializes a subrequest capsule over the embedded request/reply message pair, unpacks opcode-specific fields, optionally reconstructs already committed mutable subrequests on resent RPCs, and otherwise invokes `h->th_act(tsi)`. If the reply capsule grows and changes `pill->rc_repmsg`, the code reloads the current reply message pointer before calculating packed reply length.

On success, the function records each subreply result, resets per-subrequest MDT thread state, tracks the packed reply length, and shrinks the reply field if the client-provided reply allocation was larger than needed. Exit cleanup sets the reply count, frees bulk buffers, frees the `tg_reply_data`, frees the PTLRPC bulk descriptor, finalizes MDT thread info, and sets `tsi_reply_fail_id` to the batch update network-reply fail injection ID.

## State And Persistence Behavior

This file does not create durable metadata state directly. Its state is request scoped: allocated payload buffers, capsule state, `mti_batch_env`, `tsi_batch_env`, `tsi_batch_idx`, and the batched reply count. Durable behavior is delegated to subhandlers; in the current file the concrete subhandler enters the LDLM server path rather than updating persistent MDT objects.

Resend/replay awareness is present through `tgt_check_resent()` and `tg_reply_data.lrd_batch_idx`. For mutable future handlers, `mdt_batch()` would reconstruct replies for subrequests already covered by the last reply data and re-execute uncommitted or read-only subrequests. Because `BUT_GETATTR` is not flagged `IS_MUTABLE`, it is re-executed on resent RPCs.

## Dependencies And Integration Points

The file depends on Lustre PTLRPC request capsules, bulk I/O, LDLM server callbacks, target handler dispatch, and MDT per-thread state from `mdt_internal.h`. It integrates with `mdt_handler.c` via the `MDS_BATCH` operation and with the batch wire formats and helpers that provide `BUT_*`, `RMF_BUT_*`, `batch_update_reqmsg_next()`, and `batch_update_repmsg_next()`.

The DLM callback suite makes the batch getattr path participate in normal server-side LDLM completion, blocking, and glimpse handling. Error reporting follows Lustre target conventions using `RETURN`, `GOTO`, `err_serious()`, `CERROR`, and `DEBUG_REQ`.

## Risks And Edge Cases

Payload trust boundaries are important. The function validates top-level header presence, magic, nonzero buffer count, bulk buffer sizes below `OUT_MAXREQSIZE`, embedded message magic, and opcode support, but correctness also depends on the batch-format iterators respecting the declared buffer bounds. Tests should stress malformed `burq_count`, truncated embedded messages, reply-size underestimation, and mismatched `buh_update_count`.

The inline path only assigns `update_bufs[0]` from `buh_inline_data`; any inline request with `buh_count > 1` relies on the encoded inline payload being traversed from that first buffer or would expose invalid uninitialized update-buffer pointers. That is a format contract worth verifying at the wire-format layer.

The check `handled_update_count > buh->buh_update_count` happens before processing the next subrequest. Boundary behavior for exactly equal counts should be tested because a malformed request may try to produce more subreplies than advertised.

Bulk page-count accumulation and reply packed-length accumulation use integer-sized locals; very large counts are mostly constrained by request formats and allocation failures, but fuzzing should include overflow-shaped descriptors.

## Test Signals

Useful tests include valid one-op `BUT_GETATTR` batches, unsupported opcodes, zero-count headers, bad magic, malformed bulk descriptors, bulk receive failures, too-small and too-large reply buffers, resent read-only batches, and fail injection around `OBD_FAIL_BUT_UPDATE_NET_REP`. Integration tests should confirm LDLM enqueue semantics are identical when issued through a batch versus the non-batch path and that all allocated bulk buffers and descriptors are released on every error exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_batch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_coordinator.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_coordinator.c

## Purpose

`mdt_coordinator.c` implements the Lustre MDT HSM coordinator. The coordinator owns the server-side scheduling loop that scans persistent HSM action llogs, selects waiting archive/restore/remove/cancel records, batches them into copytool action lists, sends them to registered HSM agents, tracks active requests in memory, processes copytool progress/completion, maintains restore layout locks, exposes control/tuning interfaces, and purges or cancels stale actions.

This file is the center of the MDT HSM state machine. It bridges persistent action records managed by `mdt_hsm_cdt_actions.c`, in-memory request management from `mdt_hsm_cdt_requests.c`, copytool communication from `mdt_hsm_cdt_agent.c`, and client request validation from `mdt_hsm_cdt_client.c`.

## Important APIs, Types, And Functions

The coordinator data lives in `struct coordinator` in `mdt_internal.h`: state, wait queues, request and agent locks, request hash/list, restore-handle rhashtable, tunables, request counters, policy flags, and request masks. `struct cdt_agent_req`, `struct cdt_restore_handle`, and `struct hsm_scan_request` are the central active-request and scan-batch types.

`mdt_hsm_get_md_hsm()` and its lock-taking helper fetch an MDT object by FID and read its `MA_HSM` metadata. Several paths use this to test or modify HSM flags.

`mdt_coordinator()` is the kthread body. It waits for events or periodic housekeeping, scans the HSM llog through `cdt_llog_process()`, builds `hsm_scan_request` groups, sends work with `mdt_hsm_agent_send()`, and frees scan-time request references.

`mdt_coordinator_cb()`, `mdt_cdt_waiting_cb()`, and `mdt_cdt_started_cb()` are llog traversal callbacks. They validate records, convert `ARS_WAITING` records into sendable batches, time out old `ARS_STARTED` records during housekeeping, delete expired final records after grace delay, and update scan cursors.

`mdt_hsm_cdt_init()`, `mdt_hsm_cdt_fini()`, `mdt_hsm_cdt_stop()`, and static `mdt_hsm_cdt_start()` initialize, tear down, stop, and start the coordinator. `hsm_control_store()` exposes `enabled`, `shutdown`, `disabled`, `purge`, and `help` control commands.

`cdt_restore_handle_add()`, `cdt_restore_handle_exists()`, and `cdt_restore_handle_del()` manage restore handles keyed by FID. A handle holds an EX layout lock during restore so concurrent layout-changing operations cannot race the restore.

`mdt_hsm_add_hsr()` registers scan-selected requests into the active in-memory request set after an agent accepts work. It handles cancel records specially by marking the original on-disk request canceled and attaching the cancel request to the running request.

`mdt_hsm_update_request_state()` processes copytool progress. It validates the cookie/FID/data-FID relationship, updates the in-memory progress tree, handles completion, updates the persistent action llog record, removes the active request, and wakes the coordinator when capacity opens.

`hsm_cdt_request_completed()` applies action-specific completion semantics to MDT HSM xattrs and changelogs. Archive success sets `HS_ARCHIVED`, updates archive version, and clears `HS_LOST|HS_DIRTY`; restore success swaps layouts from the volatile data FID into the original file and releases the restore handle; remove success clears archived/existing/lost flags; failure policy decides whether the record returns to `ARS_WAITING` or reaches a final failed/canceled state.

`mdt_hsm_is_action_compat()` decides whether an HSM action is compatible with current file HSM state. It is used by client and agent paths to reject actions that no longer make sense.

The sysfs/debugfs plumbing includes policy parsing, loop period, grace delay, active request timeout, max request cap, default archive ID, remove-on-last-unlink, request counters, agent/action/active-request listings, and user/group/other request masks.

## Control Flow

Initialization sets up wait queues, locks, request lists, the request-cookie hash, a dedicated LU environment/session, root-like HSM credentials, default tunables, and an initial `cdt_max_requests` of 3 subject to a global memory budget. Starting transitions `STOPPED -> INIT`, initializes counters and restore-handle hash, and launches the `hsm_cdtr` kthread unless the bottom device is read-only.

At kthread startup, the coordinator waits for MDT configuration-log readiness, scans existing llog records to recover pending restores, takes layout locks for non-final restore records, advances `cdt_last_cookie`, resets previously started restore records to waiting, then enters `CDT_RUNNING`.

The main loop sleeps on `cdt_waitq` for explicit events or one-second bounded periods. On `CDT_DISABLE`, it marks itself idle and waits without scanning. On housekeeping intervals it scans from the beginning of the catalog; on event-driven scans it resumes from saved catalog/record cursors. Before each scan it resizes the temporary `hsd_request` array if `cdt_max_requests` changed.

During llog processing, waiting records are grouped by archive ID when possible and constrained by `LDLM_MAXREQSIZE` and `cdt_max_requests`. Restore requests receive a special scheduling rule: the scanner tries to schedule at least one restore even when the normal capacity calculation is full. Started records are inspected only during housekeeping; if they have exceeded `cdt_active_req_timeout`, the coordinator emits a failure changelog, releases restore state if needed, marks the llog record canceled, and wakes itself to refill capacity.

After scanning, if no agents are registered, the scan cursor is reset and the temporary requests are discarded. Otherwise each grouped request is sent through `mdt_hsm_agent_send()`. Failures are treated as temporary and reset the scan cursor so the work can be found again. After sending, scan-time `cdt_agent_req` references are released.

Progress from copytools enters through `mdt_hsm_update_request_state()`. Non-completion progress updates active request state and returns `-ECANCELED` if the request has a pending cancel. Completion invokes `hsm_cdt_request_completed()`, updates the relevant llog record status, removes the active request from memory, and signals the coordinator.

Purge/cancel-all disables the coordinator, waits for the kthread to become idle, sends cancel actions to running copytools where possible, releases restore layout locks, marks all waiting/started on-disk records canceled, and restores the previous coordinator state.

## State And Persistence Behavior

Persistent state is primarily the HSM action llog. Records carry action item, cookie, archive ID, status (`ARS_WAITING`, `ARS_STARTED`, final states), offsets, llog IDs, and change timestamps. The coordinator rewrites llog records when restoring startup state, timing out started actions, canceling requests, registering cancel records, and finalizing copytool progress.

In-memory state mirrors active work: `cdt_request_cookie_hash` and `cdt_request_list` hold started requests, request counters provide current capacity and stats, `cdt_agents` lists copytools, and `cdt_restore_hash` records in-progress restores and their held layout locks. `cdt_last_cookie` is recovered from llog contents or initialized from wall-clock seconds to avoid cookie collision.

Restore state deliberately spans memory locks and persistent logs. Startup recovery reconstructs restore handles for unfinished restore records so layout EX locks are reacquired after coordinator restart. On successful restore, layout swap occurs before releasing the restore handle; on final failure/cancel the restore handle is deleted so the EX layout lock is released.

HSM file metadata changes are persistent MDT xattr updates through `mdt_hsm_attr_set()`. Completion also emits HSM changelog records with event type, error code, and dirty flag signal. For restore, the changelog is emitted before releasing the layout lock to preserve ordering against concurrent file updaters.

Coordinator control state is in memory but externally visible through sysfs/debugfs. Tunables affect subsequent scheduling, timeout, request grouping, and policy decisions; they are initialized from defaults and can be overridden by configuration/control paths.

## Dependencies And Integration Points

The file depends on `mdt_internal.h` for coordinator structures, MDT object helpers, HSM APIs, request helper prototypes, and control exports. It integrates with:

- `mdt_hsm_cdt_actions.c` for llog traversal and record modification.
- `mdt_hsm_cdt_agent.c` for agent registration, agent selection, sending HALs, and statistics.
- `mdt_hsm_cdt_requests.c` for active request allocation, lookup, progress update, refcounting, and removal.
- `mdt_hsm_cdt_client.c` for client-submitted action compatibility and restore-handle checks.
- `mdt_hsm.c` for copytool progress forwarding to `mdt_hsm_update_request_state()`.
- MDT object, lock, HSM xattr, changelog, and layout-swap APIs (`mdt_object_find_lock()`, `mdt_hsm_attr_set()`, `mo_changelog()`, `mo_swap_layouts()`, `mdt_lsom_downgrade()`).
- Linux kernel kthreads, wait queues, rwsems, mutexes, atomics, rhashtable, RCU, kobjects, debugfs, and user-copy parsing.

## Risks And Edge Cases

State transitions are guarded by `cdt_transition`; new states or control paths must update the table or they can fail unexpectedly. Stop/start races are handled by taking `cdt_state_lock` around `cdt_task`, but the read-only start path initializes `CDT_INIT` and returns without launching a task, so callers need to understand the read-only behavior.

The waiting-record scan mutates temporary request lists to make room for forced restores. That logic discards trailing cars or whole request groups and must preserve request refcounts and `hsd_action_count` invariants. Tests should cover full capacity, mixed archive IDs, large HAI payloads, and the single-forced-restore rule.

Persistent llog status is the source of truth. Any failure after a copytool accepts work but before llog status update, or vice versa, can leave records to be retried, timed out, or cleaned during housekeeping. The code intentionally treats many send failures as temporary by resetting scan cursors, so repeated agent failures can cause repeated rescans.

Restore locking is high risk. `cdt_restore_handle_add()` inserts into the hash before taking the layout lock and carefully removes/drops references on lock failure. `cdt_restore_handle_del()` removes under RCU and then drops the reference that unlocks layout. Races with duplicate restore records, cancel-all, timeout cleanup, and final progress should be stress-tested.

Completion policy has subtle semantics. `CDT_NORETRY_ACTION`, copytool `HP_FLAG_RETRY`, object lookup failure, and action-specific errors decide whether records return to `ARS_WAITING` or finalize. Archive failure may mark an already archived file dirty for safety. Restore swap failure can convert a nominal copytool success into retry/failure.

User-facing tunable parsers accept action/policy names and raw numeric values. Boundary tests should include zero values, unknown names, long writes, mixed signed policy updates, and concurrent updates while the coordinator thread is scanning.

## Test Signals

Unit or integration coverage should exercise coordinator state transitions, `hsm_control` commands, startup recovery of pending restore records, llog scanning with invalid record deletion, waiting-to-started scheduling, active request timeouts, no-agent scan behavior, max-request resizing, copytool completion for archive/restore/remove/cancel, retry versus no-retry policy, cancel-all purge, request masks for user/group/other submitters, and sysfs/debugfs lifetime.

Failure-oriented tests should inject llog write errors, allocation failures for scan arrays and restore handles, object lookup failures, layout lock failures, layout swap failures, agent-send failures, and concurrent progress/cancel/stop interactions. Observable signals include llog record status, coordinator state string, active request counters, changelog events, HSM xattr flags, restore-handle existence, and copytool-visible cancel responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_coordinator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_fs.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_fs.c

## Purpose

`mdt_fs.c` provides a small MDT filesystem-interface helper for per-export observability. Its exported function, `mdt_export_stats_init()`, initializes per-client/per-export lprocfs and debugfs statistics for an MDT export and creates an `open_files` debugfs view.

The file does not implement metadata operations. It connects MDT export lifecycle code to Lustre stats/debugfs infrastructure.

## Important APIs, Types, And Functions

`mdt_open_files_seq_fops` is a `struct file_operations` table for the per-export `open_files` debugfs file. It uses `ldebugfs_mdt_open_files_seq_open()` as the open callback and standard seq-file helpers for read, seek, and release.

`mdt_export_stats_init(struct obd_device *obd, struct obd_export *exp, void *localdata)` is called with the MDT OBD device, export, and a client `struct lnet_nid`. It initializes export lprocfs state, allocates the MDT stats counter block, initializes MDT counters, initializes per-NID LDLM stats, and creates the debugfs `open_files` entry under the export's NID debugfs directory.

## Control Flow

The function begins with `lprocfs_exp_setup(exp, client_nid)`. If that returns `-EALREADY`, the condition is treated as success because the per-export proc entries already exist. Other errors are returned.

On a fresh setup, it reads `exp->exp_nid_stats`, builds a stats path of the form `mdt.<obd_name>.exports.<nid>.stats`, and calls `ldebugfs_stats_alloc()` for `LPROC_MDT_LAST` counters using `LPROCFS_STATS_FLAG_NOPERCPU`. It initializes MDT stats counters as histograms with `mdt_stats_counter_init()`.

Next it initializes LDLM per-NID stats with `lprocfs_nid_ldlm_stats_init(stats)`. If that succeeds, it creates a read-only `open_files` debugfs file bound to the `nid_stat` object and `mdt_open_files_seq_fops`.

## State And Persistence Behavior

All state is runtime observability state. The function installs debugfs/lprocfs entries and allocates stats counters associated with `exp->exp_nid_stats`. There is no durable filesystem metadata mutation. The `-EALREADY` path makes repeated initialization idempotent for already-created proc entries.

The stats allocation is attached under the NID debugfs directory. Lifetime and cleanup are owned by the surrounding export/lprocfs infrastructure rather than by this file.

## Dependencies And Integration Points

The file depends on `lustre_compat/linux/fs.h` for file operation compatibility and `mdt_internal.h` for MDT stats declarations and `ldebugfs_mdt_open_files_seq_open()`.

It integrates with MDT export creation paths in `mdt_handler.c`, which call `mdt_export_stats_init()` for client exports. It also integrates with Lustre lprocfs/debugfs stats helpers, LDLM per-NID stats setup, seq-file read helpers, and LNet NID formatting through `libcfs_nidstr()`.

## Risks And Edge Cases

Stats allocation failure returns `-ENOMEM` after export proc setup has succeeded; cleanup is expected to be handled by the caller or lprocfs export teardown. If `lprocfs_nid_ldlm_stats_init()` fails, `nid_stats` remains allocated and the function returns the error without creating `open_files`.

The generated stats name uses a fixed stack buffer sized as `MAX_OBD_NAME * 4`. `scnprintf()` prevents overflow, but long OBD/NID strings can be truncated, so any consumer expecting globally unique debugfs stats names should account for truncation.

`debugfs_create_file()` return value is ignored. This matches the common pattern where debugfs visibility is noncritical, but tests should not assume `open_files` always exists after a successful return if debugfs creation fails.

## Test Signals

Tests should cover first-time export setup, repeated setup returning `-EALREADY`, stats allocation failure, LDLM stats initialization failure, and successful creation of MDT stats with `open_files` readability. Integration signals include the per-export stats path under debugfs/lprocfs, initialized `LPROC_MDT_LAST` counters, LDLM stats presence, and the ability to read the open-files seq file for a client export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_fs.c -->
