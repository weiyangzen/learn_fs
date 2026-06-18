# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vi_structs.h

## Purpose
`vi_structs.h` defines binary queue and preemption metadata layouts for VI-era AMDGPU engines. The structures describe SDMA MQDs, compute MQDs, MQD allocation backing storage, CE/DE indirect-buffer save state, chained-IB variants, and 4 KiB graphics metadata pages. These definitions are hardware-facing ABI layouts rather than general-purpose in-memory models.

## Important APIs, Types, and Structures
`struct vi_sdma_mqd` maps SDMA ring and IB state fields such as ring base, read/write pointers, polling addresses, IB base/size, skip/context status, doorbell, and virtual address. Most of the 128 dwords are reserved to preserve hardware layout, with the final two repurposed for driver-internal `sdma_engine_id` and `sdma_queue_id`.

`struct vi_mqd` is the large compute queue descriptor. It includes compute dispatch dimensions, program/TBA/TMA addresses, resource limits, static thread-management masks, restart and wave-restore fields, user data registers, counters and timestamps, GDS/context-save state, HQD queue controls, EOP and context-save controls, IQ timer packet storage, resource packet storage, doorbell IDs, and a trailing `reserved_t[256]`. `struct vi_mqd_allocation` wraps a `vi_mqd` with `wptr_poll_mem`, `rptr_report_mem`, `dynamic_cu_mask`, and `dynamic_rb_mask` backing slots.

The graphics metadata section defines CE and DE IB state payloads (`vi_ce_ib_state`, `vi_de_ib_state`) plus chained-IB variants. `vi_gfx_meta_data` and `vi_gfx_meta_data_chained_ib` combine these payloads with alignment padding and saved PFP IB base fields into fixed 4 KiB layouts.

## Control Flow and State
There is no executable control flow. The state behavior is entirely structural: the driver writes these fields into memory shared with GPU command processors and SDMA engines, and hardware or firmware reads/writes them during queue execution, context save/restore, and preemption. Reserved fields are persistent padding and must retain layout positions even if not actively interpreted by the driver.

## Dependencies and Integration Points
The header depends on fixed-width `uint32_t` definitions from the including kernel environment. Integration points are AMDGPU gfx/compute queue setup, SDMA queue initialization, KFD/compute scheduling, context save/restore, preemption, and IB chaining logic. Any code allocating these objects must satisfy documented alignment requirements, especially 4 KiB for CE metadata and 64-byte alignment for DE payloads inside the metadata page.

## Risks
The primary risk is ABI drift: reordering, resizing, or changing types breaks the hardware-visible descriptor format. The file intentionally includes many reserved dwords, so cleanup refactors are dangerous. The field name `cp_mqd_connect_endvi_sdma_mqd_pq_wptr` appears unusual and should not be "fixed" without confirming generated source compatibility. Endianness, packing, and alignment assumptions matter because these structures are consumed by GPU hardware, not just C code.

## Test Signals
Compile-time signals include `sizeof`/offset assertions in any queue code that uses these structs. Runtime signals include successful SDMA ring bring-up, compute queue creation, dispatch, preemption, context save/restore, chained IB execution, and KFD workloads on VI ASICs. Hardware tests should include queue reset and recovery paths because MQD layout mistakes often surface during resume, preemption, or fault handling rather than simple dispatch.
