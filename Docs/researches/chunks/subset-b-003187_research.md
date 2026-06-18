# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 65982-68462

## Scope

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask header. It contains 2,109 `#define` macros and 370 register/address-block comments. Of those macros, 1,054 are `__SHIFT` constants and 1,055 are field `_MASK` constants. There are no functions, structs, enums, variables, branches, loops, allocations, locks, or persistence code in this range.

The range starts in the middle of the `BIF_CFG_DEV1_EPF1_0_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST` field definitions, covers the remainder of the `DEV1_EPF1_0` endpoint/function extended PCIe capability area, then enters `addressBlock: nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp` and covers most of the `DEV2_EPF0_0` endpoint/function configuration space through lane 13 of the 16GT equalization controls. The source path is under a Ceph mirror, but this file is AMDGPU hardware register metadata and has no distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` provides generated bitfield geometry for NBIO 7.2.0 registers. Each exported field follows the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`: the already shifted mask used to isolate, preserve, or update the field.

The constants are paired with register-address definitions from `nbio_7_2_0_offset.h`. Runtime AMDGPU code uses those paired register offsets and bitfields through SOC15/NBIO register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, and `REG_SET_FIELD`. This chunk therefore acts as part of the hardware ABI for PCIe endpoint capability, error-reporting, power, isolation, interrupt, link-training, TPH, data-link, and 16GT PHY state.

## Important Macro Families

The leading `BIF_CFG_DEV1_EPF1_0` portion covers endpoint/function 1 extended capability fields:

- Vendor-specific extended capability metadata and payload: capability ID/version/next-pointer fields, VSEC ID/revision/length, and two full-width scratch payload registers.
- PCIe Advanced Error Reporting: uncorrectable status, mask, and severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked; correctable status/mask fields for receiver error, bad TLP/DLLP, replay rollover/timeout, advisory nonfatal, internal correctable, and header log overflow; AER control fields including first error pointer and ECRC/multiple-header/prefix-log capabilities.
- Error log payloads: four 32-bit header log registers and four TLP prefix log registers, all exposed as full-width fields.
- Resizable BAR capability/control pairs for BAR1 through BAR6, including supported sizes, current size selection, number of resizable BARs, and BAR index fields.
- Power Budgeting and Dynamic Power Allocation: selector, data, system allocation, capability, DPA substate count, transition latency, status, enable/substate control, and eight substate power-allocation entries.
- Isolation and function-routing extensions: ACS capability/control, PASID capability/control, and ARI capability/control.
- TPH requester capability/control and 64 steering table entries. Each TPH ST table register carries lower and upper 8-bit entries.

The `addressBlock: nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp` portion begins a second endpoint/function instance:

- Conventional PCI configuration fields for `DEV2_EPF0_0`: vendor/device IDs, command/status, revision/class/program-interface, cache/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, adapter/subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and latency/grant fields.
- Standard and vendor capabilities: vendor capability list, adapter ID window, Power Management capability/status/control, SBRN, FLADJ, DBESL/DBESLD, PCIe capability header, device/link capability/control/status, and second-generation device/link fields.
- MSI and MSI-X: capability headers, MSI message control/address/data, 64-bit variants, mask and pending fields, MSI-X table and PBA descriptors.
- PCIe vendor-specific and Virtual Channel capability fields: VSEC header/payload registers, VC port capability/control/status, and VC0/VC1 resource capability/control/status fields.
- AER, resizable BAR, power budget, and DPA definitions mirroring the earlier `DEV1_EPF1_0` endpoint families, but under the `DEV2_EPF0_0` prefix.
- Secondary PCIe capability, link control 3, lane error status, per-lane 8GT equalization controls for lanes 0-15, ACS/PASID/LTR/ARI capability/control fields, and TPH requester controls plus steering table entries 0-63.
- Data Link Feature and 16GT PHY capability fields: DLF local/remote support and exchange-enable fields, 16GT capability/control/status, 16GT equalization status, local/retimer parity mismatch status registers, and 16GT per-lane transmit preset controls for lanes 0-13 at the chunk boundary.

## APIs, Types, And Functions

This chunk defines no callable C API and no C data types. Its public interface is the generated preprocessor namespace. The values are integer literals, usually with an `L` suffix for masks.

The macros do not encode reset defaults, access permissions, side effects, legal enumerated values, timing rules, or firmware ownership. A caller must combine these symbols with the matching `regBIF_CFG_*` or `cfgBIF_CFG_*` offset macro and with the correct access path for the register family. For example, `nbio_7_2_0_offset.h` maps `BIF_CFG_DEV1_EPF1_0_PCIE_UNCORR_ERR_STATUS` and `BIF_CFG_DEV2_EPF0_0_PCIE_UNCORR_ERR_STATUS` to distinct NBIO register addresses, and `BIF_CFG_DEV2_EPF0_0_LANE_13_EQUALIZATION_CNTL_16GT` has its own separate offset.

## Control Flow

There is no local runtime control flow. The effective flow is compile-time substitution:

1. AMDGPU code selects a generated NBIO register offset for the endpoint/function instance being accessed.
2. Code reads a hardware/config-space register, extracts fields using the matching `__SHIFT` and `_MASK`, or builds a new value with read-modify-write semantics.
3. Hardware consumes control writes or reports status/capability/log state through those bit positions.

