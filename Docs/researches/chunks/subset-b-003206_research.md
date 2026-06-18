# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 111782-114202

## Purpose

This chunk is an auto-generated AMD NBIO 7.2 shift/mask slice for PCIe configuration-space register fields under the `nbio_pcie0` BIF PLR blocks. It contains no executable driver logic. Its job is to publish stable preprocessor constants that describe how to extract or program bitfields in NBIO-backed PCI/PCIe registers.

The selected range begins at the tail of `BIFPLR1_1_PMI_STATUS_CNTL`, covers the `BIFPLR1_1` PCIe capability chain through advanced PCIe, error-reporting, link-training, margining, CCIX/ESM, and 20/25 GT lane-equalization fields, then starts the `nbio_pcie0_bifplr2_cfgdecp` address block and reaches `BIFPLR2_1_SECONDARY_STATUS`.

## Public Surface In This Chunk

The public surface is 2,162 `#define` macros in the assigned line range: 1,081 `__SHIFT` constants and 1,119 `_MASK` constants. The count is not perfectly paired because the chunk starts in the middle of a register definition and includes full-width/reserved fields plus fields whose generated names themselves contain `MASK`.

Macro names follow the generated register-field convention:

- `BIFPLR1_1_<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field in the first PLR instance.
- `BIFPLR1_1_<REGISTER>__<FIELD>_MASK` gives the pre-shifted mask used for field extraction or insertion.
- `BIFPLR2_1_<REGISTER>__<FIELD>__SHIFT` and `_MASK` do the same for the next `nbio_pcie0_bifplr2_cfgdecp` block.

There are no functions, structs, enums, storage objects, or inline helpers in this range. The API contract is the exact macro spelling and numeric value, which must match the same ASIC generation's offset header and hardware register database.

## Register Coverage

For `BIFPLR1_1`, this chunk covers the PCIe capability and related conventional PCI configuration fields:

- PM status/control tail fields for power state, PME, power management data, B2/B3 support, and bus power enable.
- PCIe capability list header and PCIe capability/device/link/slot/root capability, control, and status registers.
- PCIe capability 2 groups including completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, emergency power reduction, 10-bit tags, link speed vectors, equalization status, target link speed, compliance/SOS controls, autonomous speed disable, de-emphasis, and downstream component presence.
- MSI, SSID, MSI mapping, vendor-specific enhanced capability, virtual-channel capability/control/status, VC0/VC1 resource capability/control/status, and device serial number registers.

The same `BIFPLR1_1` block then covers reliability, isolation, and diagnostics:

- Advanced Error Reporting registers for uncorrectable error status, mask, and severity; correctable error status and mask; AER capability/control; header logs; root error command/status; error source IDs; and TLP prefix logs.
- Secondary PCIe capability, link control 3, lane error status, per-lane 8 GT equalization controls for lanes 0 through 15, ACS capability/control, and multicast capability/control/address/receive/block/overlay BAR fields.
- L1 PM substate capability/control registers and Downstream Port Containment registers, including DPC trigger reason, interrupt/message fields, RP PIO status/mask/severity/system-error/exception vectors, and RP PIO header/prefix logs.

The tail of `BIFPLR1_1` is focused on high-speed link features:

- ESM capability list, headers, status/control, and ESM capability bitmaps for many encoded data rates.
- Data Link Feature capability/status and PCIe 16 GT PHY capability, link status, local/RTM parity mismatch status, and per-lane 16 GT transmit preset fields for lanes 0 through 15.
- PCIe lane margining enhanced capability, margining port capability/status, and per-lane margining control/status for lanes 0 through 15.
- CCIX capability headers, ESM support/capability/status/control fields, ESM lane equalization controls at 20 GT and 25 GT for lanes 0 through 15, and CCIX optimized TLP format capability/control.

For `BIFPLR2_1`, the chunk begins the next PLR bridge/config decode block:

- Vendor ID, device ID, command, status, revision/class bytes, cache-line/latency/header/BIST fields.
- Bridge-style bus numbering, I/O base/limit, and secondary status fields. The following memory/prefetchable-window fields continue in the next chunk.

## Field Semantics

The macros mirror PCI and PCI Express register layouts. Command/status fields represent bus mastering, memory and I/O decode, SERR, interrupt disable, parity/abort/system-error state, and capability-chain presence. PCIe device and link fields describe payload sizing, read request sizing, relaxed ordering, no-snoop, function-level reset, link speed/width, ASPM, clocking, retrain state, link bandwidth notifications, and slot/root-port event reporting.

AER and DPC fields are policy and diagnostic fields. Their masks control which error classes are reported or suppressed, how severity is classified, which root error interrupts can fire, and where header/TLP-prefix logs and source IDs are decoded. RP PIO fields expose downstream-port containment handling for poisoned or malformed transactions.

ACS, VC, multicast, and MSI-related fields are integration-sensitive. ACS fields affect peer-to-peer forwarding, translation blocking, request/completion redirect, upstream forwarding, and egress control. VC fields describe and control virtual-channel arbitration/resource mappings. MSI/MSI-map fields describe interrupt message routing and address/data payloads.

The link-training and physical-layer groups are highly repetitive but important. The 8 GT, 16 GT, 20 GT, and 25 GT lane equalization controls expose downstream/upstream transmit preset fields per lane. The 16 GT status fields report equalization completion and phase success, while parity mismatch registers expose lane-vector diagnostics. Margining fields expose receiver number, margin type, usage model, and payload request/status per lane.

The CCIX/ESM portion describes support for extended speed mode, data-rate capability, calibration timing, quick equalization timeout selection, retimer/reach hints, current data rate, calibration completion, and optimized TLP format support. These fields should be treated as hardware protocol controls rather than generic software flags.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. AMDGPU NBIO 7.2 code includes `nbio/nbio_7_2_0_sh_mask.h` with the matching generated offset header.
2. Driver code selects a register offset such as `regBIFPLR1_1_*` or `regBIFPLR2_1_*`.
3. These `__SHIFT` and `_MASK` macros are used by register helpers or open-coded bit operations to insert, extract, compare, or preserve individual fields.
4. Actual reads and writes occur through AMDGPU MMIO/indirect register access code outside this header.

The header stores no software state and persists nothing by itself. Persistent or latched state lives in NBIO/PCIe hardware registers. Some fields are configuration controls that remain until reset, power transition, function reset, link retraining, or driver reprogramming. Other fields are hardware-updated status, sticky error, log, or write-one-to-clear fields whose behavior is defined by the hardware/specification rather than by this file.

## Dependencies And Integration Points

The direct source-tree integration point for this header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes `nbio/nbio_7_2_0_sh_mask.h` for NBIO 7.2 register access. The matching address definitions come from the generated `nbio_7_2_0_offset.h` header in the same ASIC register family; masks in this chunk must be paired with the same-generation offsets.

The semantic dependencies are the PCI and PCI Express configuration-space specifications plus AMD's generated NBIO 7.2 register database. The covered protocol areas include PCI bridge configuration, PM capability, MSI, PCIe capability versions, AER, ACS, VC, multicast, L1 PM substates, DPC/RP PIO, Data Link Feature, 16 GT PHY/equalization, lane margining, CCIX, and ESM lane equalization.

Because this is a generated header, many integration points are indirect. Consumers may include this file through NBIO implementation code, debug code, register dump paths, or generated register helper layers. The macros are not self-describing about access width, reset value, read/write permissions, side effects, or sequencing; callers must obtain those rules from the hardware programming guide and surrounding driver code.

## Risks And Maintenance Notes

- The range starts and ends mid-context. It begins after part of `BIFPLR1_1_PMI_STATUS_CNTL` and stops before the rest of the `BIFPLR2_1` bridge window/register map, so adjacent chunks are required for a full per-file report.
- Repeated lane blocks are easy to mis-review. Lane number, data rate suffix, upstream/downstream preset direction, and mask width are the only visible differences across many consecutive definitions.
- Wrong masks or shifts can silently misprogram hardware: examples include masking the wrong AER severity bit, decoding the wrong DPC trigger reason, enabling the wrong ACS isolation behavior, or programming the wrong link equalization preset.
- Full-width `0xFFFFFFFFL` masks usually represent reserved or whole-register payload/log fields. They should not be interpreted as permission to write all bits as ones.
- Names such as `*_MASK_MASK` can be valid generated names when the hardware field is itself named `MASK`; downstream code should not normalize them by hand.
- Status/log fields may be sticky, hardware-updated, or write-one-to-clear. Control fields may affect link state, error reporting, interrupt routing, power management, peer-to-peer routing, or protocol calibration.
- `BIFPLR1_1` and `BIFPLR2_1` fields are similar but not interchangeable. Each prefix must stay paired with its matching offset prefix and hardware block.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for `amdgpu/nbio_v7_2.c` and any translation units that include the NBIO 7.2 generated headers.
- Cross-header checks that every register represented here has a matching `regBIFPLR1_1_*` or `regBIFPLR2_1_*` offset in the matching NBIO 7.2 offset header.
- Generated-header comparison against AMD's authoritative NBIO 7.2 register database, especially for AER/DPC, ACS, CCIX/ESM, and lane 0-15 repeated blocks.
- Static checks that field masks fit their intended register widths and that each field with a `__SHIFT` has the expected generated `_MASK`.
- Hardware or simulator register dumps that compare decoded PCIe capability chains with `lspci -vvxxx`-style output for link capabilities, MSI, AER, ACS, DPC, L1 PM substates, and lane margining.
- Link-training tests on NBIO 7.2 hardware that exercise 8 GT, 16 GT, 20 GT, and 25 GT equalization paths and verify lane status, parity mismatch, and margining readiness without unexpected retrains.
- Error-injection or error-observation tests for AER and DPC/RP PIO paths, checking status, mask, severity, source ID, header log, TLP prefix log, and root error reporting decode.
- Isolation and virtualization tests that verify ACS and multicast behavior, plus bridge bus/window decoding, continue to match platform policy.
