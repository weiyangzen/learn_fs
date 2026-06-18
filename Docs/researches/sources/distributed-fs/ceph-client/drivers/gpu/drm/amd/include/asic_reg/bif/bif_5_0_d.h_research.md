<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_d.h

## Purpose
`bif_5_0_d.h` is a generated-style AMD GPU register-address header for the BIF 5.0 block. BIF is the bus interface block around PCIe, doorbells, host-data-path flushes, reset/power sequencing, BACO, peer apertures, SR-IOV/GPUIOV, mailbox registers, and PCIe/PB/PIF link hardware.

The file contains preprocessor constants only. It maps symbolic `mm*` names to direct MMIO/configuration-space offsets and `ix*` names to indexed PCIe/PB/PIF register addresses. Consumers combine these addresses with masks and shifts from `bif_5_0_sh_mask.h` and access them through AMDGPU register helpers such as `RREG32()`, `WREG32()`, `RREG32_PCIE()`, and `WREG32_PCIE()`.

## Important APIs, Types, and Constants
There are no C functions, structs, enums, storage definitions, or inline helpers. The exported API is the guarded macro namespace under `BIF_5_0_D_H`.

Important direct `mm*` groups include:

- `mmMM_INDEX`, `mmMM_INDEX_HI`, and `mmMM_DATA` for indirect MMIO aperture access.
- Core BIF configuration and status registers such as `mmBUS_CNTL`, `mmCONFIG_CNTL`, `mmCONFIG_MEMSIZE`, `mmCONFIG_F0_BASE`, `mmCONFIG_APER_SIZE`, `mmBIF_IOV_FUNC_IDENTIFIER`, `mmBIF_BME_STATUS`, and `mmBIF_ATOMIC_ERR_LOG`.
- Doorbell, XDMA, clock, and aperture registers such as `mmBIF_DOORBELL_APER_EN`, `mmBIF_DOORBELL_CNTL`, `mmBIF_DOORBELL_GBLAPER*_LOWER/UPPER`, `mmBIF_XDMA_LO`, `mmBIF_XDMA_HI`, `mmBIF_CLK_CTRL`, and `mmBIF_FB_EN`.
- Reset, interrupt, debug, hang-protection, and pending-transaction registers such as `mmBX_RESET_EN`, `mmBX_RESET_CNTL`, `mmINTERRUPT_CNTL`, `mmBIF_DEBUG_*`, `mmSLAVE_HANG_PROTECTION_CNTL`, `mmBIF_MST_TRANS_PENDING`, and `mmBIF_SLV_TRANS_PENDING`.
- HDP and GARLIC coherency flush families: `mmHDP_*_COHERENCY_FLUSH_CNTL`, `mmGPU_HDP_FLUSH_REQ`, `mmGPU_HDP_FLUSH_DONE`, `mmGARLIC_FLUSH_ADDR_START_*`, `mmGARLIC_FLUSH_ADDR_END_*`, `mmGARLIC_FLUSH_REQ`, `mmGPU_GARLIC_FLUSH_REQ`, and `mmGPU_GARLIC_FLUSH_DONE`.
- Peer and bus-numbering registers such as `mmPEER_REG_RANGE*`, `mmPEER*_FB_OFFSET_*`, `mmBIF_BUSNUM_*`, `mmCAPTURE_HOST_BUSNUM`, and `mmHOST_BUSNUM`.
- BACO and power-management registers including `mmBACO_CNTL`, `mmBACO_CNTL_MISC`, `mmBIF_BACO_DEBUG`, `mmBIF_BACO_DEBUG_LATCH`, `mmSMU_BIF_VDDGFX_PWR_STATUS`, `mmBIF_VDDGFX_*`, and `mmMEM_TYPE_CNTL`.
- BIOS scratch, ring-buffer, mailbox, GPUIOV, VM initialization, and virtualization registers such as `mmBIOS_SCRATCH_0` through `_15`, `mmBIF_RB_*`, `mmMAILBOX_*`, `mmBIF_VIRT_RESET_REQ`, `mmVM_INIT_STATUS`, `mmBIF_GPUIOV_*`, and `mmBIF_MMIO_MAP_RANGE*`.
- PCI configuration and extended capability offsets for vendor/device IDs, command/status, BARs, PM, PCIe, MSI/MSI-X, AER, DPA, ACS, ATS, PASID, TPH, multicast, LTR, ARI, SR-IOV, and the AMD GPUIOV vendor-specific capability.
- MSI-X table/PBA addresses, BIF RFE reset and power-down command/status registers, and IMPCTL calibration/control registers.

Important indexed `ix*` groups include:

- PCIe core and link-control registers such as `ixPCIE_CNTL`, `ixPCIE_CONFIG_CNTL`, `ixPCIE_INT_*`, `ixPCIE_BUS_CNTL`, `ixPCIE_LC_*`, `ixPCIE_TX_*`, `ixPCIE_RX_*`, `ixPCIE_FC_*`, `ixPCIE_ERR_CNTL`, and performance-counter registers.
- PCIe strap, PRBS, EFUSE, DPA, soft-reset, link-management, and clock/power-management addresses.
- `ixPB0_*` and `ixPB1_*` PHY/bridge address spaces, with global, strap, PLL, RX lane, TX lane, test/debug, and SCI status/override registers for lanes 0 through 15.
- `ixPB0_PIF_*` and `ixPB1_PIF_*` PIF command, global override, TX/RX, and per-lane override registers.
- `ixPCIEP_*` PCIe port-layer transmit/receive credit, lane status, link training, equalization, SR-IOV private control, and error-injection registers.

