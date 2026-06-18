# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nvd.h

Purpose: provides Navi-era PM4 command processor packet definitions used by AMDGPU command emission and parsing code. It is a macro-only hardware ABI header for type 0/2/3 packet construction, opcode constants, and bitfield encoders for graphics, compute, memory, queue, cache, and synchronization commands.

Important APIs/types/functions: primary helpers are `PACKET0()`, `PACKET2()`, `PACKET3()`, `PACKET3_COMPUTE()`, `CP_PACKET_GET_TYPE()`, `CP_PACKET_GET_COUNT()`, `CP_PACKET0_GET_REG()`, and `CP_PACKET3_GET_OPCODE()`. Major opcode groups include `PACKET3_WRITE_DATA`, `WAIT_REG_MEM`, `INDIRECT_BUFFER`, `COPY_DATA`, `EVENT_WRITE`, `RELEASE_MEM`, `DMA_DATA`, `ACQUIRE_MEM`, register load/set packets, queue management packets, `INVALIDATE_TLBS`, `MAP_PROCESS`, `MAP_QUEUES`, `UNMAP_QUEUES`, `QUERY_STATUS`, and GFX11 `SET_Q_PREEMPTION_MODE`.

Control flow: there is no runtime control flow. Consumers combine opcode constants and field macros into dwords placed into GPU rings or indirect buffers. The macros encode packet headers, register offsets, GPU virtual addresses, cache policy, temporal hints, event selectors, queue masks, VMID/PASID fields, and memory synchronization operations.

State and persistence behavior: no driver state is stored. The definitions must exactly match the hardware packet ABI; emitted values persist only as command stream contents consumed by the GPU command processor.

Dependencies and integration points: relies on common bitfield helper macros such as `REG_SET()` and integer types from surrounding AMDGPU headers. It integrates with GFX, KIQ/MES, VM/TLB, fence, and queue-management emitters that need Navi PM4 packet encodings, and it overlaps conceptually with SDMA packet headers that use a separate packet format.

Risks and test signals: risks are off-by-one packet counts, incorrect register ranges, stale opcode aliases, duplicate opcode values with different meanings, and field-width truncation hidden by macros. Test signals include ring tests on graphics and compute queues, VM flush and TLB invalidation tests, fence and release-memory validation, SR-IOV queue map/unmap paths, command parser validation, and GPU hang/regression coverage when adding new packet fields.
