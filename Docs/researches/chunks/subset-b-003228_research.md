# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 4880-7320

## Purpose

This chunk is an auto-generated AMD NBIO 7.4 shift/mask slice for PCI/PCIe configuration-space fields. It contains no executable driver logic. Its purpose is to expose stable preprocessor constants that let NBIO 7.4 consumers extract, compare, and program individual fields in hardware registers using the matching offsets from `nbio_7_4_offset.h`.

The selected range starts in the mask half of `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP2`, covers the rest of the `BIF_CFG_DEV0_EPF1_0` PCIe capability and extended-capability map through SR-IOV, VF resize-BAR, and AMD GPU-IOV vendor-specific registers, then enters the `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` address block and reaches the early `BIF_CFG_DEV0_SWDS0` PCIe link capability/control area.

## Public Surface In This Chunk

The public surface is 2,093 `#define` macros in this line range: 1,041 `__SHIFT` constants and 1,052 `_MASK` constants, grouped under 346 generated register comments. The counts are not perfectly paired because the chunk begins mid-register, includes whole-register payload/log fields, and has hardware fields whose generated names already include `MASK`.

Macro names follow the generated register-field convention:

- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field in the EPF1 function's config-space register.
- `BIF_CFG_DEV0_EPF1_0_<REGISTER>__<FIELD>_MASK` gives the pre-shifted mask for that field.
- `BIF_CFG_DEV0_SWDS0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` provide the same contract for the SWDS0 config-decode block.

There are no functions, structs, enums, inline helpers, storage objects, or runtime APIs in this range. The API contract is the exact macro spelling and numeric value, which must stay synchronized with the same ASIC generation's offset header and AMD's register database.

## Register Coverage

For `BIF_CFG_DEV0_EPF1_0`, this chunk covers the tail of PCIe capability 2 and a broad set of conventional and enhanced capabilities:

- Device/link/slot capability 2, control 2, and status 2 fields, including completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, target link speed, compliance controls, de-emphasis, equalization status, crosslink state, and downstream-component presence.
- MSI and MSI-X capability fields: capability-list headers, MSI enable/multi-message/64-bit/per-vector-mask bits, message address/data, mask and pending vectors, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific and virtual-channel capabilities: VSEC headers/scratch registers, VC enhanced-capability headers, port VC capability/control/status, and VC0/VC1 resource capability, arbitration, port arbitration, ID mapping, enable, negotiation, and pending status.
- Device serial number, Advanced Error Reporting, header/TLP-prefix logs, and resizable BAR-like capability/control blocks for BAR1 through BAR6.
- Power budget and Dynamic Power Allocation registers, including data selection/value fields, capability fields, transition latency indicators, DPA enable/status, substate count, and per-substate power allocation entries.
- Secondary PCIe, ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT PHY/equalization, and lane-margining capability groups.
- VF resize-BAR capability/control groups for VF BAR1 through VF BAR6.
- AMD GPU-IOV VSEC fields for SR-IOV shadowing, interrupts, reset control, HVVM mailbox dwords, context, total frame-buffer size, offsets, P2P-over-XGMI enablement, per-VF framebuffer slices for VF0 through VF30, and scheduler dwords for UVD, VCE, GFX, and UVD1 scheduling state.

The chunk then declares the start of the `BIF_CFG_DEV0_SWDS0` block:

- Conventional PCI identification and class/header fields: vendor ID, device ID, command, status, revision, program interface, subclass, base class, cache line, latency, header type, BIST, and base address.
- Bridge-style bus/window and interrupt fields: secondary/subordinate bus numbers, secondary latency, I/O base/limit, secondary status, memory and prefetchable memory windows, upper prefetchable bounds, upper I/O bounds, capability pointer, interrupt line/pin, and bridge control.
- SWDS0 power-management and PCIe capability fields through `LINK_CAP`, with `LINK_CNTL` beginning immediately after the assigned range.

## Field Semantics

The EPF1 fields mirror PCI Express endpoint and extended-capability layouts. Capability fields advertise supported protocol features, while control fields enable or disable policy such as completion timeout behavior, ARI forwarding, atomic requests, LTR, OBFF, end-to-end prefixes, MSI/MSI-X routing, VC negotiation, ACS isolation, address translation, page requests, PASID execution/privilege, multicast routing, SR-IOV VF creation, TPH steering, and resizable BAR sizing.

AER-related fields expose uncorrectable/correctable error status, masks, severity policy, first error pointer, ECRC generation/checking controls, multiple-header recording, header logs, and TLP prefix logs. These are integration-sensitive because the masks and severity bits determine which PCIe errors are reported, suppressed, or treated as fatal.

The link-training sections are highly repetitive and lane-oriented. PCIe 8 GT and 16 GT equalization blocks expose per-lane downstream/upstream transmit preset fields for lanes 0 through 15. The 16 GT PHY block also reports equalization completion and phase success, local/retimer parity mismatch vectors, modified TS usage, and lane margining capability/status/control fields for each lane.

The virtualization portion is split between standards-based SR-IOV and AMD-specific GPU-IOV VSEC registers. SR-IOV fields describe VF enablement, migration, VF counts, first VF offset, VF stride, VF device ID, system page size, VF BARs, and migration-state array offset. GPU-IOV fields describe hypervisor-facing mailbox words, interrupt status/enable bits, reset triggers, global/per-VF framebuffer allocation fields, peer-to-peer-over-XGMI enablement, and scheduling dwords for media and graphics engines.

