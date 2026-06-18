# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 39264-41634

## Scope

This chunk covers a generated AMD NBIO 7.7.0 register shift/mask header segment for RCC strap and RCC endpoint-function strap registers. The range begins in the `RCC_STRAP2_RCC_DEV0_PORT_STRAP2` mask definitions and ends after `RCC_DEV0_2_RCC_VDM_SUPPORT`, just before the next address block continues. It contains 2,371 source lines, 2,172 `#define` entries, and 159 commented register groups.

The chunk is data-only C preprocessor content. It defines no functions, structs, enums, variables, storage, or executable control flow.

## Purpose

The purpose of this section is to expose the bit-level ABI for NBIO/RCC PCIe strap registers on ASICs using the NBIO 7.7.0 register map. Each field is represented by the conventional generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for isolating or composing the field.

The sibling `nbio_7_7_0_offset.h` header supplies register addresses and base indices, for example `regRCC_STRAP2_RCC_DEV0_PORT_STRAP2`, `regRCC_DEV1_PORT_STRAP0`, `regRCC_STRAP2_RCC_BIF_STRAP0`, `regRCC_DEV0_EPF2_STRAP0`, `regRCC_DEV2_EPF2_STRAP14`, and `regRCC_DEV0_2_RCC_VDM_SUPPORT`. This file supplies the corresponding field positions and masks used by register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### Root Port Strap Registers

The first portion covers downstream/root-port strap fields:

- `RCC_STRAP2_RCC_DEV0_PORT_STRAP2` through `RCC_STRAP2_RCC_DEV0_PORT_STRAP13`.
- `RCC_DEV1_PORT_STRAP0` through `RCC_DEV1_PORT_STRAP13`.
- `RCC_DEV2_PORT_STRAP0` through `RCC_DEV2_PORT_STRAP13`.

These fields describe PCIe link and capability defaults for device/root-port instances. They include ARI, ACS, AER, completion-abort error behavior, device IDs, interrupt pins, E2E prefix handling, max payload, max link width, EPF dummy enables, DSN, ECRC check/generation, extended tag, virtual-channel count, advisory non-fatal poisoned TLP behavior, Gen2/Gen3/Gen4/Gen5 compliance and enablement, target link speed, L0s/L1 acceptable and exit latencies, link bandwidth notification, LTR, OBFF, MSI, power-management support, atomic operations, power-budget bytes, subsystem IDs, vendor IDs, class-code bytes, port/bus/device/function numbers, and PCIe lane equalization preset fields.

These are hardware strap defaults: they model what capabilities the root ports advertise and how link training/power-management defaults appear before software policy overrides or normal PCI enumeration.

### BIF Strap Registers

`RCC_STRAP2_RCC_BIF_STRAP0` through `RCC_STRAP2_RCC_BIF_STRAP6` define global BIF/NBIO strap fields. They include Gen3/Gen4 disable or kill controls, expansion-ROM validation, VGA disable, memory aperture size pins, PX capability, MSI payload behavior, NBIF error handling during FLR, PME compliance, receive-side ignore controls for malformed/error traffic, audio and BIOS-ROM strap pins, GPUIOV enablement, quicksim mode, relaxed-ordering P2P behavior, VF bus-number checking, big-APU mode, link-down reset enable, SR-IOV and VF sizing controls, MSI-X/PBA aperture sizing, VF memory aperture size, and RSMU register BAR sizing.

These fields are integration-sensitive because BIF straps influence global PCIe/GPU IO virtualization and aperture presentation rather than a single endpoint function.

### Device 0 Endpoint Function Straps

