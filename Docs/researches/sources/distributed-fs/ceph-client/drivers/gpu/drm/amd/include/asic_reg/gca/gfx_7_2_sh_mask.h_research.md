# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002706`: lines 1-4810, `Docs/researches/chunks/subset-b-002706_research.md`
- `subset-b-002707`: lines 4811-9360, `Docs/researches/chunks/subset-b-002707_research.md`
- `subset-b-002708`: lines 9361-14179, `Docs/researches/chunks/subset-b-002708_research.md`
- `subset-b-002709`: lines 14180-18444, `Docs/researches/chunks/subset-b-002709_research.md`

## Chunk Research

### subset-b-002706: lines 1-4810

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

### subset-b-002707: lines 4811-9360

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_sh_mask.h lines 4811-9360

## Scope

This chunk covers the middle of the generated AMD GCA/GFX 7.2 shift/mask header. It contains 4,550 `#define` lines: 2,275 `_MASK` constants and 2,275 matching `__SHIFT` constants. The range starts inside the `GRBM_STATUS2` field definitions, runs through GRBM status/debug/performance-counter fields, primitive assembler and scan-converter fields, clipper/setup debug fields, compute dispatch and shader-program fields, RLC power/clock/performance-control fields, SPI shader-input/debug/performance fields, and ends in the first `CGTS_CU0_SP0_CTRL_REG` fields.

This file range has no C functions, structs, enums, variables, inline helpers, conditionals, allocations, locks, callbacks, or executable branches. The exported surface is entirely the generated preprocessor namespace of hardware register bit masks and shifts.

## Purpose

`gfx_7_2_sh_mask.h` gives CIK/GFX7-era AMDGPU, KFD, and power-management code the bit-level contract for composing and decoding GCA register values. The companion offset header supplies register addresses such as `mmGRBM_GFX_INDEX`, `mmPA_SC_RASTER_CONFIG`, `mmRLC_SERDES_WR_CTRL`, `mmSPI_PS_INPUT_CNTL_0`, and `mmCGTS_SM_CTRL_REG`; this header supplies the field positions inside the 32-bit register values.

The macros let runtime code use generated names instead of raw hex fields when it:

- Selects shader engine/shader array/instance addressing through GRBM.
- Polls graphics-block busy/status and read-error state.
- Programs PA/SC viewport, clipping, rasterization, scissor, antialiasing, and performance-counter registers.
- Configures compute dispatch registers, shader resource registers, user data, and VMID/resource limits.
- Manages RLC safe mode, memory sleep, load balancing, power gating, microcode windows, SerDes controls, and streaming performance monitor delays.
- Programs SPI pixel-shader input interpolation, shader export formats, debug/trap controls, compute queue reset, CU resource reservation, and SPI performance counters.
- Controls CGTS clock/test state and TCC disable masks.

Although the repository path is under `sources/distributed-fs/ceph-client`, this chunk is AMD GPU hardware metadata and has no Ceph filesystem behavior.

## Important API Surface

The "APIs" in this chunk are generated macro pairs named `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`. They are consumed by register helpers such as `REG_SET_FIELD`/`REG_GET_FIELD` and by direct MMIO read/write paths such as `RREG32`/`WREG32`.

Key macro families in this range:

- `GRBM_*` at lines 4811-5268: status and per-SE clean/busy bits, GRBM soft-reset selectors, debug-index/data, `GRBM_GFX_INDEX` instance/SH/SE addressing and broadcast bits, read-error requester fields, interrupt enables, global and per-SE performance-counter selectors, counter high/low words, scratch registers, and generic debug index/data fields.
- `PA_CL_*`, `PA_SU_*`, and `PA_SC_*` at lines 5269-6800: viewport scale/offset/depth fields, clip control, user clip planes, point/line/primitive setup, polygon offset, AA sample locations, centroid priority, clip rectangles, edge/line/stipple controls, raster config, scissors, viewport depth bounds, FIFO sizing, screen-trap registers, PA/SC counter selectors and values, clock-control registers, and PA/SC debug access registers.
- `CLIPPER_DEBUG_REG00` through `CLIPPER_DEBUG_REG19`, `SXIFCCG_DEBUG_REG0` through `SXIFCCG_DEBUG_REG3`, and `SETUP_DEBUG_REG0` through `SETUP_DEBUG_REG5` at lines 6801-7428: debug snapshots for clipper FIFOs, primitive state machines, setup block state, and related inter-block flow-control signals.
- `COMPUTE_*` and `CSPRIV_*` at lines 7447-7666: compute dispatch initiator bits, grid dimensions and starts, per-workgroup thread counts, pipeline/perf enable bits, program/TBA/TMA pointers, `COMPUTE_PGM_RSRC1/2`, VMID, resource limits, static thread management masks per SE, temp-ring size, restart coordinates, thread-trace enable, reserved bits, user data registers 0-15, and CSPRIV thread-trace/control fields.
- `RLC_*` and `CGTT_RLC_CLK_CTRL` at lines 7667-8300: RLC control/debug, memory sleep, safe mode, soft reset, perfmon selectors and counters, clock control, load-balancing counters, driver CPDMA status, GPM microcode address/data, GPU clock count capture, power-gating controls and status, static/always-on CU masks, SerDes read/write selectors and master masks, RLC GPM general/scratch/log registers, RLC SPM interrupt/perfmon ring controls, mux selectors, and block-specific SPM sample delays for CPG/CPC/CPF/CB/DB/PA/GDS/IA/SC/TCC/TCA/TCP/TA/TD/VGT/SPI/SQG/TCS/SX/DBR/CBR.
- `SPI_*` at lines 8301-9310: pixel-shader input controls 0-31, input enable/address bitmaps, interpolation controls, shader position/Z/color export formats, arbitration priorities/cycles, GDBG trap/TBA/TMA/data controls, compute queue reset, per-CU resource reservation and enable masks for CUs 0-11, PS maximum wave ID, SPI config and debug controls, performance-counter selectors/bins/counter high-low words, config control 1, and `SPI_DEBUG_BUSY` stage/resource busy bits.
- `CGTS_*` at lines 9311-9360: shader-machine clock/test controls, read mux/data fields, TCC disable masks, user TCC disable masks, and the start of `CGTS_CU0_SP0_CTRL_REG` for SP00/SP01 override and busy/load-store/SIMD-busy controls.

