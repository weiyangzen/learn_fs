# sources/distributed-fs/ceph-client/drivers/tee/amdtee/core.c

## Purpose
`core.c` registers the AMD-TEE device with the Linux TEE subsystem and implements context lifecycle, TA firmware loading, session management, shared-memory bookkeeping, and TEE driver callbacks.

## Important APIs, Types, And Functions
`amdtee_get_version()` reports `TEE_IMPL_ID_AMDTEE` with GP generic capability. `amdtee_open()` allocates `amdtee_context_data`, initializes session and shared-memory lists, and stores it on `ctx->data`. `amdtee_release()` closes all tracked sessions by calling `release_session()`, destroys the shared-memory mutex, and frees context data.

`copy_ta_binary()` derives the firmware path `/amdtee/<uuid>.bin` from the requested TA UUID, serializes firmware loading with `drv_mutex`, rounds size to a page, allocates page memory, and copies the TA binary. `amdtee_open_session()` enforces public login, loads the TA, allocates or references an `amdtee_session`, opens a PSP session, assigns the first free bitmap slot, and rewrites `arg->session` to the driver-packed id. `amdtee_close_session()` removes a session slot, closes the firmware session, unloads the TA reference, and drops the kref. `amdtee_invoke_func()` validates the packed session id and invokes the command with the stored `session_info`.

`amdtee_map_shmem()` and `amdtee_unmap_shmem()` call firmware map/unmap helpers and maintain the context `shm_list`. `get_buffer_id()` looks up a firmware buffer id by the `tee_shm` kernel address. `amdtee_driver_init()` checks PSP TEE availability, allocates driver state, creates a shared-memory pool, allocates/registers a TEE device, and stores global `drv_data`. `amdtee_driver_exit()` unregisters the device and frees the pool.

## Control Flow And State
Every opened Linux context owns its own session list. Multiple sessions for the same TA share one `amdtee_session` object in that context, with a kref incremented by `alloc_session()` and decremented on close. `session_list_mutex` serializes context session-list lookup/mutation, while each session’s spinlock protects the bitmap and slot arrays. Shared-memory entries persist until `amdtee_unmap_shmem()` removes them from `ctxdata->shm_list`.

Driver initialization persists global `drv_data` and the registered `tee_device` until module exit. Session release on context close iterates every session object and closes every set bitmap slot, then unloads the TA for each slot.

## Dependencies And Integration Points
The file is the Linux TEE core integration point through `tee_driver_ops`, `tee_desc`, `tee_device_alloc()`, and `tee_device_register()`. It depends on firmware loading (`request_firmware()`), AMD PSP availability (`psp_check_tee_status()`), PSP command helpers from `call.c`, and the shared-memory pool from `shm_pool.c`.

## Risks
`copy_ta_binary()` uses `roundup(fw->size, PAGE_SIZE)` and page allocation but does not zero the padding after the firmware size; firmware consumers must tolerate padded content. `destroy_session()` unlocks `session_list_mutex` via `kref_put_mutex()` semantics, so callers must not alter the locking pattern casually. `amdtee_driver_exit()` unregisters and frees the pool but does not free the allocated `amdtee` or `drv_data`, which is a teardown leak in this source. Shared-memory context entries are not explicitly drained in `amdtee_release()`, so normal TEE core ordering must ensure SHM objects are freed before context teardown.

## Test Signals
Boot/probe with PSP TEE absent and present. Open/close sessions under concurrency and force error paths after TA load, after session allocation, and after PSP open-session. Release a context with live sessions to validate cleanup. Run kmemleak/module unload checks for `amdtee` and `drv_data`. Allocate and free shared memory across multiple contexts and ensure `get_buffer_id()` never crosses contexts.
