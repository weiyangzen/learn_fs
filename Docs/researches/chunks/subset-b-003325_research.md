# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h lines 6014-9163

## Purpose

This chunk is a generated register-offset map for AMD NBIO 7.9.0 hardware. It does not implement executable logic; it gives the AMDGPU driver compile-time names for MMIO, indexed, and PCI configuration-space offsets used by the SOC15 register access helpers. The line range covers the end of one NBIF/BIF register group, several `aid_nbio_nbif0_*` address blocks, IOHUB northbridge/IOMMU/RAS blocks, root-complex PCIe config space, SR-IOV VF config-space mirrors for VF0-VF7, and the beginning of VF0 PF/VF decode aliases.

Within this chunk there are 2,954 `#define`s: 1,894 address/value definitions and 1,060 matching `_BASE_IDX` definitions. The `reg*` symbols represent SOC15 MMIO/register-space offsets; the `cfg*` symbols represent PCI configuration-space offsets. Most registers in the `0x10120000`, `0x13b*`, `0x14300000`, and `0x15700000` address blocks have `_BASE_IDX 8`, GDC/SYSHUB registers under `0x1400000` use `_BASE_IDX 5`, and the VF-local PF/VF decode aliases at base `0x0` use `_BASE_IDX 2` or `0`.

## Important APIs, Types, and Macro Families

There are no C functions, structs, or enums in this chunk. The important API surface is the macro namespace consumed by AMDGPU register helpers:

- `regAID*_PF_BASE_ADDR` and `regAID*_XCC*_PF_BASE_ADDR`: AID/XCC PF base address aliases at offsets `0xcdc3` through `0xcdcb`.
- `regBIFC_DOORBELL_ACCESS_EN_PF` and `regBIFC_DOORBELL_ACCESS_EN_VF0` through `VF7`: PF/VF doorbell access enable registers used to gate doorbell pass-through behavior.
- `regBIFC_*`, `regNBIF_*`, `regSMN_MST_*`, and `regBIF_*`: BIF/NBIF control, interrupt, error logging, PASID, performance counter, power-gating, clock-gating, strap, timeout, and SDP/GMI credit-control registers.
- `regRCC_DWN_DEV0_2_*`, `regRCC_DWNP_DEV0_2_*`, `regRCC_EP_DEV0_*`, `regRCC_DEV0_*`, and `regRCC_STRAP2_*`: root-complex controller PCIe endpoint/downstream control, link/power/DPA state, requester ID, reset/config aperture, GPU IOV, peer register/FB offsets, bus-number capture, and strap registers.
- `regBIF_BX1_*` and `regBIF_BX_PF1_*`: BIF BX system/PF registers for indirect PCIe index/data windows, BIOS and driver scratch registers, MMIO register CAM remapping, VF enable/status controls, HDP flush remap controls, BIF ring pointers, mailbox registers, pad controls, and partition capability/status.
- `regS2A_DOORBELL_ENTRY_*_CTRL`, `regS2A_DOORBELL_COMMON_CTRL_REG`, `regGDC1_*`, `regXCC_DOORBELL_FENCE`, and `regSHUB_*`: GDC, S2A doorbell routing, XCC doorbell fence, reset, and host/SYSHUB integration registers. `amdgpu/nbio_v7_9.c` uses these S2A doorbell-entry offsets when programming SDMA, VCN, and IH doorbell routing.
- `regHST_CLK*`, `regDMA_CLK*`, and `regNIC400_*`: SYSHUB direct clock/control and NIC400 fabric QoS/outstanding transaction controls.
- `regNB_*`, `regSW_*`, `regCAM_*`, `regTRAP*`, and `regSB_*`: IOHUB northbridge config and misc registers for bus/MMIO/DRAM windows, southbridge location, NMI/SMI/SCI/GIC handling, CAM target data, PSP/SMU base addresses, SMU CPU blocking, trap request/response windows, and bridge config fields.
- `regPARITY_*`, `regRAS_*`, and `reg*ACTION_CONTROL`: IOHUB NB RAS configuration, parity severity/status/counter groups, global RAS status, RAS scratch, and action-control registers for PCIe port errors.
- `regNB_PCIE0DEVINDCFG*`, `regNB_NBIF1DEVINDCFG0_*`, `regNB_INTSBDEVINDCFG0_*`, `regNB_PCIE0RCBDG_INDCFG*`, and `regNB_NBIF1RCBDG_INDCFG0_*`: indirect SMN index/data windows for PCIe device and root-complex bridge configuration blocks.
- `regL2_*`, `regL2A_*`, `regL2B_*`, `regPPR_CONTROL`: IOMMU L2 A/B performance, control, page-size, translation/cache way, error-rule, power/clock-gating, update-filter, and PPR controls.
- `regFEATURES_ENABLE`: IOAPIC feature enable register.
- `cfgBIF_CFG_DEV0_RC_*`: root-complex PCI config offsets, including standard header fields, bridge windows, MSI, PCIe/VC/DSN/AER/secondary PCIe/link equalization, ACS, DLF, 16 GT/s, lane margining, and 32 GT/s capability fields.
- `cfgBIF_CFG_DEV0_EPF0_VF{0..7}_*`: repeated virtual-function PCI config offset maps for SR-IOV VF0 through VF7, covering standard config header, BARs, MSI/MSI-X, PCIe vendor-specific caps, AER logs, ATS, and ARI.
- `regBIF_BX_DEV0_EPF0_VF0_*`, `regBIF_BX_DEV0_EPF0_VF0_MM_*`, and `regRCC_DEV0_EPF0_VF0_RCC_*`: VF0 local PF/VF decode aliases for BME/atomic status, doorbell self-ring GPA aperture, HDP coherency flush/invalidate controls, GPU HDP flush request/done, transaction-pending status, mailbox buffers/control/interrupts, MM index/data windows, and VF0 RCC memory/doorbell config.

