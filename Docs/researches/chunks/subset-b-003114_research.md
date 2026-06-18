# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 112319-114771

## Scope

This chunk is a generated AMD NBIO 7.0 register bitfield mask header segment. It contains `#define` constants for field shifts and field masks, not executable code. The covered range begins in the tail of the `BIF_CFG_DEV0_EPF7_2` PCI configuration-space decode block, covers the complete `BIF_CFG_DEV1_EPF0_2` block, and starts the `BIF_CFG_DEV1_EPF1_2` block through the first DPA capability fields. The definitions are consumed by code that includes `nbio_7_0_sh_mask.h` together with the paired NBIO offset/default headers.

## Purpose

The purpose of this chunk is to provide stable symbolic field layouts for AMD NBIO/BIF PCIe configuration registers. Each register receives one or more `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros, allowing driver code to extract or compose individual fields without embedding raw bit arithmetic at call sites.

The chunk models PCI configuration and extended capability structures for endpoint/function slices:

- `BIF_CFG_DEV0_EPF7_2`: SATA capability, vendor-specific capability, Advanced Error Reporting, BAR capability/control, power budget, Dynamic Power Allocation, Access Control Services, and ARI capability fields.
- `BIF_CFG_DEV1_EPF0_2`: full PCI config header fields plus power management, PCIe capability, MSI/MSI-X, SATA, vendor-specific, Virtual Channel, Advanced Error Reporting, BAR, power budget, DPA, Secondary PCIe extended capability, per-lane equalization, ACS, LTR, and ARI fields.
- `BIF_CFG_DEV1_EPF1_2`: full PCI config header prefix through MSI/MSI-X, SATA/vendor-specific, AER, BAR, power budget, and DPA capability fields up to `PWR_ALLOC_SCALE`.

## Important APIs, Types, and Macros

There are no C types or functions in this chunk. The important public interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field mask in the register's native width, usually 16 or 32 bits.
- AMDGPU's helper macros in `drivers/gpu/drm/amd/amdgpu/amdgpu.h` compose these names:
  - `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
  - `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
  - `REG_SET_FIELD(orig_val, reg, field, field_val)` clears the mask and inserts a shifted field value.
  - `REG_GET_FIELD(value, reg, field)` masks and shifts a raw register value.

Important register groups in the chunk:

- PCI identity/header: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1..6`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, and latency grant fields for `DEV1_EPF0` and `DEV1_EPF1`.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X: message control, address/data, masks, pending bits, table BAR indicator, and PBA offsets.
- Advanced Error Reporting: uncorrectable/correctable status, mask, severity, `ADV_ERR_CAP_CNTL`, four TLP header log registers, and four TLP prefix log registers.
- BAR enhanced capability: capability header plus `BAR1..BAR6` supported-size and control fields.
- Power management extensions: Power Budgeting capability/data and DPA capability/status/control/substate allocation fields.
- PCIe isolation/routing extensions: ACS capability/control, ARI capability/control, LTR for `DEV1_EPF0`, and VC capability/resource fields for `DEV1_EPF0`.
- Link training diagnostics for `DEV1_EPF0`: secondary capability, `LINK_CNTL3`, `LANE_ERROR_STATUS`, and lane 0 through lane 15 equalization controls.

## Control Flow

This header has no runtime control flow. Its effective control flow is compile-time token expansion:

1. A driver source includes `nbio_7_0_sh_mask.h` alongside the matching NBIO register address/default headers.
2. The source reads or prepares a raw register value through AMDGPU register accessors.
3. `REG_GET_FIELD()` or `REG_SET_FIELD()` expands the selected `REGISTER__FIELD` pair into a mask/shift operation.
4. The resulting value is used for initialization, feature detection, error reporting, interrupt configuration, power management, or PCIe link handling.

Because this chunk covers PCI config-space-like structures, runtime accesses are normally mediated by NBIO/BIF register addressing and platform-specific register access layers rather than by this file directly.

## State and Persistence Behavior

The macros do not store state and do not persist values. The state they describe lives in hardware registers:

- Status fields, such as AER correctable and uncorrectable status bits, reflect PCIe error state latched by hardware and often require write-to-clear behavior at the register access layer.
- Control fields, such as MSI/MSI-X enable bits, PCIe Device Control flags, BAR sizing controls, DPA controls, ACS controls, and ARI controls, persist in the device's register/configuration state until reset or reprogramming.
- Capability fields, such as BAR sizes, ECRC support, link speeds, power allocation scales, and ARI/ACS support, are hardware capability descriptors and should usually be treated as read-only by higher-level code.
- Default reset values are described in `nbio_7_0_default.h`, not in this `sh_mask` chunk. For example, defaults exist for covered symbols such as `smnBIF_CFG_DEV0_EPF7_2_SATA_CAP_0_DEFAULT`, `smnBIF_CFG_DEV1_EPF0_2_VENDOR_ID_DEFAULT`, `smnBIF_CFG_DEV1_EPF1_2_VENDOR_ID_DEFAULT`, and `smnBIF_CFG_DEV1_EPF1_2_PCIE_DPA_CAP_DEFAULT`.

