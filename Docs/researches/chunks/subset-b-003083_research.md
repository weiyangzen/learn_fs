# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 36635-39058

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It spans 2,424 source lines and contains 2,150 `#define` lines: 1,075 `__SHIFT` constants and 1,075 `_MASK` constants across 245 register names. There are no C functions, structs, enums, global variables, allocation sites, locks, or executable statements in this range.

The range starts mid-register in `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL`: line 36634, immediately before this chunk, defines `SNOOP_LATENCY_VALUE__SHIFT`, while this chunk starts at `SNOOP_LATENCY_SCALE__SHIFT` and includes the remaining shifts and all masks for that register. It then covers the rest of the USB3_0 RCC PFC restore/auxiliary-power fields, complete RCC PFC blocks for USB3_1, ACP, AZ, MP2, SATA, GBE0, and GBE1, the NBIF0 BIF reset register block, the NBIF0 BIF RAS register block, and the beginning of the `BIF_CFG_DEV0_EPF0_2` PCI/PCIe endpoint configuration-space field layout through `PCIE_BAR2_CNTL`. The next chunk is needed for `PCIE_BAR3_*` and later endpoint capability definitions.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 hardware register contract. Each field is represented by a pair of preprocessor constants:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`, the mask that isolates or preserves that field in the containing register.

Runtime code combines these definitions with companion generated address/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and related SOC15/NBIO accessors. This header does not decide when hardware is touched. It gives NBIO v7.0 driver code the named bit positions for PCIe-facing power management, reset, RAS/error handling, interrupt status/masking, function-level reset, D-state tracking, MSI/MSI-X, AER, virtual-channel, BAR, and endpoint configuration fields.

Although this repository path sits under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The RCC PFC blocks describe per-client PCIe/Root Complex Configuration power-management and restore fields:

- `RCC_PFC_USB3_0_*` starts in the previous line and continues here with LTR scale/requirement fields, PME restore, sticky PCIe error restore, captured TLP header/prefix restore, and auxiliary-power override fields.
- `RCC_PFC_USB3_1_*`, `RCC_PFC_ACP_*`, `RCC_PFC_AZ_*`, `RCC_PFC_MP2_*`, `RCC_PFC_SATA_*`, `RCC_PFC_GBE0_*`, and `RCC_PFC_GBE1_*` repeat the same register pattern for additional clients.
- `RCC_PFC_*_RCC_PFC_LTR_CNTL` defines snoop and non-snoop latency value, scale, and requirement bits. These fields model PCIe Latency Tolerance Reporting programming for the client.
- `RCC_PFC_*_RCC_PFC_PME_RESTORE` preserves PME enable/status state across the relevant power/reset event.
- `RCC_PFC_*_RCC_PFC_STICKY_RESTORE_0` through `_5` expose sticky AER-style error status and captured TLP header/prefix restore fields, including poisoned TLP, completion timeout/abort, unexpected completion, malformed TLP, ECRC, unsupported request, and advisory non-fatal status.
- `RCC_PFC_*_RCC_PFC_AUXPWR_CNTL` exposes auxiliary-current and auxiliary-power-detected override fields.

The BIF reset block defines NBIO reset policy, reset causes, reset interrupt state, and per-function reset/D-state fields:

- `HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, and `SELF_SOFT_RST` define reset-enable masks for dispatch/config, endpoint config/private state, shadow/sticky state, strap reload, and core reset domains. `SELF_SOFT_RST` also exposes self reset trigger and grant/request style fields.
- `BIF_GFX_DRV_VPU_RST` names VPU/GFX driver reset handshake bits, including reset request, interrupt, timeout, and related mask/status controls.
- `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3` define miscellaneous reset behavior such as reset selection, clock-domain handling, FLR/D-state behavior, and debug/status controls.
- `DEV0_PF0_FLR_RST_CTRL` through `DEV0_PF7_FLR_RST_CTRL` and `DEV1_PF0_FLR_RST_CTRL` through `DEV1_PF7_FLR_RST_CTRL` describe function-level reset controls and status for two devices and up to eight physical functions each. PF0 on device 0 has the widest field set; the other PFs follow the compact completion/ack/reset-status pattern.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` define reset, FLR, D3hot-to-D0, power, and D-state interrupt status fields. Matching `_MASK` registers define the corresponding interrupt masks.
- `BIF_PF_FLR_RST` supplies PF reset command/status bits.
- `BIF_DEV0_PF*_DSTATE_VALUE`, `BIF_DEV1_PF*_DSTATE_VALUE`, `BIF_PORT0_DSTATE_VALUE`, and `BIF_PORT1_DSTATE_VALUE` expose saved or observed power-state values.
- `DEV0_PF*_D3HOTD0_RST_CTRL` and `DEV1_PF*_D3HOTD0_RST_CTRL` control reset behavior around D3hot-to-D0 transitions.

The BIF RAS block defines register fields for Reliability, Availability, and Serviceability handling:

- `BIF_RAS_LEAF0_CTRL`, `BIF_RAS_LEAF1_CTRL`, and `BIF_RAS_LEAF2_CTRL` name per-leaf RAS enable, status, inject, and mask-style fields for BIF error reporting paths.
- `BIF_RAS_MISC_CTRL`, `BIF_IOHUB_RAS_IH_CNTL`, and `BIF_RAS_VWR_FROM_IOHUB` add miscellaneous BIF RAS controls and IOHUB interrupt/vector-window integration fields.

The `BIF_CFG_DEV0_EPF0_2_*` block mirrors a PCI/PCIe endpoint configuration space and extended capability layout:

- Basic PCI configuration fields include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, min-grant/max-latency, and vendor/adapter ID write paths.
- Power-management capability fields include `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` for capability ID/version/next pointer, D-state support, PME support, current power state, PME enable/status, data select, and bridge-extension status.
- PCIe capability fields include `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and the slot-capability placeholders. These fields model maximum payload/read request size, relaxed ordering, no-snoop, FLR initiation, link speed/width, ASPM/L0s/L1 controls, link retraining, clock power management, completion timeout controls, atomic operation support, OBFF, LTR, emergency power reduction, and related PCIe status bits.
- MSI/MSI-X fields include `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data/mask/pending registers for 32-bit and 64-bit variants, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific and virtual-channel capability fields include `PCIE_VENDOR_SPECIFIC_*`, `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status fields, and VC0/VC1 resource capability/control/status fields.
- Device serial number fields include `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `DW2`.
- Advanced Error Reporting fields include `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs `PCIE_HDR_LOG0` through `_3`, and TLP prefix logs `PCIE_TLP_PREFIX_LOG0` through `_3`.
- The chunk ends with the enhanced BAR capability header plus `PCIE_BAR1_CAP`, `PCIE_BAR1_CNTL`, `PCIE_BAR2_CAP`, and `PCIE_BAR2_CNTL`. BAR3 and later BAR/power-budget capability fields continue after this range.

