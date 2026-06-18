# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 24400-26849

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 2.3 register mask header. The range starts in the `BIF_CFG_DEV0_EPF1` PCIe power-budget extended capability block and continues through the beginning of the `BIF_CFG_DEV0_EPF2` Dynamic Power Allocation capability. It contains preprocessor constants only: no C functions, structs, runtime storage, or executable control flow are defined here.

The covered register families are:

- `BIF_CFG_DEV0_EPF1` PCIe power budget, Dynamic Power Allocation, secondary PCIe, lane equalization, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data link feature, 16 GT/s PHY, lane margining, VF resizable BAR, and AMD GPUIOV vendor-specific capability fields.
- `BIF_CFG_DEV0_EPF2` PCI config header fields, conventional capability list entries, PMI, PCIe capability, MSI/MSI-X, SATA, vendor-specific scratch, Advanced Error Reporting, resizable BAR, power budget, and the opening DPA capability fields.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and NBIO 2.3 PCIe configuration-space registers. Each field is expressed as the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate the field in a 16-bit or 32-bit register image.

The actual register addresses live in the sibling generated offset headers such as `nbio_2_3_offset.h`; this file supplies the field layout. Driver code consumes these definitions through AMD register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG8`, and `WREG8`. Observed include sites for this mask header include `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU power-management files under `pm/swsmu/smu11`.

## Important Macro Families

### EPF1 PCIe Power and Link Capabilities

The first part of the chunk completes EPF1 PCIe power-related extended capabilities. `BIF_CFG_DEV0_EPF1_PCIE_PWR_BUDGET_*` defines power-budget data selection, base power, data scale, PM state/substate, type, rail, and system-allocated status. `BIF_CFG_DEV0_EPF1_PCIE_DPA_*` defines Dynamic Power Allocation capability metadata, maximum substates, transition latency units/values, power-allocation scale, current substate status, substate control enablement, and eight substate power allocation bytes.

The secondary PCIe and link-training section defines `PCIE_LINK_CNTL3`, lane error status, and per-lane `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`. Each lane equality-control register repeats downstream/upstream TX preset and RX preset-hint fields, with reserved high bits. These constants support PCIe Gen3-style equalization management and diagnostics.

### EPF1 Isolation, Translation, and Addressing Extensions

The chunk defines several PCIe extended capabilities that are central to IOMMU, virtualization, and peer-to-peer behavior:

- ACS capability/control fields for source validation, translation blocking, request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-vector size.
- ATS capability/control fields for invalidate queue depth, page-aligned request, global invalidate support, smallest translation unit, and ATC enable.
- PRI/page request fields for enable/reset, response failure, unexpected group index, stopped state, PASID-required responses, outstanding capacity, and outstanding allocation.
- PASID capability/control fields for execute permission, privileged mode, maximum PASID width, and enable bits.
- Multicast capability/control, address, receive, block-all, and block-untranslated fields.
- LTR latency value/scale fields for snooped and non-snooped latency tolerance.
- ARI capability/control fields for function-group support, next-function number, ARI group enablement, and function-group selection.

These are hardware-visible policy and capability fields rather than ordinary software state. Incorrect bit positions in these macros would affect PCIe isolation, translation, and function routing.

### EPF1 SR-IOV, VF BAR, and High-Speed Link Features

The EPF1 SR-IOV section maps capability, control, status, VF count, VF offset/stride, VF device ID, supported/system page sizes, six VF BAR base addresses, and migration-state-array offset. The VF resizable BAR section later repeats BAR1 through BAR6 capability/control patterns with supported size, BAR index, BAR total number, and BAR size fields.

The chunk also contains:

- TPH requester capability/control fields, including ST-table location/size and requester enable.
- Data Link Feature capability/status fields for DL feature exchange, remote valid, remote scale, and local/remote DLF support.
- PCIe 16 GT/s PHY extended capability fields for supported 16 GT/s data rate, 16 GT/s enablement, equalization complete/in-progress/failure state, per-lane equalization control, and parity mismatch status.
- PCIe lane margining capability/status and per-lane control/status registers for lanes 0-15. Each lane has receiver number, margin type, usage model, and payload fields, with matching status fields.