There are no local types. The effective data type for every macro is a 32-bit hardware register word, with a few software read paths combining high/low counter words into wider values outside this header.

## Control Flow

This header contributes no direct control flow. Runtime consumers use a consistent pattern:

1. Include the generated GFX 7.2 offset and mask headers.
2. Select a register offset from the companion offset header.
3. Read, modify, compose, or test a 32-bit value with the `_MASK` and `__SHIFT` macros.
4. Access hardware through AMDGPU/KFD register helpers such as `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
5. Let the surrounding GFX, KFD, or power-management sequence provide locking, ordering, polling, and reset behavior.

Concrete consumers in this tree include `amdgpu/gfx_v7_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, `amdkfd/kfd_device_queue_manager_cik.c`, CIK SDMA and DPM code, and older PowerPlay/SMU manager code that includes `gca/gfx_7_2_sh_mask.h`.

Examples of runtime behavior supplied by consumers:

- `gfx_v7_0_select_se_sh()` composes `GRBM_GFX_INDEX` with instance, SH, SE, and broadcast fields, then writes `mmGRBM_GFX_INDEX`.
- GFX clock-gating setup uses `RLC_SERDES_WR_*` and `CGTS_SM_CTRL_REG` masks while the RLC is halted and GRBM index access is serialized.
- GFX soft-reset detection reads `mmGRBM_STATUS2` and tests `GRBM_STATUS2__RLC_BUSY_MASK` before adding `GRBM_SOFT_RESET__SOFT_RESET_RLC_MASK`.
- KFD wave-control code writes `mmGRBM_GFX_INDEX`, executes an SQ command, then restores the GRBM broadcast index using the GRBM broadcast masks.

## State And Persistence Behavior

The macros are compile-time constants and persist no software state. They describe hardware state that may be persistent, transient, or read-only depending on the register:

- GRBM status, read-error, debug snapshot, and busy fields expose live hardware state. Values can change between reads as queues drain, requests complete, blocks go idle, or reset logic runs.
- GRBM GFX index state is a selector for subsequent instanced register accesses. It persists until rewritten, so callers that change it must serialize access and restore a broadcast/default value when required.
- PA/SC/CL/SU rasterization, clip, viewport, scissor, sample-location, and shader-input fields are programmed pipeline state. They persist until command submission, context restore, initialization, or reset writes new values.
- Compute program, resource, VMID, user-data, and dispatch fields are command/context state for compute workloads. Incorrect fields affect wave launch, address interpretation, and resource allocation.
- RLC control, power-gating, clock-gating, SerDes, SPM, GPM, and memory-sleep fields persist in hardware control registers and interact with firmware-managed sequencing, power transitions, suspend/resume, and GPU reset.
- SPI debug/trap/resource-reservation fields control live shader processor behavior and expose live shader-stage busy state. Debug and performance-counter fields may be volatile while workloads execute.
- Performance counters expose hardware-updated high/low words; software must handle read ordering and rollover coherently where a wider value is reconstructed.
- CGTS fields affect clock/test gating, TCC disable visibility, and per-CU/SP override behavior. They are power/stability-sensitive control bits, not generic scratch state.

This header does not encode access permissions, reset values, side effects, required delays, or lock requirements. Full-width masks such as `DATA_REGISTER_MASK`, counter masks, user-data masks, and high/low counter masks do not imply safe arbitrary writes.

## Dependencies And Integration Points

- Must remain synchronized with the generated GFX 7.2 register database and the companion `gfx_7_2_offset.h`; a correct mask with a wrong offset is still a wrong hardware access.
- Relies on AMDGPU macro naming conventions used by `REG_SET_FIELD` and `REG_GET_FIELD`: the helper expands from a register and field name to the generated `_MASK` and `__SHIFT` constants.
- Integrates with direct MMIO helpers in the GFX7 driver (`RREG32`, `WREG32`) and with locked GRBM-index selection through `adev->grbm_idx_mutex` around instanced/broadcast register access.
- Integrates with KFD wave-control and queue-management paths that need GRBM index selection, SQ command execution, compute-resource programming, and VMID/user-data setup.
- Integrates with power-management and clock-gating code through CGTT/CGTS, RLC memory-sleep, RLC power-gating, RLC SerDes, TCC disable, and SPM/performance monitor fields.
- Integrates with diagnostics and debug paths through GRBM read-error/status fields, clipper/setup/SPI/RLC debug registers, busy bits, scratch registers, and performance counters.

