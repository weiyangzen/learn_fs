# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 7321-9744

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It defines C preprocessor constants for decoding and programming bitfields in NBIF/BIF PCI configuration-space registers. The macros are register-field geometry only; they do not implement Ceph or distributed-filesystem behavior despite the mirrored source path.

The inspected range contains 2,424 source lines, 280 commented register blocks, and 2,140 `#define` entries: 1,072 `__SHIFT` constants and 1,068 `_MASK` constants. The shift/mask imbalance is from chunk boundaries: the chunk starts after the `BIF_CFG_DEV0_SWDS0_LINK_CAP` shifts have already been defined in the previous chunk and ends before all masks for `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK` have appeared.

At a high level, this range covers:

- The tail of `BIF_CFG_DEV0_SWDS0_LINK_CAP`, then the rest of the `DEV0_SWDS0` PCIe switch/downstream-port capability map through lane margining.
- Complete visible PCI configuration images for `DEV0_EPF0_VF0_0` from vendor/device identity through ATS and ARI capability/control blocks.
- The beginning and most of the same shape for `DEV0_EPF0_VF1_0`, from vendor/device identity through the start of the Advanced Error Reporting uncorrectable-error mask block.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The only API surface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

The `DEV0_SWDS0` section describes a downstream/switch-style PCIe capability set. It includes standard link and slot controls/status, device capability/control 2, link capability/control/status 2, MSI message registers, subsystem ID capability, vendor-specific enhanced capability fields, virtual channel capability/control/status for VC0 and VC1, device serial number, Advanced Error Reporting, secondary PCIe capability, per-lane equalization, ACS, data-link feature capability, 16 GT/s PHY capability and status, and lane margining controls/status for lanes 0-15.

Important `DEV0_SWDS0` macro groups include:

- Link and slot management: `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- PCIe 4.0/16 GT/s related fields: `PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local and RTM parity mismatch status, and `LANE_n_EQUALIZATION_CNTL_16GT`.
- Error handling: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs, and TLP prefix logs.
- Lane diagnostics: `PCIE_LANE_ERROR_STATUS`, `PCIE_LANE_n_EQUALIZATION_CNTL`, and `LANE_n_MARGINING_LANE_CNTL`/`STATUS` for lanes 0 through 15.
- Isolation and routing: ACS capability/control, data-link feature capability/status, virtual-channel resource capability/control/status, and vendor-specific enhanced capability registers.

The `DEV0_EPF0_VF0_0` and `DEV0_EPF0_VF1_0` blocks define virtual-function PCI configuration fields. Each has the standard PCI header identity and configuration registers: vendor/device ID, `COMMAND`, `STATUS`, revision and class-code fields, cache-line size, latency, header type, BIST, six base-address registers, adapter ID, ROM BAR, capability pointer, interrupt line/pin, PCIe capability list/header, device capability/control/status, link capability/control/status, device/link capability 2, MSI and MSI-X structures, vendor-specific enhanced capability, and AER status/logging fields.

`DEV0_EPF0_VF0_0` continues past AER into ATS and ARI:

- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` define address translation service metadata, invalidation queue depth, page-aligned request support, small translation unit, and ATS enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` define alternative routing-ID interpretation next-function, function-group, and MSI function-group controls.

`DEV0_EPF0_VF1_0` repeats the same standard VF layout visible in this chunk, but the range stops inside `PCIE_UNCORR_ERR_MASK`. Its later AER, ATS, and ARI definitions are expected in the next chunk.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is included at compile time and contributes constants to AMDGPU register access code. Runtime behavior is supplied by callers that combine these masks with matching register offsets and hardware access helpers.

The implied hardware flows are:

1. PCIe/NBIO initialization or enumeration reads identity, class-code, BAR, ROM BAR, capability pointer, interrupt, and PCIe capability fields for each exposed function.
2. Driver or firmware setup programs command enables, device control, link control, link speed targets, MSI/MSI-X controls, ACS, ATS, ARI, virtual-channel policy, and lane diagnostic controls using these masks.
3. Link bring-up and diagnostics inspect current speed/width, link training, data-link-layer active state, equalization completion, lane errors, 16 GT/s equalization, parity mismatch, and margining results.
4. PCIe error handling reads AER status, applies mask/severity policy, and decodes header/TLP-prefix logs for the selected downstream port or virtual function.
5. Virtualization paths use the VF-prefixed blocks to decode per-VF PCI configuration images and to program ATS/ARI behavior where available.

The file itself does not read or write registers, clear status bits, enforce ordering between hardware operations, or validate field values. Those semantics belong to AMDGPU's NBIO/PCIe code and the NBIO 7.4 hardware specification.

## State and Persistence

The header owns no mutable state, allocates no memory, persists nothing, and performs no I/O. The represented state lives in NBIO/BIF PCI configuration-space registers.

State categories represented by this chunk include:

- PCIe link and slot state: ASPM controls, link disable/retrain, common clock, current link speed, negotiated width, data-link-layer active state, bandwidth-management notifications, slot hotplug/presence/power bits, and link capability 2 fields.
- PCIe device policy: completion timeout, atomic operation controls, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefix controls, and virtual-channel resource assignments.
- Interrupt state: MSI capability, message control, 32/64-bit address/data, masks, pending bits, MSI-X table/PBA offset and BIR fields.
- Error-observation and error-policy state: AER uncorrectable/correctable status, masks, severity, ECRC controls, first-error pointer, multiple-header-recording controls, header logs, TLP prefix logs, and lane error status.
- Link-training diagnostics: equalization controls for lanes 0-15, 16 GT/s lane equalization coefficients, parity mismatch status, and lane margining command/status fields.
- Virtual-function configuration state: VF0/VF1 standard PCI header fields, BARs, ROM BAR, capability chain, PCIe device/link controls, AER, vendor-specific scratch fields, ATS controls, and ARI controls.

Persistence across GPU reset, PCI reset, FLR, suspend/resume, BACO, or runtime power transitions is not described by this header. A wrong macro value is persistent in the compiled driver until the generated header is corrected and the driver is rebuilt.

## Dependencies and Integration Points

The direct companion in this directory is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, which supplies the register address/offset side of the same NBIO 7.4 register map. `nbio_7_4_0_smn.h` is also present for SMN-level register definitions, while this file provides field shifts and masks for register values.

Likely AMDGPU integration areas include:

- NBIO 7.4 ASIC initialization and low-level register read/modify/write paths that include generated ASIC register headers.
- PCIe link management code that programs ASPM, retraining, target speed, bandwidth notifications, equalization, and 16 GT/s training fields.
- AER and RAS diagnostic paths that classify correctable and uncorrectable PCIe errors and decode logged TLP headers/prefixes.
- Interrupt setup for MSI and MSI-X message/control/table/PBA fields.
- Virtualization paths that expose or manage `EPF0_VF0_0` and `EPF0_VF1_0` PCI configuration images, including ATS and ARI where present.
- Isolation and routing setup that depends on ACS, virtual channels, ATS, and ARI fields.
- Manufacturing, bring-up, or debug paths that use lane equalization, parity mismatch, lane error, and margining registers.

Integration is primarily by exact symbol naming. The repeated VF0/VF1 register layouts are intentionally similar, but the prefix selects a different hardware function image.

## Risks