## APIs, Types, And Functions

There are no local callable APIs or type declarations in this chunk. The interface is the generated macro namespace. Consumers rely on exact symbol names, shifts, and masks being synchronized with the corresponding NBIO v7.0 offset/default headers and with the underlying hardware register database.

The constants are untyped preprocessor integer literals. Many masks use an `L` suffix and may represent 16-bit PCI configuration fields or 32-bit NBIO registers depending on the containing register. The macros encode field placement only. They do not encode access width, read/write permissions, reset domain, required ordering, delays, polling semantics, clear-on-write behavior, firmware ownership, or whether a bit is command, live status, latched status, sticky status, or reserved. Those properties must come from the hardware specification and from the AMDGPU call site using the fields.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU NBIO, SOC15, PCIe, power-management, reset, or virtualization code selects a register address from generated offset/SMN headers.
2. The code reads a register and decodes fields with these shifts and masks, or composes a new value with register-field helpers.
3. The resulting value is written back to hardware, used to poll status, used to preserve/restore state, or used to report PCIe/RAS/reset information upward.

Likely runtime flows involving this chunk include LTR programming for on-chip PCIe clients, PME and sticky-error restore across power events, FLR and D3hot-to-D0 reset sequencing, GPU/NBIO hard and soft reset paths, reset interrupt masking and acknowledgement, per-PF D-state tracking, BIF RAS enable/status/masking, PCI configuration setup, PCIe link capability/control handling, MSI/MSI-X setup, AER status collection and masking, virtual-channel configuration, device serial number exposure, and BAR capability sizing/control.

## State And Persistence Behavior

The header stores no software state. It names hardware-visible state in NBIO v7.0 RCC PFC, BIF reset, BIF RAS, and endpoint configuration registers. Persistence is determined by PCIe reset type, NBIO reset domains, BIOS/firmware initialization, runtime power management, suspend/resume restore flows, SR-IOV PF/VF ownership, and explicit driver writes.

