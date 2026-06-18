# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 11691-14586

## Scope

This chunk is a generated AMDGPU NBIO 7.0 register-default header slice. It contains C preprocessor constants only: `#define` names ending in `_DEFAULT` mapped to reset/default register values. There are no functions, structs, enums, branches, allocation sites, or runtime side effects in the covered lines.

The requested range begins inside the tail of the `BIFPLR3_2` PCIe root-port config-space defaults, then covers complete `BIFPLR4_2`, `BIFPLR5_2`, and `BIFPLR6_2` root-port config blocks. It continues through NBIF PCIe dummy/config blocks for RC and endpoint functions, then into NBIF/BIF MMIO defaults for system indexed access, RCC strap/endpoint/downstream registers, BIF PF virtualization/doorbell/power/reset registers, and GDC doorbell/SDP controls. The range ends in a repeated `mm`-prefixed `nbio_nbif0_rcc_ep_dev0_BIFDEC1` block.

The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`. Companion headers in the same directory provide register offsets/SMN addresses and bit masks (`nbio_7_0_offset.h`, `nbio_7_0_smn.h`, `nbio_7_0_sh_mask.h`); this file supplies the reset/default values used by ASIC-specific code and generated register knowledge.

## Purpose

The chunk documents default values for NBIO 7.0 PCIe/NBIF hardware blocks. These defaults define the expected initial programming for PCIe configuration-space capabilities and NBIF control registers before the driver applies runtime policy. The values are useful for reset programming, comparing observed hardware state against generated ASIC data, initializing saved register images, and avoiding magic constants in AMDGPU ASIC code.

Major responsibilities represented here:

- PCIe root-port config-space templates for `BIFPLR3_2` through `BIFPLR6_2`.
- Root-complex config templates for `BIF_CFG_DEV0_RC2` and `BIF_CFG_DEV1_RC2`.
- Endpoint-function config templates for `DEV0_EPF0_3`, `DEV0_EPF1_2`, `DEV0_EPF2_2` through `DEV0_EPF7_2`, and `DEV1_EPF0_2` through `DEV1_EPF2_2`.
- PCIe capability chain defaults: standard PCIe capability, MSI, SSID, vendor-specific enhanced capability, VC, device serial number, AER, secondary PCIe, ACS, multicast, BAR, power budget, DPA, ATS, PRI/page request, PASID, TPH requester, LTR, ARI, and SR-IOV-related defaults where present.
- NBIF/BIF control defaults for indexed MMIO, BIOS scratch registers, strap revision ID, endpoint LTR/DPA controls, downstream port controls, reset/interrupt/pad controls, BACO timers, VDDGFX aperture windows, doorbell apertures, HDP flush remaps, GPU IOV configuration sizes, mailbox registers, and GDC doorbell/SDP controls.

## Important Definitions

The generated names encode the access window, instance, register, and default value:

- `smnBIFPLR*_2_*_DEFAULT` names are SMN-accessible PCIe root-port defaults. The chunk starts with the remainder of `smnBIFPLR3_2` and fully covers `smnBIFPLR4_2`, `smnBIFPLR5_2`, and `smnBIFPLR6_2`.
- `smnBIF_CFG_DEV*_RC2_*_DEFAULT` names describe NBIF root-complex PCIe config defaults.
- `smnBIF_CFG_DEV*_EPF*_2_*_DEFAULT` and `smnBIF_CFG_DEV0_EPF0_3_*_DEFAULT` describe endpoint-function config-space defaults.
- `smnRCC_*` names describe root-complex controller strap, endpoint, downstream, and downstream-port defaults.
- `smnBIF_BX_PF1_*` names describe BIF PF1 MMIO/control defaults, including reset, interrupts, doorbells, BACO, VDDGFX apertures, HDP flush controls, ring buffer/mailbox state, and GPU IOV sizing.
- `smnGDC1_*` names describe GDC1 SDP, SHUB, doorbell-range, ATDMA, fence, S2A, and power-gating defaults.
- `mm*` names at the end mirror indexed/MMIO register defaults for system, syshub, strap, and endpoint blocks.

Notable non-zero defaults and patterns:

- Root-port `BIFPLR*_2` blocks use common PCIe defaults: `INTERRUPT_LINE_DEFAULT` is `0xff`, `PCIE_CAP_LIST_DEFAULT` is `0x0000a000`, `PCIE_CAP_DEFAULT` is `0x00000002`, `DEVICE_CNTL_DEFAULT` is `0x00002810`, `LINK_CAP_DEFAULT` is `0x00011c03`, `LINK_STATUS_DEFAULT` is `0x00000001`, `LINK_CAP2_DEFAULT` is `0x0000000e`, and `LINK_CNTL2_DEFAULT` is `0x00000003`.
- Root-complex `BIF_CFG_DEV*_RC2` blocks differ from endpoint/root-port templates by setting `INTERRUPT_PIN_DEFAULT` to `1`, `PCIE_CAP_DEFAULT` to `0x42`, `LINK_STATUS_DEFAULT` to `0x2001`, and lane equalization defaults to `0x00007f0f`.
- Endpoint function blocks use `PCIE_CAP_DEFAULT` `0x2`, `DEVICE_CAP_DEFAULT` `0x10000000`, `DEVICE_CNTL_DEFAULT` `0x2810`, `LINK_CAP_DEFAULT` `0x11c03`, `LINK_STATUS_DEFAULT` `1`, MSI message control `0x80`, and AER severity/masks. Full EPF0/EPF1-style functions include VC, serial number, secondary PCIe, lane equalization, ACS/ATS/PRI/PASID/TPH/MC/LTR/ARI, and SR-IOV page-size defaults; smaller EPF2-EPF7-style blocks include `FLADJ_DEFAULT` `0x20`, BAR, power-budget, DPA, ACS, and ARI defaults.
- DPA-related defaults appear in endpoint config and endpoint RCC/MMIO blocks: `PCIE_DPA_STATUS_DEFAULT` `0x100`, `EP_PCIE_F0_DPA_CAP_DEFAULT` `0x190a1000`, latency indicator `0xf0`, control `0x100`, and substate power allocations descending from `0xfa` to `0x0a`.
- Strap defaults include `RCC_DEV0_EPF0_STRAP0_DEFAULT`/`RCC_STRAP2_RCC_DEV0_EPF0_STRAP0_DEFAULT` at `0x300015dd`, the register used by NBIO code to derive the device revision ID through the corresponding mask/shift header.
- BIF PF1 has hardware-control defaults such as `BX_RESET_EN_DEFAULT` `0x00010003`, `BIF_BUSY_DELAY_CNTR_DEFAULT` `0x3f`, BACO exit timers `0x100` through `0x500`, VDDGFX aperture lower/upper pairs, doorbell global aperture lower/upper pairs, HDP flush remaps `0x385c`/`0x3858`, GPU IOV config sizes `8`, pad controls, and `DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT` `0x100`.
- GDC1 non-zero defaults include `NGDC_SDP_PORT_CTRL_DEFAULT` and `NGDC_SDP_PORT_CTRL_SOCCLK_DEFAULT` at `0xf`, plus `ATDMA_MISC_CNTL_DEFAULT` `0x04040001`.

## Control Flow

There is no direct control flow in this header. Runtime control flow belongs to AMDGPU NBIO and PCIe code that includes this generated data:

1. ASIC-specific code includes the default, offset, SMN, and mask headers for NBIO 7.0.
2. Driver paths read or write NBIO registers through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`.
3. Field helpers and mask constants from `nbio_7_0_sh_mask.h` interpret values whose defaults are defined here.
4. Reset, initialization, suspend/resume, BACO, PCIe link-management, virtualization, and diagnostics paths compare against or program hardware using the generated constants.