These fields are integration points for link training, diagnostics, PCIe speed negotiation, and VF memory exposure.

### EPF1 AMD GPUIOV Vendor-Specific Capability

The most AMD-specific part of the chunk is `BIF_CFG_DEV0_EPF1_PCIE_VENDOR_SPECIFIC_*_GPUIOV`. It describes an AMD vendor-specific extended capability for GPU I/O virtualization:

- Capability and VSEC headers expose capability ID/version/next pointer and VSEC ID/revision/length.
- `SRIOV_SHADOW` mirrors VF enable and VF number state.
- `INTR_ENABLE` and `INTR_STATUS` define per-engine interrupt bits for GFX, UVD, UVD1, and VCE command completion, self-recovered hangs, hangs requiring FLR, VM busy transitions, plus HVVM mailbox transmit-ack and receive-valid interrupts.
- `RESET_CONTROL` exposes a `SOFT_PF_FLR` bit.
- `HVVM_MBOX_DW0` selects a VF index and carries transmit/receive message data plus valid/ack bits.
- `HVVM_MBOX_DW1` maps transmit-ack and receive-valid bits for VF0 through VF15; `HVVM_MBOX_DW2` maps the same state for VF16 through VF30 plus PF transmit-ack and receive-valid bits.
- `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `REGION`, and `P2P_OVER_XGMI_ENABLE` describe context size/location/offset, total frame-buffer availability/consumption, scheduler block offsets, local frame-buffer region limits, and per-VF/PF P2P-over-XGMI enablement.
- `VF0_FB` through `VF30_FB` repeat a 16-bit VF frame-buffer size plus 16-bit offset layout for per-VF memory partitioning.
- Scheduler dword windows for `UVDSCH`, `VCESCH`, `GFXSCH`, and `UVD1SCH` each expose raw `DW0` through `DW8` fields.

This section lines up with the MxGPU virtualization layer. The local source tree's `amdgpu/mxgpu_nv.c` includes this header and implements mailbox send/ack/valid flows using NBIO mailbox-related registers. The exact GPUIOV fields in this chunk are PF/VF coordination surfaces and should be treated as privileged virtualization state.

### EPF2 PCI Config Header and Standard Capabilities

At `// addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, the chunk switches to endpoint function 2. It defines the standard PCI config header fields:

- Vendor/device ID, command, status, revision ID, class-code bytes, cache-line size, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem IDs, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- Command bits for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, fast back-to-back, and interrupt disable.
- Status bits for immediate readiness, interrupt status, capability list, parity and abort status, DEVSEL timing, system error, and detected parity error.

It then defines vendor, power-management, and PCIe capability list entries. The PMI fields cover supported power states, PME, data select/scale, bus power enable, and PMI data. The PCIe capability fields include device/port type, slot, interrupt message number, device capabilities, device control/status, link capabilities/control/status, device capabilities/control/status 2, and link capabilities/control/status 2.

### EPF2 MSI, MSI-X, SATA, AER, BAR, Power Budget, and DPA

The EPF2 interrupt capability section defines MSI and MSI-X capability list metadata, MSI enable/multiple-message/64-bit/per-vector masking fields, MSI address/data/mask/pending fields, MSI-X table size/function mask/enable, and MSI-X table/PBA BAR indicator plus offset.

The SATA capability block defines SATA capability version, BAR location/offset, indirect data port index, and data masks. The EPF2 vendor-specific block exposes a VSEC header plus two 32-bit scratch registers.

The Advanced Error Reporting block defines:

- Extended capability header metadata.
- Uncorrectable error status, mask, and severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, multicast blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.
- Correctable error status/mask bits for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header log overflow.
- AER capability/control fields for first error pointer, ECRC generation/check capabilities/enables, multi-header receive capability/enable, TLP prefix log presence, and completion timeout log capability.
- Header log and TLP prefix log dwords.

The chunk closes with EPF2 resizable BAR1-BAR6 capability/control fields, power budget fields matching EPF1, and the start of EPF2 DPA capability metadata and `DPA_CAP` field definitions.

