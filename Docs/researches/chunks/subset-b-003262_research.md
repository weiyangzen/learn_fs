# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h - subset-b-003262

## Scope

This chunk covers lines 7395-9852 of the generated AMD NBIO 7.7.0 register shift/mask header. It is the fourth chunk for the file and contains 2,458 lines, including 2,137 `#define` macros and 315 register/comment markers.

The covered range spans:

- The tail of `BIF_CFG_DEV0_EPF1` PCIe 16 GT/s lane equalization masks for lanes 5-15.
- `BIF_CFG_DEV0_EPF1` PCIe lane margining control/status masks for lanes 0-15.
- `BIF_CFG_DEV0_EPF1` VF resizable BAR enhanced capability masks for VF BARs 1-6.
- The complete `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` block.
- Most of the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block, through EPF3 ARI control.
- The first two EPF4 identity registers (`VENDOR_ID`, `DEVICE_ID`) where the next address block begins.

## Purpose

`nbio_7_7_0_sh_mask.h` supplies bit shifts and masks for the NBIO 7.7.0 PCIe/BIF configuration register map used by the AMD GPU driver. This chunk is a pure hardware description layer: it does not execute logic, allocate state, or call functions. Consumers include this header so register access code can extract or program specific fields in PCI configuration and PCIe extended capability registers without hard-coding bit positions.

The main hardware area represented here is PCIe endpoint-function configuration for device 0 functions EPF1, EPF2, and EPF3. EPF2 and EPF3 repeat a full PCI configuration-space layout: device identity, command/status, BARs, PCI power management, PCIe capability, MSI/MSI-X, SATA capability, vendor-specific capability, AER, resizable BAR, power budget, DPA, ACS, PASID, and ARI fields.

## Important API Surface

There are no C functions, structs, enums, or typedefs in this chunk. The public API is the macro namespace itself:

- Every field has a `...__FIELD__SHIFT` macro giving the least-significant bit position.
- Every field has a `...__FIELD_MASK` macro giving the field mask in its containing register.
- Register group names are preserved in comments, for example `//BIF_CFG_DEV0_EPF2_DEVICE_CNTL`.
- Address block comments divide endpoint-function register windows, for example `// addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`.

Typical consumers combine these macros with AMDGPU register helper patterns such as read-modify-write, field preparation, and field extraction. The masks are also useful when decoding register dumps because the symbolic names map raw bits back to PCIe concepts.

## Register Families Covered

### EPF1 PCIe Lane Equalization

The chunk begins mid-family with `BIF_CFG_DEV0_EPF1_LANE_5_EQUALIZATION_CNTL_16GT` and continues through lane 15. Each lane has:

- `LANE_N_DSP_16GT_TX_PRESET` at shift `0x0`, mask `0x0f`.
- `LANE_N_USP_16GT_TX_PRESET` at shift `0x4`, mask `0xf0`.

These are 16 GT/s transmit preset fields for downstream/upstream components during PCIe Gen4 equalization. The lane index is embedded in the macro name, so off-by-one lane mapping mistakes are easy to introduce during manual edits or generated-header comparisons.

### EPF1 PCIe Lane Margining

The EPF1 margining section defines the enhanced capability header and port/lane controls:

- `PCIE_MARGINING_ENH_CAP_LIST`: extended capability ID, version, and next pointer.
- `MARGINING_PORT_CAP`: `MARGINING_USES_SOFTWARE`.
- `MARGINING_PORT_STATUS`: `MARGINING_READY` and `MARGINING_SOFTWARE_READY`.
- `LANE_0_MARGINING_LANE_CNTL` through `LANE_15_MARGINING_LANE_CNTL`.
- Matching `LANE_0_MARGINING_LANE_STATUS` through `LANE_15_MARGINING_LANE_STATUS`.

Each lane control/status pair repeats the same field layout:

- `RECEIVER_NUMBER` / `RECEIVER_NUMBER_STATUS`: bits 0-2, mask `0x0007`.
- `MARGIN_TYPE` / `MARGIN_TYPE_STATUS`: bits 3-5, mask `0x0038`.
- `USAGE_MODEL` / `USAGE_MODEL_STATUS`: bit 6, mask `0x0040`.
- `MARGIN_PAYLOAD` / `MARGIN_PAYLOAD_STATUS`: bits 8-15, mask `0xff00`.

These definitions expose PCIe link margining configuration and status per lane. State is held by hardware/configuration space, not by this header.

### EPF1 VF Resizable BAR

The chunk then defines the `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST` and VF BAR1-BAR6 capability/control fields:

- `VF_BAR_SIZE_SUPPORTED` in each `VF_RESIZE_BARn_CAP`, shifted by 4 with mask `0xfffffff0`.
- `VF_BAR_INDEX`, `VF_BAR_TOTAL_NUM`, `VF_BAR_SIZE`, and `VF_BAR_SIZE_SUPPORTED_UPPER` in each `VF_RESIZE_BARn_CNTL`.

