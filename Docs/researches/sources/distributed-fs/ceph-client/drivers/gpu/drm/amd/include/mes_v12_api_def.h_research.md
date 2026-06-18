# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v12_api_def.h

## Purpose
Defines the packed MES v12 scheduler firmware API. It evolves v11 with 8-byte packing, API version `0x14`, larger logging, error reporting, RRMT register remapping, cooperative/debug context setup, richer queue/reset fields, query subcommands, SE mode switching, gang submit setup, and explicit TLB invalidation commands.

## Important APIs, Types, and Functions
Important constants include `MES_API_VERSION 0x14`, `AMDGPU_MES_LOG_BUFFER_SIZE 0xC000`, 64-dword frames, and 32 command slots. `MES_ERR_CODE` encodes API error, scheduler opcode, misc opcode, category, and an error bit into the high 32 bits of a completion fence value. New or expanded enums include `MES_RRMT_MODE`, `MES_ERROR_CATEGORY_CODE_12`, `MES_API_QUERY_MES_OPCODE`, and `MES_SE_MODE`. Command unions mirror v11 but add fields such as `enable_mes_fence_int`, unmapped doorbell handling, MES debug/co-op context, full shader memory config, timestamps, context-array indexes, connected queue indexes, query subcommands, RRMT options, `SET_GANG_SUBMIT`, `SET_SE_MODE`, and `INV_TLBS`.

## Control Flow
Runtime flow remains MES ring command submission followed by API status fence completion and optional interrupt. v12 documents error-completion encoding and source ID 181/EOP completion interrupt behavior when fence interrupts are enabled. Queue management uses add/remove/suspend/resume/reset frames with richer process/gang context indexes and connected queue identifiers.

## State and Persistence
The header owns no storage but defines firmware-visible state. GPU memory addresses reference scheduler contexts, debug contexts, co-op shared buffers, cleaner shader fences, process/gang contexts, MQDs, write pointers, log buffers, TLB invalidation ranges, and output buffers. `#pragma pack(push, 8)` is ABI-critical and differs from v11.

## Dependencies and Integration Points
It is consumed by `amdgpu/mes_v12_0.c`, `mes_v12_1.c`, common MES code, and KFD queue paths. Integration points include scheduler initialization, hardware resource programming, queue lifecycle, SDMA/gfx/compute scheduling, TLB invalidation, debug VMID setup, shader debugger control, SE mode changes, gang submit coordination, logging, health queries, and firmware error reporting.

## Risks and Test Signals
Risks include mixing v11/v12 layouts, failing to gate fields by scheduler API version, incorrect error decoding, wrong address type for `wptr_addr`, malformed RRMT steering on multi-die parts, and incomplete TLB invalidation selection. Test signals include MES v12/v12.1 queue lifecycle, API fence interrupts, error-path decoding, TLB invalidation by PASID/VMID, debug VMID setup, RRMT register access, SE mode switching, gang submit setup, and logging wrap stress.