Concrete integration observed nearby: `nbio_v7_0.c` includes this header and reads `mmRCC_DEV0_EPF0_STRAP0` to derive `STRAP_ATI_REV_ID_DEV0_F0`. Related NBIO versions use endpoint LTR control (`EP_PCIE_TX_LTR_CNTL`) to adjust LTR behavior and use the same register-access helper families. This chunk therefore participates in the data side of those flows even though it does not execute code itself.

## State And Persistence

The macros are compile-time constants and do not store state. The state they describe lives in hardware registers and PCIe configuration-space images:

- PCIe capability state: link capability/status, link-control target speed, MSI/SSID capability-list placement, AER masks/severity/log registers, VC resources, ACS/ATS/PASID/PRI/TPH/LTR/ARI/MC/secondary capability metadata, and DPA power-allocation state.
- Endpoint and root-complex state: command/status, BAR controls, bus/window registers, interrupt line/pin, link training status, and error reporting defaults.
- NBIF MMIO state: indexed access registers, BIOS scratch registers, interrupt controls, CAM remap defaults, syshub access windows, endpoint LTR/DPA controls, downstream controls, reset enables, BACO timers, VDDGFX/doorbell apertures, HDP flush remap addresses, mailbox buffers, ring-buffer pointers, and GDC doorbell/ATDMA controls.

