# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 113094-115515

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register mask header. It contains C preprocessor `#define` constants for field shifts and masks in the NBIF/BIF PCI configuration decoder for SR-IOV virtual functions on device 0, endpoint function 0. The covered slice starts in the tail of the `VF20` configuration-space block, contains complete `VF21`, `VF22`, and `VF23` address blocks, and ends in the first fields of the `VF24` block.

The chunk is declarative. It defines register-field names, bit positions, and bit masks. It does not define functions, structures, executable logic, runtime storage, or initialization code.

## Purpose

The macros provide symbolic encodings for NBIO PCI and PCIe configuration registers so AMDGPU code can compose, update, and decode register values without embedding raw bit constants at call sites. The repeated macro naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>_MASK`

For this chunk, `<n>` spans the tail of `20`, all of `21`, `22`, and `23`, and the beginning of `24`. The `_1_` namespace indicates this portion of the generated NBIO register map belongs to the second numbered instance or aperture in the naming scheme used by the hardware register generator. Register offsets are supplied by companion address headers; this `_sh_mask.h` slice supplies the per-field bit encodings.

## Address Blocks and Register Coverage

Visible address block markers in this range are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf21_bifcfgdecp` beginning at line 113366.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf22_bifcfgdecp` beginning at line 114062.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf23_bifcfgdecp` beginning at line 114758.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf24_bifcfgdecp` beginning at line 115454.

The line range begins after the `VF20` block has already started. It covers `VF20` from `MSI_PENDING` through MSI-X, vendor-specific PCIe extended capability, Advanced Error Reporting, ATS, and ARI fields. It then covers full `VF21`, `VF22`, and `VF23` blocks with standard PCI header fields, PCIe capability/control/status fields, MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions. It ends at `VF24_1_PROG_INTERFACE__PROG_INTERFACE__SHIFT`, before the corresponding mask and the rest of `VF24`.

Major register groups covered:

- Standard PCI header fields for complete `VF21` through `VF23` and partial `VF24`: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class-code fields, cache line, latency, header type, BIST, BARs, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability structures: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI message address and data registers, mask and pending registers, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific PCIe extended capability fields: enhanced capability list headers, vendor-specific headers, and scratch registers.
- PCIe Advanced Error Reporting fields: AER enhanced capability headers, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- ATS and ARI extended capability fields: ATS capability/control and ARI capability/control fields used by address translation and alternative routing-ID interpretation support.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The public interface is the generated macro namespace.

Important macro families include:

- `*_COMMAND__*`: standard PCI command bits for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, snooping, parity response, SERR, fast back-to-back, and interrupt disable.
- `*_STATUS__*`: standard PCI status bits for interrupt status, capability-list presence, DEVSEL timing, aborts, system error, parity error, and readiness.
- `*_BASE_ADDR_[1-6]__BASE_ADDR*` and `*_ROM_BASE_ADDR__BASE_ADDR*`: BAR and ROM BAR field encodings.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*`: PCIe capability fields for payload size, read request size, error enables, relaxed ordering, no-snoop, FLR initiation, link speed/width, ASPM, retraining, link disable, clock configuration, equalization, and autonomous width/speed control.
- `*_MSI_*` and `*_MSIX_*`: interrupt capability encodings for MSI enable, multi-message control, 64-bit addressing, per-vector mask/pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*`: AER status, mask, severity, ECRC controls, multi-header recording, completion-timeout logging, and log-presence fields.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*`: 32-bit log-word fields used to decode captured TLP headers and prefixes after PCIe errors.
- `*_PCIE_ATS_*` and `*_PCIE_ARI_*`: address translation service and alternative routing-ID interpretation capability/control fields, including invalidate queue depth, page-aligned request support, global invalidate support, STU, ATC enable, next function number, and ARI function-group controls.

Consumers should pair each `*_MASK` with its matching `*_SHIFT` through AMDGPU bitfield helpers such as register-field get/set macros. Masks use `L`-suffixed hexadecimal literals and cover a mix of 8-bit, 16-bit, and 32-bit fields.

## Control Flow

There is no runtime control flow in this chunk. The only compile-time behavior is header inclusion through the surrounding include guard in the full file. Runtime behavior is supplied by code that includes this header and uses these constants to access NBIO-backed PCI configuration registers.

Typical consumer flow inferred from the macro design:

1. Select the per-VF register offset from the companion NBIO register header.
2. Read a PCI config or NBIO MMIO register value using AMDGPU register access helpers.
3. Extract a field with the matching `*_MASK` and `*_SHIFT`, or compose an updated value with the same pair.
4. Write the value back when enabling, disabling, clearing, or programming a PCIe feature.

## State and Persistence Behavior

This header stores no software state and performs no persistence. The state described by these constants lives in hardware PCI configuration and PCIe extended capability registers for SR-IOV virtual functions.

