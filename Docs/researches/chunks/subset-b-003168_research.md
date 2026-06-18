# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 19644-22071

## Scope And Purpose

This chunk is a generated AMD NBIO 7.2.0 register field mask header slice. It contains only C preprocessor constants: every register field is represented by a `__SHIFT` macro and, normally, a paired `_MASK` macro. The constants describe bit layouts for PCI/PCIe configuration and extended capability registers in the AMD GPU NBIO block, with this line range covering the tail of `BIFPLR1` CCIX/ESM definitions and a large `BIFPLR2` PCIe configuration-space block.

The source is not executable logic and declares no functions, structs, enums, or storage. Its purpose is to let AMDGPU driver code read, compose, and update hardware registers through common helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT` without scattering raw bit positions through the driver.

The requested range starts inside `BIFPLR1_PCIE_CCIX_CAP_LIST`: line 19644 is the `NEXT_PTR` shift, while the preceding `CAP_ID` and `CAP_VER` shifts are outside the chunk. It ends inside `BIFPLR2_LANE_9_MARGINING_LANE_CNTL`: line 22071 defines `LANE_9_RECEIVER_NUMBER_MASK`, while the rest of lane 9 control/status masks continue after the chunk. Any merge-level file research should therefore reconcile this document with adjacent chunks for complete per-register coverage.

## Important Macro Families

The chunk contains 2,167 `#define` entries in the requested line range: 1,084 shift constants and 1,083 masks. The one-shift surplus is caused by the chunk boundary starting after the first two `BIFPLR1_PCIE_CCIX_CAP_LIST` shifts but still including all three masks for that register.

`BIFPLR1_PCIE_CCIX_*` at the beginning of the chunk describes CCIX capability list/header fields and CCIX ESM capability/control/status bits. Important fields include capability ID/version/next pointer, CCIX vendor and capability length, ESM mode support, PHY reach length, recalibration needs, calibration and quick-equalization timing, supported data rates from 2.5 GT/s through 25 GT/s, current data rate, calibration completion, enable/calibration control, link reach target, retimer presence, and quick equalization timeout selection.

`BIFPLR1_ESM_LANE_<0-15>_EQUALIZATION_CNTL_20GT` and `_25GT` repeat a compact per-lane schema. Each lane has downstream-port and upstream-port transmit preset fields at nibbles 0 and 4, with masks `0x0f` and `0xf0`. These macros let driver code program or inspect lane equalization presets for high-rate CCIX/ESM operation.

`BIFPLR1_PCIE_CCIX_TRANS_CAP` and `BIFPLR1_PCIE_CCIX_TRANS_CNTL` close the BIFPLR1 portion with a translate-mode capability and enable bit.

`BIFPLR2_*` begins after `addressBlock: nbio_pcie0_bifplr2_cfgdecp`, so the remaining chunk is mostly the PCIe root-port/link-register view for BIFPLR2. It includes standard PCI config fields such as vendor ID, device ID, command/status, revision/class code, cache line, latency, header, BIST, bridge bus numbers, I/O and memory windows, prefetchable windows, ROM base, interrupt line/pin, bridge control, and extended bridge control.

`BIFPLR2_PMI_*`, `BIFPLR2_PCIE_*`, `BIFPLR2_MSI_*`, `BIFPLR2_SSID_*`, and `BIFPLR2_MSI_MAP_*` describe common PCI/PCIe capability blocks: power-management capabilities/status-control, PCIe capability and device/link/slot/root registers, MSI control/address/data fields, subsystem ID capability, and MSI mapping.

The PCIe extended capability region includes vendor-specific, virtual-channel, device serial number, advanced error reporting, secondary PCIe, ACS, multicast, L1 PM substates, DPC, ESM, data link feature, 16 GT/s PHY, and lane margining definitions. These are all bitfield maps, not policy code.

## PCIe Capability And Error Fields

