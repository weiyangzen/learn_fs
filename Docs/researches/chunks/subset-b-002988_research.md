# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 66766-69194

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains preprocessor constants only: no C functions, structs, enums, variables, allocations, locks, or executable statements.

The range starts in the final fields for `BIF_CFG_DEV0_EPF0_1_LANE_15_MARGINING_LANE_CNTL`, covers the lane-15 margining status, VF resizable BAR capability registers, PCIe 32 GT/s capability/control/status fields, per-lane 32 GT/s equalization presets, Alternate Protocol and RTR capability fields, complete SR-IOV `VF0_1` and `VF1_1` PCI configuration templates, and the beginning of `VF2_1` through AER header/TLP prefix logs and the first ARI enhanced-capability fields. The source boundary is artificial: preceding lane-margining fields and the rest of VF2 ARI/RTR fields are outside this chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of the NBIO 4.3.0 hardware register interface. For each named NBIO or PCI configuration register, it defines:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit used to pack or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update the field.

The companion offset header provides the register/config-space addresses. AMDGPU code combines the offset and shift/mask headers through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 register accessors, and PCI/NBIO configuration-space paths.

This chunk mainly describes PCIe capability layout for NBIO device 0, endpoint function 0, including physical-function capability extensions and SR-IOV virtual-function configuration images. It is hardware metadata; although it lives under a `ceph-client` source mirror, it has no direct distributed-filesystem behavior.

## Important Macro Families

The physical-function `BIF_CFG_DEV0_EPF0_1_*` tail covers late PCIe 5.0 style capability blocks:

- Lane 15 margining fields expose receiver number, margin type, usage model, and margin payload status for PCIe lane margining.
- `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST` plus `PCIE_VF_RESIZE_BAR[1-6]_CAP/CNTL` describe VF resizable BAR support, selected BAR index, total BAR count, programmed BAR size, and upper supported-size bits.
- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT` describe 32 GT/s equalization behavior, no-equalization-needed signaling, modified training sequence modes, transmitter precoding, enhanced link behavior controls, and per-phase equalization status.
- `RECEIVED_MODIFIED_TS_DATA[1-2]` and `TRANSMITTED_MODIFIED_TS_DATA[1-2]` expose modified training sequence usage mode, vendor ID, information payload, and alternate protocol negotiation status.
- `LANE_[0-15]_EQUALIZATION_CNTL_32GT` repeats downstream/upstream 32 GT/s transmit preset fields per lane.
- `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA[1-2]`, and `AP_SEL_EN_MASK` describe Alternate Protocol capability, status/control, and protocol-selection data.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` describe Readiness Time Reporting metadata and reset, DL-up, FLR, D3hot-to-D0, and validity fields.

The `BIF_CFG_DEV0_EPF0_VF0_1_*` and `VF1_1_*` blocks repeat complete virtual-function PCI configuration templates:

- Conventional PCI header fields: vendor/device ID, command, status, revision ID, class-code bytes, cache-line size, latency timer, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- PCI command/status bits: I/O and memory access, bus mastering, special cycles, memory write invalidate, VGA palette snoop, parity response, SERR, interrupt disable, immediate readiness, interrupt status, capabilities-list presence, master-data parity, DEVSEL timing, target/master abort reporting, signaled system error, detected parity error, and status bits for unsupported request, fatal, non-fatal, and correctable PCIe errors.
- PCIe capability fields: capability IDs and next pointers, PCIe version, device/port type, slot implemented, interrupt message number, device/link capability, control, and status registers, plus device/link capability/control/status 2.
- Device and link controls: error-reporting enables, relaxed ordering, max payload, extended tags, phantom functions, aux power PM, no-snoop, max read request, bridge config retry, function-level reset, ASPM, link disable/retrain/common-clock/extended-sync, bandwidth-management interrupts, target link speed, compliance controls, de-emphasis, transmit margin, enter modified compliance, equalization phase status, completion-timeout ranges and controls, ARI forwarding, atomic operation controls, ID-based ordering, LTR, OBFF, emergency power reduction, ten-bit tags, and end-to-end TLP prefix blocking.
- MSI and MSI-X fields: capability-list metadata, MSI enable and multiple-message controls, 32-bit/64-bit message address and data registers, masks and pending bits, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability fields: capability-list metadata, VSEC ID/revision/length, and two 32-bit scratch/payload registers.
- Advanced Error Reporting: AER capability metadata; uncorrectable status/mask/severity fields for DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked; correctable status/mask fields for receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow events; AER capability/control; four TLP header log words; and four TLP prefix log words.
- ARI and RTR fields: Alternative Routing-ID Interpretation capability/control metadata, function group and next-function fields, and readiness timing fields.

The `BIF_CFG_DEV0_EPF0_VF2_1_*` block begins at `VENDOR_ID` and follows the same VF template through `PCIE_ARI_ENH_CAP_LIST__CAP_ID_MASK`. The remainder of VF2 ARI and RTR fields belongs to the next chunk.

## APIs, Types, And Functions

There are no runtime APIs or C types in this range. The exported interface is the generated macro namespace itself. Consumers rely on exact macro names, masks, and shifts staying synchronized with the matching NBIO 4.3.0 offset/default headers and with AMD's hardware register database.

