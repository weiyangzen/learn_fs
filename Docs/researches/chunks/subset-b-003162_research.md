# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 4911-7359

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register shift/mask header segment. It contains 2,098 `#define` field-layout macros for PCIe configuration-space and extended-capability registers under the `BIF_CFG_DEV0_EPF0` and `BIF_CFG_DEV0_EPF1` namespaces. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside `BIF_CFG_DEV0_EPF0_LANE_4_MARGINING_LANE_STATUS`, continues through the rest of the EPF0 PCIe lane margining, VF resizable BAR, and GPU IOV vendor-specific capability fields, then starts the generated address block `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`. The EPF1 block covers standard PCI config fields and many PCIe extended capabilities through the beginning of `BIF_CFG_DEV0_EPF1_LANE_3_MARGINING_LANE_CNTL`. Adjacent chunks are required for the beginning of EPF0 lane 4 margining status and the remainder of EPF1 lane 3 and later margining registers.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield-definition half of AMD's generated NBIO 7.2.0 register interface. This chunk provides compile-time constants used by AMDGPU code to decode or compose fields in NBIO PCIe configuration registers:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the raw register mask for that field.

The file does not perform register I/O itself. Callers combine these constants with companion register-address/default headers and AMDGPU register helpers to read, update, preserve, or report fields in the GPU's PCIe endpoint function configuration space. Although this repository path sits under a Ceph client source mirror, this header is AMD GPU hardware metadata and has no distributed-filesystem behavior.

## Important Macro Families

The initial EPF0 section finishes PCIe lane margining coverage. It starts with the status fields for lane 4, then defines lane 5 through lane 15 control/status pairs. Each lane uses the same layout: receiver number, margin type, usage model, and margin payload fields for command/control registers, with matching readback/status fields. These constants support PCIe margining diagnostics and must be interpreted with the PCIe margining capability state machine.

The EPF0 VF resizable BAR section defines capability and control fields for VF BAR1 through VF BAR6. The capability registers expose supported size encodings; the control registers expose BAR index, total BAR count, selected BAR size, and upper supported-size bits. These are relevant to SR-IOV/VF resource sizing rather than ordinary PF BAR programming.

The EPF0 GPU IOV vendor-specific capability section is the most AMD-specific part of the chunk. It defines the VSEC enhanced capability header, VSEC header length/revision/ID, SR-IOV shadow fields, interrupt enable/status fields for GFX, UVD, UVD1, VCE, and HVVM mailbox events, soft PF FLR control, HVVM mailbox data and per-VF acknowledgement/receive-valid state, context sizing/location/offset fields, total frame-buffer availability/consumption, scheduler offset fields, local frame-buffer region metadata, and P2P-over-XGMI enablement for VFs and PF.

The same GPU IOV section then maps per-VF frame-buffer allocations for VF0 through VF30. Every VF frame-buffer register has size and offset fields. It also defines opaque full-width scheduler doubleword arrays: `UVDSCH_DW0` through `DW8`, `VCESCH_DW0` through `DW8`, `GFXSCH_DW0` through `DW8`, and `UVD1SCH_DW0` through `DW8`. These are exposed as 32-bit `DWn` masks, so semantic interpretation is owned by firmware, virtualization code, or separate AMD documentation rather than by this header.

The `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` block starts a full PCI endpoint-function configuration map for EPF1. It includes vendor and device IDs, command/status bits, revision/class-code bytes, cache line and latency registers, header/BIST, six base address registers, CardBus CIS pointer, subsystem adapter IDs, expansion ROM base, capability pointer, interrupt line/pin, min grant/max latency, a vendor capability, PM capability/status-control, PCIe capability, device/link capability/control/status, device/link capability 2/control 2/status 2, and MSI/MSI-X capability fields.

The EPF1 extended-capability section covers vendor-specific capability scratch registers, virtual-channel capability and VC0/VC1 resources, device serial number, Advanced Error Reporting, BAR enhanced capability registers for BAR1 through BAR6, power budget registers, dynamic power allocation, secondary PCIe link control/equalization, ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY/equalization status, and PCIe lane margining.