## Control Flow
There is no runtime control flow. The only local flow is the include guard: once `BIF_5_0_D_H` is defined, repeated includes are skipped.

Runtime flow is entirely in consumers. VI-generation AMDGPU code reads and writes `ixPCIE_LC_CNTL`, `ixPCIE_LC_CNTL2`, `ixPCIE_LC_CNTL3`, `ixPCIE_LC_CNTL6`, `ixPCIE_LC_LINK_WIDTH_CNTL`, `ixPCIE_LC_N_FTS_CNTL`, `ixPCIE_P_CNTL`, `ixCPM_CONTROL`, `ixPCIE_CONFIG_CNTL`, and related PCIe addresses while programming ASPM and link power behavior. The same VI path toggles `mmBIF_DOORBELL_APER_EN` for non-APU doorbell aperture enablement and reads `mmPCIE_EFUSE4` for revision ID strap data. PowerPlay BACO code reads `mmCC_BIF_BX_FUSESTRAP0` to detect BACO capability and `mmBACO_CNTL` to report BACO state.

## State and Persistence Behavior
The header itself is stateless and persists nothing. It names hardware registers whose values persist in the device register file until reset, power-state transition, firmware action, BACO entry/exit, or another driver write changes them.

State represented by these addresses includes PCIe negotiated/programmed link behavior, doorbell aperture enablement, flush request/done state, peer aperture mappings, BIF scratch and BIOS scratch data, BACO mode, power-status and VDDGFX ranges, mailbox message buffers, SR-IOV/GPUIOV function state, VM initialization status, MSI-X table entries, and PHY/PIF lane controls. The header does not encode access ordering, polling requirements, write-one-clear behavior, or reset-domain rules; those must come from the companion mask header, hardware documentation, and calling code.

## Dependencies and Integration Points
The direct syntactic dependency is only the C preprocessor. Practical use depends on:

- `bif_5_0_sh_mask.h` for field masks, shifts, and field values corresponding to these addresses.
- AMDGPU register access helpers for direct MMIO, SMC, and PCIe indexed register spaces.
- ASIC-generation selection that chooses BIF 5.0 rather than neighboring maps such as `bif_4_1_d.h` or `bif_5_1_d.h`.

Known direct include sites include `amdgpu/vi.c`, `amdgpu/gmc_v8_0.c`, `amdgpu/gfx_v8_0.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/sdma_v3_0.c`, PowerPlay SMU manager files for Iceland/Tonga/Fiji/Polaris/Vegam, PowerPlay BACO files for Tonga/Fiji/Polaris/SMU7, and `pm/powerplay/inc/smu7_common.h`.

Major integration points are PCIe link and ASPM setup, doorbell aperture bring-up, HDP/GARLIC coherency flushing, BACO support and state transitions, SMU/PowerPlay register scripts, revision/fuse reads, peer-to-peer aperture setup, virtualization mailbox/GPUIOV control, and reset or hang-recovery paths.

## Risks and Edge Cases
Register-address drift is high impact. A wrong numeric value can route a read or write to unrelated hardware and cause PCIe link failures, doorbell loss, GPU hangs, reset failures, failed BACO transitions, broken flush synchronization, or bad virtualization state.

The `mm*` and `ix*` prefixes are conventions, not type-checked contracts. Passing an indexed `ix*` address to a direct MMIO helper, or a direct `mm*` offset to a PCIe indexed helper, is a realistic integration bug. Several PCI configuration symbols intentionally share offsets because they name different fields in the same DWORD, so audits must not assume one symbol per address.

This header combines several address spaces: MMIO, PCI config space, PCIe indirect space, PB0/PB1 PHY space, PIF space, PCIe port-layer space, and MSI-X table space. Callers must know which aperture and access rules apply. Reset, BACO, PHY, link training, and clock/power-management registers are sequencing-sensitive and may require delays, polling, firmware coordination, or posted-write flushing that is not visible here.

Generation mismatch is another risk. BIF 5.0 coexists with BIF 5.1 and earlier BIF maps; names may look compatible while offsets or available fields differ. Virtualization and doorbell registers are isolation-sensitive, so stale or incorrect GPUIOV/SR-IOV/doorbell programming can affect function isolation or queue submission.

## Test Signals
Primary validation signals are build and hardware integration:

- Kernel build coverage for VI/CIK-era AMDGPU and PowerPlay configurations catches missing symbols and include-guard breakage.
- Static checks can compare touched `mm*`/`ix*` names against companion `bif_5_0_sh_mask.h` field definitions where bit manipulation is expected.
- Driver probe on matching hardware should cover BIF direct MMIO accessibility, PCIe indexed access, fuse/revision reads, doorbell aperture enablement, HDP/GARLIC flushes, interrupt/ring bring-up, SDMA/GFX initialization, and BACO support detection.
- Power-management tests should exercise ASPM programming, suspend/resume, BACO entry/exit, clock gating, and reset paths.
- Failure signals include PCIe AER reports, reduced or unstable link width/speed, queue submission failures from missing doorbells, HDP flush timeouts, BACO transition timeouts, reset hangs, and virtualization mailbox or VM-init status anomalies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_d.h -->