Persistence across GPU reset, runtime suspend, BACO, hot reset, and system sleep depends on the hardware power domain and the AMDGPU reset/resume sequence that reprograms or restores registers. This header has no persistence mechanism; it supplies the expected reset/reference values used by code that manages persistence.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and include ordering. Functional dependencies include:

- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` for the actual register addresses corresponding to these defaults.
- `nbio_7_0_sh_mask.h` for masks/shifts used to interpret or modify fields in registers with these defaults.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, which includes this header and uses NBIO register definitions in ASIC-specific callbacks.
- Common AMDGPU register helpers (`RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`) and field macros (`REG_GET_FIELD`, `REG_SET_FIELD` style patterns).
- PCIe, AER, ASPM, DPA/LTR, GPU reset, BACO, virtualization/IOV, doorbell, HDP flush, and SMU/PM integration paths that rely on NBIF/NBIO state being correctly described.

The document should be merged later with adjacent chunks of the same source file. This range starts mid-block (`BIFPLR3_2`) and repeats some `mm` address blocks after SMN-prefixed equivalents, so the final per-file research should reconcile duplicate address-block names and line-boundary splits rather than treating this chunk as a complete standalone register map.

## Risks

- Generated default drift can be hard to detect. A single incorrect default in PCIe link, AER, LTR, DPA, BACO, or doorbell programming can produce link-training failures, power-management regressions, lost interrupts, or inaccessible MMIO/doorbell ranges.
- Repeated templates invite inconsistent edits. `BIFPLR4_2`, `BIFPLR5_2`, and `BIFPLR6_2` are structurally aligned; root-complex and endpoint-function families also repeat. Any intentional exception should be traceable to the ASIC register specification.
- Capability-list default values encode PCIe config-space layout. Incorrect next-capability pointers or enhanced-capability headers can confuse config-space traversal, AER setup, SR-IOV/ARI handling, or OS PCI core behavior.
- Error mask/severity defaults are security and reliability sensitive. AER masks such as uncorrectable/correctable masks and severity values determine which errors are reported, suppressed, or treated as fatal.
- Doorbell and VDDGFX aperture defaults are address-window data. Incorrect lower/upper bounds can misroute doorbells, expose unintended ranges, or break GPU/CPU synchronization.
- Reset, BACO, and pad-control defaults are platform-sensitive. Incorrect values can leave hardware stuck across reset, break wake/link behavior, or require a full power cycle.
- Manual edits to generated headers are high risk. These files should normally be regenerated from the authoritative register database and reviewed with generated diff tooling rather than changed by hand.

## Test Signals

Useful validation signals for changes touching this chunk:

- Build AMDGPU with NBIO 7.0 support enabled to catch missing or renamed macros and include-order problems.
- Compare this header against the authoritative AMD register database or regeneration output for NBIO 7.0.
- Run static symmetry checks across repeated root-port and endpoint-function blocks: identical blocks should keep matching defaults except where the ASIC spec intentionally differs.
- Boot NBIO 7.0 hardware and verify AMDGPU probe, PCIe config-space enumeration, BAR setup, AER capability reporting, and link speed/width reporting.
- Exercise suspend/resume, GPU reset, BACO entry/exit, hot reset if supported, and PCIe link retraining; watch for AMDGPU timeout/reset messages and PCIe AER logs.
- Validate LTR/DPA behavior with runtime power management enabled, especially around `EP_PCIE_TX_LTR_CNTL` and DPA substate power-allocation defaults.
- Validate doorbell/HDP paths under graphics, SDMA, UVD/VCE or video, and KFD workloads; failures here may show as queue stalls, missing interrupts, or cache/coherency flush timeouts.
- For virtualization or SR-IOV/GPU IOV configurations, verify mailbox, GPUIOV config-size, ARI/SR-IOV-related defaults, and BIF PF/VF transaction-pending registers behave as expected.