## Dependencies

The chunk depends on the generated ASIC register header ecosystem:

- `nbio_7_0_sh_mask.h` provides only field masks and shifts.
- `nbio_7_0_offset.h` provides register offsets/addresses for the same symbolic register names where present.
- `nbio_7_0_default.h` provides reset/default values for many `smn...` registers.
- `amdgpu.h` provides the token-pasting field helpers that consume these definitions.

Direct includes of the NBIO 7.0 mask header were found in:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`
- `drivers/gpu/drm/amd/amdgpu/soc15.c`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`

The local tree does not contain a `nbio_7_0_d.h`; address metadata for NBIO 7.0 is represented by `nbio_7_0_offset.h` and `nbio_7_0_smn.h`.

## Integration Points

This file is part of the AMDGPU ASIC register ABI. Integration is compile-time and symbol-name based:

- NBIO initialization code can use these masks to program doorbells, PCIe features, interrupt routing, and BIF configuration registers.
- SOC15 common code includes the header so shared register manipulation macros can target NBIO 7.0 fields.
- PowerPlay/SMU code includes the header through `smu10_inc.h`, making the same field definitions available to power-management paths.
- PCIe error handling or diagnostics can interpret AER status/mask/severity fields and header/prefix log registers using these definitions.
- PCIe link training and speed handling can inspect `LINK_CAP`, `LINK_STATUS`, `LINK_CAP2`, `LINK_STATUS2`, and per-lane equalization fields.
- Virtualization and multi-function routing logic can rely on the `DEVx_EPFy` naming to address the correct endpoint/function register block.

## Risks and Edge Cases

- Bitfield drift is high impact. Any incorrect shift or mask silently corrupts field extraction/insertion in all users of `REG_GET_FIELD()` and `REG_SET_FIELD()`.
- Register-name context matters. This chunk crosses from `DEV0_EPF7` to `DEV1_EPF0` and then to `DEV1_EPF1`; using a field macro with the wrong register prefix may compile if a similarly named field exists but target the wrong function's layout.
- Several fields are reserved or capability descriptors. Driver code should avoid writing reserved bits and should preserve them during read-modify-write operations.
- AER status, mask, and severity registers have different semantics despite sharing similar field names. Confusing status bits with mask bits or severity bits can hide errors or report incorrect severity.
- MSI and MSI-X controls include enable/function-mask/table fields with 16-bit masks; code must respect register width and not assume all config fields are 32-bit.
- BAR enhanced control fields use compact masks (`BAR_INDEX`, `BAR_TOTAL_NUM`, `BAR_SIZE`). Incorrect sizing writes can affect PCI resource aperture behavior.
- DPA and power budget fields encode units/scales and selected entries. Reading `DATA` without setting or understanding `DATA_SELECT` may produce misleading power information.
- Per-lane equalization fields repeat for lanes 0-15. Mechanical copy/paste mistakes around lane numbers can cause link training diagnostics or tuning to refer to the wrong lane.
- Some covered macros have matching defaults but may not have obvious offset matches in every generated header namespace. Users need the correct `mm`, `ix`, or `smn` address symbol family for the access path they are using.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Build coverage for AMDGPU configurations that include `nbio_v7_0.c`, `soc15.c`, and SMU10 PowerPlay headers verifies that token-pasted field names resolve.
- Static checks can verify every `__SHIFT`/`_MASK` pair is internally consistent: mask width covers the shifted field and fields do not unexpectedly overlap within a register.
- Generated-header consistency checks can compare `nbio_7_0_sh_mask.h` against `nbio_7_0_offset.h` and `nbio_7_0_default.h` for register-name coverage.
- Runtime smoke tests on NBIO 7.0 hardware should monitor PCIe link status, MSI/MSI-X interrupt delivery, BAR sizing/resource assignment, AER status reporting, and power-management transitions.
- Error-injection or PCIe AER tests should confirm correct interpretation of uncorrectable/correctable status, masks, severity, and TLP header/prefix logs.
- Link training diagnostics should confirm lane error and equalization registers map correctly across all 16 lanes for `DEV1_EPF0`.
