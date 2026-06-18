# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h lines 7298-7567

## Scope

This chunk is the final section of the generated AMDGPU MMHUB 2.0.0 shift/mask header. It contains C preprocessor constants for register bit positions and masks, not executable code. The constants are paired with register offsets from `mmhub_2_0_0_offset.h`, reset/default values from `mmhub_2_0_0_default.h`, and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

The range starts in the per-virtual-function PCIe ATS control register family at `MMVM_PCIE_ATS_CNTL_VF_1`, then covers shared MMUTCL2/MMVM PF and VC decode registers, L1 TLB control, ATC L2 performance counter result registers, ATC L2 performance counter configuration registers, and the closing `#endif` for the header.

## Purpose

The macros define the software contract for programming and decoding MMHUB 2.0.0 memory-management registers. MMHUB is the memory hub used by non-graphics clients in AMDGPU. These fields support:

- PCIe ATS/ATC enablement per SR-IOV virtual function.
- MMUTCL2 clock-gating timing and software override controls.
- PF-visible physical/system memory aperture registers, default fault page address routing, virtual reset request state, and light-sleep timing.
- VC-visible framebuffer, AGP, system aperture, and L1 TLB controls used while enabling or disabling GART/VM translation.
- ATC L2 performance counter reads, event selection, trigger setup, clear operations, and saturation behavior.

Because this is a generated register header, its main purpose is ABI-like accuracy: callers rely on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names and values when composing 32-bit MMIO writes for this ASIC generation.

## Important Macro Families

PCIe ATS and SR-IOV virtual functions:

- `MMVM_PCIE_ATS_CNTL_VF_1` through `MMVM_PCIE_ATS_CNTL_VF_31` each expose only `ATC_ENABLE` at bit 31 (`0x80000000L`).
- The immediately preceding context in the same header includes the root `MMVM_PCIE_ATS_CNTL` fields (`STU` and `ATC_ENABLE`) and `MMVM_PCIE_ATS_CNTL_VF_0`; this chunk continues that repeated VF series.
- The matching offsets in `mmhub_2_0_0_offset.h` place the registers contiguously from `mmMMVM_PCIE_ATS_CNTL_VF_1` at `0x0809` through `mmMMVM_PCIE_ATS_CNTL_VF_31` at `0x0827`, with base index 0.

Clock gating and active function state:

- `MMUTCL2_CGTT_CLK_CTRL` defines `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE_EXTRA`, `MGLS_OVERRIDE`, `SOFT_STALL_OVERRIDE`, and `SOFT_OVERRIDE`. The 2.0.0 default is `0x00000080`, so reset state has part of the `OFF_HYSTERESIS` field set.
- `MMMC_SHARED_ACTIVE_FCN_ID` has a 5-bit `VFID` field and a high-bit `VF` flag, allowing software or firmware to identify whether the active function is a PF or a VF.

PF shared MMVM decode registers:

- `MMMC_VM_NB_MMIOBASE` and `MMMC_VM_NB_MMIOLIMIT` are full 32-bit fields for northbridge MMIO aperture bounds.
- `MMMC_VM_NB_PCI_CTRL` exposes `MMIOENABLE` at bit 23; `MMMC_VM_NB_PCI_ARB` exposes `VGA_HOLE` at bit 3.
- `MMMC_VM_NB_TOP_OF_DRAM_SLOT1`, `MMMC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MMMC_VM_NB_UPPER_TOP_OF_DRAM2` encode top-of-DRAM/TOM2 ranges, with high address fragments generally shifted by bit 23.
- `MMMC_VM_FB_OFFSET` is a 24-bit framebuffer offset field.
- `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB` and `_MSB` store the default physical page number used for unmapped or faulted system aperture accesses; the LSB register is 32 bits and the MSB register contributes 4 high bits.
- `MMMC_VM_STEERING` has a 2-bit `DEFAULT_STEERING` field and resets to `0x00000001`.
- `MMMC_SHARED_VIRT_RESET_REQ` exposes 31 VF reset request bits plus a PF bit at bit 31. `MMMC_SHARED_VIRT_RESET_REQ2` adds one additional VF bit.
- `MMMC_MEM_POWER_LS` defines light-sleep setup and hold timing; its reset default is `0x00000208`.
- `MMMC_VM_CACHEABLE_DRAM_ADDRESS_START` and `_END` define 20-bit cacheable DRAM aperture bounds.
- `MMMC_VM_APT_CNTL` contains `FORCE_MTYPE_UC` and `DIRECT_SYSTEM_EN`; the 2.0.0 version has only these two fields, while later MMHUB generations add additional APT policy bits.
- `MMMC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`, `_START`, and `_END` define lock state and local HBM aperture bounds. The default end register is `0x000fffff`, meaning the full 20-bit field is set at reset.

VC shared MMVM decode registers:

