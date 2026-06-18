# sources/distributed-fs/ceph-client/drivers/tee/amdtee/call.c

## Purpose
`call.c` translates Linux TEE core operations into AMD PSP TEE command packets. It handles parameter marshaling, TA load/unload reference tracking, shared-memory map/unmap requests, open/close session commands, and invoke-command calls.

## Important APIs, Types, And Functions
`tee_params_to_amd_params()` converts `struct tee_param` arrays into `struct tee_operation`, packs parameter types four bits at a time, rejects meta parameters and invalid attributes, maps memrefs through `get_buffer_id()`, and only preserves value fields `a` and `b` because AMD TEE does not support value `c`. `amd_params_to_tee_params()` copies output/inout values back to Linux TEE params, updating output memref offsets/sizes and zeroing unsupported value `c`.

`handle_load_ta()` validates a page-aligned TA blob, sends `TEE_CMD_ID_LOAD_TA`, updates `arg->ret`/`arg->ret_origin`, and stores a driver-packed session id if a TA handle was allocated. `handle_unload_ta()` decrements the global TA reference list and sends `TEE_CMD_ID_UNLOAD_TA` only when the count reaches zero. `handle_open_session()`, `handle_close_session()`, and `handle_invoke_cmd()` wrap `TEE_CMD_ID_OPEN_SESSION`, `TEE_CMD_ID_CLOSE_SESSION`, and `TEE_CMD_ID_INVOKE_CMD`. `handle_map_shmem()` constructs a PSP scatter/gather list from page-aligned kernel virtual addresses and returns the firmware buffer id; `handle_unmap_shmem()` retires that id.

## Control Flow And State
Open-session flow starts with a loaded TA handle already placed in `arg->session` by `handle_load_ta()`. `handle_open_session()` marshals parameters, calls firmware, records returned `session_info`, and copies output params back. Invocation follows the same marshal, PSP command, unmarshal flow using the Linux session’s TA handle and the `session_info` slot value stored in `core.c`.

TA persistence is managed by a static `ta_list` protected by `ta_refcount_mutex`. Each successful TA load increments or creates an `amdtee_ta_data` entry; unload decrements and only sends the PSP unload command on the last reference. Shared-memory state itself is held in `core.c`; this file only sends firmware map/unmap commands and returns buffer ids.

## Dependencies And Integration Points
This file integrates with `linux/psp-tee.h` through `psp_tee_process_cmd()` and physical address conversion via `__psp_pa()`. It relies on `amdtee_if.h` command structures and the generic Linux TEE parameter representation. It is called by `core.c` session and shared-memory callbacks and by `shm_pool.c` indirectly through `amdtee_map_shmem()`.

## Risks
Parameter conversion assumes values fit in 32 bits and silently discards value `c`, which can break TAs expecting full GP value semantics. `handle_load_ta()` returns 0 even when firmware reports a GP error in `arg->ret`, so callers must always inspect `arg->ret`. `handle_unload_ta()` returns `-EBUSY` for non-final references, which is expected internally but can look like a command failure if reused carelessly. `handle_map_shmem()` allocates one command structure and writes `count` scatter entries without local visible bounds checking against the command’s array capacity.

## Test Signals
Exercise all GP parameter types accepted by the driver, including output memrefs and inout values; verify value `c` behavior is documented for callers. Fault-inject PSP transport failures and nonzero firmware statuses. Stress concurrent TA opens/closes to validate `ta_refcount_mutex` and ensure final unload happens exactly once. Validate map rejection for unaligned addresses and non-page-aligned sizes.