The `BIFPLR2_DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_*`, and `ROOT_*` groups mirror standard PCIe capability semantics. They cover payload size, phantom functions, extended tags, endpoint L0s/L1 latency, FLR, corrected/non-fatal/fatal/unsupported request reporting enables, relaxed ordering, max payload/request sizes, no-snoop, AUX power, transaction pending, link speed/width/ASPM/L0s/L1/clock/power-management controls, link training and bandwidth-status flags, slot power/attention/hotplug fields, and root-complex PME/system-error controls.

`BIFPLR2_DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` extend this for completion timeout programming, ARI, atomic operations, ID-based ordering, LTR, OBFF, TPH, emergency power reduction, 10-bit tags, supported link speeds, target link speed, equalization controls, compliance/de-emphasis/transmit-margin controls, equalization completion/phase results, current de-emphasis level, and downstream component presence.

`BIFPLR2_PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` map Advanced Error Reporting uncorrectable error bits such as data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, poisoned TLP egress blocked, and unsupported fields. The corresponding correctable error groups map receiver error, bad TLP/DLLP, replay timeout/count rollover, advisory non-fatal, corrected internal error, header log overflow, and parity error.

`BIFPLR2_PCIE_ADV_ERR_CAP_CNTL`, header-log, root-error command/status, error source ID, and TLP prefix log groups expose AER logging, ECRC generation/checking capability/enables, multiple-header recording, TLP prefix log presence, root error interrupt enables, root status, message receipt bits, and source IDs.

`BIFPLR2_PCIE_DPC_*` and `BIFPLR2_PCIE_RP_PIO_*` define Downstream Port Containment and root-port PIO status/mask/severity/system-error/exception controls. They are safety-critical because wrong masks could suppress link containment, misreport completion status, or route errors incorrectly.

## ESM, DLF, 16GT, And Margining

`BIFPLR2_PCIE_ESM_*` describes an Equalization/Enhanced Speed Mode capability block. It starts with capability list/header fields, minimum time in electrical idle, an `ESM_ENABLED` control bit, and seven dense bitmaps of supported ESM data rates. `BIFPLR2_PCIE_ESM_CAP_1` covers 8.0 through 10.9 GT/s in 0.1 GT/s steps, `CAP_2` covers 11.0 through 13.9, `CAP_3` covers 14.0 through 15.9, `CAP_4` covers 16.0 through 18.9, `CAP_5` covers 19.0 through 21.9, `CAP_6` covers 22.0 through 24.9, and `CAP_7` covers 25.0 through 28.0. These bitmaps are likely consumed by firmware or low-level link-management code to advertise or select supported link rates.

`BIFPLR2_DATA_LINK_FEATURE_CAP` and `_STATUS` expose local and remote data link feature support plus validity/exchange bits. They integrate with PCIe data-link feature negotiation rather than persistent driver state.

`BIFPLR2_PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, parity mismatch status registers, and `BIFPLR2_LANE_<0-15>_EQUALIZATION_CNTL_16GT` define PCIe Gen4/16 GT/s PHY and lane equalization fields. The 16 GT/s per-lane equalization registers use the same two-nibble downstream/upstream transmit preset pattern as the earlier BIFPLR1 20/25 GT/s lane groups.

`BIFPLR2_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `BIFPLR2_LANE_<0-9>_MARGINING_LANE_*` begin the lane margining capability. Each lane control/status pair has receiver number, margin type, usage model, and payload fields. The chunk fully covers lanes 0 through 8 and starts lane 9 control; lane 9 masks and later lanes continue beyond line 22071.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time macro expansion:

1. A driver C file includes `nbio/nbio_7_2_0_offset.h` for register addresses and `nbio/nbio_7_2_0_sh_mask.h` for field layout.
2. Code reads a register value through AMDGPU MMIO helpers or composes a new value in a local `u32`.
3. `REG_GET_FIELD` uses the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` constants to extract a field, or `REG_SET_FIELD` clears and writes the masked field.
4. The final value is written back through the appropriate SOC15 or PCIe-port accessor.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` is the nearby consumer for this header. That file includes this generated mask header and uses the same macro naming convention for NBIO register programming, including doorbell ranges, memory-controller access, interrupt controls, clock/power gating, HDP flush registers, and PCIe request-size configuration. The exact BIFPLR2 config-space capability constants in this chunk may be consumed by other generated-access paths or by future code even when not directly referenced in `nbio_v7_2.c`.

