# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_offset.h

## Purpose

`nbif_6_1_offset.h` is a generated AMDGPU register-offset header for the NBIF 6.1 hardware block. It exports preprocessor constants for PCI/PCIe configuration space, NBIF/BIF/RCC/SYSHUB/GDC/SION reset and RAS registers, strap registers, SR-IOV and GPUIOV virtualization registers, doorbell ranges, MSI/MSI-X tables, and indirect register windows. The file has no executable logic; its role is to provide the numeric register identifiers consumed by SOC15/NBIO register access macros and command-table driven power-management paths.

The header is protected by `_nbif_6_1_OFFSET_HEADER` and contains 1,542 `#define` entries. Names use AMD register-generation prefixes:

- `cfg...` for PCI configuration-space offsets.
- `mm...` for memory-mapped register identifiers used by SOC15-style accessors.
- `ix...` for indirect or indexed register offsets and SMN-style address spaces.
- `..._BASE_IDX` companions for many `mm...` entries, selecting the SOC15 register base segment used by access macros.

## Important APIs, Types, And Constants

This file defines constants only; it declares no C functions, structs, enums, or storage. Important exported groups include:

- PCI configuration and capability offsets: `cfgVENDOR_ID`, `cfgDEVICE_ID`, BAR registers, MSI/MSI-X capability fields, PCIe device/link capability and control fields, AER fields, ATS/PASID/ARI/LTR/ACS/SR-IOV fields, and GPUIOV vendor-specific registers.
- Bridge and shadow configuration registers: `mmSUB_BUS_NUMBER_LATENCY`, `mmIO_BASE_LIMIT`, `ixSHADOW_COMMAND`, `ixSHADOW_BASE_ADDR_*`, `ixSUC_INDEX`, and `ixSUM_INDEX`.
- GDC/NBIF/SYSHUB direct-register windows at base `0x1400000`: A2S/S2A controls, doorbell range registers, SION credit and timeslot registers, SYSHUB clock/QoS controls, GDC RAS controls, and SHUB reset controls.
- Endpoint and root-complex BIF registers: `mmEP_PCIE_*`, `mmDN_PCIE_*`, `mmPCIE_*`, `mmRCC_*`, `mmBIF_*`, `mmBACO_CNTL`, `mmBIF_FB_EN`, transaction-pending registers, and BACO exit timing registers.
- Host interface and coherency registers: `mmHDP_REG_COHERENCY_FLUSH_CNTL`, `mmHDP_MEM_COHERENCY_FLUSH_CNTL`, `mmGPU_HDP_FLUSH_REQ`, `mmGPU_HDP_FLUSH_DONE`, `mmREMAP_HDP_*`, and `mmBIF_TRANS_PENDING`.
- Virtualization and mailbox registers: SR-IOV `cfgPCIE_SRIOV_*`, GPUIOV vendor-specific config registers, `mmMAILBOX_*`, `mmBIF_VMHV_MAILBOX`, `mmBIF_*_GPUIOV_CFG_SIZE`, and PF/VF FLR reset/status registers.
- Strap and reset spaces at base `0x10100000`: `mmRCCSTRAPRCCSTRAP_*`, `mmRCC_DEV*_EPF*_STRAP*`, `ixHARD_RST_CTRL`, `ixBIF_PF_FLR_RST`, `ixBIF_PF0_VF_FLR_RST`, and D-state reset controls.
- RAS and miscellaneous NBIF controls: `ixBIF_RAS_*`, `ixGDC_RAS_*`, `ixNBIF_MGCG_CTRL`, `ixNBIF_DS_CTRL_LCLK`, `ixBIFC_*`, `ixSMN_MST_*`, and `ixNBIF_VWIRE_CTRL`.
- MSI-X backing tables: `ixPCIEMSIX_VECT0_*` through `ixPCIEMSIX_VECT31_*` plus `ixPCIEMSIX_PBA`; a smaller GFXMSIX set is also exposed through `mmGFXMSIX_*`.
- Indirect SYSHUB windows: `mmSYSHUB_INDEX`, `mmSYSHUB_DATA`, and duplicated `ixSYSHUBMMREGIND_*` offsets for indirect access.

Several constants are deliberately marked `// duplicate`, and some distinct names share the same offset. This mirrors overlapping hardware views, packed PCI capability fields, and aliases across generated address blocks. The file also guards `mmRCC_IOV_FUNC_IDENTIFIER` with `#ifndef`, indicating that this symbol can be supplied by another included header in some build combinations.

## Control Flow

There is no runtime control flow in this header. Compile-time control flow is limited to the include guard and the conditional definition of `mmRCC_IOV_FUNC_IDENTIFIER`. At runtime, control flow is created by consumers that pass these constants into register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and command-table entries.

