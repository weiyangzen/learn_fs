# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 35051-36579

## Chunk Scope

This chunk is a generated AMD GC 11.5.0 register shift/mask header segment. It contains C preprocessor constants only: `REGISTER__FIELD__SHIFT` macros and matching `REGISTER__FIELD_MASK` macros for MMIO or indexed GPU registers. There are no functions, structs, enums, variables, callbacks, allocations, locks, or executable branches.

The requested range contains 1,529 source lines and 1,275 `#define` entries: 637 shift constants and 638 mask constants. The one-extra mask is a chunk-boundary artifact: the first line is the tail mask for `FIXED_PATTERN_PERF_COUNTER_7`, whose shift definition is in the preceding chunk. This range then covers the end of fixed-pattern performance/LUT update status definitions, the complete `secacind` block in this chunk, the full visible `grtavfsind` block from `RTAVFS_REG0` through `RTAVFS_REG194`, and the `sqind` wave/debug register layouts through `SQ_WAVE_EXEC_HI`. The file ends at this chunk's final line with `#endif`.

Although the source tree path is under `ceph-client`, this is AMDGPU DRM graphics-core metadata, not distributed filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies symbolic bitfield definitions for GC 11.5.0 hardware programming. The companion `gc_11_5_0_offset.h` header provides register offsets, while this header provides the bit positions and masks consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15_PREREG`.

This particular slice names fields for:

- Fixed-pattern counters and hardware LUT update completion/error state, used by power/performance management blocks to expose pattern counter values and table-update status.
- `secacind` CAC selection and threshold registers, selecting CAC block/signal IDs and threshold values.
- `grtavfsind` RTAVFS registers, which describe real-time adaptive voltage/frequency scaling zones, CPO/ripple-counter windows, frequency/voltage-code pairs, guard bands, proportional/integral controller knobs, PSM measurement controls, CPO enable masks, live ripple counts, debug stop points, FSM status, and override/readback fields.
- `sqind` shader-queue debug and wave registers, including SQ busy status, active/valid wave masks, wave mode/status/trap state, resource allocation, outstanding instruction-buffer counters, program counter, hardware IDs, scheduler mode, scratch registers, TTMP registers, M0, and EXEC masks.

The generated macro names are part of the driver ABI for this ASIC generation. Callers depend on the exact spelling pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` when composing or decoding register values.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The exported interface is the macro namespace.

Important macro families in this range:

- `FIXED_PATTERN_PERF_COUNTER_8`, `FIXED_PATTERN_PERF_COUNTER_9`, and `FIXED_PATTERN_PERF_COUNTER_10` define 17-bit `PERF_COUNTER` fields. The first line also completes `FIXED_PATTERN_PERF_COUNTER_7` from the previous chunk.
- `HW_LUT_UPDATE_STATUS` exposes per-table completion and error state for update tables 1 through 5. Each table has `*_DONE`, `*_ERROR`, and multi-bit `*_ERROR_STEP` fields.
- `SE_CAC_ID` and `SE_CAC_CNTL` define the CAC indexed-register selector and threshold layout: `CAC_BLOCK_ID`, `CAC_SIGNAL_ID`, and `CAC_THRESHOLD`.
- `RTAVFS_REG0` through `RTAVFS_REG4` define five zone start/stop count pairs.
- `RTAVFS_REG5` through `RTAVFS_REG14` define two full-width enable masks per RTAVFS zone.
- `RTAVFS_REG15` through `RTAVFS_REG18` define four frequency-count/voltage-code pairs. `RTAVFS_REG19` defines per-zone guard-band fields.
- `RTAVFS_REG20` through `RTAVFS_REG24` and `RTAVFS_REG120` define per-zone and global CPO averaging divisors, including eight intermediate divisor fields and a final divisor field.
- `RTAVFS_REG25` through `RTAVFS_REG27`, plus several `RESERVED` fields across the block, are generated full or partial reserved layouts. They still matter for preserving register width and avoiding accidental writes to undocumented bits.
- `RTAVFS_REG28` through `RTAVFS_REG30` define zone intercept values.
- `RTAVFS_REG31` through `RTAVFS_REG42` define CPO clock dividers and RTAVFS FSM timing counters for startup, idle, reset, CPO start/stop, ripple-counter start/done, final-result ready, voltage-code ready, target-voltage ready, and wait-for-ack phases.
- `RTAVFS_REG43` through `RTAVFS_REG48` define proportional/integral control coefficients, voltage anchors, binary-search and hardware-calibration controls, VR enable/bleed controls, voltage-code overrides, low-power and sensing bits, PI anti-windup/shift/error controls, PI output limits, loop iterations, and error thresholds.
- `RTAVFS_REG49` through `RTAVFS_REG53` define PSM controls and measured min/max/average values for VDD and VREG paths.
- `RTAVFS_REG54` through `RTAVFS_REG117` define CPO0 through CPO63 start/stop counter windows.
- `RTAVFS_REG118` and `RTAVFS_REG119` provide full-width CPO enable masks for the 64 CPO counters.
- `RTAVFS_REG121` exposes live zone-in-use bits and an `RTAVFSERRORCODE`.
- `RTAVFS_REG122` through `RTAVFS_REG185` define CPO0 through CPO63 ripple-count readback fields.
- `RTAVFS_REG186` and `RTAVFS_REG187` define target/current frequency-count overrides and selector bits.
- `RTAVFS_REG189` through `RTAVFS_REG194` define PI/binary-search voltage-code readback, VDD regulator state, loop/debug controls, FSM stop-at-state controls, scaled/final CPO count readbacks, FSM state, and selected ripple-count readback.
- `SQ_DEBUG_STS_LOCAL` and `SQ_DEBUG_CTRL_LOCAL` define SQ local debug busy bits and a small control field.
- `SQ_WAVE_ACTIVE` and `SQ_WAVE_VALID_AND_IDLE` define wave-slot bitmaps.
- `SQ_WAVE_MODE` defines floating-point rounding/denormal controls, DX10 clamp, IEEE mode, LOD clamp, trap-after-instruction enable, exception enables, wave-end, FP16 overflow, and performance-disable fields.
- `SQ_WAVE_STATUS` defines wave condition/status bits including SCC, SPI/user priority, privilege, trap/thread-trace enables, export readiness, EXEC/VCC zero flags, barrier/threadgroup state, halt/trap, valid/ECC/perf bits, fatal halt, no-VGPR state, LDS parameter readiness, GS allocation/export requirements, idle, and scratch enable.
- `SQ_WAVE_TRAPSTS` defines exception, save-context, illegal instruction, high exception bits, buffer OOB, host trap, wave-start/end, performance snapshot, trap-after-instruction, and UTC error bits.
- `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_HW_ID1/2`, `SQ_WAVE_POPS_PACKER`, `SQ_WAVE_SCHED_MODE`, `SQ_WAVE_SHADER_CYCLES`, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI` describe per-wave resource allocation, outstanding counter, identity, scratch, scheduler, timing, temporary, M0, and EXEC-mask state.

## Control Flow

This header has no software control flow. Runtime sequencing is provided by AMDGPU, KFD, firmware, or hardware microcode consumers that include the generated register headers.

The typical use pattern is:

1. A GC 11.5.0 consumer includes `gc/gc_11_5_0_offset.h` and `gc/gc_11_5_0_sh_mask.h`.
2. The consumer chooses a `reg*` or `ix*` register offset from the matching offset header.
3. It composes a `u32` with `REG_SET_FIELD`, extracts values with `REG_GET_FIELD`, or tests masks directly.
4. MMIO, SOC15, indexed-register, RLC, or wave-debug accessors perform the actual hardware reads/writes while the caller owns ordering, power-domain checks, SR-IOV ownership, and polling.

The direct GC 11.5.0 consumer visible in this tree is `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which includes this header and its offset companion. That file mostly uses GCVM/GCMC fields defined in earlier chunks of the same header, but it demonstrates the integration model for this ASIC: `REG_SET_FIELD` builds register values, `RREG32_SOC15`/`WREG32_SOC15` access GC registers, and VM hub initialization derives register distances from generated offsets. The `sqind` wave fields in this chunk line up with the broader AMDGPU wave-debug pattern: other GFX generations read registers such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_MODE` through `wave_read_ind()` helpers for hang/debug dumps. KFD CWSR trap handlers carry parallel hand-written constants for `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, and `SQ_WAVE_MODE` because trap save/restore code manipulates hardware wave registers directly in assembly.

The RTAVFS and CAC blocks are register metadata only here. The header does not encode when RTAVFS should be enabled, how to tune PI coefficients, how to sequence CPO/ripple-counter sampling, how to handle LUT update errors, or whether individual fields are read-only, write-one-clear, sticky, self-clearing, or firmware-owned.

## State And Persistence Behavior

The header stores no software state and persists nothing. It names fields in hardware state whose lifetime is defined by the GPU block, firmware, reset, power management, and driver programming sequence.

Represented hardware state includes:

- Pattern counter and LUT update status state. Counter fields can reflect live or latched hardware counts, while `HW_LUT_UPDATE_STATUS` fields expose completion/error/step state for table updates.
- CAC indexed state under `secacind`, including selected block/signal IDs and threshold programming.
- RTAVFS configuration state: zone windows, zone/CPO enable masks, guard bands, intercepts, PI coefficients, voltage-code anchors, VR control, low-power sensing, PSM measurement controls, AVFS enablement, per-path scaling, anchor update control, and override selectors.
- RTAVFS live/diagnostic state: CPO and ripple counts, zone-in-use bits, error code, selected ripple readback, FSM state, voltage-code readbacks, VDD regulator state, scaled CPO counts, and debug stop-at-state bits.
- SQ debug and wave state: local SQ busy flags, active/valid wave slots, wave mode/status/trap status, GPR/LDS allocation, outstanding memory/export counters, PC, hardware identity, scheduler mode, shader cycles, temporary trap registers, M0, and EXEC masks.