## Risks And Edge Cases

- The chunk is boundary-partial. It starts after the beginning of `GRBM_STATUS2` and ends before the full `CGTS_CU0_SP0_CTRL_REG` group, so the merge/reconciliation lane must combine adjacent chunks for complete register-family documentation.
- Generation drift is the highest correctness risk. Similar macro names exist in GFX6, GFX8, and newer GC headers, but bit positions are not guaranteed to match. Mixing a GFX 7.2 mask with another generation's offset or programming sequence can silently write the wrong field.
- GRBM index handling is stateful and global to instanced register access. Missing locking or failing to restore broadcast selection can route later writes to the wrong shader engine, shader array, or instance.
- Read-modify-write sequences must preserve reserved or unrelated bits. This generated header names known fields but does not document reserved-bit behavior or write-one-to-clear/write-one-to-set semantics.
- Status and debug fields are race-prone by design. Busy bits, FIFO fullness, read-error requesters, shader-stage busy flags, and debug snapshots can change while software is polling or dumping state.
- Reset and power-control masks are high impact. Incorrect `GRBM_SOFT_RESET`, RLC safe-mode, RLC power-gating, RLC memory-sleep, SerDes, CGTT, or CGTS writes can hang graphics engines, break clock/power gating, or prevent blocks from waking.
- Compute and SPI resource fields are ABI-sensitive for queue launch and shader execution. Bad program-resource, VMID, thread-count, input-control, trap, or CU reservation fields can corrupt dispatch, break KFD queues, or produce hard-to-debug GPU faults.
- Performance counter high/low fields can tear if read while counters update. Consumers need established counter sampling order or hardware freeze mechanisms where required.
- Debug register names expose internal block signals and may not be stable across ASIC steppings. They are useful for diagnostics but should not be treated as portable policy interfaces.

## Test And Validation Signals

Useful validation is primarily build, static generated-header checks, and hardware smoke coverage:

- Build AMDGPU/KFD with CIK/GFX7 support enabled to catch duplicate/missing macro names and helper-expansion failures in consumers of `gfx_7_2_sh_mask.h`.
- Compare this header against the generated GFX 7.2 register source and `gfx_7_2_offset.h`; verify every field has one `_MASK` and one `__SHIFT`, masks align with shifts, and register-family ordering matches offsets.
- Static scan for overlapping fields inside a register, allowing intentional full-width data/counter/debug registers and documented aliases.
- Boot and run CIK/GFX7 hardware through graphics workloads, compute workloads, suspend/resume, runtime power management, and GPU reset to exercise GRBM status/reset, PA/SC/SPI programming, RLC power/clock management, and CGTS paths.
- KFD validation with queue creation/destruction, wave control, VMID/PASID mappings, compute dispatch, and trap/debug flows that depend on GRBM index and compute/SPI fields.
- Clock/power-gating validation that toggles GFX CGTS/MGCG/MGLS support and verifies RLC halt/update sequences, CGTT/CGTS programming, memory sleep, and SerDes override behavior without hangs or idle-power regressions.
- Performance-counter validation for GRBM, PA_SU, PA_SC, RLC, and SPI counters under idle, graphics, and compute workloads, including high/low rollover handling.
- Diagnostics validation by forcing or observing read-error/status/busy/debug paths and ensuring decoded fields produce plausible block names and do not misidentify the busy/reset source.

### subset-b-002708: lines 9361-14179

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_sh_mask.h lines 9361-14179

## Purpose

This chunk is a generated AMD GFX 7.2 shader/graphics-core register field mask header range. It contains C preprocessor constants for bit masks and shifts in GCA/GFX 7.2 registers, covering compute-unit clock-throttling controls, shader processor interface state, shader queue/debug/resource descriptors, thread trace packet formats, export/SX diagnostics, texture/cache performance counters, and texture processor controls. The header is declarative hardware metadata; it has no runtime logic, but it is part of the source-level ABI used by AMDGPU and KFD driver code to compose and decode 32-bit register values.

The range starts in the middle of the `CGTS_CU0_*` per-compute-unit clock-throttling definitions and ends inside the `TCP_EDC_COUNTER` family. The preceding chunk contains the beginning of the CGTS section, and the next lines contain the missing `TCP_EDC_COUNTER__DED_COUNT__SHIFT` plus later TCP/TC cache policy masks. Merge/reconciliation should treat this as a large middle slice of `gfx_7_2_sh_mask.h`, not as a complete semantic section by itself.

## Major Register Areas Covered

The opening section defines `CGTS_CU0` through `CGTS_CU15` masks for compute-unit clock-throttling and light-sleep control. Each CU has repeated control registers for SP0/SP1, LDS/SQ, TA or TA/SQC, and TD/TCP blocks. The fields are mostly per-block enable/override/busy-override/light-sleep/SIMD-busy controls, using low and high 16-bit lanes for paired units such as `SP00`/`SP01`, `LDS`/`SQ`, and `TD`/`TCP`.

