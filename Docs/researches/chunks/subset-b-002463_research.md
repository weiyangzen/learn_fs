# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 35036-37342

## Purpose

This chunk is generated AMD GC 10.1.0 register field metadata. It contains no executable driver logic; it publishes preprocessor constants for field shifts and bit masks used when reading or writing Graphics Core MMIO registers through AMDGPU's SOC15 register helpers.

The requested range spans two hardware decode areas:

- The tail of the `RLC_RLCS` register block, beginning in the final fields of `RLC_RLCS_GE_FAST_CLOCK` and then covering RLC bootload, idle/busy, interrupt-clear, power-brake, scratch/general, auxiliary-address, SPM/SQTT, CP DMA source override, UTCL2 override, MP1 doorbell, bootload-ID status, and EDC interrupt control fields.
- The beginning and a large repeated portion of `addressBlock: gc_pwrdec`, covering `CGTS` and `CGTT` clock-gating/throttling/status fields for shader arrays, quads, TCC disable state, read muxing, SPI clock override groups, and per-WGP/per-CU SIMD/SQ/SQC/LDS/TA/TD/TCP control registers through `SA1_WGP11_CU1_TCP_CTRL_REG`.

The chunk has 2,186 `#define` lines: 1,095 `__SHIFT` constants and 1,091 `_MASK` constants. The line boundaries are artificial: the first visible lines are the end of `RLC_RLCS_GE_FAST_CLOCK`, and the final visible lines stop inside `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG`. Neighboring chunks are required for complete per-file coverage.

Although this source tree is under a local `ceph-client` mirror, this header is AMDGPU kernel-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: field mask for extracting, clearing, or setting that field.

These constants are paired with address macros from `gc_10_1_0_offset.h`, such as `mmRLC_RLCS_BOOTLOAD_STATUS`, `mmCGTS_SA0_QUAD0_SM_CTRL_REG`, and `mmCGTS_TCC_DISABLE`. Runtime code then uses helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

Major field groups in this chunk:

- `RLC_RLCS_BOOTLOAD_STATUS`: reports whether RLC/RLCG IRAM has loaded and whether bootload/autoload is complete. `BOOTLOAD_COMPLETE` is the field actively polled by GFX v10 initialization.
- `RLC_RLCS_POWER_BRAKE_CNTL` and `_TH1`: expose power-brake state, interrupt clear, and hysteresis counters.
- `RLC_RLCS_GRBM_IDLE_BUSY_STAT` and `_INT_CNTL`: expose GRBM/RLC idle status, SDMA busy bits, changed bits, and interrupt-clear bits.
- `RLC_RLCS_CMP_IDLE_CNTL`: exposes compare-idle state, interrupt clear, and hysteresis controls.
- `RLC_RLCS_GENERAL_0` through `_5`: full-width 32-bit scratch/data registers.
- `RLC_RLCS_AUXILIARY_REG_1` through `_4`: 18-bit auxiliary register address fields.
- `RLC_RLCS_SPM_SQTT_MODE`, `RLC_RLCS_CP_DMA_SRCID_OVER`, `RLC_RLCS_UTCL2_CNTL`, and `RLC_RLCS_MP1_RLC_DOORBELL_CTRL`: control or override profiling/trace mode, CP DMA source ID, UTCL2 behavior, GPA/VF values, and MP1/RLC doorbell interrupt state.
- `RLC_RLCS_BOOTLOAD_ID_STATUS1` and `_STATUS2`: 64 one-bit firmware/component loaded indicators, split across two 32-bit registers.
- `CGTS_SA*_QUAD*_SM_CTRL_REG`: shader-array quad-level clock-gating mode, override, monitor, delay, and enable fields.
- `CGTS_*_CLK_MONITOR_DELAY_REG`: off/on monitor delay fields for each shader-array quad.
- `CGTS_RD_CTRL_REG` and `CGTS_RD_REG`: mux selection and 32-bit readback data for CGTS diagnostic/status reads.
- `CGTS_TCC_DISABLE` and `CGTS_USER_TCC_DISABLE`: high and low TCC-disable bitmaps consumed by GFX code to derive the disabled TCC mask.
- `CGTS_STATUS_REG`: per-quad MGCG enabled and clock-gating status fields.
- `CGTT_SPI_CGTSSM_CLK_CTRL`: SPI CGTS state-machine group override fields.
- Repeated `CGTS_SA{0,1}_WGP{00,01,02,10,11}_CU{0,1}_{SIMD0,SIMD1,TATD,TCP}_CTRL_REG` families: per-compute-unit clock/light-sleep control fields for SIMD, SQ, SQC, LDS, TA, TD, TCPF, and TCPI subblocks.

