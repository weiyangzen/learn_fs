# sources/distributed-fs/ceph-client/drivers/tee/amdtee/amdtee_if.h

## Purpose
Defines the host-to-AMD Trusted OS command ABI used by the AMDTEE driver. The structures must match the secure-world TEE side and describe operation parameters, shared-memory mapping, Trusted Application load/unload, session open/close, and command invocation.

## Important APIs, Types, and Constants
`TEE_MAX_PARAMS` is 4. Parameter structs include `memref`, `value`, `tee_op_param`, and `tee_operation`. Parameter type constants match the GlobalPlatform TEE style, with helpers `TEE_PARAM_TYPE_GET()` and `TEE_PARAM_TYPES()`. Shared-memory descriptors are `tee_sg_desc`, `tee_sg_list`, and `tee_cmd_map_shared_mem`/`tee_cmd_unmap_shared_mem`. TA/session commands are `tee_cmd_load_ta`, `tee_cmd_unload_ta`, `tee_cmd_open_session`, `tee_cmd_close_session`, and `tee_cmd_invoke_cmd`.

## Control Flow and State
The header has no code, but command flow is map shared memory, optionally load a TA, open a session with `tee_operation`, invoke commands with in/out parameters, close the session, unload the TA, and unmap memory. Output fields such as `buf_id`, `ta_handle`, `session_info`, and `return_origin` carry secure-world state handles back to the host driver.

## Dependencies and Integration Points
Depends on fixed-width Linux integer types. It is included by AMDTEE implementation files that marshal command buffers to the PSP/Trusted OS interface and translate generic TEE parameters to AMDTEE commands.

## Risks and Test Signals
This is a binary ABI: field size, alignment, order, page alignment requirements, and maximum scatterlist count must match firmware. `TEE_MAX_SG_DESC` limits map commands to 64 contiguous segments. Test signals include ABI size/static assertions where available, shared-memory maps with multiple SG entries, oversized SG rejection, open/invoke parameter round trips for value and memref types, and correct propagation of `return_origin` and TA/session handles.
