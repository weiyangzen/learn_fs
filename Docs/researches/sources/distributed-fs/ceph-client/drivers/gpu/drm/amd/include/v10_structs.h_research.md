# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v10_structs.h

## Purpose

This header defines GFX10 hardware queue and context-save memory layouts used by AMDGPU. It exposes fixed dword-ordered structures for graphics MQDs, SDMA MQDs, compute MQDs, and GFX metadata used for CE/DE indirect-buffer preemption state. These structures mirror GPU firmware/hardware save areas rather than implementing algorithms.

## Important APIs, Types, and Structures

- `struct v10_gfx_mqd`: 512 dwords of graphics MQD state. Important clusters include:
  - queue disable and base/VMID fields around offsets 106 and 128-145.
  - HQD queue state such as active, VMID, priority, quantum, ring base, read/write pointers, doorbell control, HQD control, mapped state, queue-manager control, HQ status/control, and MQD control.
  - performance/stat counters for primitives, shader thread trace, pixel/primitive/vertex/geometry/hull/domain/compute invocation counters.
  - stream-out filled sizes, DMA max size/instance counts, base IB address fields, shader resource registers, and large depth-buffer occlusion counter blocks.
  - the structure ends at reserved dword 511.
- `struct v10_sdma_mqd`: SDMA queue descriptor with ring-buffer control/base/read/write pointers, polling and report addresses, IB control/base/size, skip/context/doorbell/status/watermark fields, CSA address, preempt/dummy registers, AQL control, mid-command data registers, and driver-internal `sdma_engine_id`/`sdma_queue_id` in the final two dwords.
- `struct v10_compute_mqd`: 512 dwords of compute queue state. Important clusters include:
  - dispatch dimensions, starts, thread counts, program/TBA/TMA addresses, program resources, VMID, resource limits, static thread management, temp-ring size, restart coordinates, thread-trace enable, dispatch IDs, relaunch, and wave restore.
  - 16 compute user-data registers.
  - query/connect/save/restore timestamps and read indices.
  - GDS and context save addresses/masks.
  - HQD persistent state, pipe/queue priority, PQ base/read/write pointers, doorbell control, IB control, dequeue/semaphore/message/atomic fields, scheduler/status/control, EOP ring, context-save layout, GDS resource state, error, AQL control, suspend offsets, IQ timer packet fields, set-resource packet fields, queue doorbell IDs, and reserved padding through dword 511.
- `struct v10_ce_ib_state`: 10-dword constant-engine IB save area for non-chained and chained IB fields.
- `struct v10_de_ib_state`: 27-dword draw-engine IB save area with completion/status, chain addresses/sizes, preamble ranges, draw/dispatch indirect bases, GDS backup, index base, and sample control.
- `struct v10_gfx_meta_data`: 4 KiB metadata block containing CE payload, reserved padding, DE payload, preempted PFP IB base address, and trailing reserved padding.

## Control Flow

There is no local control flow. Runtime flow is structural:

1. Driver or firmware allocates MQD/context-save memory with the required size and alignment for the engine generation.
2. Initialization code fills selected fields and leaves reserved fields zeroed or firmware-owned.
3. Hardware/firmware consumes these layouts to schedule, save, restore, preempt, and resume graphics, compute, and SDMA queues.
4. On context save or preemption, hardware/firmware updates pointer, timestamp, counter, and metadata fields that the driver may later inspect or reuse.

The GFX metadata structures describe CE/DE IB save/restore flow: non-chained and chained IB addresses, offsets, preamble ranges, and indirect base state are captured so a preempted graphics workload can resume correctly.

## State and Persistence Behavior

These structures are persistent GPU-visible state blocks. They may live in VRAM, GTT, or firmware-managed memory and outlive individual command submissions. The many `reserved_*` dwords are part of the persisted ABI and preserve exact offsets for hardware and future fields. The final SDMA engine/queue IDs are explicitly driver-internal repurposing of otherwise reserved space. Queue pointers, doorbells, context-save addresses, counters, timestamps, EOP information, and metadata fields are all stateful across scheduling events, preemption, suspend/resume, and reset recovery.

## Dependencies and Integration Points

The header relies on `uint32_t` being available from the including context. It integrates with AMDGPU GFX10 queue setup, KFD compute queue management, SDMA queue initialization, MQD allocation, context save/restore, GPU reset, preemption, performance counter capture, shader thread tracing, and debug dump code. It is closely related to register definitions and packet builders that know the meaning of the individual CP, SQ, VGT, DB, and SDMA fields.

## Risks

- Field order and dword offsets are hardware ABI. Reordering, type-size changes, or removing reserved fields can break queue scheduling or context restore.
- There are no `static_assert(sizeof(...))` or `offsetof` checks in this header, so layout validation depends on consumers or external tests.
- The structures use hundreds of plain `uint32_t` fields instead of typed substructures; incorrect writes can compile but corrupt hardware state.
- The SDMA structure uses final reserved positions for driver-internal IDs. Any future hardware use of those positions would need coordinated migration.
- GFX metadata comments specify 4 KiB and 64-byte alignment requirements, but the header cannot enforce allocation alignment.
- Many fields are split low/high address pairs. Consumers must compose/decompose GPU addresses consistently and honor alignment requirements.
- Reserved fields should be zeroed unless explicitly owned by firmware/hardware; stale data can be interpreted by newer firmware.

## Test Signals

- Compile-time ABI tests should assert `sizeof(struct v10_gfx_mqd) == 512 * 4`, `sizeof(struct v10_compute_mqd) == 512 * 4`, expected SDMA size, and `sizeof(struct v10_gfx_meta_data) == 4096`.
- `offsetof` tests for key fields such as `disable_queue`, `cp_mqd_base_addr`, HQD pointer/doorbell fields, `sdma_engine_id`, `sdma_queue_id`, and compute `queue_doorbell_id*` should match hardware documentation.
- Runtime queue tests should cover graphics queue creation, compute dispatch, SDMA copy, preemption, suspend/resume, reset recovery, and context-save restoration on GFX10 devices.
- Debug dumps of MQDs should decode expected nonzero fields after queue activity and remain stable across suspend/resume.
- Memory sanitization tests should ensure reserved dwords are initialized to zero before firmware sees the block.
