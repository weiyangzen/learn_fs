# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_sh_mask.h lines 1-4810

## Scope

This chunk is the front section of AMD's generated GFX 7.2 register shift/mask header. It includes the copyright/license block, the `GFX_7_2_SH_MASK_H` include guard, and 4,785 preprocessor definitions through the first fields of `GRBM_STATUS2`. Within this line range there are 2,392 `__SHIFT` constants and 2,431 `_MASK` constants; the mismatch is expected for a sliced generated file because some complete register field pairs can fall outside chunk boundaries.

The chunk contains no C functions, structs, enums, storage objects, callbacks, locks, allocations, or executable branches. Its public surface is a generated macro namespace for GFX 7.2 hardware register fields.

## Purpose

The file supplies bitfield metadata for older AMD GCN/CIK-era graphics hardware. The companion `gfx_7_2_d.h` header supplies register addresses such as `mmCP_HQD_ACTIVE`, `mmGB_ADDR_CONFIG`, `mmGRBM_STATUS`, and `ix*` indirect indices, while this shift/mask header supplies the bit positions and masks used to compose or decode 32-bit register values.

The core convention is:

- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for a field.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's least significant bit.

Driver code uses these names directly or through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` when programming rings, HQDs/MQDs, color/depth buffers, cache coherency, interrupts, tiling, power-gating, and debug/status paths.

Although this repository path sits under `sources/distributed-fs/ceph-client`, this source is AMD GPU hardware metadata and has no Ceph filesystem behavior.

## Important APIs, Types, And Macro Families

The API is the macro set itself. There are no local C types; the effective data type is a 32-bit hardware register value interpreted by the paired shift and mask constants.

Important macro families in this chunk are:

- `CB_*` color-buffer fields. These include blend constants and blend controls for render targets 0 through 7, color target base/pitch/slice/view/info/attribute registers, CMASK/FMASK base and slice registers, fast-clear words, target and shader output masks, color-buffer hardware control, cache/fifo tuning, performance counter selection/data, clock-gating controls, and CB debug bus fields. These fields drive render-target setup, blend behavior, fast clear/compression, MRT write masks, and CB diagnostics.
- `CP_*` command processor fields. This is the largest family in the chunk. It covers defy/debug transfer registers, graphics ring buffer base/control/read/write pointer state, CP interrupt enable/status words for ring 0 through ring 2, ring/pipe priority and VMID assignment, PFP/ME/CE/MEC microcode and RAM access, queue write-pointer polling, CPC/CPF/CPG performance counters, draw-window/PRT/streamout/statistics registers, EOP done/fence programming, append/atomic/semaphore registers, coherency control/base/size/status registers, CP DMA registers, stalled/busy status registers, parser/ME/CE/MEC halt and invalidate controls, indirect buffer and state-buffer registers, queue thresholds/availability/status, and debug interrupt status.
- `CPC_*`, `CPF_*`, and `CPG_*` fields for command processor front-end/control sub-blocks. These expose interrupt enables/status, busy and stall telemetry, queue processing state, performance counter selection, and clock-gating controls.
- `CP_HQD_*`, `CP_MQD_*`, and `CP_HPD_*` queue fields. These describe hardware queue descriptors and memory queue descriptors: queue active state, VMID/VQID, persistent state, pipe/queue priority, quantum, packet queue base/read/write pointers, doorbell control, indirect buffer base/control, interrupt queue timers, dequeue requests, semaphore/message state, atomic preop storage, EOP queue base/control, and MQD memory/cache policy.
- `DB_*` depth-buffer fields. These include z/stencil read and write bases, depth surface layout, z/stencil info, depth size/slice/view, render control, count control, render overrides, EQAA and shader control, depth bounds, clear values, HTILE base/surface/preload, stencil reference/mask state, depth/stencil test controls, alpha-to-mask, performance counters, debug registers, credits/watermarks/fifo depths, clock-gating control, zpass/occlusion counts, and debug readbacks.
- `GB_*`, `CC_*`, and `GC_USER_*` graphics backend fields. These cover render-backend redundancy and disable masks, global address configuration, backend mapping, GPU ID, RB daisy-chain ordering, 32 `GB_TILE_MODE*` entries, 16 `GB_MACROTILE_MODE*` entries, and EDC controls. These fields define memory tiling, pipe/bank/shader-engine topology, and backend availability.
- `RAS_*` signature fields for reliability/error-analysis signatures from SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- `GRBM_*` graphics register bus manager fields. In this chunk, the visible fields cover CAM remapping, read timeout, skew/power controls, and the main `GRBM_STATUS` bits for GUI active, CP/CB/DB/PA/SC/SPI/TA/VGT/GDS/IA/WD/SX/BCI busy/clean state. The range ends in early `GRBM_STATUS2` pipe request-pending fields.

## Control Flow

There is no runtime control flow in this header. The runtime use pattern is:

1. GFX 7.2 code includes `gfx_7_2_d.h`, `gfx_7_2_enum.h` where needed, and this shift/mask header.
2. The caller chooses a register address or indirect index from the companion address header.
3. The caller builds or decodes a 32-bit value with either direct `REGISTER__FIELD_MASK`/`REGISTER__FIELD__SHIFT` expressions or `REG_SET_FIELD()`/`REG_GET_FIELD()`.
4. AMDGPU/KFD MMIO helpers such as `RREG32()`, `WREG32()`, and indirect accessors perform the actual hardware read/write.

Examples visible in the source tree include `gfx_v7_0.c` programming `GB_ADDR_CONFIG`, `DB_DEBUG*`, `CB_HW_CONTROL`, `CP_RB0_CNTL`, `CP_HQD_*`, and `CP_INT_CNTL_RING0`; `amdgpu_amdkfd_gfx_v7.c` loading HQD/MQD state and enabling queue doorbells; and `cik.c` reading `GRBM_STATUS`/`GRBM_STATUS2` for idle and reset diagnostics.

## State And Persistence Behavior

The macros themselves are compile-time constants and store no state. The hardware registers they describe are stateful:

- CB and DB surface, blend, compression, clear, and tiling fields persist as GPU context or render state until reprogrammed, context-switched, reset, or lost during a power transition.
- CP ring-buffer, read/write pointer, indirect-buffer, semaphore, EOP, DMA, and coherency fields govern live command submission. Some fields are durable configuration, while pointer/status fields change as hardware consumes work.
- HQD/MQD fields are queue state used by KFD and compute/graphics queue management. Some values are loaded from memory queue descriptors, some are read back to save queue state, and some fields such as `ACTIVE`, `PROCESSING_IQ`, `DEQUEUE_REQ`, and doorbell hit bits reflect live scheduler state.
- Interrupt enable registers persist until changed, while interrupt status/debug registers may be sticky, write-clear, or live depending on the hardware semantics outside this header.
- CP/CPC/CPF/DB/CB performance counters and busy/stall/debug registers are hardware-updated telemetry, not ordinary software variables.
- GB address/tile/macro-tile/backend registers encode ASIC topology and memory layout. Incorrect values can affect every tiled surface and render backend.
- GRBM status fields are live status/readback bits used for idle detection, reset decisions, and hang diagnosis.

The header does not encode access permissions, reset values, sticky-bit semantics, write-one-to-clear behavior, or read side effects. Consumers must rely on the ASIC programming guide and the surrounding driver sequence for those semantics.

## Dependencies

This chunk depends on generated-header synchronization across:

- `gca/gfx_7_2_d.h`, which provides matching `mm*`, `ix*`, and related register identifiers.
- `gca/gfx_7_2_enum.h`, which provides generation-specific enum values used with many of these fields.
- AMDGPU register helper macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()`, plus low-level MMIO helpers such as `RREG32()`, `WREG32()`, and indirect register accessors.
- GFX 7.2/CIK driver code that includes this exact header: `amdgpu/gfx_v7_0.c`, `amdgpu/cik.c`, `amdgpu/cik_sdma.c`, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, `amdkfd/kfd_device_queue_manager_cik.c`, legacy DPM code such as `pm/legacy-dpm/kv_dpm.c`, and older powerplay/SMU files such as `ci_baco.c` and `ci_smumgr.c`.
- Hardware-specific initialization tables and golden settings for Bonaire/Hawaii/Kaveri-style GFX 7.x devices, especially for `GB_ADDR_CONFIG`, DB/CB debug workarounds, clock gating, and queue initialization.

