# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.c

## Purpose
`hfi.c` provides the high-level Host Firmware Interface state machine wrapper. It translates V4L2 pixel formats to HFI codecs, creates/destroys sessions, serializes core/session lifecycle transitions, waits for asynchronous firmware completions, gates operations during system errors, and delegates packet transport to lower-level `venus_hfi` operations.

## Important APIs And Functions
- Core lifecycle: `hfi_create()`, `hfi_destroy()`, `hfi_reinit()`, `hfi_core_init()`, `hfi_core_deinit()`, `hfi_core_suspend()`, `hfi_core_resume()`, `hfi_core_trigger_ssr()`.
- Session lifecycle: `hfi_session_create()`, `hfi_session_destroy()`, `hfi_session_init()`, `hfi_session_deinit()`, `hfi_session_load_res()`, `hfi_session_start()`, `hfi_session_stop()`, `hfi_session_unload_res()`, `hfi_session_abort()`, `hfi_session_continue()`.
- Session operations: `hfi_session_flush()`, `hfi_session_set_buffers()`, `hfi_session_unset_buffers()`, `hfi_session_get_property()`, `hfi_session_set_property()`, `hfi_session_process_buf()`.
- IRQ wrappers: `hfi_isr()` and `hfi_isr_thread()`.

## Control Flow
`hfi_create()` initializes core state, completion, instance count, core callbacks, and packet version, then creates the Venus HFI transport. Core init sends firmware init, waits up to one second for `core->done`, checks `core->error`, and marks `CORE_INIT`. Core deinit can block until all instances are destroyed if requested, then calls transport deinit and marks `CORE_UNINIT`.

Session create adds an instance to `core->instances` under `core->lock` if `sys_error` is clear and `max_sessions_supported` is not exceeded. Session init maps pixel format to HFI codec, sends session init, waits for completion, and moves to `INST_INIT`. Load/start/stop/unload/deinit enforce expected state transitions and wait for firmware responses. Get-property waits and copies `inst->hprop`; set-property and process buffers are asynchronous fire-and-forget at this wrapper level.

## State And Persistence
- Mutates `core->state`, `core->done`, `core->error`, `core->insts_count`, `core->instances`, `core->core_ops`, and `core->ops`.
- Mutates `inst->state`, `inst->done`, `inst->error`, `inst->ops`, and `inst->hfi_codec`.
- No persistent storage; state is runtime only and synchronized with firmware messages parsed by `hfi_msgs.c`.

## Dependencies And Integration Points
- Lower transport implementation in `hfi_venus.c` through `venus_hfi_create()`, `venus_hfi_destroy()`, and queue reinit.
- Packet versioning in `hfi_cmds.c`.
- Completion callbacks in `hfi_msgs.c` set errors and complete waits.
- Called by core probe/recovery/PM and by helper/decoder/encoder stream paths.

## Risks And Edge Cases
- One-second timeout is fixed; slow firmware or lost interrupts cause `-ETIMEDOUT`.
- State checks are strict, so caller cleanup paths must call lifecycle methods in the expected order.
- `hfi_session_destroy()` assumes the instance was successfully added; misuse can corrupt counts/lists.
- `hfi_session_continue()` is a no-op on HFI 1xx, version-specific behavior callers must tolerate.
- Operations during `sys_error` return `-EIO`, which must be handled by queue and cleanup paths without deadlock.

## Test Signals
- HFI init/deinit should complete during probe/remove and SSR recovery.
- Session lifecycle tests should cover init/load/start/stop/unload/deinit, abort on errors, max-session exhaustion, and property get/set timeouts.
- Lost IRQ or firmware fault injection should produce timeout or system-error paths without list/count leaks.
