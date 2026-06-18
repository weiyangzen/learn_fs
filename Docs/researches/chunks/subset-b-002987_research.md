# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 64307-66765

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,117 `#define` field-layout macros across 2,459 source lines. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range starts in the tail of the `BIF_CFG_DEV0_RC1_*` PCIe root-complex capability layout, beginning with the control fields for Access Control Services and continuing through Data Link Feature, 16 GT/s and 32 GT/s PHY/equalization, lane margining, Alternate Protocol, and Readiness Time Reporting registers. It then switches at the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block to the `BIF_CFG_DEV0_EPF0_1_*` endpoint function 0 PCI configuration-space template. The endpoint block covers conventional PCI identity/resource registers, PM/PCIe/MSI/MSI-X/VSEC/VC/DSN/AER/BAR/PWR/DPA/ACS/PASID/MC/LTR/ARI/SR-IOV capability fields, Data Link Feature and 16 GT/s PHY fields, and most of the endpoint lane-margining sequence. The source boundary is artificial: it starts after earlier RC1 ACS capability definitions and ends after only the first field of `BIF_CFG_DEV0_EPF0_1_LANE_15_MARGINING_LANE_CNTL`.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 hardware register interface. For each named register or PCI configuration-space word, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used to position a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion `nbio_4_3_0_offset.h` supplies matching register/config offsets. Runtime AMDGPU code combines the offset macros with these shift/mask macros through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 addressing helpers, and NBIO or PCI configuration accessors.

This chunk specifically documents the software-visible bit layout for PCIe root-complex and endpoint-function configuration structures in NBIO. The represented fields control or report link training, lane equalization, lane margining, PCI command/status, BARs, interrupt delivery, error reporting, power management, traffic classes/virtual channels, isolation controls, PASID/ARI/SR-IOV virtualization features, and readiness timing.

## Important Macro Families

The initial `BIF_CFG_DEV0_RC1_*` portion covers later root-complex extended capabilities:

- `PCIE_ACS_CNTL` enables or configures source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, egress control, direct translated P2P, I/O request blocking, downstream/upstream memory target access, and unclaimed-request redirect behavior.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` expose Data Link Feature capability metadata, local feature support, exchange enablement, remote feature support, and remote support validity.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, and parity mismatch status registers describe 16 GT/s PHY capability metadata, equalization completion/phase state, link equalization requests, and local/RTM parity mismatch status.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` provide downstream/upstream 16 GT/s TX preset fields per lane.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_LANE_{CNTL,STATUS}` through `LANE_15_MARGINING_LANE_{CNTL,STATUS}` define software-controlled lane margining readiness and per-lane receiver number, margin type, usage model, and payload/status fields.
- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, `LINK_STATUS_32GT`, modified training sequence data, and `LANE_0_EQUALIZATION_CNTL_32GT` through `LANE_15_EQUALIZATION_CNTL_32GT` provide the analogous PCIe 5.0/32 GT/s capability, control, status, modified TS, and per-lane preset layout.
- `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA1`, `AP_DATA2`, and `AP_SEL_EN_MASK` cover Alternate Protocol capability/control/data fields, including capability identification, alternate protocol selection, reset behavior, enablement, and selected lane mask bits.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` define Readiness Time Reporting metadata and timing fields for reset, data-link-up, FLR, and D3hot-to-D0 transition timing, plus a validity bit.

The `BIF_CFG_DEV0_EPF0_1_*` endpoint-function portion starts a full PCI/PCIe configuration image:

- Conventional PCI header fields: vendor/device ID, command, status, revision, programming interface, subclass, base class, cache-line size, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, maximum latency, and a vendor capability header.
- PCI command/status bits: I/O and memory access enables, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, fast back-to-back, interrupt disable, immediate readiness, interrupt status, capability-list presence, DEVSEL timing, target/master abort reporting, system-error signaling, and parity error detection.
- Power Management capability fields: PM capability list header, version, PME support, D-state support, auxiliary current, power-state control, PME enable/status, data select/scale, bus-power enable, and PMI data.
- PCIe base capability fields: capability header, PCIe version, device/port type, slot implementation, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Device and link controls: correctable/non-fatal/fatal/unsupported request reporting enables, relaxed ordering, max payload, extended tags, phantom functions, auxiliary power PM, no-snoop, max read request size, FLR initiation, ASPM, link retrain/disable, common clock, extended sync, bandwidth-management interrupts, target speed, compliance, de-emphasis, equalization status, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, emergency power reduction, ten-bit tags, and end-to-end TLP prefix blocking.
- MSI/MSI-X fields: capability metadata, MSI enable and multiple-message state, 32-bit and 64-bit message address/data, masks, pending bits, MSI-X table size/function mask/enable, and MSI-X table/PBA BIR and offset fields.
- PCIe vendor-specific, Virtual Channel, Device Serial Number, Advanced Error Reporting, BAR, Power Budgeting, Dynamic Power Allocation, and Secondary PCIe capabilities.
- AER fields: uncorrectable status/mask/severity bits, correctable status/mask bits, first-error pointer, ECRC generation/check capability and enablement, multi-header receive controls, TLP prefix log presence, completion-timeout log capability, header logs, and TLP prefix logs.
- BAR and power capabilities: BAR1 through BAR6 capability/control masks for BAR size and enablement, power-budget selection/data/capability, DPA capability/status/control, latency indicator, and per-substate power allocation.
- PCIe Secondary and lane equalization fields: link control 3, lane error status, and per-lane 8 GT/s downstream/upstream TX preset and RX preset hint fields for lanes 0 through 15.
- Isolation and virtualization features: ACS capability/control, PASID capability/control, multicast capability/control/address/receive/block masks, LTR capability, ARI capability/control, and SR-IOV capability/control/status/resource fields including VF counts, offsets, stride, VF device ID, page sizes, VF BARs, and migration-state array offset.
- Endpoint DLF/16 GT/s/lane-margining fields: Data Link Feature metadata/status, 16 GT/s PHY metadata/status/equalization/parity fields, per-lane 16 GT/s presets, margining readiness, and per-lane margin control/status fields through the chunk's truncated `LANE_15_MARGINING_LANE_CNTL` start.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace. Consumers rely on the generated register names, field names, shifts, and masks staying synchronized with offsets and hardware behavior.

The constants are untyped preprocessor integer literals, generally with an `L` suffix. They encode bit positions and bit masks only. They do not encode register access width, reset value, read/write permissions, write-one-to-clear behavior, privilege requirements, ordering constraints, or side effects. Callers must know from the hardware specification and access path whether a field is read-only capability data, writable policy, sticky error status, W1C status, diagnostic log data, or a command bit that triggers hardware behavior.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU, SMU, PCIe, SR-IOV, virtualization, or display code selects an NBIO register or PCI configuration-space offset from the companion offset header.
2. The code reads a hardware value, extracts fields with the `__SHIFT` and `_MASK` constants, or composes an updated value through field helpers.
3. The decoded value drives policy or diagnostics, or the composed value is written back to hardware.

Likely flows using fields from this chunk include PCI enumeration, endpoint resource assignment, BAR sizing and enablement, memory access and bus-mastering setup, MSI/MSI-X interrupt programming, PCIe link training and equalization diagnostics, lane margining, 16 GT/s and 32 GT/s feature negotiation, AER collection/masking/clearing, power-management transitions, virtual-channel/resource setup, ACS/PASID/ARI/SR-IOV virtualization policy, VF resource exposure, multicast filtering, and readiness-time reporting.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCIe root-complex and endpoint-function configuration registers. Persistence is determined by the GPU/NBIO reset domain, PCI configuration reset, function-level reset, suspend/resume save-restore, firmware initialization, PF/VF management, hypervisor policy, and explicit driver writes.

Represented state includes static PCI identity/capability information, host-programmed command bits, BAR and ROM resource windows, interrupt routing and MSI/MSI-X message state, PCIe device/link controls, link/device status, equalization outcomes, per-lane presets and margining controls, AER status/mask/severity/log registers, power-management settings, virtual-channel resource controls, ACS/PASID/ARI/SR-IOV virtualization state, VF resource windows, multicast address/blocking state, and readiness timing data.