This register family is relevant to SR-IOV or virtual-function resource sizing. It must remain distinct from the physical-function resizable BAR fields in the EPF2/EPF3 blocks later in the chunk.

### EPF2 Standard PCI Configuration

The EPF2 block starts at `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and begins with standard PCI configuration-space fields:

- Identity/class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`.
- Command/status: `COMMAND` and `STATUS` cover I/O enable, memory enable, bus mastering, parity/SERR behavior, interrupt disable, capability-list presence, abort/error status, and DEVSEL timing.
- Header/BIST/timing fields: `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `MIN_GRANT`, `MAX_LATENCY`.
- BAR and ROM fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `ROM_BASE_ADDR`.
- Capability and interrupt navigation fields: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `VENDOR_CAP_LIST`.
- Subsystem identity fields: `ADAPTER_ID` and writable mirror `ADAPTER_ID_W`.

These masks correspond to configuration-space registers that are usually accessed through PCI config mechanisms or through GPU MMIO/config aperture logic elsewhere in the driver.

### EPF2 Power Management and PCIe Capability

The EPF2 power-management and PCIe capability masks include:

- `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, covering PME capability/support, D1/D2 support, data select/scale, power state, PME enable/status, and bus power enable.
- USB/SATA-adjacent legacy fields `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- `PCIE_CAP_LIST` and `PCIE_CAP`, defining PCIe capability version, device type, slot implementation, and interrupt message number.
- Device capability/control/status: payload size, extended tag, relaxed ordering, no-snoop, FLR, error enables, transaction pending, and emergency power reduction status.
- Link capability/control/status: speed, width, ASPM/PM support, retrain/link disable/common clock/extended sync, data link active, bandwidth management, and DRS signaling.
- PCIe capability 2 fields: completion timeout, ARI forwarding, atomic ops, IDO, LTR, OBFF, 10-bit tags, end-to-end TLP prefix support, and FRS.
- Link capability/control/status 2 fields: supported speeds, compliance controls, equalization state, presence-detect fields, crosslink resolution, and DRS message received.

These definitions are central to link bring-up diagnostics and feature gating. Wrong masks here can make the driver read a valid register but infer the wrong link state or supported feature set.

### EPF2 MSI, MSI-X, SATA, Vendor-Specific, and AER

The EPF2 interrupt and auxiliary capability sections define:

- MSI: capability header, message control, 32-bit and 64-bit message address/data, extended message data, mask, and pending fields.
- MSI-X: capability header, message control, table pointer, and pending-bit-array pointer fields.
- SATA capability: `SATA_CAP_0`, `SATA_CAP_1`, `SATA_IDP_INDEX`, and `SATA_IDP_DATA`.
- Vendor-specific PCIe enhanced capability: header fields plus two scratch registers.
- AER: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs 0-3, and TLP prefix logs 0-3.

The AER masks are diagnostic and reliability-sensitive. They distinguish data link protocol errors, surprise down, poisoned TLPs, flow control, completion timeout/abort, unexpected completion, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast blocking, atomic-op egress blocking, TLP prefix blocking, and poisoned-TLP egress blocking.

### EPF2 Resizable BAR, Power Budget, DPA, ACS, PASID, and ARI

The latter EPF2 section defines PCIe extended capability families:

- Physical-function resizable BAR: BAR1-BAR6 `BAR_SIZE_SUPPORTED` plus `BAR_INDEX`, `BAR_TOTAL_NUM`, `BAR_SIZE`, and upper supported-size bits.
- Power budget: enhanced capability header, data select, base power, data scale, PM state/substate, type, power rail, and system-allocated flag.
- Dynamic Power Allocation: substate maximum, transition latency units/values, power allocation scale, current substate/status, control substate, and eight per-substate power allocation registers.
- ACS: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer egress control, direct translated P2P, and egress-control vector size.
- PASID: executable permission support, privileged mode support, maximum PASID width, and enable bits.
- ARI: function group capability/enables and next function number.

These fields integrate with virtualization, peer-to-peer routing, power management, and device enumeration. ACS/PASID/ARI are especially relevant to IOMMU isolation and SR-IOV/multi-function behavior.

### EPF3 Repeated Endpoint-Function Block

The EPF3 block repeats the same broad layout as EPF2 from `VENDOR_ID` through `PCIE_ARI_CNTL`. In this chunk, EPF3 includes:

- Standard PCI identity, command/status, BAR, subsystem, ROM, interrupt, and vendor capability masks.
- Power management and PCIe device/link capability masks.
- MSI and MSI-X masks.
- SATA and vendor-specific enhanced capability masks.
- AER status/mask/severity and header/TLP prefix logging masks.
- Resizable BAR, power budget, DPA, ACS, PASID, and ARI masks.

The repetition implies the same endpoint-function semantics but a different function namespace. Consumers must select the EPF2 or EPF3 macro family according to the function being decoded or programmed; the field layouts are often identical, but macro prefixes prevent accidental cross-function aliasing at compile time.

### EPF4 Boundary

The chunk ends at the start of `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp` with only `EPF4_VENDOR_ID` and `EPF4_DEVICE_ID`. The rest of EPF4 belongs to the next chunk, so this document should not be treated as a complete EPF4 analysis.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow appears in downstream C code that:

1. Includes this generated header.
2. Reads a register/configuration dword from the NBIO/BIF address space.
3. Applies a `*_MASK` and `*_SHIFT` pair to extract a field, or prepares a field value.
4. Optionally writes the modified dword back to hardware.

For write paths, the masks define the legal field boundaries. For status paths, they define the bits used for decoding hardware state.

## State and Persistence

The header itself has no mutable state and no persistence behavior. It describes persistent and transient hardware/configuration state:

- PCI command, BAR, MSI/MSI-X, ACS, PASID, ARI, DPA, and power-management control bits may persist in device configuration space until reset or reprogramming.
- Status bits such as link state, AER status, MSI pending, DPA status, and lane margining status reflect current or latched hardware state.
- Log registers such as AER header logs and TLP prefix logs hold diagnostic state captured by hardware after errors.

Any persistence semantics, write-one-to-clear behavior, reset defaults, or ordering requirements are not encoded in these macros. Those must come from the hardware specification or companion default/offset headers and from the driver code that uses the masks.

## Dependencies and Integration Points

This chunk depends on the surrounding generated register-header set:

- Offset/address headers provide the register addresses corresponding to these shift/mask names.
- Default-value headers, when present, provide reset/default values.
- AMDGPU NBIO, PCIe, SR-IOV, reset, error-reporting, and power-management code consume these macros indirectly through generated ASIC register include paths.
- Linux PCI/PCIe semantics are mirrored in the register names: PCI command/status, capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, resizable BAR, DPA, and power budget.

The file is source-tree-aligned under the AMD GPU driver register include hierarchy. It should be updated only with the matching NBIO 7.7.0 register database/generator output, not by ad hoc hand edits.

## Risks

- Generated-header drift: if offsets, masks, defaults, and shift headers are regenerated from different hardware database revisions, fields can decode incorrectly while still compiling.
- Function-prefix confusion: EPF1 VF BAR fields, EPF2 physical BAR fields, and EPF3 physical BAR fields have similar names and layouts but target different endpoint functions.
- Lane-index mistakes: equalization and margining fields repeat for lanes 0-15; a single lane-number mismatch can target the wrong physical lane.
- Mask/shift mismatch: downstream code that combines a `SHIFT` from one macro family with a `MASK` from another may silently corrupt field extraction or writes.
- Write-sensitive bits: command, link control, device control, MSI/MSI-X, ACS, PASID, ARI, DPA, and resizable BAR control fields can affect enumeration, isolation, interrupt delivery, or link behavior if programmed incorrectly.
- Diagnostic false negatives: incorrect AER masks can hide or misclassify PCIe errors, making link, fabric, or memory faults harder to diagnose.
- Virtualization/isolation exposure: ACS, PASID, ARI, and VF resizable BAR fields are used around IOMMU/SR-IOV-style behavior; stale masks can affect peer-to-peer routing or process-address-space tagging assumptions.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-observation checks:

- The AMDGPU driver and any generated-register include users compile with `nbio_7_7_0_sh_mask.h` included for NBIO 7.7.0 ASICs.
- Register dump decoders extract EPF2/EPF3 PCIe command/status, link status, MSI/MSI-X, AER, BAR, ACS, PASID, and ARI fields that match `lspci -vv` or known hardware register dumps.
- PCIe link training diagnostics show coherent values for link speed/width, equalization phases, DRS, and data-link-active status.
- AER injection or real error logs map to the expected uncorrectable/correctable status bits and header/TLP-prefix log fields.
- SR-IOV or virtual-function BAR sizing tests, where applicable, report sane VF BAR supported sizes and selected sizes for EPF1.
- Power-management validation confirms PMI, DPA, power-budget, and emergency power reduction fields decode consistently across suspend/resume and reset paths.
- Cross-generation comparison against neighboring NBIO headers confirms this chunk intentionally matches or differs from other NBIO versions, rather than drifting due to generator error.

## Research Notes

This chunk is purely declarative but dense. Its main engineering value is maintaining exact symbolic alignment between the NBIO 7.7.0 hardware register database and driver code that decodes or programs PCIe endpoint-function configuration space. The most important review focus is not local algorithmic behavior, but whether repeated EPF/lane/BAR capability families are complete, consistently named, and paired with the correct address/default definitions elsewhere in the generated register set.
