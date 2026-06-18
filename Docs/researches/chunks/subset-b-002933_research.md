# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 71164-73585

## Scope

This chunk is a generated AMDGPU NBIO 2.3 shift/mask header slice. It contains C preprocessor constants for PCI configuration-space fields, not executable code. Each register field is represented by a `BIF_CFG_DEV0_EPF0_VF*_0_*__FIELD__SHIFT` macro and a matching `BIF_CFG_DEV0_EPF0_VF*_0_*__FIELD_MASK` macro.

The range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF19_0` block at `BASE_ADDR_1`, then covers the rest of VF19, all of VF20 and VF21, and most of VF22 through `PCIE_ARI_CNTL`. The explicit address-block anchors in the chunk are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf20_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf21_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf22_bifcfgdecp`

The chunk includes 2,416 comment or `#define` lines and describes repeated PCIe capability layouts for SR-IOV virtual functions 19-22 on device 0, endpoint function 0.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield contract between AMDGPU/NBIO code and NBIO 2.3 hardware registers. This chunk describes PCI configuration-space fields for late SR-IOV virtual functions. It lets C code, firmware-facing tooling, register decoders, and diagnostics compose or decode config-space dwords without hard-coding bit positions.

The fields cover:

- PCI header identity and class fields: vendor/device ID, command/status, revision, class/subclass/programming interface, cache line, latency, header type, BIST, BARs, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI Express capability fields: capability list, device/link capabilities, device/link control, device/link status, and the PCIe capability version/device type/interrupt-message metadata.
- PCIe capability 2 fields: completion timeout, ARI forwarding, atomic operation support, ID-based ordering, latency tolerance reporting, optimized buffer flush/fill, 10-bit tags, TLP prefix support, emergency power reduction, FRS support, target link speed, compliance, equalization, crosslink, DRS, and RTM presence bits.
- MSI/MSI-X capability fields: MSI enable, multiple-message capability/enable, 64-bit MSI, per-vector masking, MSI address/data/mask/pending registers, MSI-X table size, function mask, enable, table BAR indicator/offset, and PBA BAR indicator/offset.
- Vendor-specific PCIe extended capability fields: extended capability ID/version/next pointer, VSEC ID/revision/length, and two scratch dwords.
- Advanced error reporting fields: uncorrectable and correctable error status/mask/severity bits, ECRC and header-log capability/control bits, first error pointer, TLP header logs, and TLP prefix logs.
- ATS and ARI extended capability fields: ATS capability/control and ARI capability/control, including invalidate queue depth, page-aligned request, global invalidate support, STU, ATC enable, next-function number, function-group capability, and function-group enable.

The macros are generated hardware metadata. Their correctness depends on exact naming, shifts, masks, and pairing with the matching offset/default headers for NBIO 2.3.

## Important API Surface

There are no functions, structs, enums, or local types. The public surface is the preprocessor namespace consumed by AMDGPU register helpers and config-space tooling.

Repeated VF blocks:

- VF19 is boundary-partial in this chunk: its `VENDOR_ID` through the start of `BASE_ADDR_1` appear immediately before the requested range. This chunk covers VF19 BARs, legacy PCI header tail, PCIe capability, MSI/MSI-X, VSEC, AER, ATS, and ARI fields.
- VF20 and VF21 are complete in this range from `VENDOR_ID` through `PCIE_ARI_CNTL`.
- VF22 is complete from `VENDOR_ID` through `PCIE_ARI_CNTL` within the requested range.

Core config header fields:

- `VENDOR_ID` and `DEVICE_ID` expose 16-bit ID fields.
- `COMMAND` includes IO, memory, bus-master, special-cycle, memory-write-invalidate, VGA palette snoop, parity response, SERR, fast back-to-back, interrupt disable, INTx emulation disable, and bus-master P2P disable bits.
- `STATUS` exposes legacy PCI status flags such as interrupt status, capability list, parity, DEVSEL timing, target/master abort, SERR, and parity error detected.
- `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS` encode PCI class identity.
- `HEADER` separates header type from the multifunction/device-type bit, and `BIST` exposes completion/start/capability bits.
- `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, and `ROM_BASE_ADDR` are full-width address fields.
- `ADAPTER_ID` packs subsystem vendor ID and subsystem ID.

PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` define capability ID, next pointer, version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` expose payload size, phantom functions, extended tags, L0s/L1 acceptable latency, role-based error reporting, slot power limit/scale, FLR capability/initiation, error enables/status, relaxed ordering, no-snoop, max read request size, auxiliary power, pending transactions, and emergency power-reduction detection.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` expose link speed/width, ASPM/PM support, exit latencies, clock power management, surprise-down and data-link-layer active reporting, bandwidth notifications, port number, retrain/link-disable/common-clock controls, DRS signaling, current speed/width, training, slot clock, data-link active, and bandwidth status bits.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` cover completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS, and reserved status bits.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover supported/target link speeds, compliance, autonomous speed disable, deemphasis, Gen3 equalization phases, RTM presence, crosslink resolution, downstream component presence, and DRS messages.

Interrupt capability fields:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO/HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, and `MSI_PENDING_64` describe both 32-bit and 64-bit MSI layouts. Notably, the low MSI address field starts at bit 2 and masks with `0xFFFFFFFCL`.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` define MSI-X capability metadata, table size, function mask, enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