## Control Flow and State Behavior

This header chunk has no runtime control flow. Its effect is compile-time: it determines how C code composes writes and decodes reads for NBIO PCIe configuration registers.

The persistent state described by the macros is hardware state. Important state includes PCI command/status bits, link speed/width/equalization state, power-management and DPA settings, ACS/ATS/PRI/PASID enablement, SR-IOV VF counts and VF BAR exposure, per-VF framebuffer partitioning, GPUIOV mailbox and interrupt state, MSI/MSI-X address/data/mask state, AER error status/masks/severity, and resizable BAR sizes.

Several fields are status or event latches, not durable configuration. Examples include PCI status errors, EPF1 DPA status, lane error/equalization/margining status, GPUIOV interrupt status, HVVM mailbox ack/valid fields, MSI pending bits, AER status/header logs, and link status. Other fields are command-like or enable bits, such as PCI bus mastering, ATS/PRI/PASID enables, SR-IOV VF enablement, soft PF FLR, link retrain, MSI/MSI-X enable, and AER ECRC enablement. Consumers must follow the owning hardware and driver sequencing; this generated header does not encode ordering, locking, posted-write flushes, or timeout policy.

## Dependencies and Integration Points

The chunk depends on the AMD generated register-header convention:

- `nbio_2_3_offset.h` supplies register offsets and base indices for these field names.
- `nbio_2_3_default.h` supplies generated reset/default values where present.
- AMDGPU helper macros consume these `__SHIFT` and `_MASK` definitions to avoid hard-coded bit positions.

Observed include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes the NBIO 2.3 offset/default/mask headers and configures NBIO memory access, doorbells, interrupt handling, link behavior, and other NBIO state.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes this mask header and implements SR-IOV/MxGPU mailbox request, ack, polling, and reset-access flows.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include this header for NBIO/PCIe-related power-management integration.

The macros are tightly coupled to PCIe core behavior, Linux PCI enumeration and capability handling, AMDGPU PF/VF virtualization, the interrupt subsystem, SMU power policy, and AER diagnostics. Cross-generation headers such as `nbio_7_2_0_sh_mask.h` and `nbif_6_3_1_sh_mask.h` contain similar names but are not guaranteed to have identical layouts or supported fields.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can silently program the wrong PCIe capability bit, changing bus mastering, memory access, interrupts, link training, isolation, or error reporting.
- Virtualization fields are security-sensitive. ACS, ATS, PRI, PASID, SR-IOV, GPUIOV mailbox, per-VF frame-buffer partition, and P2P-over-XGMI fields affect VF isolation and PF/VF coordination.
- Status and write-clear semantics are not visible in the macros. Code using AER, PCI status, interrupt status, mailbox ack/valid, or lane diagnostics must know whether hardware expects write-one-to-clear, polling, or explicit acknowledgement.
- Link-training and margining fields can destabilize PCIe connectivity if programmed outside the intended sequence.
- Cross-generation copy/paste is risky. Similar macro names across NBIO/NBIF generations may hide layout differences, additional reserved bits, or different endpoint/function coverage.
- Raw 32-bit scheduler dword and scratch fields provide little semantic validation in the header. Higher-level code must validate ownership, engine type, VF number, and firmware expectations before writing them.

## Test Signals

Useful validation signals for code that depends on this chunk include:

- Build coverage for all include sites, especially `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 power-management files, to catch renamed or malformed macros.
- PCI enumeration on NBIO 2.3 hardware showing correct vendor/device/class, capability pointer chains, MSI/MSI-X capability state, PCIe link capability/status, and AER capability presence.
- SR-IOV/MxGPU tests that create VFs, verify VF count/stride/BAR sizing, exercise mailbox send/ack/receive-valid paths, and confirm VF framebuffer partitions match expected size/offset values.
- Link diagnostics that confirm negotiated link width/speed, lane equalization, 16 GT/s status, lane margining status, and absence of unexpected lane error bits.
- AER injection or fault-observation tests that validate uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs.
- Power-management tests that cover PMI, power-budget, DPA substate, LTR, and SMU integration without regressions in suspend/resume, runtime power transitions, or link power management.
