# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-syncop.h

## Purpose
`glusterd-syncop.h` declares the synchronous management RPC helpers implemented in `glusterd-syncop.c` and exposes the `GD_SYNCOP` convenience macro used by glusterd callers that need to submit an RPC and block the current synctask until the callback wakes it. It is the public contract for synchronous cluster lock, unlock, stage, commit, brick-operation, aggregation, and syncargs lifecycle helpers.

## Important APIs, Types, and Macros
`GD_SYNC_OPCODE_KEY` is the dict key `"sync-mgmt-operation"`. `glusterd_op_begin_synctask()` stores the operation code under this key before `gd_sync_task_begin()` reads it from the operation context.

`GD_SYNCOP(rpc, stb, cookie, cbk, req, prog, procnum, xdrproc)` is the central blocking RPC macro. It fetches the current synctask, stores it in `stb->task`, unlocks `conf->big_lock`, calls `gd_syncop_submit_request()`, yields the synctask when submit succeeds, records an error string when submit fails, and reacquires `conf->big_lock`. The macro assumes `THIS->private` is a valid `glusterd_conf_t` and the callback will wake the synctask.

`GD_ALLOC_COPY_UUID(dst_ptr, uuid, ret)` allocates a heap uuid object, copies a uuid into it, and stores the allocation result in `ret`. Syncop submitters use this for callback cookies so callbacks can identify the peer even after the stack frame returns.

The declared callback `gd_syncop_brick_op_cbk()` is used both by this file and other glusterd code that submits brick management RPCs.

`gd_syncop_submit_request()` is the common XDR serialization and RPC submit helper for all syncop requests.

`gd_syncop_mgmt_lock()`, `gd_syncop_mgmt_unlock()`, `gd_syncop_mgmt_stage_op()`, and `gd_syncop_mgmt_commit_op()` expose legacy peer management operations over the management RPC program.

`gd_synctask_barrier_wait()` exposes the lock-aware barrier wait helper for fan-out phases.

`gd_brick_op_phase()` exposes brick/service-node phase execution to callers that need to run the brick phase directly, such as snapshot or peer management paths.

`glusterd_syncop_aggr_rsp_dict()` exposes the operation-specific response aggregation dispatcher.

`gd_syncargs_init()` and `gd_syncargs_fini()` expose lifecycle management for `struct syncargs`, including mutex and barrier setup/teardown.

## Control Flow and Integration
Consumers include glusterd command handlers and management modules that either call `glusterd_op_begin_synctask()` indirectly or need direct access to brick-operation phase helpers. The header itself includes `glusterfs/syncop.h`, `glusterd-sm.h`, and `glusterd.h`, which makes `struct syncargs`, `glusterd_peerinfo_t`, `glusterd_op_t`, `dict_t`, `uuid_t`, and RPC callback types available to declarations and macros.

The `GD_SYNCOP` macro is intentionally not a simple function wrapper because it must interact with local variables, the typed `struct syncargs` pointer supplied by the caller, the current synctask, and the big-lock release/reacquire sequence. It delegates serialization and transport to `gd_syncop_submit_request()`.

## State and Persistence Behavior
The header does not persist state by itself. It defines conventions for in-memory state flow: the operation code is stored in a dict under `GD_SYNC_OPCODE_KEY`; synchronous waits store a `struct synctask *` in `syncargs`; callback cookies can own heap uuid copies; and aggregation functions mutate supplied dictionaries. Any persistent effects happen in implementation files reached through these declarations.

## Dependencies
The exported API depends on GlusterFS syncop and RPC types, glusterd peer and operation state types, dictionaries, UUIDs, and XDR procedure pointers. Because `GD_SYNCOP` references `THIS`, `THIS->private`, `glusterd_conf_t`, `synclock_unlock()`, `synctask_get()`, `synctask_yield()`, `gf_asprintf()`, and `synclock_lock()`, any translation unit using the macro must be in a glusterd context with those symbols and the big lock available.

## Risks and Edge Cases
`GD_SYNCOP` has side effects that are not obvious from its call syntax: it mutates `stb->task`, unlocks and relocks the global glusterd big lock, may allocate an error string, and yields the current synctask. Misusing it outside a synctask or without a callback that wakes `stb->task` can hang the caller.

The macro assumes `stb` is a valid pointer and that `prog->progname` is valid when submit fails. It also assumes the submit helper transfers or cleans up frame ownership correctly.

`GD_ALLOC_COPY_UUID` only sets `ret` and leaves error reporting to the caller. Callers must free the allocated uuid in callbacks or on paths where submit is not reached.

Because the header exposes mutable dictionary aggregation and syncargs lifecycle functions, callers must pair `gd_syncargs_init()` with `gd_syncargs_fini()` and must not mutate aggregate dictionaries concurrently without the lock discipline expected by `glusterd-syncop.c`.

## Test Signals
Macro-focused tests should verify that `GD_SYNCOP` releases the big lock while waiting, reacquires it on both submit success and failure, yields only after successful submit, and sets a useful error string on submit failure.

API contract tests should cover request submission with null requests, allocation failures, callback cookie ownership, `syncargs` init/fini error paths, and direct `gd_brick_op_phase()` usage from modules that do not execute the full transaction pipeline.
