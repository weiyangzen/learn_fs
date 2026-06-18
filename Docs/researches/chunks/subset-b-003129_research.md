# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 17198-19674

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11 shift/mask header. It defines C preprocessor constants for decoding and programming bitfields in NBIF/BIF PCI configuration-space registers exposed by the NBIO configuration decoder. The macros describe field geometry only; they do not implement Ceph or distributed-filesystem behavior despite the source path living under a `ceph-client` mirror.

The range covers 2,126 `#define` entries across 342 commented register blocks. It contains 1,062 `__SHIFT` definitions and 1,064 `_MASK` definitions. The two-mask surplus is caused by chunk boundaries: the range starts at the tail of `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK`, where the matching shift definitions for several corrected-error mask bits are in the previous chunk. The range ends inside `BIF_CFG_DEV0_EPF7_COMMAND`, after the `IO_ACCESS_EN` and `MEM_ACCESS_EN` shift definitions but before the remaining command shifts and masks in the next chunk.

At a high level, this chunk covers:

- The tail of device 0 endpoint/function 5 (`DEV0_EPF5`) PCIe Advanced Error Reporting and extended capability fields.
- A complete visible `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` address block for device 1 endpoint/function 1 (`DEV1_EPF1`), including PCI header fields, PCIe, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power, DPA, ACS, PASID, ARI, SR-IOV, VF resizable BAR, and reset-time-reporting fields.
- Most of the `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp` address block for device 0 endpoint/function 6 (`DEV0_EPF6`), from vendor ID through reset-time-reporting.
- The first few fields of the next `DEV0_EPF7` block: vendor ID, device ID, and the first two `COMMAND` shifts.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The interface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the zero-based starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

The chunk starts with the final masks for `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK` corrected-error sources: replay-number rollover, replay-timer timeout, advisory nonfatal error, and corrected internal error. The corresponding earlier corrected-error bits and shifts are outside this range.

The rest of the `DEV0_EPF5` tail covers:

- `PCIE_ADV_ERR_CAP_CNTL`: first-error pointer, ECRC generation/check capability and enable bits, and multiple-header-recording capability/enable.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`: full-dword logged TLP header and prefix capture fields for AER diagnostics.
- `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP`, and `PCIE_BAR1_CNTL` through `PCIE_BAR6_CNTL`: enhanced BAR capability metadata, supported sizes, BAR index, total BAR count, selected size, and upper supported-size bits.
- `PCIE_PWR_BUDGET_*`: enhanced capability list, data selector, base power, data scale, PM substate/state, type, power rail, and system-allocated indication.
- `PCIE_DPA_*`: dynamic power allocation capability, latency indicator, status, control, and per-substate power allocation registers 0-7.
- `PCIE_ACS_*`: access control services capability/control fields for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress-control vector sizing.
- `PCIE_PASID_*`: PASID enhanced capability, supported execution/privileged-mode attributes, maximum PASID width, and enable bits.
- `PCIE_ARI_*`: alternative routing-ID interpretation capability/control and next-function/function-group fields.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`: reset-time-reporting capability metadata plus reset, data-link-up, FLR, D3hot-to-D0, and valid timing fields.

The `DEV1_EPF1` block is the largest section in this chunk. It defines standard PCI configuration fields such as vendor/device ID, `COMMAND`, `STATUS`, revision ID, programming interface, subclass, base class, cache-line size, latency, header type, BIST, six base-address registers, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, maximum latency, and vendor capability list. It also defines power-management interface fields (`PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`) including PME support/status, D-state selection, no-soft-reset, data select/scale, and bridge-extension bits.

`DEV1_EPF1` then exposes the PCIe capability chain:

- PCIe capability header and endpoint capability fields: version, device type, slot implemented, interrupt message, maximum payload support, phantom function support, extended tag, L0s/L1 latency, role-based error reporting, captured slot power, and FLR capability.
- Device control/status fields: error-reporting enables, relaxed ordering, maximum payload/read request sizes, extended tag, phantom functions, aux power PM, no-snoop, corrected/nonfatal/fatal/unsupported-request status, aux power, transaction pending, ID ordering, LTR, OBFF, and end-to-end TLP prefix blocking controls.
- Link capability/control/status fields: maximum speed/width, ASPM support and control, exit latencies, clock power management, surprise/down-error reporting, active-state link, bandwidth notification, target speed, hardware autonomous speed disable, selectable de-emphasis, link training, slot clock config, data-link-layer active, bandwidth management, equalization, and lane/equalization state bits.
- MSI and MSI-X capability structures: message control, 32/64-bit address/data fields, masks, pending bits, table offset/BIR, and PBA offset/BIR.
- SATA capability/index/data fields that model SATA-specific registers in this BIF config image.
- PCIe vendor-specific enhanced capability header and vendor-specific payload dwords.
- Advanced Error Reporting: uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs.
- Enhanced BAR, power-budget, DPA, ACS, PASID, ARI, SR-IOV, VF resizable BAR, and reset-time-reporting capability blocks.

