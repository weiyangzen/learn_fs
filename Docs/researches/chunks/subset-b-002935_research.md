# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 76009-78432

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header slice for SR-IOV virtual-function PCI configuration-space fields. It contains C preprocessor constants only. There are no functions, structs, variables, allocations, locks, branches, loops, I/O calls, or direct MMIO transactions in this range.

The source range starts partway through `BIF_CFG_DEV0_EPF0_VF26_0_*`, after the earlier VF26 identity/command/status/revision fields. It then covers the remainder of VF26, complete VF27 and VF28 PCI/PCIe configuration bitfield maps, and the beginning of VF29 through `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL__MSI_MULTI_CAP__SHIFT`. The chunk includes 274 distinct register field groups and 2,415 generated shift/mask definitions across VF26, VF27, VF28, and VF29.

Although this path sits under a `ceph-client` source mirror, the content is AMDGPU hardware metadata. It is not Ceph or distributed filesystem logic.

## Purpose

`nbio_2_3_sh_mask.h` publishes the bitfield layout for NBIO 2.3 registers and PCI configuration-space registers. The paired `nbio_2_3_offset.h` header supplies the register/config-space offsets; this file supplies the `__SHIFT` and `_MASK` constants used to compose writes and decode reads through AMDGPU register helpers.

For this specific chunk, the purpose is to describe PCI/PCIe configuration bit positions for high-numbered SR-IOV virtual functions on device 0 endpoint function 0:

- Tail of VF26 class/header, BAR, capability, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields.
- Full VF27 and VF28 Type 0 PCI header fields, PCIe capability fields, MSI/MSI-X fields, vendor-specific enhanced capability fields, Advanced Error Reporting fields, ATS fields, and ARI fields.
- Beginning of VF29 through PCIe device/link capability and control/status fields and the MSI capability-list header/start of MSI message control.

The public contract is mechanical but important:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted-in-register bit mask.

Wrong values here can compile cleanly while causing runtime code or diagnostic tooling to read, write, clear, or report the wrong PCIe configuration bits.

## Important Macro Families

### VF26 Tail

The first visible lines are already inside `BIF_CFG_DEV0_EPF0_VF26_0_PROG_INTERFACE`, then continue through `SUB_CLASS`, `BASE_CLASS`, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem/vendor adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency. The earlier VF26 `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, and `REVISION_ID` definitions are outside this chunk.

The VF26 PCIe capability group includes:

- `PCIE_CAP_LIST` and `PCIE_CAP` fields for capability ID, next pointer, PCIe version, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` fields for payload size, relaxed ordering, no-snoop, extended tags, FLR capability/initiation, error enables/status, user-detected error, auxiliary power, and pending transactions.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` fields for link speed/width, ASPM/power-management support, exit latencies, common clock, retrain/disable, bandwidth interrupts/status, link training, slot clock, and data-link active state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` fields for completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, TLP prefix behavior, supported link speeds, compliance/de-emphasis controls, 8 GT/s equalization status, RTM presence, crosslink resolution, downstream component presence, and DRS message status.

The VF26 interrupt capability families cover MSI and MSI-X:

- MSI list and message-control fields: enable, multiple-message capability/enable, 64-bit capable flag, and per-vector masking capability.
- MSI address, data, mask, and pending fields, including the `_64` aliases used when interpreting the 64-bit MSI layout.
- MSI-X capability, table, and pending-bit-array fields: table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The VF26 extended capability families cover vendor-specific capability headers/data, AER uncorrectable/correctable status/mask/severity, AER capability/control, header log dwords, TLP prefix log dwords, ATS capability/control, and ARI capability/control.

### Complete VF27 and VF28 Maps

VF27 and VF28 repeat the full generated VF config-space layout from `VENDOR_ID` through `PCIE_ARI_CNTL`. Each VF has its own macro prefix:

- `BIF_CFG_DEV0_EPF0_VF27_0_*`
- `BIF_CFG_DEV0_EPF0_VF28_0_*`

