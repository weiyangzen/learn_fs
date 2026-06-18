# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 145970-148448

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in PCIe configuration-space registers under NBIO address blocks for `BIF_CFG_DEV1_EPF0_1`, `BIF_CFG_DEV1_EPF1_1`, and the start of `BIF_CFG_DEV2_EPF0_1`.

The file is not executable code. Its purpose is to provide the field-layout contract used by AMDGPU register access code when it decodes or composes PCI/PCIe configuration values. Register addresses and base indices are supplied by the paired `nbio_7_2_0_offset.h`; this header supplies the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants that consumers combine with raw config/MMIO reads and writes.

## Major Register Groups

The chunk opens in the tail of `BIF_CFG_DEV1_EPF0_1`, completing TPH Steering Tag table entries 39-63. Each table register has `TPH_ST_LOWER_ENTRY` at shift 0 and `TPH_ST_UPPER_ENTRY` at shift 8, with byte masks `0x00FFL` and `0xFF00L`.

It then defines `BIF_CFG_DEV1_EPF0_1` extended capability fields for Data Link Feature, 16 GT/s PHY, link equalization, parity mismatch status, 16 per-lane equalization-control registers, PCIe lane margining capability/status, and 16 per-lane margining control/status register pairs. These fields describe local/remote DLF support, link equalization completion and phase success, retimer parity mismatch status, downstream/upstream 16 GT/s transmit presets per lane, margining readiness, receiver number, margin type, usage model, and margin payload.

At line 146528 the address block changes to `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`. The `BIF_CFG_DEV1_EPF1_1` block covers a full PCI endpoint-function configuration image:

- Conventional PCI header fields: vendor/device IDs, command/status, revision/class codes, cache line, latency, header type, BIST, BARs, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- Vendor and power-management capability fields: vendor capability ID/next/length, PMI capability, power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PMI data.
- PCIe capability fields: PCIe capability metadata, device capability/control/status, link capability/control/status, device/link capability 2 and control/status 2, including payload sizing, read-request sizing, relaxed ordering, no-snoop, FLR, completion timeout, ARI forwarding, atomic operations, LTR, TPH completer support, target link speed, compliance controls, and 8 GT/s equalization status.
- MSI and MSI-X capability fields: enable bits, multi-message capability/enable, 64-bit MSI support, per-vector masking, extended message data, message address/data, mask/pending registers, MSI-X table/PBA BIR and offsets, function mask, and enable.
- Vendor-specific, AER, BAR, ACS, PASID, ARI, and TPH requester enhanced capability fields. The AER fields include uncorrectable status/mask/severity, correctable status/mask, capability/control, header logs, and TLP prefix logs. ACS exposes source validation, translation blocking, P2P redirect, upstream forwarding, egress control, and direct-translated P2P bits. PASID exposes support, max PASID width, and enable controls. ARI exposes function-group support/enables and next-function metadata.
- A complete `BIF_CFG_DEV1_EPF1_1_PCIE_TPH_ST_TABLE_0` through `_63` set, again using lower and upper 8-bit steering-tag entries per register.

Near line 147852 the chunk enters `BIF_CFG_DEV2_EPF0_1`, starting another endpoint-function configuration image. This range covers conventional PCI header fields, vendor/PMI/PCIe capabilities, device/link/device2/link2 fields, MSI/MSI-X, vendor-specific capability fields, and the beginning of Virtual Channel capability/resource definitions through the first fields of `PCIE_VC1_RESOURCE_CAP`.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The public surface consists entirely of preprocessor macros following two generated naming forms:

- `REGISTER__FIELD__SHIFT`: zero-based field bit offset.
- `REGISTER__FIELD_MASK`: register-width mask with the field bits set.

Consumers normally use these constants through direct bit operations or AMD register helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, after selecting the matching address macro from `nbio_7_2_0_offset.h`.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by consumers that:

1. Select the NBIO 7.2.0 register set for the detected ASIC.
2. Read a PCIe/NBIO config register using the paired offset/base-index definitions.
3. Decode fields with these masks and shifts.
4. For writable fields, preserve unrelated and reserved bits, insert shifted field values, and write the register back through AMDGPU register or PCI config access paths.

The fields in this chunk influence several hardware flows in consumers: PCI command enablement, link training/retraining, equalization status checks, lane margining requests, MSI/MSI-X programming, AER error reporting, ACS isolation, PASID enablement, ARI forwarding, TPH steering-tag configuration, and Virtual Channel arbitration/resource negotiation.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware register layouts.

