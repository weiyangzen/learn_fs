# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 91172-93606

## Scope

This chunk covers generated AMD NBIO 2.3 shift/mask definitions for the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, specifically the `_1` instance of `BIF_CFG_DEV0_EPF0`. It begins inside the `BIF_CFG_DEV0_EPF0_1_COMMAND` field definitions, then covers EPF0_1 PCI configuration header fields, PCI/PCIe capabilities, MSI/MSI-X, extended PCIe capabilities, link equalization and margining, SR-IOV and VF BAR controls, and AMD vendor-specific GPUIOV fields through the first `GPUIOV_UVD1SCH_DW0` shift macro.

The chunk is data-only C preprocessor material. It declares no functions, structs, variables, locks, allocation paths, or direct register accesses. Its interface is the standard generated pair convention:

- `<REGISTER>__<FIELD>__SHIFT` for a field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field mask.

Within this line range there are 2,097 `#define` entries across 339 register groups, nearly all forming shift/mask pairs.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield-layout side of the NBIO 2.3 hardware ABI. The matching `nbio_2_3_offset.h` header supplies the register/config-space addresses, and AMDGPU register helpers combine those offsets with these masks when composing writes or decoding reads.

This chunk describes the PCIe configuration surface for EPF0 function instance 1. It includes conventional PCI fields such as command/status, identity/class/header registers, BARs, ROM BAR, adapter/subsystem ID, interrupt line/pin, and capability pointers. It then describes PCIe capability and extended-capability fields for power management, link/device controls, MSI/MSI-X, virtual channels, device serial number, AER, resizable BARs, power budget, DPA, secondary PCIe, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s PHY, lane margining, VF resizable BAR, and AMD GPUIOV.

These definitions matter because EPF0_1 appears to expose a PCIe endpoint/function configuration image whose bit layout must be shared by the driver, firmware, hardware, PCI core, virtualization paths, and diagnostic tooling. A caller cannot use this header alone to access hardware, but every caller that programs or reports these fields depends on its masks being exact.

## Important Macro Families

### PCI Header and Base Capability Fields

The first portion covers `BIF_CFG_DEV0_EPF0_1_COMMAND` and `STATUS`, revision and class-code fields, cache-line/latency/header/BIST fields, BARs 1-6, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency. Command bits include I/O access, memory access, bus mastering, SERR, parity response, and interrupt disable. Status bits include capability-list presence, interrupt status, target/master abort status, system error, and parity detection.

Power management and PCIe capability fields follow:

- `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define PM capability list linkage, D-state support, PME support/enables/status, data select/scale, bus power, and power-state fields.
- `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` define endpoint type, payload/read-request sizing, error-report enables, relaxed ordering/no-snoop, FLR initiation, AUX power, transaction pending, and related device capabilities.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` define supported/current speed and width, ASPM/L0s/L1 behavior, clock and bandwidth controls, retraining, link disable, common clock, slot clock, compliance, and bandwidth status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` expose PCIe 2+ feature bits such as completion timeout support/control, LTR, atomic operations, ARI forwarding, ID-based ordering, OBFF, emergency power reduction, ten-bit tags, TLP prefix blocking, supported link-speed vector, target speed, equalization controls/status, crosslink, and downconfigure status.

### Interrupt and Vendor/Virtual-Channel Capabilities

MSI and MSI-X definitions include capability-list linkage, message control, 32-bit and 64-bit message address/data layouts, mask and pending registers, MSI-X table fields, and pending-bit-array fields. The presence of both regular and `_64` message-data/mask/pending families reflects layout-dependent interpretation of the MSI capability, not independent interrupt mechanisms.

The non-GPUIOV vendor-specific and virtual-channel sections include `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, `PCIE_VENDOR_SPECIFIC2`, `PCIE_VC_ENH_CAP_LIST`, port VC capabilities/control/status, and VC0/VC1 resource capability/control/status fields. These cover extended capability IDs/versions/next pointers, vendor capability metadata, low-priority and reference-clock VC counts, arbitration table offsets, TC/VC mapping, load table controls, arbitration select, and negotiation status.

### Error Reporting, BAR, Power, and Link Training Extensions

The AER block defines uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control fields, four header-log dwords, and four TLP-prefix-log dwords. Important field families include data link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, receiver error, bad TLP/DLLP, replay rollover, advisory non-fatal, corrected internal error, and header-log overflow.

Resizable BAR, power budget, and DPA definitions cover BAR1-BAR6 capability/control fields, power budget data selection and reporting, DPA capability, DPA latency/status/control, and eight DPA substate power allocation registers.