The complete maps include identity and class fields, standard PCI command/status bits, BARs, ROM and subsystem ID state, legacy interrupt fields, PCIe device/link capability/control/status, second-generation PCIe capability fields, MSI/MSI-X, vendor-specific extended capability, AER status/mask/logging, ATS, and ARI.

The repetition is intentional rather than abstracted. It lets generated AMDGPU code, firmware-facing code, debug tooling, or register dumps name a specific VF's config-space field directly. It also means copy/generator drift across adjacent VF blocks is a high-risk maintenance issue because nearly identical names differ only by VF number.

### VF29 Beginning

The VF29 section starts at `VENDOR_ID` and reaches only into `MSI_MSG_CNTL`. Within this chunk VF29 includes its Type 0 PCI header and the PCIe device/link capability groups through `LINK_STATUS2`, plus the MSI capability-list fields and the first two MSI message-control shifts (`MSI_EN` and `MSI_MULTI_CAP`). The rest of VF29 MSI message control, MSI address/data/mask/pending, MSI-X, vendor-specific, AER, ATS, and ARI fields continue in the next chunk.

## Important APIs, Types, and Constants

This chunk defines constants, not callable APIs or C types. Its important interfaces are the generated names consumed by broader AMDGPU register access infrastructure:

- `REG_SET_FIELD` and `REG_GET_FIELD` style helpers depend on the exact `__SHIFT` and `_MASK` pairs.
- Low-level AMDGPU accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and field helpers such as `WREG32_FIELD15` provide the runtime reads and writes outside this header.
- `nbio_2_3_offset.h` provides the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` addresses for these fields.
- `nbio_2_3_default.h` provides generated default values for related NBIO registers where defaults exist.

Field names mirror PCI/PCIe specification concepts: command/status, BARs, PCIe capability, device/link control, MSI, MSI-X, vendor-specific enhanced capability, Advanced Error Reporting, ATS, and ARI. That naming gives call sites and diagnostic tools a direct bridge between generated ASIC metadata and PCIe terminology.

## Control Flow

There is no executable control flow in this header range. Runtime behavior is supplied by code that includes the generated header set:

1. A caller selects a VF register/config-space offset from the NBIO 2.3 offset header or from a higher-level accessor table.
2. The caller reads a value, composes a new value, or decodes an existing value.
3. The shift/mask constants in this file identify the relevant field bits.
4. AMDGPU, PCI core, firmware, PF-mediated SR-IOV code, or hypervisor code performs the actual config-space or register transaction.

For this range, the effective control flow is mostly PCI/SR-IOV configuration and diagnostics rather than ordinary function calls in this file.

## State and Persistence Behavior

The header stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration state for virtual functions. That state can be initialized by hardware straps, firmware, the PF driver, the host PCI core, or a hypervisor, and it can be reset or replayed during FLR, VF teardown, GPU reset, suspend/resume, BACO/power transitions, or SR-IOV reconfiguration.

Important state represented by this chunk includes:

- Per-VF PCI identity, class, revision, header, BAR, ROM, subsystem, capability-pointer, and interrupt presentation.
- PCI command/status enables and sticky status/error bits, including memory access, bus mastering, SERR/parity behavior, interrupt disable, abort status, and parity error detected state.
- PCIe device controls for error reporting, relaxed ordering, payload/read-request sizing, extended tags, no-snoop, auxiliary power management, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, and TLP prefix behavior.
- PCIe link capability/control/status for speed, width, ASPM, exit latency, retrain/disable, common clock, bandwidth notifications, compliance controls, equalization status, and link activity.
- MSI/MSI-X interrupt programming state for VF26-VF28, plus the beginning of VF29 MSI metadata.
- AER status, masks, severity, capability/control, header logs, and TLP prefix logs for VF26-VF28.
- ATS and ARI capability/control state for address translation and alternative routing ID behavior on VF26-VF28.

Several represented bits are not ordinary persistent configuration. Status and AER fields may be sticky and clear-on-write according to PCIe semantics. FLR initiation, link retraining, emergency power reduction, MSI/MSI-X masks, and interrupt pending bits can have immediate hardware side effects. This header only describes bit positions; access permissions, ordering, polling, and clear semantics must come from the PCIe/NBIO specification and owning driver paths.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register database staying internally consistent:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`
- This `nbio_2_3_sh_mask.h` field-layout header.