## State And Persistence Behavior

The header itself has no state, allocation, persistence, or side effects. State exists only in the hardware registers whose fields these macros describe. Some fields are read-only capability/status indicators, some are writeable control bits, and several are write-one-to-clear or hardware-updated status bits by PCIe convention. The header does not encode those access semantics, so callers must rely on hardware documentation and the address header to choose safe access patterns.

Persistence is hardware-dependent. Values such as PCIe capability advertisement, link status, error logs, lane equalization, ESM enablement, DPC state, and margining status can persist until reset, link retrain, firmware action, explicit driver writes, or hardware clear conditions. The macros simply preserve the bit positions needed for those operations.

## Dependencies And Integration Points

This file depends on the AMDGPU register-generation scheme, not on C library code. Naming conventions are the integration contract:

- `reg...` address macros from `nbio_7_2_0_offset.h` identify the register location.
- `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` from this header identify field placement.
- AMDGPU helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD` infer these names by token pasting.
- SOC15 and PCIe-port MMIO helpers connect the field definitions to actual NBIO hardware accesses.

The field names align with PCI, PCIe, CCIX, AER, ACS, DPC, L1 PM substate, multicast, data-link-feature, ESM, 16 GT/s PHY, and lane-margining specifications. Kernel integration is through the DRM AMDGPU driver, while validation usually occurs on real hardware, emulation, or build coverage because this generated header is not unit-testable by itself.

## Risks And Edge Cases

The main risk is silent bitfield drift. A wrong shift or mask can program the wrong hardware bit while still compiling cleanly. For this chunk, high-impact areas include AER/DPC error handling, PCIe link speed/width/equalization controls, ESM supported-rate bitmaps, ACS routing/isolation controls, MSI programming, bridge memory window limits, and lane margining payload fields.

Chunk boundaries are a documentation risk. The first register in this slice is missing two shifts from the previous chunk, and the last lane-margining register is incomplete in this slice. Any automated research merge must not treat this document as complete coverage for those two register groups.

Repeated per-lane patterns are vulnerable to copy-generation mistakes. Lane equalization and margining blocks should preserve lane numbers consistently in both register names and field names. A single lane-number mismatch would be hard to catch through compilation because the macro name is still syntactically valid.

Reserved and capability fields should not be blindly written. The presence of masks such as reserved all-ones fields does not imply safe writeability. Callers must avoid treating this header as an authorization list for register writes.

Numeric literal width matters. Masks are emitted with an `L` suffix and are intended for 32-bit register values. Callers should keep operations in unsigned 32-bit contexts where possible to avoid sign-extension or truncation surprises around high bits such as `0x80000000L`.

## Test Signals

The primary static signal is successful compilation of AMDGPU code that includes `nbio_7_2_0_sh_mask.h`. Because token-pasted helpers depend on exact macro names, missing or renamed shift/mask pairs usually surface as compile errors in code that references them.

Generated-header consistency checks should verify that each field has exactly one `__SHIFT` and one `_MASK`, masks align with shifts, repeated lane groups have identical field layouts except for the lane number, and capability-list fields preserve the standard `CAP_ID`, `CAP_VER`, and `NEXT_PTR` layout.

Runtime signals come from PCIe/NBIO behavior on supported AMD GPUs: correct PCIe link negotiation, stable equalization at 16/20/25 GT/s paths, correct ESM capability reporting, correct AER/DPC logging and containment, valid MSI operation, correct ACS/VC/L1 PM behavior, and lane margining controls/status behaving as expected during diagnostics.

Regression tests are likely indirect. Driver smoke tests, GPU bring-up, suspend/resume, reset, error-injection, PCIe AER/DPC tests, link retrain tests, and hardware diagnostics are better signals than isolated unit tests, because this file only describes register bit positions.
