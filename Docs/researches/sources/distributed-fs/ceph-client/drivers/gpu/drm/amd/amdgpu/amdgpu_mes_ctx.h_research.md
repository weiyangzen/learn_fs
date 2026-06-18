## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mes_ctx.h

Purpose: defines MES context metadata layout used for GFX, compute, and SDMA queues, including ring memory, save/restore metadata, writeback slots, IB-test buffers, and per-file MES context data.

Important APIs/types: offset enums define writeback slot roles (`RPTR`, `WPTR`, `FENCE`, `COND_EXE`, `TRAIL_FENCE`) and memory offsets for ring/IB/padding. Constants bound MES context ring counts for one GFX, four compute, and two SDMA rings. `struct amdgpu_mes_ctx_meta_data` is page-aligned and contains per-ring ring buffers, GFX v10 metadata, GDS backup, MEC HPD, SDMA CSA, writeback slots, and aligned IB test buffers. `struct amdgpu_mes_ctx_data` stores the metadata BO, GPU/MC addresses, VA mapping, CPU pointer, and gang IDs by hardware IP.

Control flow contract: MES/user queue setup allocates and maps a metadata BO matching this layout, then firmware and ring tests use the fixed offsets. The fence queue flag/mask constants identify MES queue IDs in fence values.

State and persistence: metadata lives in GPU BOs mapped for the process/context lifetime. It is runtime state, not durable. Gang IDs track per-IP scheduling gang association.

Dependencies/integration: includes `v10_structs.h` for GFX metadata. Used by MES context and user-mode queue setup, ring tests, and firmware state save/restore.

Risks: this is a firmware-visible memory layout; alignment and size changes are ABI-sensitive. The header defines `AMDGPU_FENCE_MES_QUEUE_FLAG` and mask twice, which is harmless to the compiler only because values match but is a maintenance risk. Array sizing by `AMDGPU_HW_IP_DMA+1` assumes enum ordering.

Test signals: user queue/MES context allocation tests, firmware queue bring-up, IB ring tests using metadata IB buffers, and structure size/alignment assertions where available.