Several fields have side effects or non-storage semantics. `BUS_MASTER_EN` and `MEM_ACCESS_EN` gate DMA and MMIO decode; `INITIATE_FLR` starts a function-level reset; link retrain/disable controls affect PCIe link state; MSI/MSI-X enables and masks affect interrupt delivery; AER status/log bits may be sticky or write-one-to-clear; ACS/PASID/ARI/SR-IOV controls affect isolation and address routing; and lane margining/equalization fields interact with live PHY training state. The generated file only supplies bit layout, so call sites must provide ordering, privilege, and reset handling.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 4.3.0 register database and must stay aligned with sibling generated headers:

- `nbio_4_3_0_offset.h` supplies matching `reg...`/`cfg...` offsets for the register names in this file.
- Other generated NBIO 4.3.0 headers provide related defaults and register metadata where present.
- AMDGPU register helper macros consume these field constants for extraction and update.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU 13 power-management files such as `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`. The surrounding AMDGPU stack integrates these definitions with PCI probing, GPU reset, interrupt setup, power management, SR-IOV/PF/VF handling, link management, error reporting, and diagnostics.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem control flow.

## Risks And Edge Cases

- Generated mask or shift drift can compile cleanly while causing software to read, preserve, clear, or set the wrong hardware bit. This is most dangerous for command, DMA enable, interrupt, FLR, AER, ACS, PASID, ARI, SR-IOV, link-control, and lane-training fields.
- The chunk starts and ends mid-family. The previous chunk is needed for complete RC1 ACS context, and the next chunk is needed for the rest of endpoint lane 15 margining plus any later endpoint capability fields.
- Repeated per-lane definitions are intentionally mechanical. A single lane-specific mismatch can indicate register database or generator drift, but chunk-boundary truncation must not be misread as a real lane mismatch.
- PCI command and BAR masks affect resource decode and bus mastering. Incorrect values can break probing, expose the wrong MMIO window, or enable DMA at the wrong time.
- MSI/MSI-X address/data/mask/pending fields affect interrupt routing. Incorrect masks can produce lost, repeated, or misrouted interrupts.
- AER status and log fields are diagnostic evidence. Treating sticky/W1C status fields as ordinary writable state can lose error evidence or fail to quiesce an error condition.
- ACS, PASID, ARI, multicast, and SR-IOV fields affect isolation, routing, and VF resource exposure. Incorrect masks can break VF discovery, IOMMU/PASID behavior, or peer-to-peer isolation assumptions.
- Link equalization, margining, and 16/32 GT/s controls interact with live PCIe PHY state. Wrong field definitions can produce misleading link diagnostics or unstable retrain/margining flows.
- Readiness timing fields should only be trusted when their validity bits and capability metadata indicate usable data; under-waiting after reset, FLR, or D-state transitions can cause probe or resume races.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Direct macro users should catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks within registers, capability-list continuity, per-lane repetition checks, and EPF0_1/SR-IOV field consistency.
- Runtime probe on affected AMD GPUs should show stable PCI enumeration, correct vendor/device/class/capability data, sane BAR sizing, and correct command-bit transitions for memory access and bus mastering.
- Interrupt validation should exercise MSI and MSI-X enablement, table/PBA offsets, masking, pending bits, and absence of lost or spurious interrupts.
- PCIe health validation should cover negotiated speed/width, 8/16/32 GT/s equalization status, link retrain behavior, lane error status, lane margining readiness/status, and absence of unexpected AER storms.
- Error-injection or fault-observation tests should confirm AER status/mask/severity/log fields decode correctly and that diagnostic logs are not unintentionally cleared.
- Virtualization tests should cover ACS isolation, PASID enablement, ARI routing, SR-IOV VF counts/strides/BARs/page sizes, VF enumeration, FLR timing, and PF/VF reset behavior.
- Power-management and readiness tests should compare advertised reset/DL-up/FLR/D3hot-to-D0 timing fields against actual wait paths and verify validity bits are honored.
