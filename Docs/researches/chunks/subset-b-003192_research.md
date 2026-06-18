# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 78231-80663

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 register field mask header. It defines C preprocessor constants for bit shifts and masks in PCIe bridge/root-port configuration registers, primarily for `BIFPLR2_0` high-speed link capability/control extensions and the beginning of the `BIFPLR3_0` PCIe bridge configuration space.

The constants are not executable code. They provide the field layout contract used by AMDGPU register access code when reading, composing, or decoding 16-bit and 32-bit PCI/PCIe configuration and enhanced-capability registers. The corresponding register offsets live in the matching `nbio_7_2_0_offset.h`; this header supplies the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pieces used by direct bit operations and AMD helper macros such as `REG_GET_FIELD`/`REG_SET_FIELD`.

## Major Register Groups

The range opens in the middle of `BIFPLR2_0_PCIE_ESM_CAP_5`, then continues through `BIFPLR2_0_PCIE_ESM_CAP_6` and `BIFPLR2_0_PCIE_ESM_CAP_7`. These registers encode supported ESM data-rate points as one bit per 0.1 GT/s step: the visible part of cap 5 covers `ESM_19P5G` through `ESM_21P9G` plus masks for `ESM_19P0G` through `ESM_21P9G`; cap 6 covers `ESM_22P0G` through `ESM_24P9G`; cap 7 covers `ESM_25P0G` through `ESM_28P0G`.

The `BIFPLR2_0` PCIe extended capability blocks define data-link feature, 16 GT/s PHY, lane equalization, lane margining, CCIX, CCIX ESM, and CCIX transport fields. Important examples include:

- `BIFPLR2_0_PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` for Data Link Feature capability IDs, next pointers, scaled data-link feature-exchange enablement, and feature-exchange status.
- `BIFPLR2_0_PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, and parity mismatch status registers for 16 GT/s capability, equalization bypass, retimer presence, link equalization request/status, lane equalization request, and downstream/upstream component readiness.
- `BIFPLR2_0_LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`, each with downstream/upstream port preset fields, giving per-lane control for PCIe 4.0-style 16 GT/s equalization.
- `BIFPLR2_0_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_*` through `LANE_15_MARGINING_*`, which expose port-level lane margining capability plus per-lane control/status fields such as receive number, margin type, usage model, margin payload, software-ready, margin command status, error count, sample count, and lane margining ready.
- `BIFPLR2_0_PCIE_CCIX_*` registers for CCIX enhanced capability metadata, CCIX header/vendor fields, protocol capability bits, required/optional ESM rates, ESM enable/status/control, per-lane 20 GT/s and 25 GT/s ESM equalization presets, and CCIX transport capability/control.

Line 79081 marks a new address block, `nbio_pcie0_bifplr3_cfgdecp`, and the chunk then defines a broad set of `BIFPLR3_0` PCI/PCIe bridge fields. This includes conventional PCI bridge configuration registers (`VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class codes, bus numbers, I/O and memory windows, interrupt and bridge control), standard PCI capabilities (`PMI`, `PCIe`, `MSI`, `SSID`, MSI mapping), and PCIe enhanced capabilities.

The `BIFPLR3_0` PCIe capability definitions cover:

- Device, link, slot, root, and second-generation capability/control/status fields, including error-report enable bits, Max Payload/Read Request size fields, relaxed ordering, no-snoop, auxiliary power, link speed/width, ASPM, retrain/common-clock/extended-sync controls, target link speed, equalization controls, and link equalization status bits.
- MSI message control and address/data fields, including 64-bit address capability and per-vector masking indicators.
- Virtual Channel capability/resource fields for VC0 and VC1.
- Device serial number fields.
- Advanced Error Reporting registers: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe, ACS, multicast, L1 PM substate, DPC, and Root Port PIO error handling blocks.
- The start of `BIFPLR3_0_PCIE_ESM_*`, including ESM capability-list metadata, ESM headers, status/control, and ESM capability bitmaps for 8.0-13.9 GT/s.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The public surface is a large set of preprocessor macros with two naming forms:

- `REGISTER__FIELD__SHIFT`: the zero-based bit position for the field.
- `REGISTER__FIELD_MASK`: the register-width mask with the field bits set.

These definitions are consumed by register helper macros and direct bit operations elsewhere in the AMDGPU driver. Typical usage is to read a register value through the ASIC-specific MMIO/config-space accessors, extract fields with `(value & FIELD_MASK) >> FIELD__SHIFT` or `REG_GET_FIELD`, and compose writes by clearing a mask and shifting the new value into place.

## Control Flow

This header contributes no runtime control flow. Runtime behavior emerges in consumers that use these constants while initializing or diagnosing NBIO/PCIe hardware. The typical flow is:

1. The driver selects NBIO 7.2.0 register definitions for the detected ASIC.
2. Code reads a PCIe/NBIO register using an offset from `nbio_7_2_0_offset.h`.
3. The matching masks/shifts from this file decode capability, status, or error fields.
4. For writable control fields, the driver clears the field mask, inserts a shifted value, and writes the register back through AMDGPU MMIO or PCI config helpers.