## Control Flow

This header has no local control flow. It participates in driver control flow only through macro expansion in the AMDGPU GFX, SDMA, KFD, GFXHUB, SR-IOV, and platform glue code that includes `gc/gc_10_1_0_sh_mask.h`.

The clearest runtime sequences tied to this chunk are:

1. GFX v10 RLC autoload completion waits read `mmCP_STAT` and `mmRLC_RLCS_BOOTLOAD_STATUS`.
2. The driver extracts `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE` with `REG_GET_FIELD`.
3. If CP is idle and bootload is complete before `adev->usec_timeout`, GFX initialization continues; otherwise initialization fails with an RLC autoload timeout.

Clock-gating programming follows a separate path:

1. GFX v10 clock-gating update enters RLC safe mode.
2. For medium-grain clock-gating workarounds, the driver iterates arrays of `mmCGTS_*_TCP_CTRL_REG` offsets.
3. It reads each register, sets the shared `CGTS_SA0_WGP00_CU0_TCP_CTRL_REG__TCPI_LS_OVERRIDE_MASK` bit pattern, and writes the value back. The field layout is reused across the repeated TCP control registers, so one canonical mask is used for many homologous registers.
4. It iterates the quad SM control registers, clears `CGTS_SA0_QUAD0_SM_CTRL_REG__SM_MODE_MASK`, writes mode `2` at `SM_MODE__SHIFT`, and restores normal execution outside the workaround path.

TCC discovery is another direct integration point. GFX v10 reads `mmCGTS_TCC_DISABLE` and `mmCGTS_USER_TCC_DISABLE`, then derives `adev->gfx.config.tcc_disabled_mask` from `CGTS_TCC_DISABLE.TCC_DISABLE` and `HI_TCC_DISABLE`.

The RLC idle/busy, power-brake, UTCL2, bootload-ID, EDC, CGTS status, read-mux, and SPI override fields are hardware control/status surfaces. This chunk does not encode the ordering rules for using them; sequencing is imposed by the relevant GFX/RLC/power-management code and by ASIC programming requirements.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state.

The RLC fields represent firmware boot/autoload state, RLC scratch data, interrupt-clear bits, busy/idle state, doorbell state, EDC interrupt state, auxiliary register addressing, and memory/virtualization override controls. Some fields are status/readback fields, some are control fields, and some names imply side-effect semantics such as interrupt clear. The header does not distinguish read-only, write-one-to-clear, sticky, self-clearing, or reserved behavior beyond naming and masks.

The CGTS/CGTT fields represent graphics power-management and clock-gating state. Quad-level SM control registers can enable/disable or override medium-grain clock gating and monitor timing. Per-WGP/per-CU registers carry subblock light-sleep and busy-override state for SIMD, SQ, SQC, LDS, TA/TD, and TCP units. TCC-disable registers describe hardware-disabled or user-disabled cache slices; the driver persists the interpreted disabled bitmap in `adev->gfx.config.tcc_disabled_mask`.

Persistence is hardware-defined. Register values generally survive until a GPU reset, suspend/resume power transition, clock-gating reprogramming, firmware reload, or ASIC-specific power-management event changes them. Driver-maintained derived state, such as the disabled TCC mask, persists in `struct amdgpu_device` only for the lifetime of the initialized device instance.