- Chunk boundaries split register definitions. This range starts with only the masks for the tail of `BIF_CFG_DEV0_SWDS0_LINK_CAP` and ends before all masks for `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`; pair-completeness checks must run after adjacent chunks are merged.
- Repeated layouts are easy to cross-wire. Using a `VF0_0` macro while accessing a `VF1_0` offset, or using a `SWDS0` macro for a VF register, can silently decode the wrong register image.
- AER status, mask, and severity blocks have nearly identical field names. Confusing them can suppress errors, misclassify severity, or damage diagnostics.
- Link-control fields can affect enumeration and stability. Incorrect masks for retrain, link disable, target speed, autonomous speed/width disable, ASPM, equalization, or 16 GT/s fields can cause link bring-up failures or performance regressions.
- MSI/MSI-X address, data, mask, pending, table, and PBA fields are security- and reliability-sensitive. Incorrect extraction can route interrupts through the wrong BAR, vector, or mask state.
- ACS, ATS, ARI, and virtual-channel fields affect isolation and routing. Bad masks can undermine DMA isolation, break IOMMU/ATS behavior, or misroute PCIe functions.
- Lane margining and equalization registers are dense and repeated across 16 lanes. Off-by-one lane macro use can make diagnostics or tuning target the wrong lane.
- Full-dword log and scratch fields look simple, but the endpoint prefix still matters. Decoding the wrong function's header/TLP-prefix log can misattribute a PCIe fault.
- Generated `L`-suffixed masks should be used with normal unsigned register-width handling to avoid width/sign surprises when composing values.

## Test and Validation Signals

Useful validation signals for this chunk are mostly generated-header consistency checks plus hardware or emulator coverage:

- Build AMDGPU configurations that include `nbio_7_4_sh_mask.h` to catch malformed macro names, duplicate definitions, and compile-time include issues.
- After adjacent chunks are merged, verify every field has a matching `__SHIFT` and `_MASK` pair. Expected local exceptions are the starting `SWDS0_LINK_CAP` masks and the ending partial `VF1_0_PCIE_UNCORR_ERR_MASK` block.
- Cross-check register names in this range against `nbio_7_4_offset.h` so field macros have matching address macros where expected.
- Run mechanical symmetry checks across `DEV0_EPF0_VF0_0` and `DEV0_EPF0_VF1_0` for the common PCI header, PCIe, MSI/MSI-X, vendor-specific, and AER fields that are both visible in this chunk.
- Decode PCI configuration-space dumps from NBIO 7.4 hardware for `DEV0_SWDS0`, `DEV0_EPF0_VF0_0`, and `DEV0_EPF0_VF1_0`, comparing link, slot, MSI/MSI-X, AER, ATS, and ARI fields with expected capability chains.
- Exercise PCIe AER paths with controlled correctable and uncorrectable errors, then confirm status, mask, severity, first-error pointer, header log, and TLP-prefix log decoding.
- Validate MSI/MSI-X setup by checking message control, 64-bit address/data, vector masks, pending bits, table offset/BIR, and PBA offset/BIR for VF0 and VF1.
- Exercise link training and recovery paths across supported speeds, including 16 GT/s equalization where hardware supports it, and confirm link status, lane error, parity mismatch, and equalization result decoding.
- Validate ACS/ATS/ARI behavior under virtualization and IOMMU-enabled configurations, confirming function routing, DMA isolation, ATS enablement, and VF enumeration.
- Use lane margining diagnostics on hardware or simulation to confirm lane-numbered control/status macros map to the expected physical/logical lanes.

## Chunk Boundary Notes

Lines 7321-7322 are the final masks for `BIF_CFG_DEV0_SWDS0_LINK_CAP`; the matching shifts and earlier masks are in the previous chunk. Lines 7323-8554 cover the rest of the visible `DEV0_SWDS0` downstream-port/switch register definitions from `LINK_CNTL` through lane 15 margining status.

Lines 8555-9238 cover the `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` address block for `DEV0_EPF0_VF0_0`, from `VENDOR_ID` through ARI control. Lines 9239-9744 begin the `nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp` block for `DEV0_EPF0_VF1_0`, from `VENDOR_ID` through the first masks of `PCIE_UNCORR_ERR_MASK`. The next chunk is required for the rest of the VF1 AER mask block and later VF1 registers.