The constants are untyped preprocessor integer literals, mostly with an `L` suffix. They describe bit positions and masks only. They do not encode access width, read/write permissions, reset values, volatility, privilege requirements, write-one-to-clear behavior, or hardware side effects. Call sites must know whether a bit is a read-only capability bit, writable policy/control bit, sticky status bit, diagnostic log word, or command bit with immediate hardware effect.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. Driver, firmware-facing, SR-IOV, PCIe, or diagnostic code selects a register/config-space offset from the companion NBIO 4.3.0 offset header.
2. The code reads, decodes, composes, or updates register values using this file's `__SHIFT` and `_MASK` constants directly or through field helper macros.
3. The resulting value is written back, polled, saved/restored, exposed to PCI enumeration, used for interrupt routing, or reported in diagnostics.

Likely flows using this chunk include PCIe 32 GT/s link bring-up/equalization, lane margining diagnostics, VF BAR sizing, VF PCI enumeration, SR-IOV virtual-function resource enablement, MSI/MSI-X setup, function-level reset, AER collection/masking, ARI routing, Alternate Protocol negotiation, and Readiness Time Reporting.

## State And Persistence Behavior

The header itself stores no state. It names hardware-visible state in NBIO PCI configuration and PCIe extended capability registers. Persistence is determined by GPU reset domains, firmware initialization, PF/VF management, hypervisor policy, VF FLR, suspend/resume save-restore, and explicit driver writes.

Represented state includes static identity/capability values, host-programmed PCI command bits, BAR and ROM resource registers, interrupt routing state, MSI/MSI-X message address/data/mask/pending state, PCIe device/link policy and status, 32 GT/s equalization and modified-training-sequence state, lane margining status, Alternate Protocol negotiation state, AER sticky status/mask/severity/log values, ARI function-routing controls, and RTR timing-validity data.

Several fields are not ordinary storage. `MEM_ACCESS_EN`, `BUS_MASTER_EN`, MSI/MSI-X enable bits, link retrain/disable controls, `INITIATE_FLR`, AER status/log fields, AP negotiation controls, and 32 GT/s equalization controls can alter hardware behavior or clear/consume diagnostic state. This generated file only gives bit layout; sequencing, privilege, reset, and side-effect rules are enforced by hardware and by the driver code that uses the macros.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 header set:

- `nbio_4_3_0_offset.h` supplies matching `cfg`/`reg` offsets and base-index metadata for the register names covered here.
- Other generated NBIO 4.3.0 headers supply defaults or related register metadata where present.
- AMDGPU register helper macros consume these `__SHIFT` and `_MASK` definitions for field extraction and read-modify-write composition.

Integration points include AMDGPU NBIO initialization, PCIe link management, SR-IOV PF/VF presentation, Linux PCI config-space enumeration, BAR resource assignment, interrupt setup, AER reporting, reset handling, ARI routing, and power-management save/restore paths. The repeated VF templates are intended to align with hardware-configured virtual function instances; adjacent chunks must be merged before drawing whole-file conclusions about the complete VF2 template.

## Risks And Edge Cases

- Generated bitfield drift can compile cleanly while making software touch the wrong hardware bit. Risk is highest for PCI command, bus mastering, interrupt, FLR, link control, equalization, AER, ARI, AP, and RTR fields.
- The chunk starts and ends inside logical register groups. The missing beginning of lane-15 margining control and the missing tail of VF2 ARI/RTR should not be interpreted as absent hardware support.
- VF0, VF1, and VF2 repetition is intentional. Per-VF differences should be checked against the generator and companion offset header before treating them as a bug.
- Incorrect VF resizable BAR masks can produce wrong BAR sizing or expose incorrect resource windows to guests.
- Wrong PCI command or BAR fields can break VF probing, DMA enablement, memory access isolation, or host resource assignment.
- 32 GT/s link/equalization, transmitter precoding, modified training sequence, and Alternate Protocol masks affect link training and negotiation. Bad values can cause link instability or negotiation failures that look like platform or signal-integrity problems.
- MSI/MSI-X table, PBA, mask, pending, and enable fields can cause lost, repeated, or misrouted interrupts if decoded or programmed incorrectly.
- AER status and log fields are diagnostic evidence. Treating sticky or write-one-to-clear fields as ordinary writable state can lose the first-error pointer, TLP header/prefix logs, or severity information.
- ARI controls affect function routing and enumeration. Incorrect masks can hide VFs or route transactions to the wrong function.
- RTR timing fields must be gated by their validity bit; otherwise management code can under-wait, over-wait, or trust stale timing data.

## Test Signals

- Build AMDGPU with NBIO 4.3.0 support enabled. Missing or misspelled macro users should fail at compile time.
- Runtime PCI enumeration on affected AMD GPUs should show stable PF and VF config-space identity, capabilities, BAR sizing, and class information.
- SR-IOV validation should exercise at least VF0, VF1, and VF2 because this chunk contains complete templates for the first two VFs and the front of the third.
- VF resource tests should confirm resizable BAR support bits and BAR-size control fields match advertised capabilities and host-assigned windows.
- PCIe link health tests should check negotiated width/speed, successful retrain paths, 32 GT/s equalization status, and absence of unexpected AER storms.
- Lane-margining and modified-training-sequence diagnostics should decode receiver, margin type, payload, vendor, usage mode, and alternate protocol status consistently with hardware documentation.
- Interrupt smoke tests should verify MSI/MSI-X enablement, masking, pending-bit behavior, and absence of spurious or lost interrupts.
- Error-injection or platform AER tests should preserve and decode uncorrectable/correctable status, severity, first-error pointer, TLP header logs, and TLP prefix logs.
- ARI and virtualization tests should verify VF enumeration, function routing, and isolation under PF/VF and hypervisor-controlled setups.
- RTR validation should compare advertised reset, DL-up, FLR, and D3hot-to-D0 timing fields with observed waits and ensure invalid timing data is ignored.