- `MMMC_VM_FB_LOCATION_BASE` and `MMMC_VM_FB_LOCATION_TOP` describe the 24-bit framebuffer address window.
- `MMMC_VM_AGP_TOP`, `_BOT`, and `_BASE` describe the 24-bit AGP aperture programmed by the GART setup path.
- `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR` and `_HIGH_ADDR` describe logical system aperture bounds with 30-bit fields.
- `MMMC_VM_MX_L1_TLB_CNTL` controls the MMHUB L1 TLB. It exposes `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `ECO_BITS`, and `MTYPE`. Its default is `0x00000501`, and `mmhub_v2_0_init_tlb_regs()` rewrites key fields during GART enable.

ATC L2 performance counters:

- `MM_ATC_L2_PERFCOUNTER_LO` and `MM_ATC_L2_PERFCOUNTER_HI` provide the result readout. The low register is a full 32-bit counter fragment; the high register has a 16-bit high counter field plus a 16-bit `COMPARE_VALUE` field.
- `MM_ATC_L2_PERFCOUNTER0_CFG` and `MM_ATC_L2_PERFCOUNTER1_CFG` each expose 8-bit event select start/end fields, a 4-bit mode field, and `ENABLE`/`CLEAR` bits at bits 28 and 29.
- `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL` selects the visible counter result and controls start/stop triggers, global enable, global clear, and stop-on-saturate behavior. Its reset/default value is `0x04000000`, so `STOP_ALL_ON_SATURATE` is set by default.

## Control Flow and Runtime Use

There is no function-level control flow in this header. Runtime control flow is in the MMHUB implementation files that include it. For MMHUB 2.0.0, `amdgpu/mmhub_v2_0.c` includes this header and its matching offset/default headers.

Key runtime flows supported by this chunk:

1. `mmhub_v2_0_gart_enable()` initializes GART and VM translation by calling aperture, TLB, cache, system-domain, identity-aperture, VMID, and invalidation setup routines.
2. `mmhub_v2_0_init_system_aperture_regs()` programs the AGP registers, system aperture low/high registers, default system aperture physical page registers, and protection fault default address registers. In SR-IOV VF mode it skips the AGP and system aperture low/high writes because those shared registers are PF-managed.
3. `mmhub_v2_0_init_tlb_regs()` reads `mmMMMC_VM_MX_L1_TLB_CNTL`, sets `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `ENABLE_ADVANCED_DRIVER_MODEL`, clears `SYSTEM_APERTURE_UNMAPPED_ACCESS`, sets `MTYPE` to uncached, and writes the register back.
4. `mmhub_v2_0_gart_disable()` disables all VM contexts and then clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL` in `MMMC_VM_MX_L1_TLB_CNTL`.
5. `mmhub_v2_0_update_medium_grain_clock_gating()` and `mmhub_v2_0_update_medium_grain_light_sleep()` use nearby MMHUB clock-gating registers; this chunk's `MMUTCL2_CGTT_CLK_CTRL` is part of the same clock/power-management register area even though the v2.0 code path directly toggles ATC L2 and DAGB registers.

The performance-counter macros define hardware observability controls, but the searched tree does not show an in-tree MMHUB 2.0 path actively programming `MM_ATC_L2_PERFCOUNTER*_CFG` with `REG_SET_FIELD`. They are still exported for debug/perf tooling or future driver paths that need the generated names.

## State and Persistence Behavior

The header itself stores no state. All state represented here lives in hardware MMIO registers and persists until GPU reset, power-domain loss, suspend/resume reinitialization, PF reprogramming, or explicit driver writes.

Important persistent hardware state:

- ATS enable bits for each VF determine whether a VF can use the address translation cache path. Incorrect persistence across reset or VF assignment would affect isolation and address translation behavior.
- System aperture, AGP, framebuffer, default page, local HBM, and cacheable DRAM bounds shape how MMHUB routes and translates memory accesses.
- `MMMC_VM_MX_L1_TLB_CNTL` controls whether L1 TLB caching and the advanced driver model are active. GART enable/disable paths intentionally mutate this register.
- Virtual reset request bits can be sticky coordination state between PF/VF management paths and should be treated as hardware-owned request state rather than ordinary scratch bits.
- ATC L2 performance counters are accumulating hardware state. `CLEAR`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE` affect whether counters continue, reset, or stop when saturated.

The default header records reset values for the same register region: ATS defaults to disabled, APT control defaults to zero, L1 TLB control defaults to `0x00000501`, performance counters default to zero except result control with stop-on-saturate set, and the local HBM end field defaults to all ones in its 20-bit address field.

## Dependencies and Integration Points

Generated-register dependencies:

- `mmhub_2_0_0_offset.h` provides addresses such as `mmMMMC_VM_MX_L1_TLB_CNTL`, `mmMMMC_VM_SYSTEM_APERTURE_LOW_ADDR`, and `mmMM_ATC_L2_PERFCOUNTER_RSLT_CNTL`.
- `mmhub_2_0_0_default.h` provides the reset/default values used as safe initialization baselines.
- Other chunks of `mmhub_2_0_0_sh_mask.h` define the preceding main ATS register, VF0 ATS register, VM context registers, L2 cache/protection-fault registers, and invalidation engine fields that are programmed in the same MMHUB setup sequence.

Driver integration:

- `amdgpu/mmhub_v2_0.c` is the primary MMHUB 2.0 consumer. It programs GART apertures, system apertures, L1 TLB, L2 cache, VMID contexts, invalidation ranges, fault handling, and clock gating.
- Later MMHUB implementation files such as `mmhub_v3_0.c`, `mmhub_v3_3.c`, and `mmhub_v4_2_0.c` use equivalent field names where compatible, but offsets and some masks differ by generation. This chunk must stay paired with MMHUB 2.0.0 offsets and defaults.
- Display DC files include `mmhub_2_0_0_sh_mask.h` for generated register field visibility, but the searched direct uses of this chunk's functional fields are primarily in the AMDGPU MMHUB memory-management code.
- SR-IOV integration is visible through per-VF ATS registers, shared active-function IDs, virtual reset request registers, and driver branches such as `amdgpu_sriov_vf(adev)` that avoid programming PF-only shared aperture/cache registers from a VF.

## Risks and Edge Cases

- Mixing this mask header with offsets from another MMHUB generation can silently write the wrong bits. Later generations have similar names but different register layouts; for example, newer `MMMC_VM_APT_CNTL`, reset request, clock-gating, and framebuffer aperture layouts add or move fields.
- The chunk starts at `MMVM_PCIE_ATS_CNTL_VF_1`, so whole-file research must include the previous lines for the main ATS register and VF0. Treating this chunk alone as the complete ATS definition would miss the STU field and VF0 bit.
- Enabling `ATC_ENABLE` for the wrong VF can break isolation, translation correctness, or IOMMU/ATS expectations in SR-IOV deployments.
- Incorrect system aperture or framebuffer/AGP bounds can route MMHUB traffic to the wrong physical address range, causing VM faults, data corruption, or hangs.
- The default physical page registers are split across LSB/MSB page-number fields. Bad shifting when programming these fields can redirect faults/unmapped accesses to the wrong page.
- `MMMC_VM_MX_L1_TLB_CNTL` fields directly affect translation caching. Disabling the L1 TLB or advanced driver model at the wrong time can cause translation misses or performance collapse; enabling them before page-table/aperture setup can expose invalid translations.
- Virtual reset request registers are shared coordination points. Drivers should avoid treating them as local scratch state, especially under PF/VF management.
- Performance counter configuration can perturb observability if counters are not cleared, selected, or stopped consistently. The default stop-on-saturate bit means tests should account for counters ceasing to advance after saturation.

## Test and Verification Signals

Useful validation signals for this chunk are integration and hardware readback tests:

- Build coverage for MMHUB 2.0.0 paths that include `mmhub_2_0_0_sh_mask.h` and call `REG_SET_FIELD`/`REG_GET_FIELD` with these field names.
- Register readback after `mmhub_v2_0_gart_enable()` should show `MMMC_VM_MX_L1_TLB_CNTL.ENABLE_L1_TLB=1`, `ENABLE_ADVANCED_DRIVER_MODEL=1`, `SYSTEM_ACCESS_MODE=3`, and uncached `MTYPE` as programmed by `mmhub_v2_0_init_tlb_regs()`.
- Register readback after `mmhub_v2_0_gart_disable()` should show `ENABLE_L1_TLB=0` and `ENABLE_ADVANCED_DRIVER_MODEL=0`.
- GART/VM smoke tests should exercise AGP, framebuffer, and system aperture access ranges and confirm faults are redirected to configured default/fault pages rather than arbitrary memory.
- SR-IOV tests should verify VF paths do not attempt PF-only aperture/cache writes and that per-VF ATS enable/reset-request behavior is controlled by the expected function-management layer.
- Suspend/resume and GPU reset tests should confirm that aperture, TLB, and default page registers are restored after hardware state loss.
- Performance-counter validation can program `MM_ATC_L2_PERFCOUNTER0_CFG` or `1_CFG`, clear counters, enable triggers, generate MMHUB/ATC traffic, and read `MM_ATC_L2_PERFCOUNTER_LO/HI` while checking saturation and result-select behavior.

## Cross-Chunk Notes

This slice is the end of `mmhub_2_0_0_sh_mask.h`. It begins after the root `MMVM_PCIE_ATS_CNTL` and `MMVM_PCIE_ATS_CNTL_VF_0` definitions, so the final per-file document should merge this with the preceding chunk for a complete ATS description. It also relies on earlier chunks for VM context, invalidation, L2 cache, and protection-fault fields used by the same `mmhub_v2_0.c` setup sequence.