The state described by these macros lives in NBIO/PCIe configuration registers. Some fields are static or firmware-programmed capability state, such as capability IDs, capability versions, next pointers, supported link speed/width, FLR support, MSI/MSI-X capabilities, PASID width, ACS support, TPH table size/location, and VC resource capabilities. Other fields are live or sticky status, including PCI status errors, device status errors, link training/equalization status, DLF remote support validity, margining readiness/status payloads, AER error bits, AER header/prefix logs, MSI pending bits, and VC negotiation/arbitration status.

Writable controls, including PCI command bits, power-management state, PCIe device/link controls, completion-timeout controls, MSI/MSI-X enable/mask fields, AER masks/severity, ACS controls, PASID controls, ARI controls, TPH requester controls, TPH table entries, and VC controls persist only as hardware register contents across the relevant reset and power domains. This header does not encode reset defaults, access permissions, or write-one-to-clear behavior.

## Dependencies And Integration Points

This chunk depends on exact synchronization with `nbio_7_2_0_offset.h`. For example, `BIF_CFG_DEV1_EPF1_1_DEVICE_CNTL__MAX_PAYLOAD_SIZE_MASK` is only useful with the matching `regBIF_CFG_DEV1_EPF1_1_DEVICE_CNTL` address and base index, while `BIF_CFG_DEV2_EPF0_1_MSIX_TABLE__MSIX_TABLE_OFFSET_MASK` relies on the corresponding `DEV2_EPF0_1` offset.

Integration points include:

- AMDGPU NBIO 7.2.0 initialization and register-access paths that include the generated NBIO headers for ASIC-specific register definitions.
- PCIe configuration, reset, and diagnostics paths that inspect or program endpoint-function command/status, BAR, power-management, device control, link control, and link status fields.
- Link-training and signal-quality diagnostics that use DLF, 16 GT/s equalization, lane margining, and link status fields.
- Interrupt setup paths that program MSI/MSI-X capability, message address/data, mask, pending, table, and PBA fields.
- RAS/AER error handling that decodes correctable and uncorrectable PCIe error status, masks, severity, header logs, and TLP prefix logs.
- IOMMU/SR-IOV or isolation-adjacent paths that care about ACS, PASID, ARI, TPH, and VC capability/control fields.

The register families are highly repetitive across device/function instances. Exact symbol names are part of the integration contract: `BIF_CFG_DEV1_EPF1_1_*` and `BIF_CFG_DEV2_EPF0_1_*` often share layouts but target different endpoint-function configuration images.

## Risks

The primary risk is silent hardware misprogramming if a generated mask or shift is wrong or paired with the wrong offset symbol. A one-bit drift can enable the wrong PCI command, misreport link speed or width, mask the wrong AER error, corrupt MSI/MSI-X setup, break ACS/PASID/ARI policy, or write the wrong TPH steering-tag entry.

The repeated per-lane and per-table sections are vulnerable to localized generation mistakes. A single incorrect lane number in the 16 GT/s equalization or margining groups could show up only on wider links or on specific physical lanes. A single incorrect `PCIE_TPH_ST_TABLE_N` macro can route steering tags incorrectly while the rest of the table appears valid.

Several fields represent status registers with hardware-defined side effects. The header does not say whether status bits are read-only, sticky, write-one-to-clear, or destructive-on-read. Consumers must follow the register specification or established driver patterns before writing AER status, PCI status, device status, MSI pending, VC status, or margining status fields.

Mixed register widths are also a risk. Many PCI capability fields are 8- or 16-bit logical fields embedded in config DWORDs, while AER logs, BAR controls, TPH capability, and VC resource fields are 32-bit masks. Consumers must use appropriate access widths and preserve reserved bits on read-modify-write operations.

## Test Signals

Useful validation signals are hardware-facing and integration-oriented:

- The AMDGPU tree builds with NBIO 7.2.0 headers included, proving referenced macro names resolve.
- Cross-checks against `nbio_7_2_0_offset.h` show every covered register family has a matching offset/base-index definition for the same `DEV1_EPF0_1`, `DEV1_EPF1_1`, or `DEV2_EPF0_1` name.
- PCIe enumeration and `lspci -vv` style diagnostics on matching hardware report plausible vendor/device/class, PCIe, PM, MSI/MSI-X, AER, ACS, PASID, ARI, TPH, and VC capabilities.
- Link status and training logs show expected negotiated speed/width and no unexpected equalization, retimer, DLF, or lane-margining failures.
- MSI/MSI-X interrupt setup works without lost or misrouted interrupts, including masking and pending-bit behavior where supported.
- AER/RAS fault injection or real error logs decode the same uncorrectable/correctable status, severity, header-log, and prefix-log fields as hardware documentation.
- Suspend/resume, FLR, hot reset, and GPU reset paths restore or reinitialize writable PCIe controls, interrupt controls, AER masks, ACS/PASID/ARI state, TPH tables, and VC controls as expected.
