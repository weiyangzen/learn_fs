# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c

## Purpose

`mmhub_v9_4.c` implements the Arcturus-era MMHUB 9.4 backend used by GMC v9. It handles two MMHUB instances separated by a fixed register offset, programs GART/VM translation state, configures SDMA snoop overrides, manages clock gating, and exposes MMHUB RAS error-count/status operations.

## Important APIs, Types, And Functions

The exported MMHUB table is `mmhub_v9_4_funcs`; the exported RAS descriptor is `mmhub_v9_4_ras`, backed by `mmhub_v9_4_ras_hw_ops`. Core functions include `mmhub_v9_4_init`, `mmhub_v9_4_gart_enable`, `mmhub_v9_4_gart_disable`, `mmhub_v9_4_set_fault_enable_default`, `mmhub_v9_4_setup_vm_pt_regs`, `mmhub_v9_4_get_fb_location`, `mmhub_v9_4_update_medium_grain_clock_gating`, and `mmhub_v9_4_update_medium_grain_light_sleep`. RAS helpers include `mmhub_v9_4_query_ras_error_count`, `mmhub_v9_4_reset_ras_error_count`, and `mmhub_v9_4_query_ras_error_status`.

## Control Flow

`init` fills two VM hub structures, `AMDGPU_MMHUB0(0)` and `AMDGPU_MMHUB1(0)`, by adding `MMHUB_INSTANCE_REGISTER_OFFSET` to base SOC15 offsets. `gart_enable` loops over both instances and programs VMID0, AGP/system aperture, TLB, L2 cache on PF paths, SDMA snoop overrides, system domain, identity aperture on PF paths, VMID contexts, and invalidation engines. `setup_vm_pt_regs` writes a page-table base into both hubs. RAS count query scans a table of EDC counter registers, decodes matching field descriptors, logs nonzero SEC/DED subblock counts, and updates `ras_err_data`.

## State And Persistence Behavior

The backend writes persistent MMHUB register state for two instances. `get_fb_location` reads base/top from shared VC0 registers and also updates `adev->gmc.fb_start` and `adev->gmc.fb_end`. VMID setup adjusts page-table depth/block size when `adev->gmc.translate_further` is active and uses `adev->gmc.noretry` for retry behavior. RAS counters are read-to-clear during reset; error status registers are sampled to warn about fatal SDP read/write/parity states before reset.

## Dependencies And Integration Points

The file depends on `amdgpu_ras.h`, generated `mmhub_9_4_1` and `athub_1_0` headers, Vega10 enums, SOC15 helpers, and the GMC v9 selection code. `gmc_v9_0.c` assigns `mmhub_v9_4_funcs` and `mmhub_v9_4_ras`. It integrates with generic RAS infrastructure through `amdgpu_ras_block_hw_ops` and with clock/power management only for `CHIP_ARCTURUS`.

## Risks

The two-instance arithmetic is hard-coded; an offset error corrupts the wrong hub. `mmhub_v9_4_get_clockgating` appears to read `mmATCL2_0_ATC_L2_MISC_CG` twice instead of reading a DAGB register for `data1`, so MGCG reporting may be unreliable. The RAS field table is very large and repetitive across MMEA0-MMEA7; copy/paste field mistakes would miscount SEC/DED errors. The comment spelling `Acrturus/arcturas` is cosmetic, but the behavior is ASIC-specific and must not be generalized casually.

## Test Signals

Test signals include Arcturus boot, GART enable on both MMHUB instances, VM page-table updates reaching both hubs, SDMA cache-coherency workloads validating snoop overrides, fault-default toggling, clock-gating flag checks, and RAS injection or register mocking that confirms SEC/DED accumulation, read-to-clear reset, and fatal status warnings.