Some represented fields are configuration state that can persist until device reset, VF reset, function-level reset, or PF-driven reinitialization. Examples include `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `INT_DIS`, PCIe error-reporting enables, payload/read request sizing, MSI/MSI-X enablement, MSI-X function mask, ATS `ATC_ENABLE`, ARI controls, link-control bits, and completion-timeout settings.

Other fields represent hardware-observed status or error state, such as PCI status abort/parity bits, PCIe device/link status, AER correctable and uncorrectable status, AER first-error pointers, and TLP header/prefix logs. These may be read-only, sticky, or clear-on-write according to the underlying PCIe register semantics; the header only names the bits and does not enforce access policy.

Because this is VF configuration space, the underlying register contents can also be affected by SR-IOV lifecycle events, guest driver behavior, host PCI core policy, PF virtualization setup, FLR, hot reset, and device teardown/recreation.

## Dependencies and Integration Points

Dependencies are structural and generated-header based:

- The companion NBIO 2.3 register-offset header supplies register addresses; this file supplies field shifts and masks.
- AMDGPU register access and bitfield helper macros are the expected consumers for constructing and decoding register values.
- Linux PCI/PCIe enumeration and configuration paths provide the protocol model reflected by the field names: standard PCI header, PCIe capability, MSI/MSI-X, AER, ATS, and ARI.
- SR-IOV support depends on the repeated VF blocks. `VF21`, `VF22`, and `VF23` are complete in this chunk, while `VF20` and `VF24` require neighboring chunks for full per-VF coverage.
- Interrupt setup integrates through MSI and MSI-X fields, especially message address/data, vector mask/pending registers, table/PBA offsets, MSI-X function mask, and enable bits.
- PCIe error handling and diagnostics integrate through AER status/mask/severity fields, ECRC controls, first-error pointer, and captured TLP header/prefix log fields.
- IOMMU and address translation integration can use ATS fields such as invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.
- ARI integration depends on the ARI enhanced capability list, next-function number, and function-group enable fields used to expose or route extended PCIe function numbering.

## Risks and Edge Cases

- Generated macro drift is the main risk. If a shift or mask differs from the NBIO 2.3 hardware register database, downstream reads and writes can silently target the wrong bits.
- The line-range boundaries are partial. `VF20` begins before this chunk and `VF24` continues after it, so final per-file reconciliation should not treat either as complete from this document alone.
- The repeated VF blocks are intentionally near-identical. Generator or copy errors can be difficult to spot because most lines differ only by `VF21`, `VF22`, or `VF23`.
- Several fields can affect VF availability or data movement if programmed incorrectly, including `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `INITIATE_FLR`, `LINK_DIS`, `RETRAIN_LINK`, MSI/MSI-X enables, MSI-X function mask, ATS `ATC_ENABLE`, and ARI controls.
- AER status, mask, and severity fields use very similar names. Mixing the families can suppress reporting, misclassify errors, or inspect/clear the wrong status.
- Width handling matters. Some masks represent 8-bit or 16-bit PCI fields while others represent full 32-bit registers; consumers should avoid implicit truncation and should preserve reserved bits when updating partial fields.
- BAR and MSI-X table/PBA fields carry address-like encodings where low bits may be selectors or reserved bits. Incorrect masking can corrupt BIR selection or offset alignment.
- The final line contains only `VF24_1_PROG_INTERFACE__PROG_INTERFACE__SHIFT`; its mask is outside this chunk. Any automated completeness check must account for the boundary rather than flagging this as a malformed block in the source file.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency checks, and hardware integration tests:

- Normal AMDGPU build coverage for code that includes `nbio_2_3_sh_mask.h`; duplicate macro names, missing dependencies, or syntax errors should fail compilation.
- Static comparison against the companion NBIO register-offset header and the authoritative AMD register database to confirm every field has the expected shift and mask.
- Pattern checks across complete `VF21`, `VF22`, and `VF23` blocks to confirm equivalent register families have identical field encodings, with only the VF number changing.
- Boundary-aware checks that compare the tail of `VF20` and beginning of `VF24` against adjacent chunks before drawing conclusions about completeness.
- Runtime SR-IOV smoke tests on supported AMD hardware: create VFs, enumerate them, bind host/guest drivers, enable memory and bus mastering, and verify configuration-space access behaves as expected.
- Interrupt tests that program MSI and MSI-X for VFs and confirm vectors are delivered, masking/pending state decodes correctly, and MSI-X table/PBA offsets are sane.
- PCIe capability inspection with `lspci -vv`, debugfs, or driver debug dumps to confirm payload, read request, FLR, link, AER, ATS, and ARI values decode as expected.
- Error-path tests that inject or observe PCIe AER events and verify correctable/uncorrectable status, masks, severity fields, first-error pointer, and header/prefix logs decode correctly.
- Reset and lifecycle tests around VF FLR, PF-driven VF teardown/recreation, and hot reset to confirm control and status fields return to expected values.
