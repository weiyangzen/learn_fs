# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_2_d.h

## Purpose

`gmc_8_2_d.h` is a generated-style AMDGPU hardware register address map for the GMC 8.2 memory-controller block. It exports preprocessor constants whose names begin with `mm` and whose values are MMIO register offsets used by the VI-generation AMD GPU driver stack. The file does not implement algorithms; it is the address vocabulary that lets memory-controller, virtual-memory, display, writeback, performance-monitoring, SR-IOV, ATC/ATS, and power-management code address the right hardware registers.

The register groups covered include memory-controller arbitration (`mmMC_ARB_*`), client-interface credits and watermarks (`mmMC_CITF_*`), hub read/write request routing (`mmMC_HUB_*`), reorder/page buffer controls (`mmMC_RPB_*`), frame-buffer and system aperture programming (`mmMC_VM_*`), VM L1/L2 TLB and page-table context registers (`mmVM_*`), crossbar and peer routing (`mmMC_XBAR_*`, `mmMC_XPB_*`), ATC/ATS address-translation registers (`mmATC_*`), GMCON firmware/power-management registers (`mmGMCON_*`), DRAM/fuse and GRUB controls, and DCE writeback buffer-manager registers (`mmMCIF_WB*`).

## Important APIs, Types, And Constants

This header defines constants only; it declares no functions, structs, or C types.

Important exported constant families:

- `mmMC_VM_FB_LOCATION`, `mmMC_VM_AGP_*`, `mmMC_VM_SYSTEM_APERTURE_*`, and `mmMC_VM_FB_OFFSET` define memory-aperture programming registers used to lay out VRAM, GART, AGP, and default/unmapped addresses in GPU physical address space.
- `mmVM_L2_CNTL`, `mmVM_L2_CNTL2`, `mmVM_L2_CNTL3`, and `mmVM_L2_CNTL4` define VM L2 cache/TLB control registers. Companion context registers such as `mmVM_CONTEXT0_PAGE_TABLE_BASE_ADDR`, `mmVM_CONTEXT*_PAGE_TABLE_START_ADDR`, `mmVM_CONTEXT*_PAGE_TABLE_END_ADDR`, `mmVM_CONTEXT*_CNTL`, and protection-fault registers are used to enable GPU page tables and diagnose VM faults.
- `mmMC_VM_MX_L1_TLB_CNTL` and related `mmMC_VM_MB_*` / `mmMC_VM_MD_*` registers expose L1 TLB and memory-bank debug/status controls.
- `mmMC_HUB_RDREQ_*`, `mmMC_HUB_WDP_*`, and `mmMC_HUB_WRRET_*` define per-client read/write hub controls for blocks such as SDMA, HDP, UVD, VCE, RLC, SMU, XDMA, ISP, and memory-channel destinations.
- `mmMC_CITF_*`, `mmMC_ARB_*`, `mmMC_XBAR_*`, and `mmMC_XPB_*` define arbitration, credit, crossbar, routing, peer-to-peer, and performance-tuning registers.
- `mmATC_*` registers describe aperture, PASID/VMID mapping, ATS status/fault, and ATC L1/L2 cache controls.
- `mmMCIF_WB*` registers define display writeback buffer-manager controls and per-buffer address/status registers for writeback instances 0, 1, and 2.

The macros are consumed as register indices by low-level access helpers such as `RREG32(...)`, `WREG32(...)`, display `dm_read_reg(...)` / `dm_write_reg(...)`, and by field helpers together with `gmc_8_2_sh_mask.h`.

## Control Flow

There is no runtime control flow in this header. Its behavior is entirely compile-time substitution: including C files compile symbolic register names into numeric offsets. Runtime control flow appears in consumers, for example:

