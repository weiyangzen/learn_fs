# sources/distributed-fs/lustre-release/lustre/mdc/mdc_locks.c

## Purpose

`mdc_locks.c` implements MDC metadata LDLM lock acquisition, intent RPC packing/completion, lock revalidation, lock data association, replay-sensitive layout saving, and asynchronous intent/getattr or flock enqueue support. It is the bridge between high-level metadata operations (`lookup_intent`, `md_op_data`) and LDLM IBITS/FLOCK locking over MDT resources.

## Important APIs, Types, And Functions

Externally visible functions include `it_open_error()`, `mdc_set_lock_data()`, `mdc_lock_match()`, `mdc_cancel_unused()`, `mdc_null_inode()`, `mdc_save_lmm()`, `mdc_finish_enqueue()`, `mdc_enqueue()`, `mdc_enqueue_async()`, `mdc_revalidate_lock()`, `mdc_intent_lock()`, and `mdc_intent_getattr_async()`.

Internal request packers include `mdc_intent_open_pack()`, `mdc_intent_create_pack()`, `mdc_intent_getxattr_pack()`, `mdc_intent_getattr_pack()`, `mdc_intent_layout_pack()`, and `mdc_enqueue_pack()`. Shared orchestration is in `mdc_enqueue_base()`, with completion split between `mdc_finish_enqueue()` and `mdc_finish_intent_lock()`. Async helpers are `mdc_enqueue_async_interpret()` and `mdc_intent_getattr_async_interpret()`.

## Control Flow

`mdc_intent_lock()` first attempts local revalidation for sane child FIDs on lookup/getattr/readdir, allocates a new FID for create if needed, then delegates to `mdc_enqueue_base()`. `mdc_enqueue_base()` selects a lock policy from the intent: update for getattr/readdir/create, layout for layout intents, xattr for getxattr, lookup otherwise. It then packs the correct LDLM intent request, sets project ID and LDLM slot behavior, installs a DOM glimpse callback, and calls `ldlm_cli_enqueue()`.

Open/create packing performs early cancellation of conflicting parent update or child open/layout locks, obtains SELinux policy, marks replayable open requests, and reserves reply fields for MDT body, layout EA, ACL, security/encryption contexts, default LMV, and possible Data-on-MDT inline data. Getattr/getxattr/layout intents reserve only their required reply fields. When a server returns `-EINPROGRESS`, `mdc_enqueue_base()` retries while the import generation is unchanged; `-ERANGE` on old ACL buffers triggers a rebuild with maximum EA-size ACL capacity.

`mdc_finish_enqueue()` decodes LDLM reply disposition/status into the lookup intent, adjusts lock mode if the server granted a different mode, clears replay flags for failed/nonexecuted operations, extracts MDT body and layout data, saves layout EA into the request for replay when needed, installs layout LVB data on layout locks, and updates DOM LVBs for DOM locks. `mdc_finish_intent_lock()` converts disposition into VFS-visible references: it retains request refs for successful create/open phases, handles failed phases, and replaces duplicate locks with an existing matching one when possible.

## State And Persistence Behavior

Persistent state is remote MDT metadata; local state includes LDLM resources, inode association in `lr_lvb_inode`, `lookup_intent` disposition/status/lock handles, request replay flags, and saved EA buffers for recovery. `mdc_save_lmm()` can enlarge the request buffer and copy layout metadata so open/create/layout operations can be replayed correctly after recovery. Lock revalidation either validates an existing handle or searches the namespace for matching IBITS according to the intent.

## Dependencies And Integration Points

The file depends on LDLM locking, PTLRPC request capsules, Lustre intent/disposition definitions, MDC packers in `mdc_lib.c`, replay helpers in `mdc_request.c`, Data-on-MDT callbacks from `mdc_dev.c`, ACL sizing, SELinux policy helpers, and lprocfs counters. It is exported through `mdc_md_ops` in `mdc_request.c` as metadata enqueue, intent lock, async getattr, lock matching, and cancel-unused support.

## Risks

This is a high-risk concurrency and recovery file. Incorrect replay flag clearing could replay failed creates/opens or lose needed recovery data. ACL `-ERANGE` retry paths must free and rebuild requests without leaking locks. Infinite `-EINPROGRESS` retry depends on signal handling and import generation checks. Layout LVB installation allocates memory under completion flow and must avoid trusting blocked locks. `mdc_set_lock_data()` assumes any previous inode pointer is freeing when changed. Async completion must maintain lock references so failed lock cleanup and upcalls occur in a safe order.

## Test Signals

Important tests include lookup/getattr/open/create/readdir/getxattr/layout intents, local lock revalidation, duplicate lock replacement, open/create recovery replay, ACL large-reply retry, `-EINPROGRESS` retry and cross-eviction stop, DOM lock LVB update, layout lock LVB save/install, async flock enqueue, async getattr completion, and failure hooks such as `OBD_FAIL_MDC_GETATTR_ENQUEUE` and enqueue race failpoints.
