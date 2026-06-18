# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_offset.h

## Purpose

`mmhub_1_0_offset.h` is an AMDGPU generated register-offset map for the SOC15 MMHUB 1.0 hardware block used by Vega/Raven-era GPU memory management. It contains preprocessor constants only: each `mm...` symbol maps a named MMHUB register to a 32-bit register offset, and each paired `..._BASE_IDX` selects the SOC15 register base index, which is `0` throughout this header. Consumers combine these offsets with SOC15 register-access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, and `SOC15_REG_ENTRY`.

The header is a hardware ABI surface for MMHUB programming. It lets the driver initialize GPU virtual memory, GART apertures, L1/L2 TLB and cache policy, VM fault handling, invalidation engines, address translation cache controls, display/multimedia MMHUB access, clock/power gating, and RAS/EDC counters without hard-coding numeric MMIO offsets in each consumer.

## Register Map Contents

The file is protected by `_mmhub_1_0_OFFSET_HEADER` and has no functions, structs, enums, or runtime data. Its important exported symbols are grouped by generated address-block comments:

- `mmhub_dagbdec`, base `0x68000`: `mmDAGB0_*` and `mmDAGB1_*` define two DAGB decoder instances. Each instance exposes read/write client slots, read/write control, GMI controls, address/data path burst and lazy timer registers, virtual-channel controls, credit/pending status, FIFO status, perf counters, and reserved slots. `mmDAGB0_CNTL_MISC2`/`mmDAGB1_CNTL_MISC2` are used by clock-gating code.
- `mmhub_ea_mmeadec`, base `0x68400`: `mmMMEA0_*` and `mmMMEA1_*` define two memory-manager external-address blocks. They cover DRAM and IO client-to-group maps, priority and urgency controls, address normalization, DRAM address decoding/hash/harvest configuration, SDP arbitration/credits, latency sampling, perf counters, EDC/DSM controls, clock controls, and error status.
- `mmhub_pctldec`, base `0x68e00`: `mmPCTL*` registers expose MMHUB deepsleep, power-gating, register-save ranges, RAM index/data, and execution control for low-power state management.
- `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, and `mmhub_l1tlb_vml1prdec`, bases `0x69600`, `0x69650`, and `0x69670`: L1 TLB status and performance counter controls/results.
- Standalone walker definitions: `mmVM_L2_SAW_CONTEXT0_*`, `mmVM_L2_SAW_CONTEXTS_DISABLE`, `mmVM_L2_SAW_CNTL4`, plus bit offsets `VMC_TAP_PDE_REQUEST_SNOOP_OFFSET`, `VMC_TAP_PTE_REQUEST_SNOOP_OFFSET`, `CONTEXT0_CNTL_ENABLE_OFFSET`, and `CONTEXT0_CNTL_PAGE_TABLE_DEPTH_OFFSET`.
- `mmhub_utcl2_atcl2dec`, base `0x69900`: ATC L2 controls, cache data, status, clock gating, and memory light-sleep controls.
- `mmhub_utcl2_vml2pfdec`, base `0x69a00`: VM L2 controls, dummy-page fault address/control, protection-fault control/status/default address, context-identity aperture registers, L2 bank/cache parity/group controls, and clock control.
- `mmhub_utcl2_vml2vcdec`, base `0x69b00`: VM context controls for context 0 through 15, context disable mask, invalidation engine sem/request/ack registers for engines 0 through 17, invalidation address ranges, and per-context page-table base/start/end low/high registers.
- `mmhub_utcl2_vml2pldec` and `mmhub_utcl2_vml2prdec`, bases `0x69e90` and `0x69ee0`: VM L2 performance counter controls and result registers.
- `mmhub_utcl2_vmsharedhvdec`, base `0x69f30`: SR-IOV/hypervisor-facing VF framebuffer size offsets, IOMMU controls, MARC base/relocation/length registers, PCIe ATS controls for PF and VF0-VF15, and `mmUTCL2_CGTT_CLK_CTRL`.
- `mmhub_utcl2_vmsharedpfdec`, base `0x6a040`: NB MMIO/PCI/DRAM limits, framebuffer offset, default system aperture address, steering, shared virtualization reset, cacheable DRAM window, APT controls, local HBM window, and late XGMI local-framebuffer additions `mmMC_VM_XGMI_LFB_CNTL` and `mmMC_VM_XGMI_LFB_SIZE`.
- `mmhub_utcl2_vmsharedvcdec`, base `0x6a0b0`: framebuffer location, AGP aperture, system aperture low/high, and L1 TLB control.
- `mmhub_utcl2_atcl2pfcntrdec` and `mmhub_utcl2_atcl2pfcntldec`, bases `0x6a100` and `0x6a120`: ATC L2 performance counter results and configuration.

The final `MMEA` block adds Vega20-specific aliases such as `mmMMEA0_EDC_CNT_VG20`, `mmMMEA0_EDC_CNT2_VG20`, `mmMMEA1_EDC_CNT_VG20`, and `mmMMEA1_EDC_CNT2_VG20`. These overlap the normal DSM-control address area for ASIC-specific RAS counter interpretation and are intentionally consumed by MMHUB v1.0 RAS code.

## Important APIs, Types, and Functions

This file defines no callable API. Its API is the macro namespace:

- Offset macros such as `mmVM_CONTEXT0_CNTL`, `mmVM_L2_CNTL`, `mmMC_VM_FB_LOCATION_BASE`, `mmDAGB0_CNTL_MISC2`, `mmATC_L2_MISC_CG`, and `mmMMEA0_EDC_CNT_VG20`.
- Base-index macros such as `mmVM_CONTEXT0_CNTL_BASE_IDX`, used by generated SOC15 register helpers and kept adjacent to the offset symbol for mechanical consistency.
- A few bit-position helper constants for SAW programming: `VMC_TAP_PDE_REQUEST_SNOOP_OFFSET`, `VMC_TAP_PTE_REQUEST_SNOOP_OFFSET`, `CONTEXT0_CNTL_ENABLE_OFFSET`, and `CONTEXT0_CNTL_PAGE_TABLE_DEPTH_OFFSET`.

Actual bit masks and shifts are supplied by `mmhub_1_0_sh_mask.h`; reset/default values are supplied by `mmhub_1_0_default.h`. The main implementation consumer is `drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c`, which includes all three files and programs the MMHUB through the SOC15 register helpers.

## Control Flow and Runtime Use

There is no control flow inside the header. Runtime control flow appears in consumers that rely on its constants:

- `mmhub_v1_0_get_fb_location()` reads `mmMC_VM_FB_LOCATION_BASE` and `mmMC_VM_FB_LOCATION_TOP` to derive `adev->gmc.fb_start` and `adev->gmc.fb_end`.
- `mmhub_v1_0_init_gart_aperture_regs()` programs context 0 page-table base/start/end registers using the `mmVM_CONTEXT0_PAGE_TABLE_*` offsets.
- `mmhub_v1_0_init_system_aperture_regs()` programs `mmMC_VM_AGP_*`, `mmMC_VM_SYSTEM_APERTURE_*`, default aperture address, and VM L2 protection fault default address/control registers.
- `mmhub_v1_0_init_tlb_regs()` uses `mmMC_VM_MX_L1_TLB_CNTL`; `mmhub_v1_0_init_cache_regs()` uses `mmVM_L2_CNTL*`.
- `mmhub_v1_0_setup_vmid_config()` iterates VMID contexts by computing distances from `mmVM_CONTEXT1_CNTL - mmVM_CONTEXT0_CNTL` and page-table-address spacing from `mmVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - mmVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`.
- `mmhub_v1_0_program_invalidation()` initializes 18 invalidation engines by stepping from `mmVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`/`HI32` using `hub->eng_addr_distance`.
- `mmhub_v1_0_gart_disable()` disables all VM contexts by iterating from `mmVM_CONTEXT0_CNTL` and turns off L1/L2 controls.
- Clock-gating paths read and modify `mmATC_L2_MISC_CG`, `mmDAGB0_CNTL_MISC2`, and `mmDAGB1_CNTL_MISC2`.
- RAS paths build field entries over the Vega20 MMEA EDC aliases to report correctable/uncorrectable memory errors.

Other integration points include `gmc_v9_0.c` golden register tables, `uvd_v7_0.c`, `vce_v4_0.c`, and `display/dc/resource/dce120/dce120_resource.c`, which include this header to address MMHUB registers for generation-specific GPU setup.

## State and Persistence Behavior

The header itself is compile-time state only. It persists no runtime data and performs no I/O. Its macro values determine which hardware registers are read or written by the driver:

- Device state affected by consumers includes framebuffer location, AGP/GART/system apertures, page-table roots and ranges, VMID enablement, L1 TLB and VM L2 cache configuration, VM fault redirection/default page behavior, invalidation engine address ranges, clock-gating/light-sleep controls, SR-IOV VF framebuffer offsets, ATS/IOMMU controls, and RAS/EDC counters.
- Register writes persist in hardware until reset, power-state transition, firmware action, or a later driver write. Some PCTL and clock-gating registers influence low-power save/restore behavior.
- The `BASE_IDX` value of `0` means all offsets are expected to be resolved against SOC15 MMHUB base segment 0 for this generation. A wrong base index or offset silently targets the wrong register window.

## Dependencies and Integration Points

The file depends only on the C preprocessor. Its practical dependencies are the generated companion headers and SOC15 access layer:

- `mmhub_1_0_sh_mask.h` for fields used with `REG_SET_FIELD`, `SOC15_REG_FIELD`, and mask/shift operations.
- `mmhub_1_0_default.h` for default register values such as `mmVM_L2_CNTL3_DEFAULT` and `mmVM_L2_CNTL4_DEFAULT`.
- SOC15 helpers in the AMDGPU tree for translating `(HWIP, instance, offset)` into MMIO addresses.
- `amdgpu_vmhub` initialization, which stores absolute register offsets derived from this header for later VM invalidation and fault handling.
- ASIC-specific branches in `mmhub_v1_0.c`, including SR-IOV VF behavior, Raven special handling, Vega20 RAS aliases, and XGMI local framebuffer controls.

The repeated and contiguous register layout is an implicit contract. Consumers calculate register strides by subtracting adjacent constants rather than enumerating every offset manually.

## Risks and Maintenance Notes

- Offset drift is high impact. Any wrong `mmVM_CONTEXT*`, `mmVM_INVALIDATE_ENG*`, `mmMC_VM_*`, or `mmVM_L2_*` value can corrupt GPU VM setup, cause page faults, break GART, hang the device, or make invalidation acknowledgements target the wrong engine.
- The header uses old `mm`-prefixed names, while newer MMHUB headers often use `reg`-prefixed names and different base indices. Mixing generations can compile in some contexts but program the wrong hardware.
- Consumer stride calculations assume contiguous register spacing. Inserting, deleting, or renumbering one context/invalidation macro can break loops even if individual named accesses still look correct.
- Reserved registers are exported as named offsets. They should not be newly programmed without hardware documentation because their behavior can be ASIC stepping dependent.
- Vega20 alias macros intentionally overlap with non-VG20 symbolic regions. Treat them as ASIC-specific aliases, not duplicate definitions to deduplicate mechanically.
- SR-IOV and APU paths are sensitive to framebuffer/aperture registers. `mmMC_VM_FB_LOCATION_BASE/TOP` and system aperture high-address handling are known to have generation-specific workarounds in consumers.
- Because this is generated hardware register data, manual edits should be avoided unless synchronized with the corresponding mask/default headers and implementation code.

## Test Signals

Useful validation signals for changes touching this header or its consumers:

- Build coverage for AMDGPU with `mmhub_v1_0.c`, display `dce120_resource.c`, UVD/VCE, and `gmc_v9_0.c` enabled to catch missing or renamed macros.
- Boot/probe logs on MMHUB 1.0 ASICs should show successful AMDGPU initialization without VM fault storms, GART setup failures, or GPU reset loops.
- Exercise GART and VM paths: buffer object allocation/mapping, command submission from multiple VMIDs, page-table updates, and VM invalidation completion.
- Check suspend/resume and runtime power-management behavior for clock-gating and light-sleep paths that use DAGB and ATC offsets.
- Run SR-IOV VF smoke tests where available; VF framebuffer location and aperture registers are explicitly programmed by the driver.
- Inspect RAS/EDC reporting on Vega20-class hardware for sane MMEA counter reads through the `_VG20` aliases.
- Compare register dumps against known-good hardware documentation or upstream generated headers after any offset regeneration.
