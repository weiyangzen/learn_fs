# sources/distributed-fs/ceph-client/fs/dlm/lock.c

## Purpose
`lock.c` is the core DLM lock manager implementation. It handles public kernel lock/unlock calls, userspace lock operations, resource lookup and master discovery, local queue manipulation, remote wire-message send/receive paths, lock value block transfer, blocking/completion AST queueing, waiter tracking, and major pieces of post-membership-change recovery.

## Important APIs and Functions
- Public kernel APIs: `dlm_lock()` and `dlm_unlock()`.
- Userspace APIs used by device/user code: `dlm_user_request()`, `dlm_user_convert()`, `dlm_user_adopt_orphan()`, `dlm_user_unlock()`, `dlm_user_cancel()`, `dlm_user_deadlock()`, `dlm_user_purge()`, and `dlm_clear_proc_locks()`.
- Resource and lock lifetime helpers: `find_rsb()`, `find_rsb_dir()`, `find_rsb_nodir()`, `dlm_search_rsb_tree()`, `rsb_insert()`, `deactivate_rsb()`, `free_inactive_rsb()`, `create_lkb()`, `find_lkb()`, `dlm_put_lkb()`, `attach_lkb()`, and `detach_lkb()`.
- Queue/grant logic: `can_be_granted()`, `_can_be_granted()`, `conversion_deadlock_detect()`, `grant_pending_locks()`, `grant_pending_convert()`, `grant_pending_wait()`, `queue_cast()`, and `queue_bast()`.
- Four-stage operation pipeline: `request_lock()`/`convert_lock()`/`unlock_lock()`/`cancel_lock()`, then `_request_lock()`/`_convert_lock()`/`_unlock_lock()`/`_cancel_lock()`, then `do_request()`/`do_convert()`/`do_unlock()`/`do_cancel()`.
- Message send/receive: `send_request()`, `send_convert()`, `send_unlock()`, `send_cancel()`, `send_grant()`, `send_bast()`, `send_lookup()`, `send_remove()`, corresponding `receive_*()` handlers, `dlm_receive_buffer()`, and `dlm_receive_message_saved()`.
- Recovery hooks: `dlm_recover_waiters_pre()`, `dlm_recover_waiters_post()`, `dlm_recover_purge()`, `dlm_recover_grant()`, `dlm_recover_master_copy()`, and `dlm_recover_process_copy()`.
- Debug hooks: `dlm_debug_add_lkb()` and `dlm_debug_add_lkb_to_waiters()`.

## Control Flow
The file documents its own four-stage model. Stage 1 validates public entry-point arguments and chooses request, convert, unlock, or cancel. Stage 2 finds the target RSB and locks it. Stage 3 decides local-vs-remote based on `res_nodeid`. Stage 4 performs queue mutations and queues callbacks. For remote operations, the local stage sends a DLM message and waits for the corresponding reply; the remote receiver runs the same stage-4 logic on a master-copy LKB and replies.

Resource lookup uses `jhash()` of the resource name and `dlm_hash2nodeid()` to determine the directory node. With directories enabled, `find_rsb_dir()` may create an RSB, reactivate an inactive RSB, preserve a directory record, mark a stale master as uncertain, or return `-ENOTBLK` when a request reached a non-master. Without directories, `find_rsb_nodir()` maps the hash directly to the master. Master lookup messages are serialized through `set_master()`: the first LKB triggering a lookup waits on `ls_waiters`, while additional LKBs for the same unresolved RSB wait on `res_lookup`.

Grant decisions are driven by VMS-style compatibility matrices and queue ordering. `do_request()` grants immediately, queues on the wait queue, or returns noqueue failure. `do_convert()` handles immediate grant, conversion queueing, conversion deadlock detection/demotion, and noqueue failure. Unlock removes a lock and then grants newly unblocked locks. Cancel reverts a converting/waiting lock and may also unblock others. Blocking ASTs are sent to granted locks whose modes block queued requests.

Messaging builds `struct dlm_message` payloads through `_create_message()`, `create_message()`, and `send_args()`, using midcomms message handles. Receive paths validate lock identity and copy type, deserialize flags/LVBs, run local queue operations, and send replies. `receive_lookup()` can optimize lookup into a request when the directory node is also the master.

## State and Persistence Behavior
The central runtime state is `struct dlm_ls` containing an LKB xarray, RSB rhashtable, active/inactive slow lists, waiters list, orphan list, request queue, and recovery structures. RSBs are refcounted while active; when their refcount drops, `deactivate_rsb()` moves them to the inactive list and optionally the scan list. The scan timer later frees tossable inactive resources and sends `DLM_MSG_REMOVE` to a directory node when needed.

LKBs are refcounted through the lockspace xarray and through queue/list ownership. Adding an LKB to a resource queue takes a reference; deleting it drops that reference. Waiters also hold references while replies are outstanding. Userspace locks add a process-list reference; persistent locks can move to the lockspace orphan list.

LVB state is held per resource (`res_lvbptr`, `res_lvbseq`, invalid flags) and per lock (`lkb_lvbptr`, `lkb_lvbseq`). `set_lvb_lock()`, `set_lvb_unlock()`, and `set_lvb_lock_pc()` implement direction-specific copy/invalidate behavior based on the old and requested lock modes.

There is no durable storage. Membership changes trigger recovery: waiters are completed or flagged for resend, dead-node master-copy locks are purged, locks are rebuilt on new masters via RCOM, process copies learn new remote ids, and pending queues are retried.

## Dependencies and Integration Points
`lock.c` integrates with midcomms for DLM messages, RCOM/recovery code for master-copy rebuild, `dir.c` for hash-to-directory mapping, `member.c` for membership/removal checks, `requestqueue.c` for saving messages during recovery, `ast.c` for callbacks, `user.c` for userspace lock ownership, `memory.c` for object allocation, `lvb_table.h` for LVB sizing, and `lockspace.c` for lockspace lifecycle.

## Risks
- The code is lock-order sensitive. It mixes `res_lock`, `ls_rsbtbl_lock`, `ls_lkbxa_lock`, waiters lock, requestqueue lock, scan lock, and recovery semaphores.
- Remote reply and overlap handling is subtle: force-unlock/cancel can overlap request/convert and must correctly clear waiter counts and flags.
- `res_nodeid` and `res_master_nodeid` have different semantics; stale or partially recovered master state can cause retry loops, `-ENOTBLK`, or incorrect local/remote decisions.
- Conversion deadlock, alternate-mode grant, and LVB invalidation rules are behaviorally dense and easy to regress with queue changes.
- Recovery paths intentionally synthesize local replies and forcibly reset waiter refcounts. Refcount mistakes can leak or prematurely free LKBs.
- Debug helpers can create artificial state and should not be treated as safe production input paths.

## Test Signals
- Lock mode compatibility tests should cover all matrix entries, conversions, `QUECVT`, `NOQUEUE`, `EXPEDITE`, `ALTPR`, `ALTCW`, and `CONVDEADLK`.
- Multi-node tests should cover remote request/convert/unlock/cancel, async grant, BAST delivery, lookup-to-request optimization, and directory remove races.
- Recovery tests should kill a master with pending requests, conversions, unlocks, cancels, and lookups, then verify waiter resend/completion and RCOM remid repair.
- LVB tests should cover VALBLK and IVVALBLK on lock, convert, unlock, remote reply, and failed holder recovery.
- Userspace tests should cover persistent orphan adoption, purge, process close cleanup, deadlock cancel, and mixed user/kernel lock rejection.
- Lockdep/KCSAN-style stress is important around scan timer reactivation, inactive RSB reuse, and requestqueue blocking during recovery.
