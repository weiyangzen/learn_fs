# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 66319-68739

## Scope

This chunk is part of AMDGPU's generated NBIO 2.3 register mask header. It contains C preprocessor `#define` constants for bit shifts and masks in the NBIF/BIF PCI configuration decoder for SR-IOV virtual functions on device 0, endpoint function 0. The covered slice starts in the tail of the `VF12` configuration space, contains complete `VF13` and `VF14` address blocks, and ends in the early MSI-X fields of `VF15`.

The chunk is declarative: it defines register field names, bit positions, and masks. It does not define functions, structures, executable control flow, storage, or initialization logic.

## Purpose

The macros provide symbolic field encodings for NBIO PCIe configuration registers so driver code can read, write, compose, and decode MMIO or PCI config-space values without hard-coded bit constants. The repeated prefix layout is:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK`

For this chunk, `<n>` spans `12`, `13`, `14`, and `15`. These map the same PCI/PCIe capability and extended capability fields for multiple virtual functions. The constants are expected to be paired with register offset definitions from the companion NBIO register header, while this file supplies only per-field shifts and masks.

## Address Blocks and Register Coverage

The visible address block markers are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp` beginning at line 66900.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp` beginning at line 67596.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp` beginning at line 68292.

The line range begins after the `VF12` block has already started. It includes the tail of `VF12`, beginning with `ROM_BASE_ADDR`/`CAP_PTR`-area fields and continuing through PCIe, MSI/MSI-X, vendor-specific, Advanced Error Reporting, ATS, and ARI capability fields. The line range ends before the `VF15` block reaches the vendor-specific, AER, ATS, and ARI definitions.

Major register groups covered:

- Basic PCI header fields for complete `VF13`, `VF14`, and partial `VF15`: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class-code fields, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability list and capability/control/status fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI and MSI-X capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data fields, mask and pending fields, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific PCIe extended capability fields for `VF12` through `VF14`: enhanced capability list header, vendor-specific header, and scratch registers.
- PCIe Advanced Error Reporting fields for `VF12` through `VF14`: enhanced capability list header, uncorrectable error status/mask/severity, correctable error status/mask, error capability/control, TLP header logs, and TLP prefix logs.
- ATS and ARI extended capability fields for `VF12` through `VF14`: ATS capability/control and ARI capability/control.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The usable interface is the macro namespace itself.

Important macro families:

- `*_COMMAND__*`: standard PCI command bits such as I/O access, memory access, bus mastering, SERR, and interrupt disable.
- `*_STATUS__*`: standard PCI status bits such as interrupt status, capability list support, abort indications, system error, and parity error.
- `*_BASE_ADDR_[1-6]__BASE_ADDR_*` and `*_ROM_BASE_ADDR__BASE_ADDR_*`: BAR/ROM BAR field masks.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*`: PCIe capability fields for payload/read request sizing, FLR, link width/speed, ASPM/PM controls, link retrain/disable, and equalization status.
- `*_MSI_*` and `*_MSIX_*`: interrupt capability programming fields for MSI enablement, 64-bit address support, vector masks/pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*`: AER status, mask, severity, ECRC, multi-header recording, and log-presence fields.
- `*_PCIE_ATS_*` and `*_PCIE_ARI_*`: address translation service and alternative routing-ID interpretation capability/control fields.

All constants use integer literal masks with an `L` suffix and hex shifts. Consumers should use the mask width implied by the register: many fields are 16-bit PCI capability words, while others are 32-bit extended capability or BAR/log registers.

## Control Flow

There is no runtime control flow. Inclusion is controlled by the surrounding header guard in the full file, outside this slice. At compile time, source files that include the generated NBIO headers gain access to these constants. Runtime behavior happens only in code that uses these macros to operate on hardware registers.

Typical consumer flow inferred from the macro design:

1. Read a PCIe config or NBIO register value through AMDGPU's register access helpers.
2. Use `*_MASK` and `*_SHIFT` to extract a field or prepare an updated value.
3. Write the composed value back to the register when enabling or disabling PCI/PCIe features.

## State and Persistence Behavior

