# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v11_structs.h

## Purpose

This header defines GFX11 hardware queue descriptor layouts for AMDGPU. Like the GFX10 header, it models firmware/hardware ABI state rather than executable logic, but it updates the graphics, SDMA, and compute MQD layouts for the GFX11 generation. New fields cover shadow/GDS/firmware work areas, checksums/query state, control buffers, fences, GWS values, expanded SDMA mid-command/debug state, and GFX11 compute dispatch/control fields.

## Important APIs, Types, and Structures

- `struct v11_gfx_mqd`: 512 dwords of graphics MQD state. Compared with GFX10, early dwords include `shadow_base_*`, `gds_bkup_base_*`, `fw_work_area_base_*`, `shadow_initialized`, and `ib_vmid`. Other notable clusters:
  - checksum and MQD query fields around offsets 84-95.
  - `control_buf_addr_*` at offsets 104-105, queue disable at 106, and the familiar CP graphics HQD cluster at 128-162.
  - primitive counters, shader thread trace fields, graphics invocation counters, stream-out filled sizes, DMA limits, base IB address fields, shader resource fields, and depth-buffer occlusion counters.
  - `fence_address_lo/hi` at final offsets 510-511.
- `struct v11_sdma_mqd`: SDMA queue descriptor with offset comments. It includes ring base/read/write pointers, report addresses, IB controls, skip/context/doorbell fields, CSA address, scheduler control, preempt and ring-buffer preempt fields, AQL/minor-pointer update fields, mid-command data 0-10, mid-command control, F32 debug registers, reserved space, and driver-internal `sdma_engine_id`/`sdma_queue_id`.
- `struct v11_compute_mqd`: 512 dwords of compute state. Important clusters include:
  - dispatch dimensions, starts, thread counts, program address, dispatch packet address, dispatch scratch base, program resources, VMID, resource limits, static thread management SE0-SE7, request control, user accumulators, program resource 3, DDID index, shader checksum, dispatch interleave, relaunch, and wave restore.
  - 16 compute user-data registers and compute invocation counters.
  - MQD query/connect/save/restore timestamp fields and read indices.
  - GDS/context save state, PQ execution and packet status, HQD state, EOP/context-save state, AQL and queue pointer fields.
  - IQ timer packet and set-resource packet storage, 16 queue doorbell IDs, control-buffer address/write/drop pointers/entry count, draw-ring address, fence address, and 64 GWS value dwords at the end.

## Control Flow

There is no direct control flow. Runtime behavior follows the queue lifecycle:

1. Driver code allocates and initializes GFX11 MQD memory for graphics, SDMA, or compute queues.
2. Hardware/firmware reads fixed offsets to configure rings, doorbells, VMIDs, priorities, context-save areas, and dispatch metadata.
3. During scheduling, preemption, query, or reset, firmware updates timestamp, pointer, status, fence, control-buffer, and GWS fields.
4. Driver debug, reset, and queue-management paths inspect or rewrite these layouts to resume work or diagnose failures.

The layout extends GFX10 flows with GFX11-specific shadow/control-buffer and fence/GWS state that makes queue restore and synchronization more explicit.

## State and Persistence Behavior

The structures define persistent GPU-visible queue state. Address pairs, read/write pointers, doorbell controls, VMIDs, priorities, context-save base addresses, EOP state, control buffers, query timestamps, and fence/GWS values persist across queue scheduling events. Reserved dwords are also persistent ABI padding and must be preserved or zeroed according to the owning path. The final SDMA `sdma_engine_id` and `sdma_queue_id` are driver-internal state stored inside the descriptor.

## Dependencies and Integration Points

The header relies on `uint32_t` being available in the including context. It integrates with AMDGPU GFX11 graphics queue management, compute/KFD queue creation, SDMA queue setup, firmware scheduling, GDS/GWS handling, context save/restore, preemption, GPU reset recovery, shader tracing, queue debug dumps, and hardware counter collection. It shares naming and layout patterns with `v10_structs.h` but must be selected by generation-specific code, not treated as interchangeable with GFX10.

## Risks

- GFX11 offsets are ABI-critical. The added early fields in `v11_gfx_mqd` and compute fields mean reuse of GFX10 initialization logic without generation guards can write the wrong dwords.
- The header has no `static_assert` or `offsetof` checks to verify the documented offset comments.
- Some SDMA offset comments around reserved fields appear inconsistent (`reserved_71` onward restarts decimal offset comments briefly), so comments should not be the sole source of truth for generated checks.
- Driver-internal SDMA engine/queue IDs occupy repurposed reserved dwords; this depends on firmware not using those slots.
- Many address fields are low/high pairs; misprogramming address halves can corrupt queue state or fault firmware.
- Fence, control-buffer, and GWS fields add synchronization and state-restoration surface; stale values after reset or descriptor reuse can cause subtle queue behavior.
- Reserved fields and generation-specific additions must be zeroed or initialized exactly as firmware expects.

## Test Signals

- ABI tests should assert `sizeof(struct v11_gfx_mqd) == 512 * 4`, `sizeof(struct v11_compute_mqd) == 512 * 4`, expected SDMA size, and key offsets for `shadow_base_lo`, `checksum_lo`, `control_buf_addr_lo`, `disable_queue`, `cp_mqd_base_addr`, graphics `fence_address_lo`, compute `queue_doorbell_id0`, control-buffer fields, compute `fence_address_lo`, and GWS values.
- Runtime tests on GFX11 hardware should cover graphics and compute queue creation, SDMA copy queues, preemption, suspend/resume, reset recovery, queue fences, GWS usage, and control-buffer operation.
- Debug dumps should show generation-correct field interpretation and avoid treating GFX11 MQDs as GFX10 layouts.
- Stress tests should cover descriptor reuse after reset and verify stale fence/GWS/control-buffer fields do not leak into new queues.
- Static analysis can compare offset comments to compiler `offsetof` output to catch drift or comment mistakes.