The EPF1 AER group defines uncorrectable error status/mask/severity fields for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. It also defines correctable error status/mask fields, AER capability/control fields, TLP header logs, and TLP prefix logs.

The per-lane equalization groups are repeated for lanes 0 through 15. The regular secondary PCIe lane controls expose downstream/upstream 8 GT/s TX presets and RX preset hints. The 16 GT/s PHY capability later exposes link status bits for equalization complete and phases 1-3 success, parity mismatch status registers, and lane 0 through lane 15 downstream/upstream 16 GT/s TX preset fields.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public surface is the generated preprocessor macro namespace:

- `BIF_CFG_DEV0_EPF0_*` for endpoint function 0 fields, especially margining, VF resizable BARs, and GPU IOV VSEC registers.
- `BIF_CFG_DEV0_EPF1_*` for endpoint function 1 standard PCI config-space and PCIe extended-capability fields.

The constants are untyped preprocessor integer literals, usually with an `L` suffix. They encode only bit geometry. They do not encode register addresses, access permissions, reset values, legal values, write-one-to-clear behavior, hardware sequencing, firmware ownership, or side effects.

## Control Flow

This header has no local runtime control flow. The effective flow is external and compile-time assisted:

1. AMDGPU code selects a register address from sibling generated NBIO address metadata.
2. The driver reads a PCIe/NBIO register, or prepares a value to write.
3. The caller uses the `*_MASK` and `*__SHIFT` constants, commonly through AMDGPU bitfield helpers, to extract, set, or preserve fields.
4. Hardware and firmware implement the actual behavior: link training, equalization, AER logging, SR-IOV resource exposure, mailbox signalling, VF frame-buffer partitioning, ACS/ATS/PASID/PRI transaction handling, MSI/MSI-X delivery, and PCIe margining.

Several represented hardware flows are asynchronous. Examples include PCIe link retraining, 8 GT/s and 16 GT/s equalization phases, AER status logging/clearing, DPA and power-management state changes, virtual-channel negotiation, page-request failure/status reporting, SR-IOV VF enablement and migration state, HVVM mailbox handshakes, and margining ready/status transitions.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes state stored in GPU NBIO PCIe configuration registers. Persistence depends on the GPU reset domain, PCIe fundamental reset, function-level reset, power management, firmware/BIOS initialization, driver restore paths, and any explicit AMDGPU writes.

Represented state includes endpoint identity and class metadata, PCI command/status enables, BAR and ROM windows, interrupt routing, MSI/MSI-X tables and pending/mask bits, PM state and PME control, device/link control/status, AER status/masks/severity/logs, VC arbitration and resource status, ACS isolation controls, ATS/PRI/PASID enablement, SR-IOV VF counts and VF BARs, VF frame-buffer partition fields, P2P-over-XGMI enablement, mailbox acknowledgement/valid state, scheduler data words, 8 GT/s and 16 GT/s equalization presets/status, Data Link Feature support/status, and lane margining control/status fields.

Because many of these fields are hardware status latches or control bits with side effects, a mask definition alone is not enough to determine safe write behavior. Code that updates these registers must preserve reserved bits, avoid blind read-modify-write on write-one-to-clear status, and coordinate with firmware and PCI core ownership where applicable.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database. The `_sh_mask` header supplies field offsets and masks; sibling NBIO offset/SMN headers provide register addresses; sibling default headers provide reset/default values where generated for this ASIC. Consumers are expected to use these macros through established AMDGPU register and bitfield helpers rather than by hand-rolling shifts at call sites.

Semantic dependencies come from the PCI and PCI Express specifications for standard config space, PM capability, PCIe device/link capability, MSI/MSI-X, AER, VC, resizable BAR, power budgeting, DPA, secondary PCIe/equalization, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, TPH, Data Link Feature, 16 GT/s PHY capability, and lane margining. The GPU IOV VSEC fields are AMD-specific and integrate with SR-IOV, GPU virtualization, hypervisor/firmware mailbox protocols, VF frame-buffer partitioning, media/GFX scheduling metadata, and XGMI peer-to-peer policy.