Persistence is hardware-defined. Some fields are configuration values that last until rewritten, reset, suspend/resume reprogramming, power-gating loss, RLC/firmware restore, or ASIC reset. Other fields are live counters/status bits that change while the GPU runs. Several controls have likely side effects when written, especially debug stop controls, save/restore CPO weights, loop-run bits, reset-retention bits, wave flush controls, and trap/status fields. The masks do not describe those side effects by themselves.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` must stay synchronized with this shift/mask header. Offsets from one ASIC generation should not be paired with masks from another.
- AMDGPU register helper infrastructure supplies `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15_PREREG`, and related accessors.
- Indexed-register access is relevant for the `secacind`, `grtavfsind`, and `sqind` address blocks. Consumers need the correct index/data access path and instance selection, not just the bit masks.

Observed and expected integration points:

- `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` includes this header for GC 11.5.0 VM-hub programming and demonstrates the direct generated-header use model.
- Generic GC 11 code such as `gfx_v11_0.c`, IMU, MES, and firmware-loading paths select GC 11.5.0 firmware and register metadata for this ASIC family.
- Wave-dump and hang-diagnosis paths in AMDGPU use `SQ_WAVE_*` indexed registers across generations to capture PC, EXEC, allocation, status, and scheduler state. The GC 11.5.0 field names in this chunk are the decode contract for the same class of data on this ASIC.
- KFD CWSR and trap-handling logic depends on wave-mode/status/trap bit layouts. In assembly, those constants may be duplicated rather than included from this C header, so drift between generated headers and trap-handler constants is a meaningful integration risk.
- Power-management, firmware, or RLC/SMU-owned flows are the likely consumers for RTAVFS and fixed-pattern/LUT update registers. Even when not directly referenced in open C code, these definitions document the hardware contract for diagnostics, golden settings, debugfs tooling, or firmware-assisted programming.

## Risks And Edge Cases

- Header/offset mismatch is the largest correctness risk. These constants compile as untyped integer macros, so using GC 11.5.0 masks with another generation's offsets can silently write or decode the wrong bits.
- The chunk starts inside a register group. `FIXED_PATTERN_PERF_COUNTER_7` is incomplete here, so adjacent chunks are required for a full per-register audit.
- Full-width `RESERVED`, `UNUSED`, or `DATA` masks do not imply whole-register writes are safe. Callers still need hardware documentation or established driver sequences before changing reserved bits.
- RTAVFS fields include control, calibration, debug, counter, override, and live-status semantics in one address block. Treating all `RTAVFS_REG*` entries as ordinary configuration can accidentally start loops, force overrides, reset retention state, stop the FSM at debug points, or perturb adaptive-voltage behavior.
- Status fields such as `HW_LUT_UPDATE_STATUS`, `RTAVFS_REG121__RTAVFSERRORCODE`, `RTAVFS_REG193__RTAVFSFSMSTATE`, `SQ_DEBUG_STS_LOCAL`, `SQ_WAVE_STATUS`, and `SQ_WAVE_TRAPSTS` may be live, sticky, or clear-on-write depending on hardware semantics not captured by the mask names.
- Wave registers are highly context-sensitive. Correct reads require selecting the intended wave/SIMD/WGP/instance and ensuring the wave is halted or otherwise safely observable; otherwise PC, EXEC, counters, and trap state can race with execution.
- Trap/CWSR constants are duplicated in assembly for some generations. Any GC 11.5.0 update to `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, or `SQ_WAVE_MODE` must be checked against trap save/restore code that cannot directly consume these macros.
- Several masks span high bits or partial high words (`SQ_WAVE_HW_ID1__DP_RATE_MASK`, `SQ_WAVE_IB_STS__VS_CNT_MASK`, `RTAVFS_REG19__RTAVFSGB_ZONE4_MASK`, etc.). Callers must use unsigned 32-bit math and proper helper macros to avoid sign-extension or stale-bit bugs.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-access, and hardware-observation checks:

- Build coverage for GC 11.5.0 AMDGPU paths should catch missing or misspelled macro names when consumers use `REG_SET_FIELD`/`REG_GET_FIELD`.
- A generated-header consistency check should verify that every complete register field in the range has both `__SHIFT` and `_MASK` definitions, allowing for known chunk-boundary exceptions such as `FIXED_PATTERN_PERF_COUNTER_7`.
- ASIC bring-up or VM-hub smoke tests on GC 11.5.0 hardware should confirm that including this header alongside `gc_11_5_0_offset.h` still allows GART enable/disable, VM fault handling, and reset/resume flows to complete.
- Wave dump or GPU hang diagnostics should produce plausible `SQ_WAVE_*` values: valid PC high/low pairs, EXEC masks, wave IDs, SIMD/WGP/SA/SE IDs, allocation sizes, and outstanding counter fields.
- Trap/CWSR tests should verify that saved/restored wave status, trap status, mode, TTMP, M0, and EXEC state match the hardware layout for the active ASIC.
- Power-management or firmware diagnostics for RTAVFS should check that zone enable masks, CPO start/stop windows, ripple counts, FSM state, error code, voltage-code readbacks, and override selectors decode to expected values after firmware or RLC programming.
- Negative testing should avoid blind writes to `RESERVED`/`UNUSED` fields and should verify that read-modify-write paths preserve undocumented bits unless an approved golden-register table intentionally writes a full register value.
