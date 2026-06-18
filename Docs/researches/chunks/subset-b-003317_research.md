# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 140116-142581

## Purpose

This chunk is part of the generated AMD NBIO 7.7.0 register shift/mask header used by the AMDGPU driver. It contains preprocessor constants for extracting and composing fields in PCI/PCIe configuration-space registers exposed by NBIO/BIF blocks. The chunk has 2,111 `#define` entries, split almost exactly into paired `__SHIFT` and `_MASK` macros, so its role is declarative register metadata rather than executable behavior.

The slice starts in the tail of the `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` area, covers the full `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, and then begins `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` through the EPF2 MSI-X table fields. These names describe device 0 endpoint function 1 and function 2 PCIe configuration decode paths.

## Important APIs, Types, and Macro Contracts

There are no C functions, structs, enums, or storage definitions in this chunk. The exported API is the macro naming convention consumed by AMDGPU register helpers:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted register-width bit mask for the same field.
- Consumers combine these with common AMDGPU helpers such as `REG_GET_FIELD(value, REGISTER, FIELD)` and `REG_SET_FIELD(value, REGISTER, FIELD, field_value)`.
- The matching address header, `nbio_7_7_0_offset.h`, supplies `reg<REGISTER>` offsets. This file supplies only field layout.

The directly related C integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and this `nbio_7_7_0_sh_mask.h`. That file shows the expected pattern: read a 32-bit register with `RREG32_*`, alter fields with shift/mask macros through `REG_SET_FIELD` or manual mask/shift operations, then write with `WREG32_*`.

## Register Groups Covered

The EPF0 tail in this chunk defines GPU IOV vendor-specific data:

- `BIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF13_FB` through `VF15_FB`, each with VF frame-buffer `SIZE` and `OFFSET` fields.
- `GPUIOV_UVDSCH_DW0..DW8`, `GPUIOV_VCESCH_DW0..DW8`, and `GPUIOV_GFXSCH_DW0..DW8`, each exposing full 32-bit `DWn` fields for virtualization scheduling data.

The full EPF1 block is broad and covers standard PCI config header fields plus many PCIe capabilities:

- Basic PCI header: vendor/device IDs, command/status, revision/class/interface bytes, cache line/latency/header/BIST, BAR1-BAR6, ROM BAR, subsystem adapter IDs, interrupt line/pin, and capability pointer.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` fields for PME support, D-state selection, PME status/enables, and data scale/select.
- PCIe core capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus PCIe capability version 2 registers such as `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capabilities: MSI and MSI-X capability headers and controls, message address/data registers, per-vector masks, pending bits, MSI-X table and PBA BIR/offset fields.
- Extended and vendor capabilities: vendor-specific enhanced capability headers, scratch registers, PCIe device serial number, Advanced Error Reporting, Resizable BAR, power budgeting, Dynamic Power Allocation, Secondary PCIe, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, Data Link Feature, 16 GT/s PHY, lane margining, and VF Resizable BAR fields.

The EPF2 block begins a second function's equivalent PCI config layout:

- Basic PCI header fields, power management, SuperSpeed/USB-adjacent fields (`SBRN`, `FLADJ`, `DBESL_DBESLD`), PCIe capability, device/link capability/control/status, MSI, and MSI-X definitions through `BIF_CFG_DEV0_EPF2_1_MSIX_TABLE`.
- The slice ends before completing EPF2 MSI-X PBA, so later chunks must reconcile the remainder.

## Control Flow and Data Flow

This header has no runtime control flow. Its data flow is compile-time textual substitution:

1. Driver code includes the offset and shift/mask headers for the target ASIC.
2. A register value is read from MMIO or PCIe-port access paths.
3. `REG_GET_FIELD` masks and shifts the value using these macros, or `REG_SET_FIELD` clears the mask and inserts a shifted field value.
4. The resulting value may be written back to hardware, used for capability detection, or reported to higher driver layers.

Because this chunk describes PCIe config-space fields, the macros influence behavior around link training/status reporting, error handling, power-management states, interrupt configuration, virtualization, IOMMU-related features, and BAR sizing. The actual branch decisions and sequencing live in AMDGPU/NBIO driver C files, not in this generated header.

## State and Persistence Behavior

The macros themselves hold no mutable state and perform no persistence. They describe persistent hardware-visible register state:

- Configuration registers such as command/status, BARs, MSI/MSI-X, SR-IOV, ACS, ATS, PASID, and PRI may be written by firmware, the kernel PCI core, or AMDGPU initialization paths and remain in hardware until reset or reconfiguration.
- Status fields such as PCIe error status, device/link status, lane error status, margining status, MSI pending, and SR-IOV status reflect hardware state and may be sticky, write-1-to-clear, or capability-defined depending on the PCIe register.
- Scratch and vendor-specific DW fields may bridge firmware, virtualization, or driver-defined coordination; this chunk does not define the policy for those values.

Persistence risk is indirect: wrong masks or shifts can cause a driver to preserve, clear, or set the wrong hardware bits when it performs read-modify-write operations.

## Dependencies and Integration Points

The chunk depends on several repository and platform conventions:

- It is protected by the whole-file include guard `_nbio_7_7_0_SH_MASK_HEADER`, visible at the file top.
- It pairs with `nbio_7_7_0_offset.h`, whose `reg*` constants name register addresses matching the register base names in this header.
- AMDGPU SOC15 access macros such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET` provide the hardware access paths.
- `REG_GET_FIELD` and `REG_SET_FIELD` require the exact macro spelling convention used here, so generated-name drift is a build break or silent behavior hazard if the wrong ASIC header is included.
- PCI/PCIe semantics are external dependencies: fields map to PCI command/status, PM, PCIe capability, AER, ACS/ATS/PRI/PASID, SR-IOV, MSI/MSI-X, DPA, LTR, ARI, 16GT equalization, margining, and resizable BAR specifications.