The next section covers clock gating and SPI state. `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, and `CGTT_BCI_CLK_CTRL` provide on-delay, off-hysteresis, and soft override fields. `SPI_WF_LIFETIME_*` exposes wavefront lifetime limit/status controls. `SPI_SLAVE_DEBUG_BUSY`, `SPI_LB_*`, `SPI_PG_ENABLE_STATIC_CU_MASK`, `SPI_GDS_CREDITS`, `SPI_SX_*`, `SPI_CSQ_WF_ACTIVE_*`, `BCI_DEBUG_READ`, trap screen registers, shader trap base/memory address registers, shader program address registers, and shader resource registers describe SPI wave dispatch, debugging, trap handling, static CU masks, GDS/SX buffering, and active wave accounting.

The shader-programming block covers PS, VS, GS, ES, HS, and LS stages. It defines trap base/address and trap memory address low/high registers, program base low/high registers, `SPI_SHADER_PGM_RSRC1/2/3_*` fields for VGPR/SGPR usage, priority, float mode, privilege, DX10 clamp, debug/IEEE mode, CU enable, wave limits, LDS size, scratch/trap/user-SGPR setup, stream-out enables, exception enables, and stage-specific allocation controls. The same section defines `SPI_SHADER_USER_DATA_*_0` through `_15` payload registers for each stage, all as full-width data fields.

The SQ/SQC section covers shader queue configuration, cache configuration, random wave priority, register credits, FIFO sizes, interrupt auto-mask/message control, performance counter control/masking/select/readback, SQC bank disable masks, clock controls, power throttling, shader time registers, thread trace buffer programming, SQ low-bandwidth counters, SEC/DED error counters, buffer/image resource descriptors, sampler descriptors, flat scratch descriptors, indirect SQ register access, SQ commands, wave register snapshots, debug status, local memory configuration, and SQC policy/volatile controls.

Thread-trace and decode metadata are a large part of the middle of the chunk. `SQ_THREAD_TRACE_*` programming registers describe trace buffer address, size, masks, userdata, mode, token masks, write pointer, status, counter, and high-water state. `SQ_THREAD_TRACE_WORD_*` masks describe emitted trace packet layouts for common, instruction, PC, userdata, timestamp, wave, misc, wave-start, register, event, issue, and perf packets. The `SQ_INTERRUPT_WORD_*` groups define SQ interrupt packet layouts, while `SQ_SOP2`, `SQ_VOP1`, `SQ_MTBUF`, `SQ_EXP`, `SQ_MUBUF`, `SQ_INST`, `SQ_VOP3`, `SQ_SOPP`, `SQ_FLAT`, `SQ_MIMG`, `SQ_SMRD`, `SQ_SOP1`, `SQ_SOPC`, `SQ_DS`, `SQ_SOPK`, `SQ_VOPC`, and `SQ_VINTRP` describe instruction encoding fields.

The SX/export block defines clock controls `CGTT_SX_CLK_CTRL0` through `_4`, extensive `SX_DEBUG_BUSY*` status fields for export path, scoreboard, column-buffer, bank, FIFO, and DBIF busy/valid state, `SX_DEBUG_1`, and four SX performance counters with select/select1 and low/high readback registers.

The final cache/texture section covers TCC/TCA/TCS/TD/TA/TCP controls and counters. `TCC_CTRL`, `TCC_EDC_COUNTER`, `TCC_REDUNDANCY`, and `TCC_CGTT_SCLK_CTRL` describe cache sizing, rate, writeback/invalidate behavior, EDC counts, redundancy, and clock controls. `TCC`, `TCA`, `TCS`, `TD`, `TA`, and `TCP` performance counter families provide select, secondary select, mode, and low/high counter fields. `TD_CNTL`, `TD_STATUS`, debug, scratch, and performance counters define texture data pipe behavior. `TA_CNTL`, `TA_CNTL_AUX`, broadcast base addresses, status, debug, scratch, and performance counters define texture address/control behavior. `SH_HIDDEN_PRIVATE_BASE_VMID`, `SH_STATIC_MEM_CONFIG`, `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, channel steering, address configuration, credits, buffer address hash control, and the first `TCP_EDC_COUNTER` fields define shader memory/TCP cache behavior.

## Important APIs, Types, and Functions

There are no C functions, structs, enums, or inline helpers in this chunk. The exposed API surface is the macro namespace:

- `REGISTER__FIELD_MASK` constants identify the field bits within a 32-bit register value.
- `REGISTER__FIELD__SHIFT` constants identify the right shift for the field.
- Full-width data, address, counter, and scratch fields use `0xffffffff` masks, while high address halves commonly use 8-bit or narrower masks.
- Repeated register families rely on exact spelling and numbering, for example `CGTS_CU15_TD_TCP_CTRL_REG__TCP_SIMDBUSY_OVERRIDE_MASK` or `SPI_SHADER_USER_DATA_PS_15__DATA_MASK`.

