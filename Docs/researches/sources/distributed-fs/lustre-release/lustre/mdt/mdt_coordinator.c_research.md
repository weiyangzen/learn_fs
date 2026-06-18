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
