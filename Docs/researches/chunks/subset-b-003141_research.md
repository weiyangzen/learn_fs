# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 46732-49193

## Purpose

This chunk is an auto-generated AMD NBIO 7.11.0 shift/mask header slice for PCIe configuration-space fields under the NBIF `BIF_CFG_DEV2` endpoint-function decode blocks. It starts in the tail of the `BIF_CFG_DEV2_EPF3_0` block, continues through the generated address blocks `nbio_nbif0_bif_cfg_dev2_epf4_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev2_epf5_bifcfgdecp`, and begins `nbio_nbif0_bif_cfg_dev2_epf6_bifcfgdecp`.

The file contains no executable driver logic. Its purpose is to expose preprocessor constants that decode and compose hardware register fields: each field has a `REGISTER__FIELD__SHIFT` bit position and a `REGISTER__FIELD_MASK` raw-value mask. Consumers combine these constants with register offsets from sibling NBIO headers and AMDGPU register access helpers.

## Public Surface In This Chunk

The exported API is the generated macro namespace for four adjacent PCIe endpoint-function regions:

- `BIF_CFG_DEV2_EPF3_0_*`: the end of the EPF3 block, covering BAR6 capability/control, power budget, dynamic power allocation, ACS, PASID, ARI, reset timing reporting, and related enhanced-capability list headers.
- `BIF_CFG_DEV2_EPF4_0_*`: a complete endpoint-function style PCI/PCIe config block, from vendor/device ID through reset timing reporting.
- `BIF_CFG_DEV2_EPF5_0_*`: a near-complete matching endpoint-function block, from vendor/device ID through reset timing reporting.
- `BIF_CFG_DEV2_EPF6_0_*`: the beginning of the next endpoint-function block, from vendor/device ID through the first `LINK_CAP` shift definitions. This requested range ends before the rest of `BIF_CFG_DEV2_EPF6_0_LINK_CAP` appears.

The register-family comments in the chunk identify 323 register blocks. The main repeated fields are standard PCI config header fields, PM capability fields, PCIe capability device/link fields, MSI/MSI-X fields, SATA capability/IDP fields, vendor-specific enhanced capability fields, AER fields, BAR enhanced capability fields, power budget and DPA fields, ACS/PASID/ARI fields, and reset timing reporting (`RTR`) fields.

## Important Register Families

The EPF3 tail contains late enhanced-capability groups. BAR6 capability/control defines supported BAR size and encoded BAR index/size fields. Power budget fields provide a selector, base power, scale, PM state/substate, type, power rail, and system allocation bit. DPA fields expose substate count, transition latency units/values, power allocation scale, active substate status, enable/control state, and eight per-substate power allocation bytes. ACS fields describe and control source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, P2P egress control, and direct translated P2P. PASID and ARI fields expose PASID width/permissions and ARI function-group/next-function controls. Reset timing reporting fields expose reset, DL-up, FLR, and D3hot-to-D0 timing plus a validity bit.

The EPF4 block is the fullest block in this slice. Its standard PCI header fields include vendor/device ID, command bits (`IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`), status bits, revision and class-code bytes, cache-line and latency timers, header/BIST fields, six base-address registers, subsystem IDs, ROM base address, capability pointer, interrupt line/pin, and min/max latency fields. It also includes a vendor capability list and writable adapter ID aliases.

EPF4 PM and PCIe capability fields define PM version/support, PME control/status/data, secondary bus revision number, frame-length adjustment, and DBESL/DBESLD bytes. PCIe device and link fields cover max payload support/size, extended tags, role-based error reporting, captured slot power limit/scale, FLR capability/initiation, correctable/nonfatal/fatal/unsupported error enables, relaxed ordering, no-snoop, max read request size, link speed/width, ASPM and clock PM, link disable/retrain, common clock, bandwidth interrupts, DRS signaling, current negotiated link state, and PCIe capability 2 fields such as completion-timeout control, ARI/AtomicOp/LTR/OBFF/10-bit tag/TLP-prefix capabilities, supported link speeds, equalization status, RTM presence, crosslink, and DRS support.

EPF4 interrupt and storage-capability fields include MSI capability/control, 32-bit and 64-bit MSI address/data, extended message data, mask and pending bits, MSI-X table/PBA descriptors, and SATA capability/IDP index/data registers. The MSI/MSI-X masks are full-width for vector mask/pending arrays, while message address/data fields expose the PCI-defined aligned address and 16-bit data fields.

EPF4 and EPF5 both include vendor-specific enhanced capabilities, AER, enhanced BAR, power budget, DPA, ACS, PASID, ARI, and RTR groups. AER fields cover uncorrectable status/mask/severity for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked conditions. Correctable AER status/mask fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, and internal correctable errors. AER capability/control fields expose first-error pointer, ECRC generation/check capability and enables, and multi-header recording. Header log and TLP prefix log registers are modeled as full 32-bit fields.

