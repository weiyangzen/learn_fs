# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 44103-46534

## Scope

This chunk is a generated AMD NBIO 4.3.0 shift/mask header segment for BIF/NBIF PCI configuration-space registers on device 0, endpoint function 0 virtual functions. It contains only C preprocessor macros: no functions, structs, executable statements, storage declarations, locking, or initialization logic.

The range starts inside the virtual-function 10 (`VF10`) PCIe Advanced Error Reporting tail, beginning at the final `PCIE_UNCORR_ERR_STATUS` masks and continuing through VF10 AER mask/severity, correctable-error, AER capability/control, TLP header/prefix log, and ARI definitions. It then contains full address blocks for `VF11`, `VF12`, and `VF13`, and ends after the early `VF14` PCIe capability header fields at `BIF_CFG_DEV0_EPF0_VF14_PCIE_CAP__INT_MESSAGE_NUM_MASK`.

The visible address-block markers are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp`

There is no address-block marker for `VF10` in this range because the chunk begins in the middle of the preceding VF10 block.

## Purpose

The macros define bit positions and masks for NBIO 4.3.0 PCI/PCIe configuration decode fields. AMDGPU code pairs these definitions with register offsets from `nbio_4_3_0_offset.h` and register access helpers so it can read, decode, compose, or write hardware register values without embedding raw bit constants.

The dominant macro shape is:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>_MASK`

where `<n>` is `10`, `11`, `12`, `13`, or `14` in this chunk. The full VF11, VF12, and VF13 blocks are mechanically repeated per virtual function and model a PCI function's standard header, PCIe capability, MSI/MSI-X capability, vendor-specific extended capability, AER diagnostics, TLP log registers, and ARI extended capability. VF10 and VF14 are partial due to chunk boundaries.

## Register Coverage

VF10 coverage in this chunk is the tail of its PCIe error and routing capability definitions:

- AER uncorrectable error status masks for data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked cases.
- AER uncorrectable error mask and severity fields for the same error classes.
- Correctable error status and mask fields for receiver error, bad TLP, bad DLLP, replay number rollover, replay timer timeout, advisory nonfatal, correctable internal error, and header-log overflow.
- AER capability/control fields such as first-error pointer, ECRC generation/checking capability and enable bits, multi-header recording controls, TLP prefix logging presence, and completion-timeout logging capability.
- Four 32-bit TLP header log words and four 32-bit TLP prefix log words.
- ARI enhanced capability list, ARI capability, and ARI control fields.

VF11, VF12, and VF13 are complete within this chunk. Each full VF block includes:

- Standard PCI header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list header, PCIe capability word, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- MSI fields: MSI capability list, message control, low/high message address, message data, extended message data, vector mask, 64-bit data/mask aliases, and pending bits.
- MSI-X fields: MSI-X capability list, table size, function mask, enable bit, table BIR/offset, and pending-bit-array BIR/offset.
- Vendor-specific PCIe extended capability fields: enhanced capability list metadata, vendor-specific header metadata, and two 32-bit scratch registers.
- AER fields: enhanced capability list metadata, uncorrectable status/mask/severity, correctable status/mask, AER capability/control, four header log dwords, and four TLP prefix log dwords.
- ARI fields: enhanced capability list metadata, multifunction/ACS function-group capability bits, next function number, function-group enable bits, and function-group selector.

VF14 coverage starts a new full VF block but ends early. It includes the standard PCI header field definitions through `MAX_LATENCY`, the `PCIE_CAP_LIST` fields, and the `PCIE_CAP` fields for PCIe capability version, device type, slot implemented, and interrupt message number. The remaining VF14 PCIe device/link/MSI/MSI-X/vendor-specific/AER/ARI field definitions belong to the next chunk.

## Important APIs, Types, and Functions