For error handling and diagnostics, AER/DPC/RP PIO status fields in this chunk identify which error class triggered, whether it is masked or severe, which header/prefix logs are valid, and which source ID is associated with a root error. For link training features, the equalization, margining, and ESM fields guide per-lane training and capability reporting rather than branching inside this header.

## State And Persistence

The file itself has no mutable state and persists no data. It is a generated compile-time description of hardware state layout.

The state represented by these masks lives in NBIO/PCIe hardware registers. Some fields describe static or firmware-programmed capability state, such as capability IDs, versions, next pointers, maximum link speed/width, CCIX support, ESM rate support, ACS capability, and L1 PM substate capability. Others represent live or sticky hardware status, including link equalization completion/failure, margining ready/status/error counts, AER correctable and uncorrectable error bits, DPC trigger status, RP PIO status, and TLP header/prefix logs. Control fields such as PCI command enables, PCIe device/link controls, MSI enables, AER masks/severity, ACS controls, DPC controls, and ESM enable/rate controls can be modified by kernel code and persist only as hardware register contents across the relevant device power/reset domain.

## Dependencies And Integration Points

This chunk depends on consistent pairing with the generated NBIO 7.2.0 offset header. For example, this file defines field positions such as `BIFPLR2_0_PCIE_CCIX_ESM_CNTL__ESM_ENABLE_MASK` and `BIFPLR3_0_PCIE_DPC_STATUS__DPC_TRIGGER_STATUS_MASK`, while `nbio_7_2_0_offset.h` supplies the corresponding register addresses and base indices.

Integration points include:

- AMDGPU NBIO initialization and platform-specific register access paths, which select `asic_reg/nbio/nbio_7_2_0_*` definitions for NBIO 7.2.0 devices.
- PCIe link management paths that inspect or program link speed, width, equalization, retimer, lane error, and lane margining registers.
- RAS/AER/DPC handling paths that decode uncorrectable/correctable PCIe errors, root error status, source IDs, DPC status, and RP PIO exception/header logs.
- PCI bridge enumeration or reset support that depends on conventional bridge command/status, bus-number, memory-window, interrupt, and bridge-control fields.
- Capability discovery code that walks PCIe enhanced capability lists using `CAP_ID`, `CAP_VER`, and `NEXT_PTR` fields.

The same named fields appear in related NBIO generation headers such as `nbio_7_0_sh_mask.h` and `nbio_7_7_0_sh_mask.h`, so maintainers often compare these generated files when validating ASIC-generation differences. One notable generation-specific detail in this chunk is that `BIFPLR2_0_PCIE_CCIX_ESM_CNTL` in NBIO 7.2.0 has rate/control, reach, retimer, and timeout-select fields but lacks the `ESM_COMPLIANCE` bit visible in at least some later generated NBIO headers.

## Risks

The main risk is silent hardware misprogramming if any mask or shift is incorrect. A single wrong bit position can enable the wrong PCI command, decode an error as the wrong class, mask a real AER/DPC fault, corrupt a lane training request, or advertise an unsupported link/ESM capability.

The definitions are highly repetitive, especially the per-lane equalization and margining groups. Copy-generation mistakes can affect only one lane, making failures topology- or link-width-dependent. The ESM capability bitmaps are similarly easy to misalign because each bit represents a 0.1 GT/s increment; an off-by-one shift changes the advertised or selected data rate.

Mixed register widths are another risk. Many PCI config fields are 16-bit masks, while AER logs, TLP prefix logs, capability lists, and some controls are 32-bit masks. Consumers must use the correct access width and preserve reserved bits on read-modify-write operations.

Status and error fields may have side effects defined by hardware, such as write-one-to-clear behavior or sticky logging. This header does not encode access semantics, so consumers need the register spec or existing driver patterns before writing fields like AER status, DPC status, RP PIO status, and log registers.

## Test Signals

Useful validation signals are mostly integration and hardware-facing rather than unit tests:

- The driver builds with NBIO 7.2.0 headers included, proving all generated macro names referenced by source code resolve.
- PCIe capability enumeration on supported AMD GPUs reports plausible bridge, PCIe, AER, ACS, DPC, L1 PM substate, lane equalization, margining, CCIX, and ESM capabilities.
- Link training and retraining logs show expected negotiated speed/width and no unexpected equalization failure bits.
- AER/DPC/RAS tests or fault injection decode the same error status/source/log fields as hardware documentation and `lspci -vv`/kernel PCIe AER reporting.
- Lane margining diagnostics, where supported, produce per-lane ready/status/error/sample values without cross-lane swaps.
- Suspend/resume, FLR, hot reset, and GPU reset paths preserve or reinitialize writable controls such as command enables, AER masks/severity, ACS controls, DPC controls, ESM controls, and link controls as expected.
