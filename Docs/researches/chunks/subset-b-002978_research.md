# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 41681-44102

## Scope And Purpose

This chunk is part of the generated AMDGPU NBIO 4.3.0 shift/mask register header. It contains C preprocessor constants for decoding and composing bitfields in NBIO/BIF PCI configuration-space registers for SR-IOV virtual functions under `BIF_CFG_DEV0_EPF0`. The source is declarative: it has no executable functions, no structs, and no runtime control flow. Its purpose is to give AMDGPU code stable symbolic names for register field shifts and bit masks.

The covered range starts in the middle of VF7's PCIe capability block at `BIF_CFG_DEV0_EPF0_VF7_LINK_CAP`, continues through the rest of VF7's PCIe/MSI/MSI-X/AER/ARI field definitions, covers complete VF8 and VF9 virtual-function configuration layouts, and ends in VF10 after `BIF_CFG_DEV0_EPF0_VF10_PCIE_UNCORR_ERR_STATUS`. VF8 and VF9 each include 622 `#define` entries in this slice; VF7 contributes the tail of its map, and VF10 contributes its beginning through uncorrectable-error status.

## Register Families Covered

The macros follow the generated naming convention:

- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>_MASK` gives the field mask already positioned in the register.
- Comment lines such as `//BIF_CFG_DEV0_EPF0_VF8_COMMAND` delimit a logical register section.
- `// addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp` and similar comments identify the generated address block for full VF maps.

Major register groups in the range are:

- PCI configuration identity and header fields for VF8, VF9, and the beginning of VF10: vendor/device IDs, command/status, revision and class code fields, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI Express capability registers: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI registers: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data registers, extended data, masks, pending bits, and 64-bit message variants.
- MSI-X registers: `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific enhanced capability registers: list header, vendor-specific header, and two scratch registers.
- Advanced Error Reporting registers: enhanced capability list, uncorrectable-error status/mask/severity, correctable-error status/mask, AER capability/control, header logs, and TLP prefix logs. VF10 in this chunk reaches only the uncorrectable-error status register; its following mask/severity definitions are outside this chunk.
- ARI extended capability registers for VF7, VF8, and VF9: capability-list header, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

## Important Fields

The PCIe capability fields expose link negotiation, power management, and error-reporting controls. `LINK_CAP` and `LINK_STATUS` encode link speed, width, power-management support, exit latencies, data-link active reporting, link bandwidth notification, current link speed, negotiated width, link training, slot clock, and autonomous bandwidth status. `LINK_CNTL` and `LINK_CNTL2` provide writable controls such as PM control, link disable, retrain link, common clock configuration, autonomous width/speed disable, target link speed, compliance mode, de-emphasis, and transmit margin.

`DEVICE_CAP`, `DEVICE_CNTL`, and their second-generation variants model core PCIe endpoint features: payload/read-request sizes, relaxed ordering, extended tags, function-level reset initiation, completion-timeout support/configuration, ARI forwarding, atomic operations, ID-based ordering, LTR, ten-bit tags, OBFF, end-to-end TLP prefix behavior, and emergency power reduction signaling. `DEVICE_STATUS` exposes error and transaction-pending state bits.

The interrupt capability blocks define MSI and MSI-X programming fields: capability IDs and next pointers, MSI enable/multiple-message settings, 64-bit MSI support, per-vector masking capability, message address/data payloads, interrupt masks, pending bits, MSI-X table size, function mask, MSI-X enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

The AER fields are diagnostic and recovery-sensitive. Uncorrectable-error fields include data link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic operation egress blocked, TLP prefix blocked, and poisoned TLP egress blocked status. Correctable-error fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory non-fatal error, corrected internal error, and header log overflow. Header-log and TLP-prefix-log registers expose raw captured dwords.

## APIs, Types, And Functions

This chunk defines no C APIs, types, functions, or inline helpers. The public surface is entirely macro names and literal constants. Downstream code typically combines these definitions with the matching address macros from `nbio_4_3_0_offset.h` and register read/write helpers in AMDGPU code, for example using the mask to isolate a field and the shift to normalize it:

```c
field = (reg_value & BIF_CFG_DEV0_EPF0_VF8_LINK_STATUS__CURRENT_LINK_SPEED_MASK) >>
        BIF_CFG_DEV0_EPF0_VF8_LINK_STATUS__CURRENT_LINK_SPEED__SHIFT;
```

The header is included directly by NBIO 4.3 integration code such as `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and by SMU13 power-management files that also include the matching NBIO offset header. Those consumers provide the actual register access functions and hardware sequencing.