The SWDS0 block has bridge/root-port style semantics. It combines conventional PCI command/status and decode-window fields with PM and PCIe capability fields for payload sizing, request sizing, relaxed ordering, no-snoop, error reporting, function-level reset, link speed/width, ASPM, exit latencies, clock power management, surprise-down reporting, data-link-active reporting, bandwidth notifications, and port number.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. NBIO 7.4-aware AMDGPU, display, or power-management code includes `nbio/nbio_7_4_sh_mask.h` with the matching NBIO 7.4 offset header.
2. Driver code selects a `cfgBIF_CFG_DEV0_EPF1_0_*` or `cfgBIF_CFG_DEV0_SWDS0_*` offset from `nbio_7_4_offset.h`.
3. These `__SHIFT` and `_MASK` macros are used by register helpers or open-coded bit operations to extract, insert, preserve, or compare fields.
4. Actual reads and writes happen through PCI config-space, MMIO, indirect register, or SMU/PSP integration code outside this header.

The header stores no software state and persists nothing by itself. Persistent state lives in NBIO/PCIe hardware registers. Some fields are configuration controls that survive until reset, function reset, power transition, link retrain, VF lifecycle change, or explicit reprogramming. Other fields are hardware-updated status, sticky error, mailbox, log, pending, or write-one-to-clear fields whose behavior is defined by the hardware and PCIe specifications.

## Dependencies And Integration Points

The direct generated-header dependency is `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`; every mask in this chunk must be paired with the same-generation offset macro. Source-tree include sites for NBIO 7.4 masks include `amdgpu/nbio_v7_4.c`, `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, and older PowerPlay Vega20 code. NBIO 7.4 offsets are also used by PSP and display DCN paths.

Semantic dependencies include the PCI and PCI Express configuration-space specifications, SR-IOV, ATS, PRI, PASID, ACS, MSI/MSI-X, AER, VC, multicast, LTR, DPA, TPH, Data Link Feature, 16 GT PHY/equalization, lane margining, and AMD's NBIO/GPU-IOV register definitions.

Because this is a generated header, most integration is indirect. Callers may use these macros through AMDGPU register helper macros, power-management feature code, debug/register dump paths, virtualization setup code, or firmware-facing SMU/PSP coordination paths. The macros do not encode access width, reset value, read/write permissions, side effects, sequencing, or W1C behavior; consumers must get those rules from the hardware programming guide and surrounding driver logic.

## Risks And Maintenance Notes

- The range starts and ends mid-context. It begins after part of `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP2` and ends after `BIF_CFG_DEV0_SWDS0_LINK_CAP`, just before `BIF_CFG_DEV0_SWDS0_LINK_CNTL` continues in the next chunk.
- Repeated per-lane and per-VF blocks are easy to mis-review. Lane number, VF number, speed suffix, preset direction, and scheduler engine name are often the only visible differences across many consecutive definitions.
- Wrong shifts or masks can silently misprogram hardware: examples include AER severity, ACS isolation, SR-IOV VF counts/stride/BARs, GPU-IOV framebuffer allocation, MSI/MSI-X routing, or link equalization presets.
- Names like `*_MASK_MASK` are valid when the hardware field is itself named `MASK`; tooling or reviewers should not normalize them by hand.
- Full-width `0xFFFFFFFFL` masks often represent whole-register payloads, logs, mailbox words, serial-number halves, BAR capability bitmaps, or reserved fields. They should not be interpreted as permission to write all bits as ones.
- Status/log/pending fields may be sticky, hardware-updated, firmware-owned, or write-one-to-clear. Control fields can affect link state, virtualization isolation, interrupt routing, power behavior, address translation, and BAR decode.
- EPF1 and SWDS0 prefixes are not interchangeable. Each mask prefix must remain paired with the matching `cfgBIF_CFG_DEV0_EPF1_0_*` or `cfgBIF_CFG_DEV0_SWDS0_*` offset prefix.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for NBIO 7.4 include sites, especially `amdgpu/nbio_v7_4.c`, Arcturus/Aldebaran/SMU 13.0.6 power-management files, and Vega20 PowerPlay code.
- Cross-header checks that each register block represented here has a matching `cfgBIF_CFG_DEV0_EPF1_0_*` or `cfgBIF_CFG_DEV0_SWDS0_*` definition in `nbio_7_4_offset.h`.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, with special attention to AER, ACS/ATS/PRI/PASID, SR-IOV, GPU-IOV VSEC, per-lane equalization, lane margining, and SWDS0 bridge windows.
- Static checks that field masks fit the intended 8/16/32-bit register widths and that every field with a `__SHIFT` has the expected generated `_MASK`.
- Hardware or simulator register dumps that decode the EPF1 capability chain and SWDS0 bridge config space consistently with `lspci -vvxxx`-style PCIe output.
- SR-IOV and GPU-IOV validation that VF count, BAR sizing, VF framebuffer allocation, interrupt/reset/mailbox, and scheduler fields decode correctly without cross-VF leakage.
- PCIe link-training tests on NBIO 7.4 hardware that exercise 8 GT and 16 GT equalization, parity mismatch reporting, margining control/status, and bandwidth/link-status reporting.
- Error-injection tests for AER and downstream isolation paths, checking status, masks, severity, header logs, TLP prefix logs, source behavior, and driver reporting.
