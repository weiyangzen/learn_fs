# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v11_api_def.h

## Purpose
Defines the packed MES v11 scheduler firmware API. It is the binary command-frame contract used by the host driver to configure MES resources, add/remove queues, schedule gangs, suspend/resume/reset queues, configure logging, manage debug VMIDs, perform misc register/TLB/debugger operations, update root page tables, and pass AMD log buffers.

## Important APIs, Types, and Functions
Important constants are `MES_API_VERSION 1`, `AMDGPU_MES_LOG_BUFFER_SIZE 0x4000`, `API_FRAME_SIZE_IN_DWORDS 64`, and `API_NUMBER_OF_COMMAND_MAX 32`. Important enums include scheduler opcodes, priority levels, queue types, VM hub types, debug VMID operations, log operations/states, and misc opcodes. `union MES_API_HEADER` encodes type/opcode/dword size. Every command union overlays a typed struct with `max_dwords_in_api[64]`, enforcing fixed-size frames. Key unions include `MESAPI_SET_HW_RESOURCES`, `MESAPI_SET_HW_RESOURCES_1`, `MESAPI__ADD_QUEUE`, `REMOVE_QUEUE`, `SET_SCHEDULING_CONFIG`, `SUSPEND`, `RESUME`, `RESET`, `SET_LOGGING_BUFFER`, `QUERY_MES_STATUS`, `PROGRAM_GDS`, `SET_DEBUG_VMID`, `MISC`, `UPDATE_ROOT_PAGE_TABLE`, and `MESAPI_AMD_LOG`.

## Control Flow
There is no C implementation. Runtime flow is firmware-command based: host code fills a command union, sets header fields, writes it to the MES ring, then waits for `MES_API_STATUS` fence completion or query/log output. Queue lifecycle generally flows through resource setup, scheduling configuration, queue add, then suspend/resume/reset/remove as workloads or faults require.

## State and Persistence
The header defines serialized state layouts. Persistent MES state lives in firmware and GPU memory referenced by scheduler contexts, process/gang contexts, MQDs, write pointers, log buffers, event history, fences, and page-table addresses. `#pragma pack(push, 4)` is ABI-critical.

## Dependencies and Integration Points
The header is consumed by `amdgpu/mes_v11_0.c` and common MES code. It integrates with AMDGPU queue management, KFD process queues, GPUVM updates, debug trap/shader debugger setup, GDS programming, reset/hang detection, firmware logging, and interrupt/fence completion.

## Risks and Test Signals
Primary risk is binary layout drift: field order, packing, bitfields, enum values, and 64-dword frame size must match firmware. Additional risks include wrong address type, wrong doorbell offset, missing status fence, and version-gated command variants. Test signals include MES queue add/remove across queue types, fence completion, suspend/resume/reset, logging wrap behavior, debug VMID allocation/release, misc register commands, and root page-table update under active workloads.