- `gmc_v8_0_vram_gtt_location()` reads `mmMC_VM_FB_LOCATION` to derive the VRAM base on non-SR-IOV physical functions.
- `gmc_v8_0_mc_program()` writes `mmMC_VM_SYSTEM_APERTURE_*`, `mmMC_VM_FB_LOCATION`, and AGP aperture registers when programming the memory controller.
- `gmc_v8_0_gart_enable()` reads and writes `mmMC_VM_MX_L1_TLB_CNTL`, `mmVM_L2_CNTL*`, page-table base/end registers, and protection-fault registers while enabling GPU virtual memory.
- DCE 11 display code includes this file for GMC/DCN-adjacent writeback and memory-input register offsets.

## State And Persistence Behavior

The header itself has no mutable state, persistence, initialization, or teardown. The constants address hardware state that persists in GPU registers after writes until changed by the driver, firmware, reset, power-gating transition, suspend/resume, or device removal. The most sensitive persistent hardware state behind these constants includes:

- VRAM, GART, AGP, system aperture, and default-page mappings.
- VM L1/L2 TLB enablement, invalidation, fragment size, cache behavior, and context page-table bases.
- SR-IOV virtual-function aperture sizing through `mmMC_VM_FB_SIZE_OFFSET_VF*`.
- ATC PASID/VMID mappings and ATS fault/status registers.
- Display writeback buffer addresses, pitches, status, interrupt enable/ack, and buffer-manager enable bits.

Because the constants are ABI-like hardware encodings, changes to their numeric values are not normal software refactors. Any mismatch between the header and the ASIC register map can create persistent device misconfiguration until reset.

## Dependencies

Direct dependencies are minimal: the file is standalone apart from its include guard and C preprocessor support. Operational dependencies are in consumers:

- `gmc_8_2_sh_mask.h` supplies field shift/mask definitions for the registers named here.
- AMDGPU register-access helpers (`RREG32`, `WREG32`, `REG_SET_FIELD`) interpret these constants as MMIO register offsets.
- Display Core code uses display service register accessors with these offsets for DCE 11 era memory-input/writeback paths.
- ASIC selection code must include this header only for hardware whose register map matches GMC 8.2.

## Integration Points

Observed integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/gmc_v8_0.c` uses the VM and memory-aperture registers to derive VRAM placement, program MC apertures, enable the GART, configure VM L1/L2 behavior, and manage page-table context registers.
- `drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c` includes this header alongside `gmc_8_2_sh_mask.h` and other VI block headers while configuring GFX8/VI hardware.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_vi.c` includes this header for VI SR-IOV / MxGPU register access.
- `drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.c` and `dce110_mem_input_v.c` include it with DCE 11 register headers, tying GMC offsets into display compression, memory input, and writeback paths.

## Risks

- Wrong register offsets can corrupt memory-controller programming, break GPU virtual memory, cause invalid VRAM/GART placement, trigger VM faults, or hang the device.
- The header uses global macro names with no type checking. Accidentally including the wrong ASIC generation's register header can still compile while targeting incompatible registers.
- Some register names are duplicated aliases for instance-specific writeback blocks, such as generic `mmMCIF_WB_*` names and `mmMCIF_WB0_*` names sharing the same offsets. Consumers must pick the right instance and not assume all aliases are independent registers.
- SR-IOV and ATC/ATS registers are especially sensitive because host/guest aperture or PASID mapping mistakes can affect isolation and device fault behavior.
- The file encodes low-level hardware details without local validation; correctness depends on generator/source register specs and integration tests on matching hardware.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Kernel build coverage for VI AMDGPU and DCE 11 display configurations that include `gmc_8_2_d.h` with `gmc_8_2_sh_mask.h`.
- Boot/probe on matching GMC 8.2 GPUs with no MC idle timeout warnings, no early VM faults, and correct VRAM size/base reporting.
- GART and GPUVM smoke tests: page-table setup succeeds, VM context faults are absent or expected, and TLB invalidation paths complete.
- Display scanout, compression, memory-input, and writeback tests on DCE 11 paths that include this header.
- SR-IOV VF/PF tests for `mmMC_VM_FB_LOCATION` and `mmMC_VM_FB_SIZE_OFFSET_VF*` behavior.
- Suspend/resume and GPU reset tests, because register state addressed by this header must be restored in the correct order.