The file is consumed together with the matching GFX 7.2 offset header `gfx_7_2_d.h`, which provides corresponding `mm*` and `ix*` register addresses such as `mmCGTS_CU0_LDS_SQ_CTRL_REG`, `mmSPI_SHADER_PGM_LO_PS`, `mmSQ_CONFIG`, `mmTCC_CTRL`, `mmTD_CNTL`, `mmTA_STATUS`, and `mmTCP_CNTL`. Callers normally use AMDGPU helpers such as `REG_SET_FIELD`, direct shifts/masks, `RREG32`, `WREG32`, and indexed SQ reads.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time and caller-driven:

1. AMDGPU, KFD, SDMA, or power-management code includes `gfx_7_2_sh_mask.h` with the matching offset definitions.
2. The caller selects a register field macro for a hardware programming or decode path.
3. Register helper macros or direct bit operations shift and mask the field value.
4. The caller reads or writes the associated MMIO/indexed register, or decodes a register/status/trace value returned by hardware.

In-tree examples include `gfx_v7_0_enable_mgcg()` using CGTS mask fields to configure `mmCGTS_SM_CTRL_REG`, `gfx_v7_0_ring_soft_recovery()` composing `SQ_CMD` with `REG_SET_FIELD`, and `wave_read_ind()`/`wave_read_regs()` using `SQ_IND_INDEX` shifts and masks before reading `SQ_IND_DATA`. This chunk also supports code that writes shader memory registers, SQ configuration, `TA_CNTL_AUX`, and wave/debug register snapshots.

## State and Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe lives in GFX 7.2 hardware registers and persists according to GPU lifecycle rules, not C object lifetime.

CGTS/CGTT fields describe clock-gating, throttling, and light-sleep state that can remain active until driver reconfiguration, power management changes, suspend/resume, GPU reset, or firmware/RLC sequences overwrite it. SPI shader program, trap, resource, and user-data fields describe per-stage programming state used during draw and dispatch setup. SQ/SQC fields describe shader queue control, cache policy, register-credit state, performance counter selection, thread-trace buffers, interrupt packet formats, wave debug state, memory aperture/base behavior, and shader resource descriptors. SX, TCC, TCA, TCS, TD, TA, and TCP fields describe export/cache/texture status, performance counters, cache invalidation/hash/channel behavior, address steering, EDC counts, debug selection, and busy/status signals.

Many described registers are control or status registers with hardware side effects. This header does not encode access mode, reset value, read-only/write-only semantics, sticky status behavior, write-one-to-clear behavior, or required sequencing. Callers must apply the hardware specification and driver synchronization rules around GRBM/SRBM indexing, SQ indirect access, power-gating transitions, cache invalidation, and performance counter programming.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor but must stay synchronized with AMD's generated GFX 7.2 register database and companion files under `include/asic_reg/gca/`, especially `gfx_7_2_d.h` and `gfx_7_2_enum.h`. The numeric masks are only meaningful for the GFX 7.2 register layout; mixing them with another ASIC generation's offsets can silently target wrong fields.

Known source integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`, which includes this header for GFX v7 initialization, clock-gating setup, SQ commands, shader memory configuration, wave debug reads, and status handling.
- `drivers/gpu/drm/amd/amdgpu/cik.c`, `cik_sdma.c`, and power-management files under `pm/legacy-dpm` and `pm/powerplay`, which include the GFX 7.2 masks for CIK-era ASIC setup and power features.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v7.c` and `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_cik.c`, which integrate GFX v7/KFD queue and shader-memory state with HSA/KFD operation.
- Performance tooling and debug paths that program SQ/SX/TCC/TCA/TCS/TD/TA/TCP counters or decode SQ thread traces, wave state, and busy/status registers.

The field names are source contracts. Token-pasting helpers such as `REG_SET_FIELD(value, SQ_CMD, VM_ID, vmid)` depend on exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names, so renaming a macro is a source break even if its numeric value remains the same.

## Risks and Edge Cases

The primary risk is generated bitfield drift. A wrong mask or shift can misprogram clock gating, enable the wrong CU override, corrupt shader resource descriptors, point a shader program/trap base at the wrong address, mis-size SGPR/VGPR/LDS resources, select the wrong performance event, decode thread trace packets incorrectly, miss ECC/EDC signals, or change TCP/texture cache behavior. These failures typically appear as hangs, GPU faults, missed interrupts, bad debug data, performance counter nonsense, or subtle rendering/compute corruption.

The chunk contains many highly repetitive families. Per-CU `CGTS_CU*` registers, shader stage resource/user-data registers, SQ performance counters 0-15, SX/TCC/TCA/TCS/TCP performance counters, and TA/TD counter groups differ mostly by index and stage. Generator errors, copy/paste mistakes, or partial edits are difficult to review manually and should be checked mechanically against the authoritative register database.

Partial chunk boundaries are important. The first line starts after `CGTS_CU0_SP0_CTRL_REG`, so `CGTS_CU0` is not fully covered here. The last listed line contains `TCP_EDC_COUNTER__DED_COUNT_MASK` without its matching `__SHIFT`, which appears after this chunk. A consumer or merger should not infer that `TCP_EDC_COUNTER` is complete from this document alone.