## Dependencies And Integration Points

This header must stay in sync with AMD's generated GC 10.1.0 register database, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the matching `mm...` register offsets and `_BASE_IDX` values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h`, where generated reset/default values are available for related registers.
- SOC15 register access helpers and field helpers used by AMDGPU code, including `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`

Observed direct consumers of fields from this chunk include:

- `gfx_v10_0_wait_for_rlc_autoload_complete()`, which polls `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`.
- `gfx_v10_0_get_tcc_info()`, which reads `CGTS_TCC_DISABLE` and `CGTS_USER_TCC_DISABLE` fields to form the disabled TCC mask.
- `gfx_v10_0_apply_medium_grain_clock_gating_workaround()`, which uses CGTS TCP light-sleep override masks and quad SM mode masks/shifts.
- GFX debug/register dump tables, which include `mmRLC_RLCS_BOOTLOAD_STATUS` in the GC register list for diagnostic capture.

## Risks And Edge Cases

- The macros are untyped numeric constants. A wrong shift or mask compiles cleanly but can read the wrong bit, clear a reserved bit, miss a firmware-completion condition, or program an unintended clock-gating override.
- The range contains many structurally repeated register families. A copy or generation error in one `SA`, `WGP`, `CU`, or subblock instance may only fail on a subset of shader arrays, compute units, or ASIC variants.
- Some GFX code intentionally reuses a representative mask, such as `CGTS_SA0_WGP00_CU0_TCP_CTRL_REG__TCPI_LS_OVERRIDE_MASK`, across homologous TCP control registers. That assumes identical field layout across the repeated family; if a future generated header diverges, this pattern becomes risky.
- RLC bootload completion is on an initialization critical path. If `BOOTLOAD_COMPLETE` is wrong, GFX initialization can time out even when firmware loaded, or proceed before firmware is ready.
- Interrupt-clear and status fields are side-effect-sensitive. Misusing fields named `INT_CLEAR`, busy-changed, EDC interrupt, or doorbell clear can lose events or leave interrupt sources latched.
- Reserved masks are present throughout the RLC and CGTS fields. Driver code must avoid blindly writing reserved bits unless hardware programming guides explicitly require the full value.
- Clock-gating and light-sleep overrides affect power and stability. Incorrect CGTS programming can cause higher power draw, hangs during idle transitions, shader/TCP/SQ/LDS unit wake failures, or bugs that reproduce only under low-load or suspend/resume paths.
- The chunk's first and last register families are partial. File-level analysis must merge this document with adjacent chunks before making claims about complete `RLC_RLCS_GE_FAST_CLOCK` or `CGTS_SA1_WGP11_CU1_TCP_CTRL_REG` coverage.

## Test Signals

Useful validation signals are integration and hardware-oriented rather than unit-test oriented:

- Kernel build coverage for AMDGPU with `gfx_v10_0.c`, KFD, SDMA, GFXHUB, and SR-IOV include paths enabled catches missing or renamed macros.
- GFX v10 probe/init logs should not show `rlc autoload: gc ucode autoload timeout`; that path exercises `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`.
- Register dumps should include sane `mmRLC_RLCS_BOOTLOAD_STATUS` values alongside RLC/CP status registers after initialization.
- TCC topology reporting should produce a stable `adev->gfx.config.tcc_disabled_mask` across boots for the same ASIC and fuse state.
- Clock-gating validation should exercise idle, load, suspend/resume, and runtime power-management transitions with `AMD_CG_SUPPORT_GFX_CGTS_LS` and related GFX CG flags enabled.
- GPU stress workloads should run cleanly after `gfx_v10_0_apply_medium_grain_clock_gating_workaround()` modifies CGTS TCP and SM control registers; failures may appear as hangs, VM faults, ring timeouts, or unstable power-state transitions.
- Low-level register tracing around CGTS writes can verify that only intended override and mode fields are changed and reserved bits are preserved.
