# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 36713-39156

## Purpose

This chunk is an auto-generated AMD NBIO 7.2 shift/mask slice for NBIF PCIe root-complex configuration registers. It does not implement executable logic. Instead, it exports preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields inside NBIO-backed PCI/PCIe configuration-space registers.

The selected range starts in the middle of the `DEV0_RC0` root-port capability map, covers the complete `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` address block, and begins the `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp` address block. These masks are meant to be paired with the same-named register offsets in `nbio_7_2_0_offset.h` and then consumed through AMDGPU NBIO register access helpers.

## Public Surface In This Chunk

The public surface is 2,144 `#define` macros: 1,071 shift definitions and 1,073 mask definitions. The extra masks come from a couple of continuation/end-boundary fields where this chunk starts or stops in the middle of a register definition.

Macro names follow the generated pattern:

- `BIF_CFG_DEV*_RC0_<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `BIF_CFG_DEV*_RC0_<REGISTER>__<FIELD>_MASK` gives the field mask before shifting extracted values down.
- The `DEV0_RC0`, `DEV1_RC0`, and `DEV2_RC0` prefixes identify NBIF root-complex device blocks, not software structures.

There are no functions, structs, enums, or inline helpers in this range. The important API contract is the exact spelling and numeric value of the macros, because downstream code and generated offset headers rely on those names.

## Register Coverage

For `DEV0_RC0`, the chunk continues after lane 3 PCIe 8 GT equalization and covers:

- PCIe lane 4 through lane 15 8 GT equalization control fields for downstream/upstream transmit presets and receiver preset hints.
- ACS enhanced capability list, ACS capability bits, and ACS control enables for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, and direct translated peer-to-peer behavior.
- Data Link Feature enhanced capability, local/remote DLF support bitmaps, exchange enable, and remote-valid status.
- PCIe 16 GT PHY enhanced capability, reserved 16 GT link capability/control dwords, 16 GT link equalization completion/phase/request status, local/RTM parity mismatch status, and per-lane 16 GT transmit preset fields.
- PCIe lane margining enhanced capability, margining port readiness, and lane 0 through lane 15 margining control/status fields.

For `DEV1_RC0`, the range covers a full root-complex PCI/PCIe configuration map:

- Standard PCI header fields: vendor/device ID, command bits, status bits, revision/class bytes, cache line, latency, header/BIST, BARs, bus numbering, IO/memory/prefetchable windows, ROM BAR, interrupt line/pin, bridge control, and extended bridge control.
- PM capability and control/status fields, including power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PMI data.
- PCIe capability, device capability/control/status, link capability/control/status, slot/root capability/control/status, and PCIe capability 2/link 2/slot 2 groups.
- MSI capability and message address/data fields plus SSID and MSI mapping capability fields.
- Vendor-specific enhanced capability and virtual-channel capability/control/status/resource fields for VC0 and VC1.
- Device serial number fields.
- Advanced Error Reporting capability fields: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four header-log dwords, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe capability, link control 3, lane error status, lane 0 through lane 15 8 GT equalization controls, ACS, data-link feature, 16 GT link/equalization/parity status, and lane margining capability/control/status.

For `DEV2_RC0`, the chunk begins the root-complex block and reaches only the start of the PCIe capability. It covers vendor/device ID, command/status, revision/class bytes, bridge-style bus/window registers, BARs, interrupt and bridge control fields, PM capability/control/status, and the PCIe capability list header. The actual `DEV2_RC0_PCIE_CAP` fields continue in the following chunk.

## Field Semantics

The chunk mirrors PCI and PCI Express register layouts. Standard command/status fields describe IO and memory decoding, bus mastering, SERR, interrupt disable, capability-list presence, abort/parity/system-error status, and bridge discard timers. Bridge window fields split bus numbers, IO ranges, memory ranges, and prefetchable range upper/lower components into packed bitfields.

PCIe capability fields describe device type, payload/read-request sizing, relaxed ordering, extended tags, no-snoop behavior, function-level reset, atomic operation support, completion timeout controls, OBFF, LTR, emergency power reduction, link speed/width, ASPM/L0s/L1 latencies, clock configuration, link training state, slot controls, and root error reporting.

AER fields are particularly dense. They expose correctable and uncorrectable error status, masks, severity selection, ECRC support/enablement, multi-header log controls, header/TLP prefix logs, root error report enables, root error status, and source identifiers. These fields are diagnostic and policy-bearing: a mask or severity bit changes what the hardware reports to the driver or root complex.

The high-speed link-training sections cover two related generations of link behavior. The 8 GT equalization lane controls provide downstream/upstream transmit presets and receiver hints. The 16 GT section adds equalization completion/phase status, parity mismatch vectors, and per-lane downstream/upstream transmit presets. The lane margining section exposes port readiness plus per-lane receiver number, margin type, usage model, and payload request/status fields.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. AMDGPU code includes `nbio/nbio_7_2_0_sh_mask.h` together with the matching offset header.
2. Code selects an NBIO register offset such as `regBIF_CFG_DEV1_RC0_*`.
3. The corresponding macros in this chunk are used to insert, extract, mask, or test individual fields.
4. Actual reads and writes happen through AMDGPU register access code outside this header.

The header stores no software state and has no persistence behavior. Persistent state lives in the GPU's NBIO/PCIe hardware registers and may survive until hardware reset, link retraining, function reset, power transition, or driver reprogramming depending on the field. Many status fields are latched by hardware, while control fields can change link behavior, reporting policy, address decoding, interrupt routing, power management, or isolation semantics.

## Dependencies And Integration Points

The primary source-tree dependency is the generated AMD ASIC register header scheme. This file supplies field masks; `nbio_7_2_0_offset.h` supplies the register addresses and base indices. Consumers must use matching generation headers because the names and numeric values are ASIC-generation-specific.

The direct C include in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which binds these definitions into the NBIO 7.2 implementation. More broadly, AMDGPU PCIe/NBIO code, debug paths, display resource code that includes NBIO headers, and any generated register access helpers depend on these symbols remaining stable.

The semantic dependencies are the PCI and PCI Express specifications for bridge/root-port configuration space, PM capability, MSI, PCIe device/link/slot/root capability structures, VC, AER, ACS, Data Link Feature, PCIe 16 GT PHY/link equalization, and lane margining. The header itself does not encode access permissions, write-one-to-clear behavior, reset values, or sequencing requirements.

## Risks And Maintenance Notes

- This range starts and ends mid-definition context. It begins after the first part of `DEV0_RC0_PCIE_LANE_3_EQUALIZATION_CNTL` and ends at the comment for `DEV2_RC0_PCIE_CAP`; adjacent chunks are required for the final per-file report.
- Generated headers are easy to mis-review. Most lane, margining, AER, ACS, and capability blocks differ only by device number, lane number, field suffix, or mask value.
- A wrong mask or shift can silently corrupt register programming: for example, extracting the wrong AER bit, programming the wrong link equalization preset, or enabling the wrong ACS isolation behavior.
- Some field names contain repeated words such as `*_MASK_MASK` because the register field itself is named `*_MASK`. Consumers should treat these as generated names rather than hand-normalizing them.
- Full-width `0xFFFFFFFFL` masks represent whole-register payload/log/reserved fields, not necessarily fields that are safe to write as all ones.
- Status fields may be sticky, write-one-to-clear, or hardware-updated. Control fields can affect link training, bus decoding, interrupt delivery, power state, error reporting, or peer-to-peer routing.
- Root-complex device blocks are similar but not interchangeable. `DEV0_RC0`, `DEV1_RC0`, and `DEV2_RC0` must be paired with their matching offsets and hardware instance.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for `amdgpu/nbio_v7_2.c` and any translation units that include NBIO 7.2 generated headers.
- Static checks that every consumed `BIF_CFG_DEV*_RC0_*__SHIFT` has a matching mask with the expected generated name and that the values fit the register width.
- Cross-header checks that registers in this shift/mask range have matching `regBIF_CFG_DEV*_RC0_*` offsets in `nbio_7_2_0_offset.h`.
- Generated-header comparison against AMD's authoritative NBIO 7.2 register database, especially for repeated lane 0-15 equalization and margining blocks.
- Hardware smoke tests on NBIO 7.2 ASICs that read PCI config-space capability chains and compare decoded fields with `lspci -vvxxx` or equivalent debug dumps.
- Link tests that exercise 8 GT and 16 GT negotiation/equalization, lane error status, parity mismatch status, and margining readiness without unexpected retrains or link drops.
- Error-reporting tests that inject or observe AER correctable/uncorrectable events and verify status, mask, severity, root error, source ID, header log, and TLP prefix decoding.
- Isolation and virtualization tests that verify ACS behavior, bus/window decoding, and peer-to-peer routing continue to match platform expectations.