This header stores no software state and performs no persistence. The state represented by the macros lives in hardware PCI configuration registers for SR-IOV VFs. Some fields are configuration bits that persist until reset or function-level reset, such as `BUS_MASTER_EN`, `MEM_ACCESS_EN`, MSI/MSI-X enables, ATS enable, ARI controls, completion timeout controls, and link-control bits. Other fields expose hardware status or write-one-to-clear-style error state in the PCIe/AER register model, such as device status, link status, correctable and uncorrectable error status, and header/TLP prefix logs.

Because this slice contains virtual-function config-space fields, state is sensitive to SR-IOV lifecycle events. VF reset, FLR, PF-driven virtualization setup, guest driver programming, and host PCI core policy can all change the underlying register contents independently of this header.

## Dependencies and Integration Points

Dependencies are mostly structural:

- The companion NBIO 2.3 register offset header supplies register addresses; this `_sh_mask.h` file supplies field encodings.
- AMDGPU register access macros and helpers use these constants to build `REG_SET_FIELD`, `REG_GET_FIELD`, or equivalent bitfield operations.
- Linux PCI/PCIe behavior is reflected in the field naming: the register layout follows standard PCI configuration header, PCIe capability, MSI/MSI-X capability, AER extended capability, ATS, and ARI definitions.
- SR-IOV support depends on the PF/VF hardware model. The repeated `VF12`, `VF13`, `VF14`, and `VF15` blocks are integration points for per-VF configuration decode windows.
- Interrupt setup integrates with MSI/MSI-X programming paths through `MSI_MSG_CNTL`, message address/data, mask/pending, MSI-X table, and PBA fields.
- Error handling and diagnostics integrate with PCIe AER paths through uncorrectable/correctable status/mask/severity fields and header/TLP prefix logs.
- IOMMU and address translation integration can use ATS fields: invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.

## Risks and Edge Cases

- Generated macro drift is the primary risk. If masks or shifts do not match the hardware register database for NBIO 2.3, all downstream bitfield reads/writes can silently target the wrong bits.
- The chunk boundaries are partial: `VF12` begins before this range and `VF15` continues after it. A final per-file reconciliation should avoid treating this chunk as a complete view of either VF block.
- The repeated VF blocks are intentionally near-identical. Copy-generation mistakes are hard to detect by review because most lines differ only by VF number.
- Several control bits can affect device availability or PCIe link behavior if used incorrectly, including `INITIATE_FLR`, `LINK_DIS`, `RETRAIN_LINK`, `HW_AUTONOMOUS_WIDTH_DISABLE`, `HW_AUTONOMOUS_SPEED_DISABLE`, MSI/MSI-X enables, ATS `ATC_ENABLE`, and ARI forwarding/function-group controls.
- AER registers include status, mask, and severity fields with similar names. Confusing these families can suppress reporting, misclassify errors, or clear/inspect the wrong status.
- Width handling matters. Some masks cover 8-bit, 16-bit, or 32-bit fields; consumers should avoid truncation or sign-extension assumptions around `L`-suffixed literals.
- BAR and MSI-X table/PBA fields carry address or offset encodings where low bits are either reserved or BIR selectors. Consumers must preserve reserved/selector bits as required by PCIe layout.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/driver integration checks:

- Compile coverage for files including `nbio_2_3_sh_mask.h`; undefined macro or duplicate-name issues should fail normal AMDGPU builds.
- Static consistency checks comparing this `_sh_mask.h` against the corresponding NBIO register-offset header and AMD hardware register database.
- Pattern checks across `VF12`, `VF13`, `VF14`, and `VF15` blocks to confirm that identical register families have identical field shifts/masks, except where the line-range boundary intentionally omits fields.
- Runtime smoke tests on hardware with SR-IOV enabled: enumerate VFs, bind guest/host drivers, enable memory and bus-master access, program MSI/MSI-X, and verify interrupts arrive.
- PCIe capability inspection with tools such as `lspci -vv` or driver debug dumps to confirm exposed payload size, FLR capability, link speed/width, AER, ATS, and ARI values line up with expected hardware behavior.
- Error-path tests that inject or observe PCIe AER conditions and verify correctable/uncorrectable status, masks, severity bits, and header logs decode correctly.
- Reset tests around VF FLR and PF-driven VF teardown/recreation to ensure status and control fields return to expected reset values.