## Control Flow

The header has no branches or runtime control flow. Its control effect appears only after inclusion by C files that call AMDGPU register access macros such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_SOC15_EXT`, `WREG32_FIELD15_PREREG`, and `SOC15_REG_OFFSET`.

For example, `amdgpu/nbio_v7_9.c` includes this header and uses chunk-defined offsets to:

- Enable PF doorbell pass-through via `regBIFC_DOORBELL_ACCESS_EN_PF`.
- Toggle the RCC doorbell aperture through `regRCC_DEV0_EPF0_RCC_DOORBELL_APER_EN`.
- Read memory sizing through `regRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`.
- Program S2A doorbell routing with `regS2A_DOORBELL_ENTRY_*_CTRL` for SDMA, VCN, and IH clients.

Because the macros are constants, call-site control flow is driven by the consuming NBIO logic and the hardware state. A wrong offset or base index here changes which hardware register the existing control flow touches.

## State and Persistence Behavior

This chunk defines hardware state locations but stores no software state. Persistence is entirely in the target hardware registers:

- Doorbell aperture and S2A routing registers persist until reset or reprogramming and affect command submission, interrupt handling, and multimedia/SDMA doorbell delivery.
- RCC, BIF, and NBIF registers influence PCIe endpoint/root-complex behavior, request routing, bus numbering, reset handling, peer memory windows, and GPU IOV partitioning.
- BIOS/driver scratch registers can be used as firmware-driver coordination state.
- RAS/parity status and counter registers reflect hardware error state and may require explicit clearing by code outside this chunk.
- IOMMU L2 registers affect translation/cache/performance behavior and are stateful hardware controls.
- PCI config-space macros describe standard and extended capabilities exposed to the host or virtual functions; their values are hardware/firmware-backed, not stored by this header.

## Dependencies

The chunk depends on the AMD SOC15 register access convention:

- `_BASE_IDX` values must match the register's SOC15 aperture/base table entry used by `SOC15_REG_OFFSET` and the read/write helpers.
- Bitfield programming depends on the sibling mask/shift header `nbio_7_9_0_sh_mask.h`; offsets here identify the register, while the mask header identifies fields within it.
- Interrupt source IDs used with NBIO are supplied by `ivsrcid/nbio/irqsrcs_nbif_7_4.h`.
- Runtime consumers are in the AMDGPU NBIO and RAS code, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`.
- The generated register map must stay aligned with the actual NBIO 7.9.0 ASIC register database and with equivalent generated headers for adjacent ASICs.