The chunk defines `RCC_STRAP2_RCC_DEV0_EPF0_STRAP*` for function 0 and `RCC_STRAP2_RCC_DEV0_EPF1_STRAP*` plus `RCC_DEV0_EPF2_STRAP*` through `RCC_DEV0_EPF7_STRAP*` for additional endpoint functions. Covered strap groups include function/device IDs, revision IDs, function enable bits, legacy device type, D1/D2 support, no-soft-reset behavior, resizable BAR enablement, PASID capability bits and width, MSI per-vector masking, AER/ACS, DPA, VC, MSI multi-message capability, poisoned advisory non-fatal support, power enable, subsystem IDs/vendor IDs, MSI/MSI-X enable, PMC DSI, all-MSI-event support, SMN error status mask enables, clock PM, true PM status, RTR, atomic and FLR support, PME support, interrupt pin, AUX power, aperture enables and prefetchable bits, class codes, vendor IDs, and function-specific BAR/aper controls.

Function 0 has the richest set of fields, including EPF0-only strap 8/9/15/16/17/18 groups. Functions 2 through 7 mostly follow a repeated template: identity, capability, power/interrupt, aperture, class-code, and vendor-ID fields.

### Device 1 and Device 2 Endpoint Function Straps

The range also covers endpoint-function straps for secondary device instances:

- `RCC_DEV1_EPF0_STRAP*` through `RCC_DEV1_EPF5_STRAP*`.
- `RCC_DEV2_EPF0_STRAP*` through `RCC_DEV2_EPF2_STRAP14`.

These repeat the same generated field model used by Device 0 endpoint functions, with suffixes such as `DEV1_F0`, `DEV1_F5`, `DEV2_F0`, and `DEV2_F2` distinguishing the PCIe device/function instance. The repeated fields are important for multi-function or multi-device ASIC exposure because incorrect suffix selection would silently program or decode the wrong function's advertised PCI capability state.

### Vendor Defined Message Support

The chunk ends with `RCC_DEV0_2_RCC_VDM_SUPPORT`, under address block `nbio_nbif0_rcc_dev0_RCCPORTDEC`. Its fields advertise or route vendor-defined message handling:

- `MCTP_SUPPORT`
- `AMPTP_SUPPORT`
- `OTHER_VDM_SUPPORT`
- `ROUTE_TO_RC_CHECK_IN_RCMODE`
- `ROUTE_BROADCAST_CHECK_IN_RCMODE`

These are capability/routing bits for VDM traffic and are separate from the broader strap capability blocks.

## APIs, Types, and Functions

There are no C APIs or types defined in this chunk. The public interface is the macro namespace itself. Consumers include the generated offset header and normal AMDGPU register helpers:

- `RREG32_SOC15` / `WREG32_SOC15` for direct SOC15 register reads and writes.
- `RREG32_PCIE_PORT` / `WREG32_PCIE_PORT` for indexed PCIe-port register access where applicable.
- `REG_SET_FIELD` and `REG_GET_FIELD`, which rely on the exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` naming convention.
- `SOC15_REG_OFFSET`, which combines a hardware IP block, instance, and `reg*` address macro from the offset header.

The direct NBIO 7.7 integration file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`. That file primarily uses other fields from the same generated header for revision ID, memory size, doorbell aperture, interrupt, HDP flush, clock-gating, and one EPF strap write; the strap families in this chunk provide the same constant vocabulary for less commonly touched RCC strap registers.

## Control Flow

No runtime control flow exists in this header section. At compile time, the C preprocessor substitutes integer constants into driver code. Runtime behavior appears only in consumers that:

1. Read a register using the matching `reg*` address macro.
2. Isolate fields using the `_MASK` and `__SHIFT` constants, or compose writes through `REG_SET_FIELD`.
3. Optionally write a modified 32-bit register value back to NBIO hardware.

For strap-like registers, many fields are expected to be read as hardware-derived defaults rather than repeatedly programmed at runtime. When software does write such registers, the control flow must be read-modify-write so unrelated strap bits in the same 32-bit register are preserved.

## State and Persistence Behavior

The macros themselves have no state and no persistence. They describe persistent or latched hardware state in NBIO/RCC registers:

- Strap fields usually reflect fuse, pin, firmware, or early hardware initialization defaults that survive into OS driver probing.
- Capability bits influence what PCIe features are advertised for root ports and endpoint functions.
- Identity fields such as device ID, vendor ID, subsystem ID, class code, revision ID, port number, bus number, device number, and function ID determine externally visible PCI configuration identity.
- Aperture, BAR, MSI/MSI-X, PASID, ACS, AER, FLR, SR-IOV/VF, and power-management fields influence how the device can be enumerated, isolated, reset, interrupted, and mapped.

Any persistent effect comes from hardware register values, not from this header. Incorrect constants would persist indirectly by causing the driver to read, clear, or set the wrong bits.

## Dependencies and Integration Points

Primary dependencies are generated AMD register-map conventions:

- `nbio_7_7_0_offset.h` for register addresses and base indices.
- SOC15/NBIO register access helpers from the AMDGPU driver.
- Field helper macros that require the exact generated `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling.
- PCIe/NBIO initialization, enumeration, reset, doorbell, SR-IOV, and clock/power-management paths that include the NBIO 7.7 register headers.

The chunk also aligns with equivalent register families in other generated ASIC headers such as NBIO 7.2.0 and NBIF 6.x variants. Those similar names are useful for cross-ASIC comparison, but they are not interchangeable: masks and shifts can differ between generated hardware maps.

## Risks

- Bitfield drift: generated mask/shift values must match the ASIC register specification exactly. A one-bit error can corrupt adjacent capability fields in the same 32-bit register.
- Wrong instance suffix: many macros differ only by `DEV0`, `DEV1`, `DEV2`, `F0`, `F1`, etc. Using the wrong suffix can affect the wrong PCIe function or decode the wrong identity/capability field.
- Read-modify-write hazards: strap registers pack many unrelated fields. Direct writes without preserving other bits can unintentionally alter advertised PCIe capabilities, BAR/aperture behavior, power states, interrupt routing, or virtualization support.
- Cross-generation confusion: similar `RCC_*` names exist in `nbio_7_2_0_sh_mask.h`, `nbif_6_3_1_sh_mask.h`, and other generated headers. Copying constants across ASIC generations can silently introduce invalid masks.
- PCIe compatibility impact: fields for AER, ACS, PASID, ATS-like identity/capability exposure, MSI/MSI-X, FLR, PME, D1/D2, and link speed/latency affect OS enumeration, IOMMU isolation, reset behavior, and link training.
- Virtualization impact: BIF and endpoint fields for SR-IOV, VF count, VF BAR sizing, VF bus-number checking, PASID, and ACS can affect guest isolation and device assignment safety.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Compile coverage of AMDGPU with NBIO 7.7 enabled, ensuring all generated macro names still satisfy `REG_SET_FIELD` and direct mask/shift uses.
- Register-header consistency checks: every field in this chunk should have a matching shift/mask pair, masks should align with shifts and field widths, and register names should exist in `nbio_7_7_0_offset.h` where software can address them.
- Boot/probe logs on NBIO 7.7 hardware showing successful PCI enumeration, correct device/vendor/subsystem/class IDs, and no unexpected AER/PCIe capability errors.
- `lspci -vv` comparison for advertised capabilities such as ACS, AER, MSI/MSI-X, FLR, PME/D-states, PASID-related fields, max payload, link speed/width, and SR-IOV/VF capability where supported.
- SR-IOV and VF assignment tests when touching BIF or endpoint-function strap fields related to VF enablement, BAR sizing, PASID, ACS, or bus-number checking.
- Link-training and power-management testing for fields around target link speed, Gen2/Gen3/Gen4/Gen5 enablement, L0s/L1 latencies, LTR, OBFF, PME, and clock PM.
- Runtime register readback diagnostics comparing expected strap values against the decoded fields for the specific ASIC stepping.
