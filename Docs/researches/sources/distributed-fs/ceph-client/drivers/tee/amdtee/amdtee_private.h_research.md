# sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_private.h

## Purpose
`amdtee_private.h` is the private contract for the AMD-TEE Linux driver. It defines driver identity, selected GlobalPlatform return codes, session limits, firmware TA path conventions, per-device/per-context state containers, shared-memory bookkeeping, TA reference bookkeeping, session-id packing helpers, and internal function prototypes shared by AMD-TEE core, PSP command, and shared-memory pool code.

## Important APIs, Types, And Functions
The main service type is `struct amdtee`, which binds a client `tee_device` to a `tee_shm_pool`. `struct amdtee_context_data` is attached to each `tee_context` and persists two lists: `sess_list` for TA sessions and `shm_list` for mapped buffers, with `shm_mutex` protecting shared-memory entries. `struct amdtee_session` tracks a loaded TA handle, kref lifetime, up to `TEE_NUM_SESSIONS` per-TA `session_info` values, and a bitmap protected by a spinlock. `struct amdtee_shm_data` maps a kernel virtual address to the PSP/TEE buffer id returned by `TEE_CMD_ID_MAP_SHARED_MEM`. `struct amdtee_ta_data` is used by the command layer to maintain global TA load reference counts.

`set_session_id()`, `get_ta_handle()`, and `get_session_index()` encode a synthetic Linux session id: lower 16 bits carry the TA handle and upper 16 bits carry the per-TA session slot. Prototypes expose TEE core callbacks (`amdtee_open_session()`, `amdtee_close_session()`, `amdtee_invoke_func()`, `amdtee_cancel_req()`), shared-memory hooks (`amdtee_map_shmem()`, `amdtee_unmap_shmem()`, `amdtee_config_shm()`, `get_buffer_id()`), and lower-level PSP command wrappers (`handle_load_ta()`, `handle_open_session()`, `handle_invoke_cmd()`, etc.).

## Control Flow And State
The header’s key state model is two-tiered. Per Linux TEE context, `amdtee_context_data` owns the active session list and mapped shared-memory list. Separately, the command layer keeps a global `amdtee_ta_data` list keyed by TA handle to avoid unloading a TA while multiple sessions still reference it. Session ids are not opaque PSP ids; they are driver-packed values that must remain consistent with bitmap slot allocation in `core.c`.

## Dependencies And Integration Points
The file depends on Linux TEE core types, list/mutex/spinlock/kref primitives, bitmaps, and AMD PSP command structure definitions from `amdtee_if.h`. Its prototypes are implemented in `core.c`, `call.c`, and `shm_pool.c`, and its exported semantics must match the generic `/dev/tee*` core callbacks.

## Risks
The 16-bit TA handle encoding (`LOWER_TWO_BYTE_MASK`) assumes TA handles fit the lower two bytes; if firmware returns wider meaningful handles, session lookup can alias. Shared-memory lookup by `kaddr` also assumes unique live mappings per context. The session limit is hard-coded to 32 per TA instance, so overflow paths must reliably close the just-opened firmware session and unload the TA reference.

## Test Signals
Useful signals include opening more than 32 sessions to one TA, opening sessions to multiple TAs in one context, releasing a context with live sessions and mapped buffers, mapping/unmapping shared memory repeatedly, and injecting PSP command failures to ensure session and TA reference cleanup stays balanced.