## Control Flow

There is no local control flow. The operational control flow lives in AMDGPU call paths that include this header, select an NBIO register address from the offset header, read or modify the register, and apply these masks and shifts to access individual fields. Typical flows include:

- Reading link status fields to report or validate negotiated PCIe speed/width.
- Updating link-control fields when forcing retrain, changing target link speed, or managing autonomous width/speed behavior.
- Inspecting AER status/log fields during PCIe error handling.
- Programming MSI/MSI-X registers as part of virtual-function interrupt setup.
- Reading or writing SR-IOV VF configuration-space shadow registers while managing virtual functions.

Because this file only names bit positions, it does not impose ordering, locking, polling, timeout, or reset behavior. Callers must supply those semantics according to the PCIe spec, the NBIO IP block rules, and the AMDGPU subsystem that is touching the register.

## State And Persistence Behavior

The header itself has no state and no persistence. The state represented by these macros is hardware-backed PCI configuration and capability state for AMD NBIO virtual functions. Some fields are read-only hardware capability/status bits, some are software-programmable configuration bits, and some are write-1-to-clear or otherwise side-effecting status bits depending on the underlying PCIe register semantics.

State persists in device registers across normal driver reads and writes, but may be reset by GPU reset, PCI function reset, virtual-function reset, power transitions, or firmware-managed reinitialization. BAR, command/status, MSI/MSI-X, AER, and link-control values are particularly sensitive because they affect memory decoding, interrupt delivery, error reporting, and PCIe link behavior.

## Dependencies And Integration Points

This chunk depends on generated ASIC register metadata being consistent across the NBIO 4.3.0 register header family:

- `nbio_4_3_0_offset.h` supplies corresponding register offsets/addresses.
- `nbio_4_3_0_default.h`, where present in the same generated family, supplies reset/default values for registers.
- AMDGPU NBIO code supplies register access wrappers, device discovery, and IP-version dispatch.
- SMU13 power-management code includes the same header for NBIO-related power, clock, or link-management fields.
- Linux PCIe, SR-IOV, MSI/MSI-X, and AER subsystems provide the higher-level concepts these register fields mirror.

The integration boundary is intentionally low-level. Higher layers should not duplicate numeric masks; they should refer to these generated names so ASIC header updates remain centralized.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask, shift, or VF register mapping can silently decode the wrong bits or write reserved bits in hardware registers.
- The chunk boundaries split logical register maps. VF7 starts before this chunk and VF10 continues after it, so research or tooling that treats this chunk as a complete per-file contract must account for adjacent chunks.
- Several registers use overlapping PCIe terms such as `MASK` as both a field name and the generated suffix, producing names like `...MSI_MASK__MSI_MASK_MASK`. Consumers must use exact generated identifiers.
- AER status registers may have side-effecting clear behavior in hardware. Using these macros in read-modify-write code without respecting PCIe semantics can lose diagnostic information.
- Link-control fields such as retrain, link disable, target speed, compliance mode, and autonomous speed/width disable can disrupt the PCIe link if written at the wrong time.
- MSI/MSI-X address, data, mask, pending, table, and PBA fields are security and stability sensitive for SR-IOV VFs; incorrect programming can break interrupt delivery or leak interrupts across isolation boundaries.
- Some fields are 16-bit PCI capability fields and others are 32-bit enhanced-capability or BAR/log fields. Callers must use access widths and register offsets that match the underlying register, not just the mask literal width.

## Test Signals

Useful validation for this chunk is mostly compile-time and hardware/driver-integration oriented:

- Build AMDGPU objects that include `nbio_4_3_0_sh_mask.h`, especially `amdgpu/nbio_v4_3.c` and SMU13 files, with warnings enabled.
- Run generated-header consistency checks that compare every `__SHIFT`/`_MASK` pair against the register database and matching offset/default headers.
- Verify that masks are contiguous where the field is multi-bit, are aligned with their shift values, and do not overlap unexpected adjacent fields inside each register.
- Exercise PCIe link reporting and management on NBIO 4.3 ASICs and confirm decoded link speed/width/status values match Linux PCI core observations.
- Exercise SR-IOV VF creation/reset paths and confirm VF8/VF9/VF10 config-space fields, BARs, MSI/MSI-X capabilities, and ARI capability exposure match expected hardware behavior.
- Trigger or inject PCIe AER conditions where possible and verify uncorrectable/correctable status, severity/mask, header-log, and TLP-prefix-log decoding uses the documented bits.
- Run suspend/resume, GPU reset, function-level reset, and VF reset tests to catch stale assumptions about which register fields persist across resets.