## Risks and Edge Cases

- This is generated hardware ABI data. Manual edits are high risk because a one-bit mask or shift error can corrupt PCIe configuration, interrupt routing, BAR sizing, SR-IOV layout, or error reporting.
- Chunk boundaries are mid-structure: the first EPF0 VF12/13 transition and the final EPF2 MSI-X/PBA transition are incomplete in this slice. The merge lane must avoid treating this chunk as a whole-file summary.
- EPF1 and EPF2 register names are highly repetitive. Copy/paste or generator-template defects could accidentally assign EPF1 masks to EPF2 names or vice versa; such defects may still compile.
- Several masks represent multi-bit fields that must be range-checked by callers before insertion. The macros do not enforce valid link speeds, widths, latency encodings, PASID widths, VF counts, BAR sizes, or MSI-X table sizes.
- Some PCIe status/error fields are commonly sticky or clear-on-write according to hardware semantics. Generic read-modify-write code that uses masks mechanically can accidentally acknowledge or preserve status incorrectly if it ignores the register's access type.
- Virtualization-sensitive fields, including SR-IOV, ATS, PASID, PRI, ACS, VF BARs, and GPU IOV scheduling data, can affect isolation and DMA translation behavior. Incorrect definitions here can become security or data-corruption bugs rather than simple device-init failures.

## Test and Validation Signals

Useful validation is mostly generated-header and hardware-integration oriented:

- Build coverage for `amdgpu/nbio_v7_7.c` and any other ASIC code that includes `nbio_7_7_0_sh_mask.h`; missing or misspelled macros fail at compile time.
- Generator consistency checks: every field should have matching `__SHIFT` and `_MASK` definitions, masks should match shifts and field widths, and EPF1/EPF2 duplicated layouts should differ only where the register spec differs.
- Header/offset alignment checks: every register base used here should have a matching `reg...` offset in `nbio_7_7_0_offset.h` when it is meant to be addressable.
- Runtime PCIe smoke tests on NBIO 7.7.0 hardware: link speed/width reporting, MSI/MSI-X interrupt delivery, AER error reporting, BAR sizing, power-management transitions, SR-IOV VF enumeration, ATS/PASID/PRI enablement, and resizable BAR behavior.
- Negative tests around read-modify-write helpers: verify `REG_SET_FIELD` does not disturb adjacent bits for representative multi-bit fields such as link width/speed, MSI-X table size, SR-IOV VF counts, ACS controls, PASID width, lane equalization, lane margining payload, and VF resize BAR size.