The `DEV1_EPF1` SR-IOV fields define capability/control/status bits for VF migration, ARI-capable hierarchy, VF MSE, VF enable, VF migration interrupt, initial/total/active VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, and VF BAR0 through VF BAR5 encodings. Its VF resizable BAR registers define supported VF BAR sizes, selected size, BAR index, total BAR count, and upper supported-size bits for BAR1 through BAR6.

The `DEV0_EPF6` block repeats most of the same endpoint/function shape as `DEV1_EPF1` but, in this chunk, stops after ARI and reset-time-reporting and does not include the `DEV1_EPF1` SR-IOV or VF resizable BAR blocks. It includes standard PCI header fields, PM capability/status, PCIe device/link/device2/link2 controls, MSI/MSI-X, SATA, vendor-specific enhanced capability, AER, header/prefix logs, BAR enhanced capability controls, power budgeting, DPA, ACS, PASID, ARI, and RTR timing.

The `DEV0_EPF7` block begins at the end of the chunk with `VENDOR_ID`, `DEVICE_ID`, and the first two command-register shifts (`IO_ACCESS_EN` and `MEM_ACCESS_EN`). The rest of `COMMAND` belongs to the next chunk.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is included at compile time and contributes constants to AMDGPU/NBIO register access code. Runtime behavior is implied by code that pairs these macros with register addresses from the matching offset header and with register read/modify/write helpers such as AMDGPU's SOC15/NBIO access wrappers and bitfield helpers.

The implied hardware flows are:

1. PCI enumeration or ASIC initialization reads identity, class-code, header, BAR, ROM BAR, capability pointer, interrupt, and capability-list fields for each exposed endpoint/function.
2. Driver or firmware setup programs `COMMAND`, PM, PCIe device control, link control, MSI/MSI-X, ACS, PASID, ARI, SR-IOV, and BAR-related controls through these bit masks.
3. PCIe error handling reads AER uncorrectable/correctable status, applies masks/severity policy, and can use header/TLP-prefix log dwords to diagnose the faulting transaction.
4. Power-management and virtualization paths inspect or program power budgeting, dynamic power allocation, PASID, ACS isolation, ARI routing, SR-IOV VF topology, and VF BAR sizing.
5. Reset and recovery paths can use RTR timing fields to understand reset, data-link-up, function-level reset, and D3hot-to-D0 timing metadata.

The file itself does not read hardware, write hardware, clear latched status bits, validate field values, or sequence operations. Those semantics belong to the driver paths and the NBIO 7.11 hardware specification.

## State and Persistence

The header owns no state, allocates no memory, persists nothing, and performs no I/O. The represented state lives in NBIO/BIF PCI configuration-space registers.

State categories represented by this chunk include:

- PCI function identity and enumeration state: vendor/device IDs, revision and class codes, header/BIST, BARs, ROM base, adapter ID, capability pointers, interrupt line/pin, and grant/latency fields.
- Configuration policy state: PCI command enables, error-response enables, PM controls, PCIe device/link controls, MSI/MSI-X enablement and vector table pointers, ACS isolation controls, PASID enables, ARI controls, SR-IOV enables, and VF BAR sizing.
- Error-observation and error-policy state: AER uncorrectable/correctable status, masks, severity, ECRC capability/control, first-error pointer, and transaction logs.
- Power and performance state: power budgeting records, dynamic power allocation substate controls, transition latency indicators, and per-substate power allocations.
- Reset/recovery timing state: reset, data-link-up, FLR, D3hot-to-D0, and valid timing fields in RTR data registers.

Persistence across GPU reset, PCI reset, FLR, suspend/resume, BACO, or runtime power transitions is not described by this header. A wrong macro value, however, is persistent in the compiled driver until the generated header is corrected and the driver rebuilt.

## Dependencies and Integration Points

