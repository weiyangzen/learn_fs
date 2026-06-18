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