Observed integration examples in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/uvd_v7_0.c` directly includes `nbif/nbif_6_1_offset.h` alongside UVD, VCE, MMHUB, and IRQ headers, making NBIF offsets available while configuring UVD 7.0 paths on NBIF 6.1-era ASICs.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` uses the same register-name conventions for SYSHUB indirect access by writing `mmSYSHUB_INDEX` and reading/writing `mmSYSHUB_DATA`.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.c` uses NBIF register constants such as `mmBIF_DOORBELL_CNTL`, `mmBIF_FB_EN`, `mmBACO_CNTL`, and their `_BASE_IDX` values in BACO power-state command tables.

The typical flow is: a hardware-management path selects an ASIC/IP block instance, chooses a generated register macro from this header, combines it with the matching base index, and lets the SOC15 or PCIE helper resolve the final MMIO/SMN/config-space access.

## State And Persistence Behavior

The header itself has no state and performs no persistence. The constants identify hardware state owned by the GPU and platform firmware. Writes through consumers can persist for the current boot, power state, PCI function lifetime, or reset domain depending on the target register:

- Scratch, mailbox, and GPUIOV registers hold driver/firmware/hypervisor communication state.
- PCI config, strap, and capability offsets describe device enumeration, BARs, interrupt capabilities, SR-IOV layout, and link behavior.
- Doorbell, HDP flush, transaction-pending, and ring-buffer related registers affect live command submission and host/GPU coherency.
- BACO, D-state, FLR, hard reset, and soft reset registers affect power and reset transitions.
- RAS registers expose or control error-reporting behavior.

Because many registers are stateful hardware controls, incorrect numeric offsets can cause silent misconfiguration, hangs, failed resume, broken interrupts, or device reset failures even though this header compiles successfully.

## Dependencies

This header has no includes and depends only on the C preprocessor. Its practical dependencies are architectural:

- The AMDGPU SOC15 register-access layer, which interprets `mm...` constants and `_BASE_IDX` selectors.
- Companion shift/mask headers such as `nbif_6_1_sh_mask.h`, which provide bitfield masks for the offsets defined here.
- ASIC include aggregators such as `vega12_inc.h` and direct consumers such as `uvd_v7_0.c`.
- Kernel PCIe, SR-IOV, MSI/MSI-X, interrupt, reset, and power-management code that relies on AMDGPU programming these hardware registers correctly.

The numeric spaces are not uniform. Some blocks use base address `0x0`, some use `0x1400000`, strap/reset/misc/RAS blocks use `0x10100000`, and MSI-X spaces use `0x10170000` and `0x10171000`. Consumers must use the correct access path for the prefix and base index; treating an `ix...` indirect offset as a direct `mm...` register, or using an NBIO header with a different base-index convention, can target the wrong hardware address.

## Integration Points

The file integrates with AMDGPU as a hardware ABI surface:

- UVD and multimedia initialization includes it so UVD 7.0 code can reference NBIF 6.1 registers for platform-level doorbells, interrupts, virtualization, and host interface behavior.
- Power-management BACO tables consume NBIF offsets and bit masks to enter and leave bus-active/chip-off states.
- NBIO and SOC15 helpers consume the same generated names and base-index model for direct and indirect register access.
- SR-IOV/GPUIOV support depends on the PCIe capability and mailbox offsets for PF/VF enumeration, reset notification, VF framebuffer layout, and hypervisor/VM communication.
- RAS and reset paths depend on the BIF/GDC RAS and FLR/reset constants for fault handling and recovery.

The header is source-tree-aligned with sibling generated files under `include/asic_reg/nbif/`, especially `nbif_6_1_sh_mask.h`. The offset header supplies addresses; the shift/mask header supplies bit definitions for fields at those addresses.

## Risks And Maintenance Notes

- Generated duplicate names and aliasing are intentional. Deduplicating or renaming by hand can break callers that rely on a specific generated symbol or on PCI capability aliases sharing an offset.
- Offsets differ between related IP families. For example, similarly named NBIO 6.1 constants exist under `include/asic_reg/nbio/`, but their base indices and offsets are not necessarily interchangeable with this NBIF 6.1 header.
- `_BASE_IDX` values are part of the access contract. A correct register number with a wrong base index can resolve to the wrong MMIO aperture.
- Conditional `mmRCC_IOV_FUNC_IDENTIFIER` suggests include-order sensitivity with other generated headers. Removing the guard may introduce macro redefinition warnings or build breaks.
- PCIe/SR-IOV/MSI-X constants are externally visible hardware contracts. Incorrect changes may only fail on machines with specific firmware, virtualization, interrupt, or power-state configurations.
- Reset, BACO, and D-state registers are high-risk because wrong writes can make the GPU disappear from the bus, fail resume, or wedge command submission.
- The file lacks semantic validation in normal compilation because macros are untyped integers. Many offset mistakes compile cleanly and require hardware testing to expose.

## Test Signals

Useful validation signals for this header are mostly integration and hardware oriented:

- Build coverage for AMDGPU targets that include `uvd_v7_0.c`, NBIF/NBIO support, and Vega-era power-management code.
- Compile checks with `nbif_6_1_offset.h` and `nbif_6_1_sh_mask.h` included together to catch missing or conflicting macros.
- Boot and probe logs showing successful AMDGPU initialization on NBIF 6.1 hardware without MMIO access faults or PCI configuration errors.
- UVD/VCE encode/decode smoke tests, because UVD 7.0 includes this header directly.
- Doorbell and interrupt tests, including IH doorbell routing and MSI/MSI-X interrupt delivery.
- BACO suspend/resume or runtime power-management tests on Vega-era hardware, watching for failed BACO entry/exit or broken bus mastering after resume.
- SR-IOV/GPUIOV tests when available: PF/VF creation, FLR, mailbox exchange, VF framebuffer sizing, and reset notification.
- RAS/reset tests that verify BIF/GDC error status paths and FLR/D3HOT-D0 transitions do not regress.
- Static review comparing generated offsets against the vendor register database or known-good upstream generated headers; this is the strongest signal for a macro-only hardware ABI file.