Secondary PCIe and PHY/link-training definitions include `PCIE_LINK_CNTL3`, lane error status, per-lane 8 GT/s equalization control for lanes 0-15, 16 GT/s enhanced capability linkage, 16 GT/s link capability/control/status, parity mismatch status fields, and per-lane 16 GT/s equalization control for lanes 0-15. These fields describe preset/hint values, equalization phase success, retimer/link-equalization request status, and lane-level training diagnostics.

### Isolation, Address Translation, and Virtualization Fields

ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, and data-link feature blocks define a broad PCIe virtualization and fabric-integration surface:

- `PCIE_ACS_CAP` and `PCIE_ACS_CNTL` expose source validation, translation blocking, peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size/control fields.
- `PCIE_ATS_CAP` and `PCIE_ATS_CNTL` expose invalidation queue depth, page-aligned request support, small-page invalidation, and ATS enable/STU fields.
- `PCIE_PAGE_REQ_*`, outstanding page request capacity/allocation, `PCIE_PASID_*`, multicast, LTR, and ARI blocks describe address-translation participation, PASID width and modes, multicast address/blocking state, snoop/no-snoop latency encoding, and alternative routing ID forwarding/function-group behavior.
- `PCIE_SRIOV_*` fields define SR-IOV capability/control/status, initial/total/current VF counts, dependency link, first VF offset, VF stride, VF device ID, page sizes, VF BAR base-address fields, and migration state array offset.
- `PCIE_TPH_REQR_*` and data-link feature fields define TPH requester capabilities/control and data-link feature exchange support/status.

### Lane Margining and GPUIOV

The PCIe margining block contains a port capability/status pair and per-lane lane-margining control/status pairs for lanes 0-15. Each lane pair has receiver number, margin type, usage model, and payload fields, with status variants reporting the resulting receiver/type/model/payload.

VF resizable BAR definitions cover VF BAR1-BAR6 capability/control fields. The AMD GPUIOV vendor-specific block then exposes a second vendor-specific extended capability header, a GPUIOV-specific header, an SR-IOV shadow field, interrupt enable/status bits for guest/PF/VF FLR and doorbell events, reset control, hypervisor/VM mailbox dwords, context, total framebuffer, offsets, region selection, P2P-over-XGMI enablement, per-VF framebuffer size/offset pairs for VF0 through VF30, and scheduler descriptor dwords for UVD, VCE, and GFX. The chunk ends at `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW0__DW0__SHIFT`; the matching mask and later UVD1 scheduler dwords continue outside this chunk.

## Control Flow

There is no executable control flow in this header. Runtime behavior is entirely external:

1. AMDGPU or related code includes the NBIO 2.3 offset, default, and shift/mask headers.
2. Code chooses a register address from `nbio_2_3_offset.h` and a field mask/shift from this header.
3. Helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_*`, `WREG32_*`, or PCIe index/data accessors shift, mask, read, and write the field.
4. Hardware, firmware, the Linux PCI core, or a virtualization manager observes the resulting PCIe configuration or vendor-specific state.

Because this chunk represents PCIe configuration-space and vendor-specific capability fields, not ordinary driver-owned memory, many side effects are defined by PCIe/NBIO hardware semantics rather than C control flow.

## State and Persistence Behavior

The macros are compile-time constants and have no local persistence. The state they name is hardware-visible NBIO/PCIe configuration state. Persistence depends on the owning register:

- PCI identity, class, header, capability-chain, capability support, BAR capability, supported link speed/width, supported page size, and similar capability fields are generally read-only or read-mostly values established by hardware straps, firmware, or configuration logic.
- Command, PM status/control, device/link control, MSI/MSI-X control, VC control, ACS/ATS/PASID/ARI/SR-IOV control, TPH control, DPA control, margining control, VF resize BAR control, GPUIOV interrupt enable, reset control, framebuffer partitioning, P2P-over-XGMI, and scheduler fields are mutable hardware configuration state.
- Status/log fields such as PCI status, device/link status, AER status, AER header/TLP prefix logs, VC status, DPA status, lane error status, 16 GT/s equalization/parity status, margining status, data-link feature status, SR-IOV status, page request status, and GPUIOV interrupt status are transient diagnostic or event state.
- Reset, FLR, GPU reset, VF teardown, power transitions, firmware ownership changes, and hypervisor actions can clear or reinitialize many fields. The header does not encode save/restore ordering or ownership rules.

Several fields are command-like or write-one-to-clear in PCIe-style hardware, including FLR initiation, link retraining, AER and PCI status bits, interrupt status, page request status, and possibly lane/error logs. The masks only identify bit positions; callers need the hardware specification and owning subsystem policy before writing them.

## Dependencies and Integration Points

Direct dependencies:

- `nbio_2_3_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_1_*` addresses for these field definitions.
- `nbio_2_3_default.h` supplies reset/default values for the same generated hardware family.
- AMDGPU register helpers and SOC15/PCIe accessors supply the actual read/modify/write mechanics.
- Linux PCI/PCIe semantics define many standard fields mirrored here: PM, PCIe capability, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, LTR, ARI, SR-IOV, TPH, VC, DPA, resizable BAR, lane equalization, and margining.

Observed source-tree integration for this header family includes AMDGPU NBIO 2.3 code and virtualization/SMU platform code that include `nbio_2_3_sh_mask.h` alongside offset/default headers. The specific EPF0_1 definitions align with `cfgBIF_CFG_DEV0_EPF0_1_*` entries in `nbio_2_3_offset.h`, including the GPUIOV block beginning around the `0xfffe10200504` configuration-space region.

Integration-sensitive areas include:

- PCI core ownership of command/status, BAR sizing, PM, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, SR-IOV, and link-control policy.
- AMDGPU NBIO initialization and power-management flows that may read or program PCIe link, LTR, ASPM, DPA, and data-link feature state.
- SR-IOV and GPUIOV PF/VF lifecycle code, including VF enumeration, VF BAR exposure, FLR/reset handling, mailbox signaling, interrupt routing, framebuffer partitioning, and per-engine scheduling descriptors.
- Diagnostics and debug tooling that decode AER, lane equalization, lane margining, parity mismatch, data-link feature, and GPUIOV interrupt/status registers.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can silently modify an adjacent PCIe/NBIO bit while compiling cleanly.
- Register/address mismatches are easy. These macros do not carry addresses; callers must pair `BIF_CFG_DEV0_EPF0_1_*` masks with the matching `cfgBIF_CFG_DEV0_EPF0_1_*` offsets.
- EPF/function suffixes matter. `EPF0_1` definitions are mechanically similar to neighboring EPF0, EPF1, and VF blocks; using the wrong suffix can target the wrong endpoint/function image.
- PCI core policy conflicts can occur if AMDGPU directly writes MSI/MSI-X, AER, ACS, ATS, PASID, SR-IOV, BAR, PM, or link-control fields outside a coordinated path.
- Status and log fields can be destructive to write. PCI status, AER status/logs, page request status, GPUIOV interrupt status, and lane diagnostics may use write-one-to-clear or capture-first-error behavior.
- Link training and margining fields are timing-sensitive. Equalization presets, target speed, retraining, compliance, lane margining payloads, and 16 GT/s controls can destabilize the PCIe link if changed outside expected link states.
- Virtualization fields are isolation-sensitive. SR-IOV, ATS/PASID/PRI, ACS, GPUIOV mailbox, framebuffer partitioning, reset, interrupt, P2P-over-XGMI, and scheduler fields can affect guest isolation, DMA translation, and active VF workloads.
- Chunk boundaries are partial. The first `COMMAND` comment and field start are before line 91172, and the UVD1 scheduler block continues after line 93606. File-level conclusions need reconciliation with neighboring chunks.

## Test and Validation Signals

Useful validation for changes touching this chunk or callers of its macros includes:

- Build coverage for AMDGPU code paths that include `nbio_2_3_sh_mask.h` with the matching NBIO 2.3 offset/default headers.
- Static generated-header checks comparing `BIF_CFG_DEV0_EPF0_1_*` field names against `cfgBIF_CFG_DEV0_EPF0_1_*` offsets and neighboring generated NBIO revisions to catch missing fields, suffix drift, and mask-width changes.
- PCIe enumeration checks with `lspci -vv` or equivalent should show sane command/status, BARs, PM, PCIe, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, LTR, ARI, SR-IOV, resizable BAR, and link capability data.
- Link tests should verify negotiated speed/width, ASPM/LTR behavior, retraining, equalization, 16 GT/s status, lane error status, and margining readiness across boot, suspend/resume, runtime power management, and GPU reset.
- SR-IOV/GPUIOV tests should cover VF creation/removal, VF BAR sizing, VF memory-space enablement, FLR/reset handling, mailbox traffic, per-VF framebuffer partition reporting, interrupt enable/status behavior, and guest driver load/unload.
- Error-injection or fault-observation tests should verify AER uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, PCI status bits, and clear behavior.
- Interrupt tests should validate MSI/MSI-X message programming, mask/pending behavior, table/PBA interpretation, and interaction with GPUIOV interrupt status.
- Power-management tests should watch DPA, PM state, LTR, OBFF, ASPM, data-link feature, and link low-power behavior for latency or stability regressions.

## Unresolved Cross-Chunk References

Line 91172 starts after the beginning of the `BIF_CFG_DEV0_EPF0_1_COMMAND` field list, so earlier command fields and the `addressBlock` marker are immediately before this chunk. Line 93606 ends at the `GPUIOV_UVD1SCH_DW0` shift definition; the matching mask and additional UVD1 scheduler dwords continue in the next chunk. The final per-file document should stitch those boundaries before making complete claims about the full EPF0_1 map.