## Integration Points

The primary integration point is AMDGPU's `adev->nbio` operation table and NBIO initialization/control routines. These offsets let NBIO code program doorbells, memory-controller access windows, PCIe link/root-complex behavior, self-ring apertures, RAS interrupt wiring, and hardware virtualization surfaces without hard-coded numeric addresses in the driver body.

The config-space aliases integrate with PCIe enumeration and SR-IOV virtualization. The root-complex block maps bridge and extended capability offsets, while the repeated VF0-VF7 blocks describe the exposed virtual function config layout. The VF-local decode aliases at the end of the chunk are especially relevant to SR-IOV guests or host-mediated VF handling because they expose VF0 mailbox, HDP flush, transaction-pending, and RCC memory/doorbell controls through a different base index.

The IOHUB and IOMMU blocks connect NBIO to platform fabric functions outside classic graphics command submission: RAS accounting, interrupt routing, northbridge window setup, trap machinery, IOAPIC features, IOMMU L2 controls, and SMN indirect access windows.

## Risks and Edge Cases

- Offset drift is high impact. A stale generated offset can write the wrong NBIO/RCC/IOMMU register, causing PCIe link instability, broken doorbells, inaccessible memory windows, bad RAS reporting, or VF isolation failures.
- `_BASE_IDX` drift is as risky as numeric offset drift. The same offset with the wrong base index can address a different aperture.
- The repeated VF config-space blocks are intentionally similar; copy-generation mistakes may only affect one VF and can be missed if tests exercise only VF0.
- Several names alias the same numeric offset, especially PCI/DPA/MSI fields and packed capability registers. Consumers must use the correct mask/shift definitions for the selected semantic view.
- RAS and parity status/counter registers may be write-one-to-clear or otherwise side-effectful in the real hardware. Read/write tests must avoid destructive probing unless the ASIC spec allows it.
- Doorbell access and self-ring aperture registers affect command submission and interrupt paths. Bad programming can look like unrelated engine hangs.
- IOMMU L2 control and error-rule registers can affect address translation behavior; changes should be validated under DMA, ATS/PASID, and SR-IOV workloads.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for AMDGPU configurations that compile `nbio_v7_9.c` and `amdgpu_ras_nbio_v7_9.c`; missing or renamed macros should fail compilation.
- Boot/probe on an NBIO 7.9.0 ASIC with clean `dmesg`, successful PCIe enumeration, correct BAR sizing, and successful `amdgpu` device initialization.
- Doorbell smoke tests: graphics/compute queue submission, SDMA copies, VCN operation, and interrupt handling after `nbio_v7_9_*_doorbell_range()` programs the S2A and BIF doorbell registers.
- SR-IOV tests with multiple VFs, not just VF0: VF config-space visibility, MSI/MSI-X operation, ATS/ARI capability behavior, VF mailbox traffic, HDP flush completion, and VF doorbell/FB access status.
- RAS tests or fault-injection on supported hardware: parity status/counter visibility, RAS global status changes, and correct IRQ registration through the NBIO RAS manager.
- PCIe stress: link retrain/speed checks, AER status logging, lane equalization/margining visibility, and reset/FLR behavior.
- IOMMU/ATS/PASID DMA workloads to detect incorrect L2 and translation-related offsets.
- Register audit scripts comparing generated offsets and `_BASE_IDX` values against the authoritative ASIC register database for NBIO 7.9.0.