Within AMDGPU, this header integrates with the SOC15/NBIO include stack and low-level NBIO, PCIe, virtualization, interrupt, reset, and power-management code. Higher-level code should not treat the generated names as policy; the policy lives in call sites that decide when to expose VFs, enable bus mastering, configure interrupts, clear errors, initiate FLR, alter ACS/ATS/PASID/PRI, or run PCIe diagnostics.

## Risks And Edge Cases

- The chunk starts mid-register at EPF0 lane 4 margining status and ends mid-register-family at EPF1 lane 3 margining control. Whole-file analysis must reconcile adjacent chunks before treating either margining sequence as complete.
- Generated mask/shift drift can compile cleanly but decode or program the wrong hardware bits. That class of error can surface as broken VF resource sizing, failed mailbox handshakes, bad frame-buffer partitioning, missing interrupts, incorrect AER handling, failed link equalization, or PCIe isolation/security regressions.
- Many EPF1 status fields are likely hardware-latched and some PCIe status bits are write-one-to-clear. The macros do not mark those semantics, so callers need hardware/spec knowledge before writing.
- ACS, ATS, PRI, PASID, ARI, SR-IOV, and P2P-over-XGMI fields affect DMA routing, address translation, peer-to-peer access, and VF isolation. Misprogramming can become a security or data-corruption issue, not just a link issue.
- VF BAR resize and VF frame-buffer offset/size fields are resource-partitioning sensitive. Off-by-one sizes, stale masks, or mismatched VF counts can expose overlapping memory windows or hide usable memory from VFs.
- GPU IOV mailbox and interrupt bits represent a protocol, not independent flags. Polling and clearing code needs ordering, timeout, and race handling outside this header.
- Repeated lane and VF blocks are review-hostile. A single generation error in one lane or VF can affect only that instance while the surrounding pattern appears correct.
- Full-width `0xFFFFFFFFL` fields and high-bit masks such as `0x80000000L` should stay on the established AMDGPU integer/register helper types to avoid signedness or truncation surprises.
- Reserved fields such as `LINK_CAP_16GT` and `LINK_CNTL_16GT` are exposed as full-width reserved masks in this slice. Writers must not infer that all bits are writable simply because a generated mask exists.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU paths that include NBIO 7.2.0 register headers. Compile-time coverage catches missing, renamed, or malformed generated macros.
- Run generated-header consistency checks: every field should have a matching `__SHIFT` and `_MASK`; masks should align with shifts; repeated lane 0-15 and VF0-VF30 layouts should be mechanically consistent except for lane/VF numbering.
- Cross-check the register names in this slice against sibling NBIO 7.2.0 offset/SMN/default headers so the field layouts map to known register addresses and defaults where applicable.
- On supported hardware, compare decoded EPF1 PCI config space with `lspci -vvxxx`, AMDGPU debug register dumps, or firmware-provided tables for vendor/device IDs, class code, BARs, PM state, link speed/width, MSI/MSI-X, AER, VC, ACS, ATS, PRI, PASID, SR-IOV, and LTR fields.
- Exercise SR-IOV/GPU virtualization paths: enable and disable VFs, validate VF BAR sizing, verify VF frame-buffer size/offset partitioning, check mailbox ACK/valid transitions, and confirm GPU IOV interrupt enable/status bits report expected GFX/media/HVVM events.
- Exercise PCIe error handling: inject or observe AER correctable/uncorrectable errors, verify severity/mask programming, collect header/TLP prefix logs, and confirm status clearing does not disturb unrelated bits.
- Validate PCIe link diagnostics and power behavior around retraining, 8 GT/s and 16 GT/s equalization, data-link feature status, lane error/equalization status, LTR reporting, DPA/power-budget fields, and lane margining readiness/status.
- For code that writes any fields described here, inspect register traces to ensure reserved bits are preserved, write-one-to-clear status is handled intentionally, and firmware-owned GPU IOV scheduler/mailbox fields are not overwritten by generic read-modify-write code.