The represented hardware behavior is asynchronous and protocol-driven. AER status and logs are latched by PCIe errors, MSI/MSI-X fields affect interrupt routing, BAR controls affect address decode, DPA and power-management fields affect power-state policy, ACS/PASID/ARI/LTR affect routing/isolation/latency semantics, TPH fields affect transaction steering hints, and lane/link fields reflect PCIe link training and 16GT equalization state.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes NBIO PCIe configuration registers whose contents live in hardware and are affected by firmware initialization, PCI enumeration, hot reset, function-level reset, link retraining, GPU reset, suspend/resume, D-state transitions, and explicit driver writes.

State categories represented here include:

- Identity and decode state: IDs, class-code fields, BARs, ROM BARs, capability pointers, and subsystem/adapter identifiers.
- Control policy state: PCI command bits, PM controls, PCIe device/link controls, MSI/MSI-X controls, AER masks/severities, BAR size selections, DPA controls, ACS/PASID/ARI controls, LTR, TPH controls, Data Link Feature exchange enable, and lane equalization transmit presets.
- Status and diagnostics: PCI/device/link status, AER correctable/uncorrectable status, header and TLP-prefix logs, DPA status, lane error status, Data Link Feature status, 16GT equalization status, and local/retimer parity mismatch status.
- Capability readback state: vendor-specific capability metadata, PM, PCIe, MSI/MSI-X, VC, AER, resizable BAR, power budget, DPA, ACS, PASID, LTR, ARI, TPH, DLF, and 16GT PHY capability fields.

The header does not say which status bits are sticky or write-one-to-clear, which control bits are firmware-owned, or which capability fields are read-only. Callers need PCIe rules, AMD register specifications, and established AMDGPU sequencing to avoid clearing logs too early or overwriting reserved bits.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h` supplies the matching register offsets and base indices. These shift/mask definitions are meaningful only when paired with the correct endpoint/function register address.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` directly includes `nbio_7_2_0_sh_mask.h`, along with the matching offset header, for NBIO 7.2 register work.
- AMDGPU's SOC15/NBIO access layer provides the practical consumers: register read/write helpers, `SOC15_REG_OFFSET`, and field helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`.
- PCIe architectural behavior supplies the semantic contract for many field names: AER, MSI/MSI-X, PM, PCIe device/link capabilities, VC, resizable BAR, ACS, PASID, LTR, ARI, TPH, DLF, and 16GT PHY/equalization.

The namespace is instance-sensitive. `DEV1_EPF1_0` and `DEV2_EPF0_0` fields often have identical field names and bit positions, but they refer to different endpoint/function instances and must not be substituted mechanically.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing wrong field extraction or writes. The highest-risk families in this chunk are AER, MSI/MSI-X, BAR sizing, ACS/PASID/ARI, DPA/power, TPH, DLF, and 16GT link-training fields because mistakes can affect enumeration, DMA reachability, interrupt delivery, isolation, link stability, or error handling.
- This range begins after the `CAP_ID__SHIFT` line for `BIF_CFG_DEV1_EPF1_0_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`; the complete capability-list field set starts in the previous chunk. Whole-file reconciliation should treat the first register family as boundary-spanning.
- This range ends after the complete lane 13 16GT equalization control masks. Lanes 14-15 and the subsequent PCIe margining capability/control/status definitions continue in the next chunk.
- Full-width log, scratch, BAR, mask, and pending fields need to be treated as payloads rather than single-bit flags.
- Status/log fields may require read-before-clear ordering. AER header logs, TLP prefix logs, parity mismatch, lane errors, and interrupt pending bits are especially sensitive to careless writeback.
- Repeated per-lane and per-BAR patterns are easy to mis-index. The preprocessor does not provide array semantics, so any caller iterating lanes, BARs, DPA substates, or TPH steering-table entries has to map indexes to the exact register macro names.
- Access width and path matter. Some conventional PCI config registers are byte or word sized, while many enhanced capability registers are dword sized; reserved bits must be preserved during read-modify-write operations.

## Test Signals

Useful validation signals are mostly generated-header consistency checks plus hardware behavior on NBIO 7.2 systems:

- Build AMDGPU configurations that include NBIO 7.2.0 to catch missing, renamed, or syntactically invalid macros.
- Verify that each complete register family in this chunk has paired `__SHIFT` and `_MASK` definitions, with masks aligned to shifts and expected field widths. Boundary exceptions are the leading vendor-specific capability-list register and any families that continue after lane 13 in the next chunk.
- Cross-check `BIF_CFG_DEV1_EPF1_0` and `BIF_CFG_DEV2_EPF0_0` field names against `nbio_7_2_0_offset.h` so every field layout maps to the intended endpoint/function offset.
- On supported hardware, validate PCIe enumeration, BAR sizing and restore, MSI/MSI-X interrupt delivery and masking, AER correctable/nonfatal/fatal reporting, DPA/power transitions, ACS/PASID/ARI isolation behavior, LTR exposure, and TPH requester behavior.
- Exercise link diagnostics under reset, suspend/resume, retrain, and load: lane error status, DLF exchange/status, 16GT equalization completion/phase status, local and retimer parity mismatch status, and per-lane 16GT preset programming.
- Inspect register traces for writers to confirm reserved bits are preserved, logs are read before destructive clears, and writes target the intended `DEV1_EPF1_0` or `DEV2_EPF0_0` instance.

## Chunk Boundary Notes

Line 65982 is already inside `BIF_CFG_DEV1_EPF1_0_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`; the `CAP_ID__SHIFT` definition is on line 65981 in the previous chunk. The remaining fields in this capability-list register are present here.

Line 68462 completes `BIF_CFG_DEV2_EPF0_0_LANE_13_EQUALIZATION_CNTL_16GT`. The generated file continues with lane 14, lane 15, PCIe margining capability, and per-lane margining controls/status in the following chunk. These are chunking artifacts, not missing definitions in the source header.