Full-width masks require careful handling in C expressions. The header uses unsigned-looking constants but not uniformly `U` or `UL` suffixes, so callers should keep operations in unsigned 32-bit types where appropriate. Address split fields also require pairing low and high registers correctly; using only the low 32 bits of shader program, trap, broadcast, or resource addresses can produce invalid GPU virtual addresses.

The header cannot tell whether a field is reserved, read-only, write-only, debug-only, or side-effecting. This matters for busy/status fields, invalidate controls, EDC/DED counters, debug index/data registers, SQ indirect access, thread-trace control/status, cache/TCP controls, clock/power-gating override bits, and performance counter select/readback registers.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Build the AMDGPU tree with CIK/GFX v7 and KFD support enabled to catch syntax errors, duplicate definitions, missing macros, and token-pasting mismatches.
- Compare lines 9361-14179 against the authoritative AMD GFX 7.2 register database and the matching `gfx_7_2_d.h` offsets to verify field names, shifts, masks, widths, and register grouping.
- Exercise CIK/GFX v7 hardware initialization, clock-gating enable/disable, suspend/resume, GPU reset, and power transitions to catch CGTS/CGTT/TCC/TCA/TCS/TD/TA/TCP programming mistakes.
- Run graphics and compute workloads that cover PS/VS/GS/ES/HS/LS shader programming, scratch, traps, user SGPRs, LDS sizing, stream-out, texture sampling, buffer/image descriptors, and cache policy.
- Validate KFD/HSA queue operation and shader-memory configuration, especially `SH_MEM_*`, `SQ_CMD`, SQ indirect wave reads, and VMID-sensitive behavior.
- Use debug/perf tests for SQ thread trace, SQ/SX/TCC/TCA/TCS/TD/TA/TCP performance counters, wave register dumps, busy/status decoding, EDC/SEC/DED counters, and cache/TCP invalidation where supported by hardware.

### subset-b-002709: lines 14180-18444

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_7_2_sh_mask.h lines 14180-18444

## Purpose

This chunk is the final large slice of the generated AMD GFX 7.2 shader/register mask header. It contains C preprocessor constants that describe bit masks and bit shifts for 32-bit GPU registers used by the Southern Islands/CIK-era GFX7 AMDGPU stack. The range begins at the tail of `TCP_EDC_COUNTER`, covers texture/cache policy and watchpoint fields, GDS/GWS/OA register fields, VGT/IA/WD graphics pipeline fields, debug and performance-counter fields, and ends with DIDT indirect power-throttling controls for SQ, DB, TD, and TCP.

The file is declarative hardware binding data. It has no executable logic, but the constants are part of the ABI between driver code and GFX 7.2 hardware/firmware. Driver paths include this header with companion register-address headers such as `gfx_7_2_d.h` or `gfx_7_0_d.h`, then use the masks and shifts to compose MMIO writes, decode MMIO reads, or build PM4 packets that program graphics and compute state.

## Major Register Areas Covered

The first section defines cache and texture client fields. `TC_CFG_L1_LOAD_POLICY0/1`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY0/1`, `TC_CFG_L2_STORE_POLICY0/1`, and `TC_CFG_L2_ATOMIC_POLICY` expose per-policy low-bit fields for cache behavior. `TC_CFG_L1_VOLATILE` and `TC_CFG_L2_VOLATILE` provide volatile-control nibbles. `TCP_WATCH0..3_ADDR_H/L` and `TCP_WATCH0..3_CNTL` describe four TCP memory watchpoints, including address bits, mask, VMID, access mode, and valid bit. `TCP_BUFFER_ADDR_HASH_CNTL` and `TCP_EDC_COUNTER` appear at the chunk boundary through channel/bank hash and SEC/DED counter fields.

Clock-gating and local block controls follow. `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCP_CLK_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, and `CGTT_WD_CLK_CTRL` share the generated layout for on-delay, off-hysteresis, and soft override bits. `TCI_STATUS` and `TCI_CNTL_1/2` provide texture client interface status/control fields.

The GDS section is a dense map for global data share, global wave sync, and ordered append state. It includes `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, `GDS_ENHANCE2`, protection fault registers, SECDED counters, OA DED/error reporting, debug controls/data, direct read/write and burst access registers, `GDS_ATOM_*` atomic command/source/destination/readback fields, `GDS_GWS_RESOURCE*`, `GDS_OA_*`, `GDS_VMID0..15_BASE/SIZE`, `GDS_GWS_VMID0..15`, `GDS_OA_VMID0..15`, `GDS_GWS_RESET0/1`, `GDS_GWS_RESOURCE_RESET`, `GDS_COMPUTE_MAX_WAVE_ID`, and OA reset/restore masks. These fields support both allocation state and low-level command/debug plumbing for compute and graphics use of GDS/GWS/OA resources.

The VGT/IA/WD section covers front-end graphics state. Draw and event submission fields include `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, `VGT_EVENT_ADDRESS_REG`, DMA base/index/type/size/control registers, index count/instance/primitive registers, primitive ID controls, vertex reuse and output deallocation, multi-primitive reset, output path, tessellation controls, group vector controls, FIFO depths, and copy-state fields. Geometry, tessellation, stream-out, and multi-VGT fields include `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, `VGT_GS_OUT_PRIM_TYPE`, `VGT_CACHE_INVALIDATION`, `VGT_STRMOUT_*`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_DMA_LS_HS_CONFIG`, `VGT_TF_PARAM`, `VGT_SYS_CONFIG`, `VGT_HS_OFFCHIP_PARAM`, `VGT_GS_INSTANCE_CNT`, `IA_MULTI_VGT_PARAM`, ESGS/GSVS ring sizes and offsets, and GS item sizes. `IA_CNTL_STATUS`, `IA_VMID_OVERRIDE`, `WD_CNTL_STATUS`, `GFX_PIPE_CONTROL`, `GFX_PIPE_PRIORITY`, `CC_GC_SHADER_ARRAY_CONFIG`, `GC_USER_SHADER_ARRAY_CONFIG`, `CC_GC_PRIM_CONFIG`, and `GC_USER_PRIM_CONFIG` connect this front-end state to shader-array and primitive routing controls.