There are no C APIs, type definitions, or functions in this header slice. Its consumed interface is the macro namespace itself.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` define standard PCI command/status bits such as I/O access, memory access, bus master enable, SERR, interrupt disable, capability-list presence, target/master abort reporting, parity reporting, and interrupt status.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, and `*_MSIX_PBA__*` expose address-like registers whose low bits encode enablement, type, BIR, validation, or reserved state. Consumers must preserve those encodings rather than treating every bit as a plain address.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` model PCIe capability metadata, device type, slot implementation, interrupt message number, FLR capability/initiation, payload and read-request sizing, relaxed ordering, no-snoop, completion-timeout controls, ASPM, link retrain/disable, negotiated speed/width, bandwidth status, equalization status, retimer and crosslink indicators, and supported link speed vectors.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability programming: MSI enablement, multi-message capability/enable values, 64-bit address support, per-vector mask capability, message address/data registers, vector masks, pending bits, MSI-X table sizing, function masking, enablement, and table/PBA locations.
- `*_PCIE_VENDOR_SPECIFIC_*` fields define the vendor-specific enhanced capability list header, VSEC ID/revision/length, and scratch dwords.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define PCIe AER reporting status, reporting masks, severity classification, ECRC controls, multi-header recording, TLP prefix log presence, completion-timeout log capability, and first-error pointer fields.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw 32-bit diagnostic capture words used after PCIe/AER events.
- `*_PCIE_ARI_*` defines Alternate Routing-ID Interpretation capability and control fields for function grouping and next-function discovery.

## Control Flow

This chunk has no runtime control flow. Inclusion is governed by the surrounding header guard in the full file. At compile time, translation units that include `nbio_4_3_0_sh_mask.h` receive these symbolic constants.

The intended consumer flow is inferred from generated AMDGPU register conventions:

1. A caller selects a register address from `nbio_4_3_0_offset.h`, for example a `cfgBIF_CFG_DEV0_EPF0_VF11_*` register.
2. The driver reads or writes the register through AMDGPU/SOC15 PCI config, MMIO, or indirect register helpers.
3. Field extraction or composition uses these `__SHIFT` and `_MASK` definitions, commonly through helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`.
4. The resulting values control or inspect VF configuration, interrupt delivery, PCIe link/device controls, AER diagnostics, or ARI routing metadata.

Direct include users found in this tree are `amdgpu/nbio_v4_3.c`, `pm/swsmu/smu13/smu_v13_0_0_ppt.c`, and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`. These files include the NBIO 4.3.0 offset and shift/mask headers to access NBIO/PCIe register fields in a SoC-version-specific way.

## State and Persistence Behavior

The header stores no software state and performs no persistence. It describes bit layout for state held in hardware PCI configuration and PCIe extended-capability registers.

State represented by these macros is per virtual function. Configuration/control fields can persist in hardware until reset, function-level reset, PF-mediated VF teardown/recreation, or driver reprogramming. Examples include PCI command enables (`MEM_ACCESS_EN`, `BUS_MASTER_EN`, `IO_ACCESS_EN`), interrupt disable, MSI/MSI-X enables and masks, device-control fields such as payload size, extended tag enable, relaxed ordering, no-snoop, completion timeout, FLR initiation, link-control fields, AER mask/severity/ECRC controls, and ARI function-group controls.

Status and diagnostic fields are hardware-updated. PCI status bits, device/link status bits, AER correctable and uncorrectable status bits, first-error pointer, TLP header logs, TLP prefix logs, MSI pending bits, and link equalization indicators can be sticky, read-only, clear-on-write, or otherwise side-effectful according to PCIe and NBIO hardware rules. This header does not encode those access semantics; it only supplies bit positions and masks.

Because this range covers SR-IOV VF config decode windows, mistakes in a VF number or macro family can affect the wrong VF's configuration view. That is especially important for VF11 through VF13, which are complete and nearly identical aside from the numeric VF prefix.

## Dependencies and Integration Points

Key dependencies and integration points:

- `nbio_4_3_0_offset.h` supplies the matching register offsets. This header supplies the bitfield masks and shifts for those offsets.
- Other generated NBIO 4.3.0 headers, especially default-value headers, must remain synchronized with this register database.
- AMDGPU register helper macros consume the generated naming convention. The `__SHIFT` and `_MASK` suffixes are expected by field-access patterns such as `REG_GET_FIELD`/`REG_SET_FIELD`.
- `amdgpu/nbio_v4_3.c` is the direct NBIO runtime integration point in the tree for this generation.
- SMU 13.0.0 and 13.0.7 power-management code includes this header, so build coverage for those paths also validates that the macro names remain available.
- Linux PCI/PCIe concepts mirrored by this chunk include SR-IOV VFs, PCI command/status, BAR/ROM layout, capability lists, PCIe device/link capability, MSI, MSI-X, AER, and ARI.
- PCIe diagnostics and recovery paths can use the AER and TLP log field definitions when decoding error status from NBIO hardware.
- Interrupt setup and teardown paths depend on the MSI/MSI-X field definitions when programming VF interrupt delivery, masks, pending bits, and table/PBA locations.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file itself is AMD GPU driver hardware metadata and has no Ceph filesystem behavior.

## Risks and Edge Cases

- This is generated, highly repetitive hardware metadata. A single wrong shift or mask can silently corrupt all consumers that decode or compose the affected register field.
- Chunk boundaries are partial. VF10 begins before this range and VF14 continues after it. Whole-VF conclusions for those two functions require adjacent chunks.
- VF11, VF12, and VF13 should be structurally identical except for VF number. Copy-generation drift between these blocks is difficult to catch by manual review.
- AER status, mask, and severity families use almost identical field names. Using a status mask where a reporting mask or severity mask is intended can suppress errors, misclassify errors, or inspect/clear the wrong hardware state.
- Correctable and uncorrectable AER status fields may have write-one-to-clear or sticky behavior. The macros do not communicate those semantics, so consumers need hardware/PCIe knowledge when writing them.
- BAR, ROM, MSI-X table, and MSI-X PBA fields contain encoded low bits. Treating them as raw addresses can damage BIR/type/enable/reserved fields.
- MSI and MSI-X fields include 32-bit and 64-bit layout aliases. Consumers must select offsets and masks consistently with the capability's 64-bit addressing and per-vector masking bits.
- Link-control fields such as retrain, disable, autonomous speed disable, compliance controls, and equalization-related controls can affect device reachability if written incorrectly.
- ARI controls interact with PCIe function routing and enumeration. Enabling or interpreting ARI function groups incorrectly can expose the wrong function topology to software.
- Literal masks use `L` suffixes and cover 8-bit, 16-bit, and 32-bit fields. Consumers should avoid implicit truncation, sign-extension, or host-width assumptions.

## Test Signals

Useful validation signals for this chunk:

- Compile AMDGPU configurations that include `nbio_4_3_0_sh_mask.h`, especially `amdgpu/nbio_v4_3.c` and SMU 13.0.0/13.0.7 paths; malformed or missing macro names should fail the build.
- Run generated-header consistency checks against the authoritative NBIO 4.3.0 register database, ensuring every offset in `nbio_4_3_0_offset.h` has the expected shift/mask definitions and vice versa.
- Pattern-check VF11, VF12, and VF13 for identical register families, field names, shifts, and masks after normalizing the VF number. Treat VF10 and VF14 separately because they are partial in this chunk.
- Validate mask/shift consistency mechanically: each `_MASK` should align with its paired `__SHIFT`, multi-bit masks should have contiguous bit ranges where expected, and full-dword fields should use shift `0x0` with mask `0xFFFFFFFFL`.
- On NBIO 4.3.0 SR-IOV-capable hardware, enable enough virtual functions to exercise VF11 through VF13, enumerate them, bind host/guest drivers, and compare decoded PCI config-space capability fields with `lspci -vv` or driver debug output.
- Exercise MSI/MSI-X on VF11 through VF13: enable vectors, program message address/data, toggle masks, inspect pending bits, and verify interrupts are delivered and quiesced as expected.
- Use PCIe/AER injection or observed error paths to verify uncorrectable/correctable status, mask, severity, first-error pointer, header logs, and TLP prefix logs decode correctly.
- Run VF lifecycle tests around FLR, guest detach/attach, PF reset, and VF recreation to confirm command/status, interrupt, AER, and ARI state returns to expected defaults.
- Merge-lane validation should explicitly reconcile the adjacent chunks so VF10 and VF14 are not represented as complete blocks based on this slice alone.
