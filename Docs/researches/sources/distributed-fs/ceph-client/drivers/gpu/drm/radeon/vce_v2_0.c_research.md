# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v2_0.c

## Purpose

`vce_v2_0.c` implements VCE 2.0 resume-time memory-controller/cache setup and generation-specific medium-grain clock-gating behavior. Compared with VCE 1.0, it uses a 40-bit cache BAR register and separates dynamic versus software clock gating paths.

## Important APIs, Types, and Functions

- `vce_v2_0_set_sw_cg()` programs software clock-gating bits in `VCE_CLOCK_GATING_B`, `VCE_UENC_CLOCK_GATING`, `VCE_UENC_REG_CLOCK_GATING`, and `VCE_CGTT_CLK_OVERRIDE`.
- `vce_v2_0_set_dyn_cg()` programs dynamic clock-gating bits and clears stale UENC gating masks.
- `vce_v2_0_disable_cg()` forces the clock override.
- `vce_v2_0_enable_mgcg()` chooses dynamic clock gating by default and gates only when requested and supported by `rdev->cg_flags`.
- `vce_v2_0_init_cg()` programs gating delay timers and wait-awake behavior.
- `vce_v2_0_bo_size()` returns firmware plus stack plus per-handle data size.
- `vce_v2_0_resume()` initializes LMI/cache registers, writes `VCE_LMI_VCPU_CACHE_40BIT_BAR`, programs three cache regions, enables trap interrupts, and initializes clock gating.

## Control Flow

Resume first disables/normalizes clock-gating state, configures LMI/cache/swap/VM registers, writes the upper address BAR from the VCE BO, programs firmware/stack/data cache windows, enables trap interrupt delivery, and initializes generation-specific clock-gating timers. MGC clock gating can later be toggled by DPM or ASIC code through `vce_v2_0_enable_mgcg()`.

## State and Persistence Behavior

Persistent hardware state includes VCE cache BAR and offsets/sizes, interrupt enable, LMI state, clock-gating registers, and clock override state. The file stores no private C state.

## Dependencies and Integration Points

- Depends on Radeon VCE firmware state, `RADEON_MAX_VCE_HANDLES`, `rdev->cg_flags`, register access macros, and `cikd.h`.
- Used by Radeon ASIC generation tables and by callers that toggle VCE MGC clock gating through `vce.h`.

## Risks and Edge Cases

- `vce_v2_0_bo_size()` warns if firmware exceeds 256 KiB but does not fail; callers must enforce allocation/upload safety elsewhere.
- The local `sw_cg` debug variable is hardcoded false, so software clock-gating paths are present but not normally exercised.
- Cache offset programming masks addresses with `0x7fffffff` after reducing `addr` to low bits; mistakes in BAR/offset split would break high-address BO placement.

## Test Signals

- Resume tests should validate cache BAR/offset programming for BOs above 4 GiB.
- Clock-gating tests should exercise enable/disable paths with and without `RADEON_CG_SUPPORT_VCE_MGCG`.
- Interrupt tests should confirm trap interrupt enable is set after resume.