The debug and performance-counter tail is intentionally repetitive. `WD_DEBUG_REG0..5`, `IA_DEBUG_REG0..9`, and `VGT_DEBUG_REG0..35` expose many internal ready/valid, FIFO, request, state-machine, primitive, tessellation, ring, and pipe status bits. `GDS_PERFCOUNTER*`, `VGT_PERFCOUNTER*`, `IA_PERFCOUNTER*`, and `WD_PERFCOUNTER*` define selector, mode, low, and high counter fields for perfmon reads. The final DIDT section defines indirect-register index/data fields and common DIDT controls for `SQ`, `DB`, `TD`, and `TCP`: enable/reset/clock override, reference clock, phase offset, min/max power, max power delta, interval sizing, long-term ratio, and weight tables `WEIGHT0_3`, `WEIGHT4_7`, and `WEIGHT8_11`.

## Important APIs, Types, and Functions

There are no functions, structs, typedefs, or enums in this chunk. The exported interface is the generated macro namespace:

- `REGISTER__FIELD_MASK` gives the bit mask for a field in a 32-bit register.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- Full-width fields use `0xffffffff` masks and shift zero, while repeated indexed registers use the register name to encode the instance, such as `GDS_VMID15_SIZE` or `TCP_WATCH3_CNTL`.

Representative consumers in this tree include `amdgpu/gfx_v7_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v7.c`, `amdkfd/kfd_device_queue_manager_cik.c`, `pm/legacy-dpm/kv_dpm.c`, and powerplay/SMU management code. These files include `gca/gfx_7_2_sh_mask.h` and pair the macros with register-address constants from the GCA headers. Access helpers include direct MMIO helpers such as `RREG32`, `WREG32`, `RREG32_DIDT`, and `WREG32_DIDT`, field-write helpers such as `CGS_WREG32_FIELD_IND`, and command stream packet construction that writes register offsets and values into rings.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time expansion:

1. A GFX7 AMDGPU, KFD, or power-management source file includes the generated register offset and mask headers.
2. The code selects a register by hardware generation, VMID, queue, shader stage, or front-end block.
3. The caller combines masks and shifts with a desired field value, often by shifting manually or through a register-field helper.
4. The result is written to an MMIO register, an indirect DIDT register, or a PM4 packet payload, or a register read is decoded with the same field constants.

Several important hardware flows are implied by these masks. GFX initialization programs GDS VMID base/size and GWS/OA allocation defaults, VGT cache invalidation, GS vertex reuse, and queue/ring state. KFD debug support programs TCP watch address/control fields per VMID and address range. Command submission can emit GDS reset and `GDS_COMPUTE_MAX_WAVE_ID` writes when a compute IB needs GDS wave ID resynchronization. Power-management code reads and writes DIDT indirect registers to enable or disable per-block dynamic throttling based on platform capabilities.

## State and Persistence Behavior

The header stores no state. The state described by the macros lives in hardware registers and persists according to GPU reset, power-gating, clock-gating, queue selection, and driver save/restore sequencing.

GDS fields hold resource allocation and fault/debug state for VMIDs, GWS resource ownership, ordered append counters and addresses, atomic command operands and results, protection faults, ECC counters, and restore/reset data. These values affect command processor and shader-visible behavior until reprogrammed or reset. The `GDS_COMPUTE_MAX_WAVE_ID` flow is notable because the GFX7 driver writes it from a command stream path to resynchronize ME and GDS wave ID counters after certain compute workloads.

VGT, IA, and WD fields describe transient graphics pipeline state, but many are context-state registers saved/restored by clear-state tables, RLC firmware, or command stream setup. Stream-out configuration, tessellation rings, ESGS/GSVS rings, instance counts, primitive type, index limits, and shader stage enables must match the active pipeline state or draw/dispatch behavior can be corrupted.

TCP watchpoint fields are debug state scoped by address, mask, mode, valid bit, and VMID. DIDT fields are power-control state accessed through `DIDT_IND_INDEX` and `DIDT_IND_DATA`; they control throttling/ramping behavior for SQ, DB, TD, and TCP blocks and are toggled by legacy DPM and powerplay paths. Perf counter selector and counter registers are mutable profiling state; debug register fields are mostly readback/status or debug-only control surfaces, but the header itself does not annotate access type or clear semantics.