Extended capability fields:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` expose VSEC list metadata, VSEC ID/revision/length, and scratch registers.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0-3`, and `PCIE_TLP_PREFIX_LOG0-3` define the AER reporting surface for uncorrectable/correctable PCIe errors and captured packet headers.
- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` define ATS metadata, invalidate queue capability, page-aligned request support, global invalidate support, STU, and ATC enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` define ARI metadata, function-group capabilities, next-function number, and function-group controls.

## Control Flow and Runtime Use

This header has no executable control flow. Runtime behavior is supplied by code that includes the generated NBIO 2.3 headers and performs PCIe/NBIO register access.

The usual flow for these macros is:

1. Select the matching config-space offset from `nbio_2_3_offset.h`, such as `cfgBIF_CFG_DEV0_EPF0_VF20_0_VENDOR_ID` at `0x0000`, `cfgBIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1` at `0x0010`, or `cfgBIF_CFG_DEV0_EPF0_VF22_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST` at `0x0150`.
2. Read a 16-bit or 32-bit config-space value through the appropriate NBIO/PCIe access path.
3. Decode with `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, or update by clearing the mask and shifting the new field value into place.
4. Write the value back only when the field is writable and when PF/VF ownership permits the access.

In this repository snapshot, direct references to the late-VF macro names are not present in the main C consumers. The header is still included by `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`. Those files mostly use NBIO 2.3 register helpers and non-VF or SMN names for PCIe link, LTR, doorbell, HDP flush, clock-gating, and virtualization-related control. The VF19-22 definitions therefore act as generated ABI coverage for register decoders, diagnostics, firmware/PF management paths, and future code rather than as heavily used in-tree C symbols in this snapshot.

## State and Persistence Behavior

The macros themselves are stateless compile-time constants. The state they describe is PCI configuration and PCIe extended capability state for SR-IOV virtual functions in NBIO hardware.

Important hardware state represented by this chunk includes:

- BAR and ROM BAR registers, which define MMIO aperture exposure for each VF. These values persist in config space until reset, FLR, PF/firmware reconfiguration, or OS PCI resource assignment changes them.
- Command register bits, which govern memory/IO decode, bus mastering, SERR, parity behavior, interrupt disable, and VF-specific forwarding controls. Incorrect persistence here can make a VF unable to DMA or can leave decode enabled when it should be disabled.
- Device/link control state, including max payload, max read request, relaxed ordering, no-snoop, FLR initiation, link disable/retrain/common-clock/autonomous width/speed controls, target link speed, and compliance settings.
- Device/link status and AER status/log fields, which are live hardware status surfaces. Some error status bits may be write-one-to-clear depending on PCIe semantics, and captured header/TLP prefix logs preserve diagnostic data until cleared or overwritten.
- MSI/MSI-X state, including enable bits, MSI address/data, vector masks, pending bits, MSI-X function mask, table size, table location, and PBA location. These fields coordinate with host interrupt programming and must remain consistent with OS/PCI core ownership.
- ATS and ARI state, which affects address translation services, ATC enablement, STU programming, and function routing/grouping for virtualization.
- VSEC scratch registers, which may be used by firmware, PF management, diagnostics, or virtualization workflows as device-specific coordination state.

`nbio_2_3_default.h` provides reset/default values for these config fields. Examples found near this chunk's companion definitions include default zeroes for VF BAR/ID fields and `0x20020000` for `cfgBIF_CFG_DEV0_EPF0_VF22_0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST_DEFAULT`. Any initialization or validation code should use the default header rather than inferring reset values from masks.

## Dependencies and Integration Points

Generated-register dependencies:

- `nbio_2_3_offset.h` supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. Many VF blocks reuse standard PCI config offsets, so the register name and selected VF address block are both part of the identity.
- `nbio_2_3_default.h` supplies matching `cfg..._DEFAULT` reset values.
- Other parts of `nbio_2_3_sh_mask.h` define adjacent VF blocks and the non-VF/PF NBIO fields used by the same include consumers.

Driver and subsystem integration:

- `amdgpu/nbio_v2_3.c` includes this header and implements NBIO 2.3 behavior for doorbell ranges, HDP flush registers, PCIe link controls, LTR controls, medium-grain clock gating, and related NBIO function-table hooks.
- `amdgpu/mxgpu_nv.c` includes the same header for Navi virtualization support, making the SR-IOV VF config-space layout relevant to PF/VF management even when the exact late-VF macros are not referenced by name in this file.
- SMU11 files include NBIO 2.3 masks for platform and power-management interactions with PCIe/NBIO state.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, and SOC15 offset helpers are the normal access style for nearby NBIO fields. Config-space users must still choose the access path that is valid for `cfg...` registers.
- Linux PCI core, SR-IOV enablement, VF assignment, IOMMU/ATS policy, and interrupt setup all interact with the same config-space concepts described by this generated header.

## Risks and Edge Cases

- This chunk starts mid-register-family for VF19. A final per-file report must merge the previous chunk to document VF19 identity, command/status, class, header, and `BASE_ADDR_1` start completely.
- VF20, VF21, and VF22 repeat almost identical field names. Copying a mask from the wrong VF block is compile-time valid if the symbol exists, but semantically points at a different virtual function.
- Offset/mask generation mismatch is high risk. These masks must be paired with `nbio_2_3_offset.h`; using NBIO 2.3 masks with another NBIO generation or a nonmatching offset header can silently decode or program wrong bits.
- PCI config-space fields are not uniformly 32-bit. Some capability registers are byte or word-sized by PCI layout, while the generated macros use C integer masks. Access width and alignment must match the hardware/config mechanism.
- BAR, ROM BAR, MSI/MSI-X, ATS, ARI, and command bits are OS/PF-owned in many configurations. Driver or debug writes outside the owner path can break VF assignment, DMA isolation, or interrupt delivery.
- AER status/log fields are diagnostic state. Clearing status or overwriting masks/severity while error handling is active can hide root-cause data or change whether errors are reported as fatal/nonfatal/correctable.
- `DEVICE_CNTL__INITIATE_FLR` and completion-timeout controls affect reset and transaction behavior. Incorrect programming can strand pending transactions or reset a VF unexpectedly.
- ATS/ATC enablement must be coordinated with IOMMU and host support. Enabling ATS for a VF without the right platform policy can compromise correctness or isolation.
- MSI 32-bit and 64-bit layouts intentionally alias some config offsets in the companion offset header. Code must select fields according to `MSI_64BIT` capability rather than assuming both layouts are independently present.
- Link capability/control/status fields may reflect shared physical link state, not per-VF independent hardware. Treating VF link fields as freely programmable can conflict with PF-controlled link management.

## Test and Verification Signals

- Build AMDGPU configurations that include `nbio_2_3_sh_mask.h` and the NBIO 2.3 consumers to catch missing or renamed generated macros.
- Static generation checks should verify that every `BIF_CFG_DEV0_EPF0_VF19_0` through `VF22_0` shift macro in this range has a matching mask macro and a companion `cfg...` offset in `nbio_2_3_offset.h`.
- Compare defaults in `nbio_2_3_default.h` with readback after cold reset or PF reinitialization on matching Navi/NBIO 2.3 hardware.
- In SR-IOV enablement tests, enumerate VFs and confirm vendor/device/class/capability-list fields decode as expected for VF19-22.
- Validate BAR assignment and command register transitions through the Linux PCI core: memory decode and bus mastering should follow VF bind/unbind and assignment state.
- Exercise MSI and MSI-X enable paths for VFs and confirm message address/data, vector mask, pending bits, MSI-X table/PBA locations, and function mask behavior match the generated masks.
- Trigger or inject PCIe correctable and uncorrectable error paths where supported, then verify AER status, mask, severity, first-error pointer, header log, and TLP prefix log decoding.
- Test VF FLR and reset flows and confirm `DEVICE_STATUS__TRANSACTIONS_PEND`, `DEVICE_CNTL__INITIATE_FLR`, AER logs, MSI state, and BAR/command state return to expected post-reset values.
- Validate ATS and ARI exposure under an IOMMU-enabled SR-IOV setup, including ATS capability/control fields and ARI next-function/function-group fields.
- Run register-decode or golden-register tooling against these macros using the NBIO 2.3 offset/default headers to detect drift from AMD's generated register source.