## Integration Points

Key integration points in the tree are:

- Graphics initialization in `gfx_v7_0.c`, which sets GB address configuration, DB debug and CB hardware-control workarounds, shader memory settings, command processor rings, HQD/MQD defaults, CP interrupts, clock gating, and idle/reset paths using these field definitions.
- KFD queue management in `amdgpu_amdkfd_gfx_v7.c` and `kfd_device_queue_manager_cik.c`, which uses `CP_HQD_*`, `CP_MQD_*`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_IQ_TIMER`, and `CP_HQD_DEQUEUE_REQUEST` fields to load, activate, inspect, and drain hardware queues.
- GPU reset and hang diagnostics in `cik.c` and `gfx_v7_0.c`, where `GRBM_STATUS`, `GRBM_STATUS2`, CP busy/stalled status, CB/DB clean/busy bits, and queue status fields indicate whether engines are idle or wedged.
- Power and clock management code that touches CB/DB/CP clock-gating and memory sleep controls, BACO/SMU paths, and DIDT/EDC-adjacent controls.
- Render and memory layout programming through CB/DB/GB fields. Surface setup, fast clear/compression, tiling, macro-tiling, render-backend mapping, and depth/stencil behavior all depend on this header matching the hardware generation.
- Performance and debug tooling that selects CB/DB/CP/CPC/CPF/CPG performance counters and decodes low/high counter words, debug buses, and signature registers.

## Risks And Edge Cases

- Header/address mismatch is the main correctness risk. Pairing GFX 7.2 masks with another generation's offset header can compile if names overlap, but it may program wrong bits or wrong registers.
- This chunk ends mid-register at `GRBM_STATUS2`; later fields for the same register and subsequent register families are outside this research slice and must be merged from later chunks.
- Many fields are generation-sensitive despite familiar names across GFX generations. `CP_HQD_*`, `CP_MQD_*`, `GB_TILE_MODE*`, `DB_DEBUG*`, and interrupt word layouts are especially risky to copy between ASICs.
- Full-width masks such as `0xffffffff` appear for addresses, data, counters, clear words, debug reads, and signatures. A full-width mask does not imply the register is safe for arbitrary writes.
- Address fields often have alignment implied by the shift or low-bit mask, such as 256-byte bases, 4-byte queue pointers, or 8-byte semaphore addresses. Writing unaligned values can silently drop low bits.
- Queue and ring pointer fields are live producer/consumer state. Incorrect `RB_BUFSZ`, `RB_BLKSZ`, read-pointer reporting addresses, doorbell offsets, or write-pointer polling settings can hang command submission.
- HQD dequeue and interrupt-queue bits are live scheduler state. Polling code must tolerate races with hardware clearing `ACTIVE`, `PROCESSING_IQ`, `IQ_REQ_PEND`, and related status bits.
- Interrupt enable and status names are very similar across ring, CPC, ME1/ME2 pipe, and debug variants. Confusing enable/status/asserted fields can leave interrupts masked, uncleared, or spuriously enabled.
- DB/CB debug and compression controls are workaround-sensitive. Incorrect values can break fast clears, HTILE/CMASK/FMASK behavior, depth/stencil tests, color writes, or performance.
- GB tiling and backend topology fields affect memory swizzle and render-backend routing. Bad `GB_ADDR_CONFIG`, tile mode, macro-tile mode, or backend-disable settings can corrupt rendering globally.
- Reserved fields and undocumented bits should be preserved in read-modify-write sequences unless the hardware sequence explicitly calls for a full-register write.

## Test And Validation Signals

Useful validation for this generated-header chunk is mostly build, static, and hardware smoke coverage:

- Build CIK/GFX7 AMDGPU and KFD translation units that include `gfx_7_2_sh_mask.h`, especially `gfx_v7_0.c`, `cik.c`, `cik_sdma.c`, `amdgpu_amdkfd_gfx_v7.c`, `kfd_device_queue_manager_cik.c`, `kv_dpm.c`, `ci_baco.c`, and `ci_smumgr.c`.
- Static generated-header checks that field masks align with shifts, fields do not unexpectedly overlap inside a register, and names match the companion `gfx_7_2_d.h` register-address header.
- Boot and modeset smoke tests on GFX 7.x hardware that exercise golden register initialization, `GB_ADDR_CONFIG`, DB/CB workarounds, clock/power gating, suspend/resume, and GPU reset.
- Graphics rendering tests covering blend state, MRT masks, fast clear, CMASK/FMASK, depth/stencil, HTILE, MSAA/EQAA, alpha-to-mask, and tiled/macro-tiled surfaces.
- Command submission tests for graphics rings and KFD queues: ring init, read/write pointer reporting, doorbell writes, indirect buffers, EOP fences, semaphores, dequeue, queue destroy, and GPU reset while queues are active.
- Interrupt tests for CP ring/context interrupts, timestamp/opcode/error paths, CPC/ME pipe interrupts, and interrupt enable/status clearing.
- Hang and idle-detection tests that compare `GRBM_STATUS`, `GRBM_STATUS2`, `CP_STAT`, `CP_BUSY_STAT`, `CP_CPC_BUSY_STAT`, `CP_CPF_BUSY_STAT`, CB debug bus, and DB debug readouts against expected busy/idle transitions.
- Performance-counter tests that select CB/DB/CP/CPC/CPF/CPG counters and verify low/high counter reads change plausibly under idle, graphics, compute, and memory-heavy workloads.