Represented persistent or semi-persistent state includes LTR values, PME enable/status restore state, sticky AER restore bits, captured TLP header/prefix logs, auxiliary power override state, reset-enable policy, FLR/D3hot-to-D0 control, interrupt mask settings, PF D-state values, RAS enable/mask/inject/status bits, PCI command/status fields, BAR controls, MSI/MSI-X table and masking controls, PCIe device/link capability/control fields, AER error masks/severity, and AER header/TLP-prefix logs.

Several fields are not passive storage. Reset request/enable bits, `INITIATE_FLR`, D3hot-to-D0 reset controls, RAS injection bits, PME status, interrupt status bits, AER status bits, and MSI/MSI-X mask/pending controls can have side effects or hardware-defined clear semantics. Full-register writes are risky unless the caller intentionally owns every bit in the target register; read-modify-write with the generated masks is normally the safer pattern for mixed control/status/reserved registers.

## Dependencies And Integration Points

This chunk depends on the generated NBIO v7.0 register database and must stay aligned with companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` for matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h` for SMN-addressed register names where applicable.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` for reset/default values.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Those users pull this generated mask namespace into NBIO v7.0 initialization, SOC15 device handling, and SMU10 power-management register programming. The endpoint configuration symbols also integrate with generic PCIe concepts: command/status setup, link configuration, power management, MSI/MSI-X, AER, virtual channels, serial-number capability, and BAR sizing/control.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing driver code to set or decode the wrong hardware bit. The highest-impact fields here are reset controls, FLR/D3hot-to-D0 paths, PCIe command/device/link controls, MSI/MSI-X mask and pending fields, and AER status/mask/severity fields.
- The source range starts mid-register. A reader needs the previous line for the complete `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` shift set.
- The range ends before BAR3 and later endpoint capability fields. A merged per-file document should treat this as the first half of the `BIF_CFG_DEV0_EPF0_2` extended capability layout, not the whole endpoint config block.
- RCC PFC blocks are intentionally repetitive across USB3, ACP, AZ, MP2, SATA, and GBE clients. A mismatched field width or mask pattern could be a real per-client hardware difference, but it is also a strong signal to verify generator output.
- Reset registers mix command, enable, status, sticky, and interrupt fields. Incorrect writes can leave a PF stuck in reset, miss FLR completion, clear a diagnostic status too early, or trigger an unintended NBIO/core reset.
- PCIe capability/control fields include negotiated link width/speed, ASPM, clock power management, completion timeout, atomic operations, LTR, OBFF, and FLR initiation. Bad programming can show up as link training failures, AER storms, failed resume, performance loss, or device disappearance.
- AER and sticky-restore fields represent latched error state and captured TLP/header context. Wrong masks can hide real PCIe faults or produce misleading error reports.
- MSI/MSI-X mask/pending fields are interrupt-critical. Incorrect bit positions can cause lost interrupts, interrupt storms, or incorrect interrupt affinity/debugging conclusions.
- RAS injection and status fields should be treated as lab or controlled-validation surfaces unless the caller is explicitly handling BIF RAS test flows.
- Reserved or undocumented bits are not modeled by separate macros. Callers should preserve them unless a hardware sequence explicitly requires a literal write.

## Test Signals

- Build AMDGPU with NBIO v7.0/SOC15 and SMU10 support enabled. Direct include users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO v7.0 register database: register-name alignment across offset/default/shift/mask headers, mask-width checks, non-overlap checks within each register, and repeated-client consistency checks for RCC PFC blocks.
- Verify chunk boundaries during merge: `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` should include the missing first shift from the previous line, and `BIF_CFG_DEV0_EPF0_2_PCIE_BAR3_*` should continue immediately after this chunk.
- On NBIO v7.0 hardware, boot and suspend/resume tests should show stable PCIe enumeration, expected BAR sizing, expected MSI/MSI-X behavior, no unexpected AER storms, and stable negotiated link width/speed.
- Exercise FLR, GPU reset, D3hot-to-D0, runtime suspend, and system suspend flows while checking that reset interrupts are delivered/masked/cleared as expected and PF D-state values are sane.
- Validate PCIe power-management paths that use LTR, ASPM, clock power management, PME, and auxiliary-power fields.
- RAS validation should cover BIF RAS enable/mask/status paths and controlled injection where supported, with expected interrupt routing through IOHUB handling.
- PCIe error tests should verify uncorrectable/correctable AER status, mask, severity, header log, and TLP prefix log decoding against known error injections or platform traces.