EPF5 mirrors the EPF4 layout for the same endpoint-function class, but the requested slice reaches it after EPF4 and continues through EPF5 reset timing reporting. The repeated structure is significant: any consumer code or generator change should treat EPF4 and EPF5 as independent hardware functions with similar layouts, not as aliases. Matching register names have distinct `EPF4` or `EPF5` prefixes and distinct offsets in `nbio_7_11_0_offset.h`.

The EPF6 portion starts a new address block and covers only the early configuration header and initial PCIe capability fields. It defines standard identification, command/status, class, BAR, subsystem, ROM, interrupt, vendor capability, PM capability/status-control, PCIe capability header, device capability/control/status, and the beginning of link capability fields. The chunk ends after `BIF_CFG_DEV2_EPF6_0_LINK_CAP__LINK_BW_NOTIFICATION_CAP__SHIFT`, so the remaining `LINK_CAP` shifts and all `LINK_CAP` masks are in the following chunk.

## Control Flow And State

There is no C control flow, no functions, and no data structure ownership in this range. Runtime behavior is supplied by code that includes this header, reads or writes a hardware register using a matching offset macro, and applies the generated mask/shift constants.

The relevant state lives in GPU NBIO/PCIe configuration registers. Some fields are static identification or capability descriptors, while others are mutable control and status. Mutable or side-effectful families include PCI command enables, PM/PME state, PCIe device control and status, link retraining and target speed controls, MSI/MSI-X routing state, AER status/mask/severity, BAR sizing/control, DPA control/status, ACS isolation controls, PASID and ARI enables, and RTR validity/timing fields. Status fields may be latched by hardware and may require PCIe-specified clear semantics outside this header.

## Dependencies And Integration Points

This header is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which is the NBIO 7.11 AMDGPU integration point for this generated register family. The shift/mask constants are paired with address macros in `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h`; spot checks show corresponding offsets for representative registers such as `regBIF_CFG_DEV2_EPF4_0_PCIE_BAR1_CAP`, `regBIF_CFG_DEV2_EPF5_0_PCIE_UNCORR_ERR_STATUS`, and `regBIF_CFG_DEV2_EPF6_0_LINK_CAP`, all using base index 5.

The semantic dependencies are the PCI and PCI Express configuration specifications: standard type-0 header fields, PM capability, PCIe capability, MSI/MSI-X capabilities, SATA capability, vendor-specific enhanced capability, Advanced Error Reporting, Resizable/Enhanced BAR-style capability fields, Power Budgeting, Dynamic Power Allocation, Access Control Services, PASID, ARI, and Reset Timing Reporting. The generated macros name these fields but do not validate legal PCIe state transitions or safe write ordering.

## Risks And Maintenance Notes

- The requested range starts mid-block in EPF3 and ends mid-register in EPF6. Adjacent chunks are required for complete EPF3 and EPF6 analysis.
- These constants must stay synchronized with the generated NBIO 7.11.0 hardware database and sibling offset headers. A wrong mask or shift can silently decode the wrong bit or program unrelated PCIe controls.
- EPF4 and EPF5 are highly repetitive. Reviewers should watch for generator drift where one function's field width, mask, or register presence diverges unexpectedly from the matching function.
- Several controls affect isolation, DMA reachability, and interrupt delivery: `BUS_MASTER_EN`, memory access enables, ACS controls, PASID enables, ARI controls, MSI/MSI-X enables/masks, and BAR sizing/control.
- AER and device-status fields can be clear-on-write or otherwise side-effectful at the hardware level. The presence of full masks in this header does not mean read-modify-write is safe for every status register.
- Link and power fields can affect PCIe stability and resume behavior, including ASPM/clock PM, retraining, target speed, equalization status, DPA substates, power budget reporting, PME state, and reset timing.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` rely on the established AMDGPU unsigned register helper patterns; ad hoc signed arithmetic can create truncation or sign-extension mistakes.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for translation units including `nbio_7_11_0_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`.
- Static checks that each complete field in this slice has a matching `*_SHIFT` and `*_MASK`, with masks aligned to shifts. The EPF6 `LINK_CAP` group should be exempted or reconciled with the next chunk because this range ends before its masks.
- Cross-header checks that every complete register block here has matching `regBIF_CFG_DEV2_EPF*_0_*` offset and base-index macros in `nbio_7_11_0_offset.h`.
- Hardware or simulator PCIe config dumps for NBIO 7.11 devices validating decoded vendor/device IDs, command/status bits, class codes, BAR values, PM state, PCIe link speed/width, MSI/MSI-X state, AER status/masks, ACS/PASID/ARI enables, DPA status, and reset timing values against these masks.
- Error-path tests around AER status/mask/severity decoding and clearing, including completion timeout, malformed TLP, ECRC, unsupported request, ACS violation, internal error, AtomicOp egress blocked, and TLP-prefix blocked conditions.
- Link and power-management tests covering FLR initiation, D3hot-to-D0 timing, PME behavior, ASPM/clock power management, link retraining, link bandwidth notifications, DPA substate control, and power-budget reporting.