Observed source-tree integration for the NBIO 2.3 generated headers includes AMDGPU NBIO, MxGPU, and SMU platform code. The most relevant consumers are code paths that include this header and then use the generated field macros through AMDGPU register helpers, including NBIO 2.3 setup, virtualization/MxGPU support, and SMU11 platform behavior.

The specific `BIF_CFG_DEV0_EPF0_VF*_0_*` fields integrate with SR-IOV virtual-function PCI config-space presentation. They are the bit-level companion to the offset-header VF blocks that map each VF's config-space addresses. In a virtualized setup, PF code, VF guest code, host PCI core, firmware, and hypervisor policy may all observe or mediate parts of this state.

## Risks and Edge Cases

- Chunk boundaries split register families. VF26 begins before this range, and VF29 continues after it. The later file-level report must merge neighboring chunks before making complete claims about VF26 or VF29.
- The file is generated and highly repetitive. A single wrong mask, shift, or VF number can compile successfully while targeting the wrong virtual function or corrupting an unrelated field.
- PCI command, status, AER, MSI/MSI-X, FLR, and link-control fields have side effects. Generic read/modify/write treatment can accidentally clear errors, trigger resets, retrain links, mask interrupts, or lose diagnostic logs.
- VF numbering is isolation-sensitive. Cross-wiring VF27/VF28/VF29 field names would be especially hard to catch by compilation and could affect SR-IOV guest isolation or device enumeration.
- MSI 32-bit and 64-bit layouts share conceptual registers and aliases. Consumers must interpret message address/data/mask/pending fields according to the MSI capability format rather than treating all generated names as independent storage.
- AER log, TLP prefix log, ATS, and ARI fields influence error diagnosis, IOMMU/address-translation behavior, and routing-ID handling. Incorrect bit definitions can hide failures or break virtualized PCIe behavior.
- Link capability/control/status fields can influence ASPM, link retraining, compliance, and equalization behavior. Bad masks can appear as intermittent link, power-management, or performance regressions rather than obvious build failures.
- Visibility does not imply write permission. PF, VF, guest, host, firmware, and hypervisor contexts may have different access rights to the same conceptual fields.

## Test and Validation Signals

Useful validation is mostly build-time, generated-header consistency, and hardware/SR-IOV behavior:

- Build AMDGPU code paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MxGPU, and SMU11 platform files.
- Compare repeated VF26-VF29 field layouts against adjacent VF chunks and against the matching `nbio_2_3_offset.h` blocks to catch missing fields, wrong VF prefixes, and mask-width drift.
- SR-IOV enumeration should expose coherent PCI IDs, class codes, BARs, capability pointers, PCIe capability structures, MSI/MSI-X capabilities, AER, ATS, and ARI for VF26-VF29 where these VFs are enabled.
- VF reset and teardown tests should validate FLR initiation/status behavior and restored command/status defaults.
- MSI/MSI-X interrupt tests should verify vector delivery, mask/pending behavior, table/PBA interpretation, and 32-bit versus 64-bit MSI layout handling for covered VFs.
- PCIe link and power-management tests should watch payload/read-request sizing, ASPM/LTR/OBFF behavior, link retraining, bandwidth status, equalization, and compliance bits.
- AER error injection or diagnostics should verify uncorrectable/correctable status, masks, severity, header-log, and TLP-prefix-log decoding and clearing for VF26-VF28.
- Virtualization tests should cover PF/VF policy boundaries, guest config-space access, ATS/ARI enablement, and absence of unexpected AER storms, lost interrupts, or VF isolation failures.

## Unresolved Cross-Chunk References

Line 76009 starts after earlier VF26 fields; the preceding chunk is needed for VF26 `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, and `REVISION_ID`. Line 78432 ends inside VF29 `MSI_MSG_CNTL`; the following chunk is needed for the rest of VF29 MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions.