The direct companion in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h`, which provides the register address/offset side of the same NBIO 7.11 register map.

No `nbio_7_11_0_default.h` or `nbio_7_11_0_smn.h` file is present beside this header in the inspected tree. Consumers therefore depend on this shift/mask header plus the available offset header and any generated defaults or SMN metadata supplied elsewhere in the build or by hardware documentation.

Likely integration areas in AMDGPU include:

- NBIO 7.11 ASIC bring-up and low-level register access paths that include generated ASIC register headers.
- PCIe and NBIF setup code that programs endpoint/function PCI configuration images.
- AER and RAS-related diagnostic paths that classify correctable/uncorrectable PCIe errors and decode logged TLP headers.
- Interrupt setup for MSI/MSI-X capabilities and vector masks.
- Power-management code that handles PM capability, D-states, power budgeting, DPA, ASPM, LTR, and OBFF controls.
- Virtualization and isolation paths that depend on ACS, PASID, ARI, SR-IOV, VF BAR, and VF count/stride/offset fields.
- Reset and recovery paths that care about FLR, D3hot-to-D0, reset, and data-link-up timing fields.

Integration is primarily by exact symbol naming. `BIF_CFG_DEV1_EPF1_*`, `BIF_CFG_DEV0_EPF6_*`, and `BIF_CFG_DEV0_EPF5_*` name different hardware function configuration images even when their field layouts are structurally identical.

## Risks

- Chunk boundaries split register definitions. This range starts mid-`DEV0_EPF5_PCIE_CORR_ERR_MASK` and ends mid-`DEV0_EPF7_COMMAND`; pair-completeness checks must be done after merging adjacent chunks.
- Repeated endpoint/function layouts are easy to cross-wire. Using a `DEV1_EPF1` macro while accessing a `DEV0_EPF6` offset would decode the same-looking field from the wrong function image.
- AER status, mask, and severity registers have similar field names. Confusing status with mask, or severity with status, can hide errors, misclassify correctable versus fatal events, or corrupt diagnostics.
- PCIe control fields such as maximum payload size, maximum read request size, relaxed ordering, no-snoop, ASPM, target link speed, LTR, OBFF, ACS, PASID, ARI, and SR-IOV affect bus behavior and device isolation. Incorrect masks can create enumeration failures, performance regressions, DMA isolation problems, or broken virtualization.
- MSI/MSI-X table and PBA fields combine offset and BIR subfields. Incorrect extraction can point interrupt code at the wrong BAR or table location.
- SR-IOV and VF resizable BAR fields are dense and repeated. Wrong VF count, stride, first-offset, page-size, or BAR-size masks can expose invalid VF topology or resource apertures.
- Header/TLP-prefix logs are full-dword fields. They look mechanically simple, but using the wrong function prefix can make diagnostics report the wrong endpoint's captured transaction.
- The `L` suffix and 16-bit-looking masks are generated for C macro use. Consumers should keep normal unsigned register-width handling to avoid sign/width surprises when composing values.

## Test and Validation Signals

Useful validation signals for this chunk are mostly generated-header consistency checks plus hardware or emulator coverage:

- Build AMDGPU configurations that include NBIO 7.11 generated headers to catch malformed macro names and duplicate or missing definitions.
- Check that, after adjacent chunks are merged, every register field has a matching `__SHIFT` and `_MASK` pair. The expected local exceptions are the four starting `DEV0_EPF5_PCIE_CORR_ERR_MASK` masks and the incomplete ending `DEV0_EPF7_COMMAND` block.
- Cross-check all register names in this range against `nbio_7_11_0_offset.h` so field macros have matching address macros where expected.
- Run mechanical symmetry checks across repeated endpoint/function layouts: `DEV1_EPF1` and `DEV0_EPF6` should match for common PCI header, PM, PCIe, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, and RTR fields, while `DEV1_EPF1` legitimately has extra SR-IOV and VF resize BAR sections in this range.
- Validate PCI config-space dumps on NBIO 7.11 hardware by decoding `DEV0_EPF5`, `DEV1_EPF1`, `DEV0_EPF6`, and `DEV0_EPF7` registers with these masks and comparing against expected capability chains.
- Exercise AER paths with controlled correctable and uncorrectable PCIe errors, then confirm status, mask, severity, first-error pointer, header log, and TLP-prefix log decoding.
- Validate MSI/MSI-X setup by checking message control, 64-bit address/data, vector masks, pending bits, table offset/BIR, and PBA offset/BIR for the relevant endpoint/function.
- Validate virtualization/isolation paths by enabling ACS/PASID/ARI and, for `DEV1_EPF1`, SR-IOV/VF BAR settings, then confirming enumeration, DMA isolation, VF resource sizing, and function routing.
- Run reset, FLR, D3 transition, and suspend/resume coverage to confirm driver initialization restores policy fields and that RTR timing/status fields decode as expected.

## Chunk Boundary Notes

This chunk begins at line 17198 with only the final masks of `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK`; the shifts and earlier corrected-error masks are in the previous work item. It then completes the visible `DEV0_EPF5` advanced-error and extended-capability tail through `RTR_DATA2`.

Lines 17501-18655 cover the visible `DEV1_EPF1` block from `VENDOR_ID` through `RTR_DATA2`, including SR-IOV and VF resizable BAR definitions. Lines 18656-19662 cover the visible `DEV0_EPF6` block from `VENDOR_ID` through `RTR_DATA2`. The chunk then starts `DEV0_EPF7` at line 19665 and stops at line 19674 after `COMMAND__MEM_ACCESS_EN__SHIFT`; the next chunk is required for the rest of `DEV0_EPF7_COMMAND` and later `DEV0_EPF7` fields.