## Dependencies and Integration Points

The only syntactic dependency is the C preprocessor. Operationally, this chunk must stay synchronized with the generated GFX 7.2 register-offset and enum headers in `include/asic_reg/gca`, especially `gfx_7_2_d.h`, `gfx_7_2_enum.h`, and related GFX7/GMC/OSS/DCE headers included by the same driver files.

Important integration points are:

- `amdgpu/gfx_v7_0.c` includes this header, defines `amdgpu_gds_reg_offset[]` from GDS VMID/GWS/OA register addresses, initializes GDS and VGT state, writes `VGT_CACHE_INVALIDATION`, and emits `GDS_COMPUTE_MAX_WAVE_ID` packets for GDS wave ID reset handling.
- `amdgpu/amdgpu_amdkfd_gfx_v7.c` and `amdkfd/kfd_device_queue_manager_cik.c` include the header for CIK KFD queue management, VMID/queue targeting, and debug-register programming; related newer-generation KFD paths show the same TCP watchpoint field pattern.
- `pm/legacy-dpm/kv_dpm.c` uses `RREG32_DIDT`/`WREG32_DIDT` and `DIDT_SQ_CTRL0__DIDT_CTRL_EN_MASK` or `DIDT_DB_CTRL0__DIDT_CTRL_EN_MASK` to enable or disable dynamic throttling for supported blocks.
- `pm/powerplay/hwmgr/smu7_powertune.c` uses `CGS_WREG32_FIELD_IND` with DIDT block/control field names to program indirect DIDT fields from power-tuning tables.
- Clear-state and context-save code depends on VGT/IA/GDS register layouts being correct even when it writes literal register values rather than using every field macro directly.
- Perf, RAS, fault, and debug consumers depend on the masks to decode GDS protection faults, SECDED counters, VGT/IA/WD/GDS performance counters, and internal debug status.

## Risks and Edge Cases

The highest risk is silent hardware misprogramming. A bad mask or shift can compile cleanly while corrupting cache policy, watchpoint routing, GDS allocation, draw initiation, tessellation and stream-out state, performance counter selection, or DIDT power controls.

The chunk contains many repeated register families with near-identical layouts: policy arrays, four TCP watchpoints, sixteen GDS VMID entries, sixteen GDS GWS/OA VMID entries, GWS reset masks, dozens of VGT/IA/WD debug registers, and replicated DIDT layouts for multiple blocks. Generated or manual drift in one instance can be hard to detect by review because the repetition is expected.

Some fields are full-width data paths, some are side-effectful controls, and some are sticky status or counters. The header does not distinguish read-only, write-one-to-clear, write-only, indirect, or debug-only fields. Callers must know hardware sequencing for GDS atomics, GDS resets, cache invalidation, stream-out counters, TCP watchpoint validity, DIDT reset/enable bits, and clock-gating soft overrides.

The requested range starts mid-register at `TCP_EDC_COUNTER__DED_COUNT__SHIFT` and ends at the file guard. Earlier chunks are required for complete `TCP_EDC_COUNTER` and complete file-level context. Conversely, this chunk includes the final `#endif`, so line-based tools must not treat this as a standalone include file unless they also provide the opening guard and earlier definitions.

Generation/version skew is another practical edge case. `gfx_7_0.c` includes `gfx_7_0_d.h` while using `gfx_7_2_sh_mask.h`; that is an established local pattern for this CIK-era code, but it means address definitions and mask definitions must be validated as a matched hardware generation set rather than renamed independently.

## Test Signals

Useful validation signals are build-time, static-generation, and hardware-execution oriented:

- Kernel builds that enable AMDGPU GFX7, KFD CIK, legacy DPM, and powerplay should compile without missing or renamed GDS, VGT, IA, WD, TCP, TC, CGTT, or DIDT macros.
- A generated-header comparison against AMD's register database should verify every `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` pair in lines 14180-18444, including indexed GDS VMID/GWS/OA families and replicated DIDT blocks.
- Field round-trip checks can validate representative macros such as `TCP_WATCH0_CNTL__VMID/VALID`, `GDS_GWS_VMID0__BASE/SIZE`, `GDS_OA_RESET_MASK`, `VGT_CACHE_INVALIDATION__CACHE_INVALIDATION/AUTO_INVLD_EN`, `VGT_DRAW_INITIATOR`, `IA_MULTI_VGT_PARAM`, and `DIDT_SQ_CTRL0__DIDT_CTRL_EN`.
- GFX7 hardware tests should cover graphics draws, tessellation, geometry shader paths, stream-out, indexed and instanced draws, compute queues using GDS/GWS/OA, and the `AMDGPU_IB_FLAG_RESET_GDS_MAX_WAVE_ID` path.
- KFD debug tests should program and clear TCP watchpoints across all four watch address slots and multiple VMIDs, confirming address high/low, mask, mode, and valid fields route correctly.
- Power-management tests should toggle DIDT through both legacy DPM and powerplay paths and confirm SQ/DB/TD/TCP throttling state changes without breaking suspend/resume, power-gating, or clock-gating transitions.
- Perf/debug validation should verify GDS, VGT, IA, and WD performance counter selection/readback and debug/status decode against expected hardware events.
