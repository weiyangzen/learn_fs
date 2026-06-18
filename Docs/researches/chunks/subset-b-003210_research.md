# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 121458-123881

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 register shift/mask header. It defines C preprocessor constants for fields in PCIe bridge/root-port configuration and enhanced capability registers. The range starts in the tail of the `BIFPLR4_1` port's lane margining and CCIX/ESM fields, then line 121745 switches to the `nbio_pcie0_bifplr5_cfgdecp` address block and defines most of the `BIFPLR5_1` PCI/PCIe configuration-space field layout through the beginning of lane 6 margining control.

The file contains no executable code. Its job is to provide the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used with the matching NBIO 7.2.0 offset header when AMDGPU code reads, decodes, composes, or writes hardware register values. The related offsets for representative registers in this chunk are in `nbio_7_2_0_offset.h`, for example `regBIFPLR4_1_PCIE_CCIX_ESM_CNTL`, `regBIFPLR5_1_PCIE_LANE_0_EQUALIZATION_CNTL`, `regBIFPLR5_1_PCIE_DPC_STATUS`, `regBIFPLR5_1_PCIE_ESM_CAP_7`, and `regBIFPLR5_1_LANE_0_MARGINING_LANE_CNTL`, all with base index 5.

## Major Register Groups

The opening `BIFPLR4_1` portion completes per-lane PCIe margining definitions for lanes 13 through 15. Each lane has `MARGINING_LANE_CNTL` and `MARGINING_LANE_STATUS` fields for receiver number, margin type, usage model, and margin payload/status. This continues the same repetitive lane schema from earlier lines and allows software to issue or observe lane margining commands per physical lane.

The `BIFPLR4_1_PCIE_CCIX_*` block describes CCIX enhanced capability metadata and controls. It includes capability-list fields (`CAP_ID`, `CAP_VER`, `NEXT_PTR`), CCIX vendor/header fields, ESM capability bits, required ESM support at 2.5/5/8/16/20/25 GT/s, current ESM status, and ESM control fields such as data-rate selectors, calibration trigger, enable, phase 2/3 timeout selectors, link reach target, retimer presence, and quick equalization timeout. It also defines per-lane 20 GT/s and 25 GT/s ESM equalization preset fields for lanes 0 through 15, plus CCIX transport capability/control for optimized TLP format support and enablement.

Line 121745 starts the `BIFPLR5_1` address block. The first large section maps conventional PCI bridge configuration registers: vendor/device ID, command, status, revision and class codes, cache-line/latency/header/BIST fields, primary/secondary/subordinate bus numbers, I/O and memory base/limit windows, prefetchable window upper addresses, capability pointer, ROM base, interrupt line/pin, and bridge control bits. These are the bit definitions needed to decode or program the root-port/bridge-facing PCI config image exposed by NBIO.

The standard PCI capability groups include vendor-specific capability headers, adapter ID, Power Management Interface capability and status/control, PCI Express capability structures, MSI capability/message address/data fields, subsystem ID capability, and MSI mapping. The PCIe capability definitions cover device, link, slot, root, and second-generation capability/control/status registers. Important fields include error reporting enables, Max Payload and Max Read Request size, relaxed ordering, no-snoop, function-level reset, link speed and width, ASPM, common-clock/retrain controls, target link speed, selectable de-emphasis, equalization request/control, equalization status, slot power indicators, and root error reporting controls.

The PCIe enhanced capability groups in this chunk cover vendor-specific, Virtual Channel, device serial number, Advanced Error Reporting, Secondary PCIe, ACS, multicast, L1 PM substates, Downstream Port Containment, Root Port PIO, ESM, Data Link Feature, 16 GT/s PHY, lane equalization, and lane margining. The AER block defines uncorrectable/correctable error status, mask, and severity fields; AER capability/control; TLP header and prefix logs; root error command/status; and source IDs. The DPC/RP PIO block defines DPC trigger/control/status fields, DPC source ID, root-port PIO completion timeout/unsupported-request/completer-abort fields for config/I/O/memory traffic, masks, severities, system-error policy, exception bits, and header/prefix logs.

The `BIFPLR5_1_PCIE_ESM_*` section is a dense ESM capability bitmap. `PCIE_ESM_CAP_LIST`, `HEADER_1`, and `HEADER_2` identify the capability and vendor header. `PCIE_ESM_STATUS` encodes minimum time in EI value/scale, and `PCIE_ESM_CTRL` exposes the `ESM_ENABLED` bit. `PCIE_ESM_CAP_1` through `CAP_7` map supported data rates from 8.0 GT/s through 28.0 GT/s in 0.1 GT/s increments. Most registers cover 30 adjacent rates with bit 0 mapped to the first rate in that register; `CAP_7` reaches `ESM_28P0G` at bit 30.

The tail covers Data Link Feature capability/status, the PCIe 16 GT/s PHY enhanced capability, 16 GT/s link status and parity mismatch status registers, per-lane 16 GT/s downstream/upstream transmit presets for lanes 0 through 15, the PCIe margining enhanced capability, port-level margining ready/software-ready bits, and per-lane margining control/status for lanes 0 through 5. The chunk ends after defining only `BIFPLR5_1_LANE_6_MARGINING_LANE_CNTL__LANE_6_RECEIVER_NUMBER__SHIFT`, so lane 6 and later margining fields are completed in the next chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this range. The public surface is generated preprocessor constants in two forms:

- `REGISTER__FIELD__SHIFT`: zero-based bit position for a hardware register field.
- `REGISTER__FIELD_MASK`: field mask in the register's access width.

Consumers combine these definitions with register offsets from `nbio_7_2_0_offset.h`. The normal usage pattern is to read a hardware register or PCI config dword, extract a field with `(value & FIELD_MASK) >> FIELD__SHIFT` or AMDGPU helper macros such as `REG_GET_FIELD`, and construct writes by clearing a field mask and ORing in `new_value << FIELD__SHIFT`.

## Control Flow

This header has no branches, loops, or callable flow. Runtime control flow belongs to AMDGPU and PCIe subsystem code that uses the constants:

1. Hardware discovery selects NBIO 7.2.0 register headers for the detected ASIC.
2. Driver code reads a register using an offset macro from `nbio_7_2_0_offset.h`.
3. The shift/mask constants in this header decode capability, status, control, error, or per-lane fields.
4. For writable controls, code performs a read-modify-write so unrelated and reserved bits are preserved.

The field groups here influence several runtime paths: PCI bridge setup, MSI and PM capability programming, PCIe link training/retraining, lane equalization, AER/DPC error handling, Root Port PIO logging, ACS isolation policy, L1 PM substate configuration, CCIX/ESM discovery and setup, and lane margining diagnostics.

## State And Persistence

The header itself stores no mutable state. It is a compile-time hardware layout contract.

The represented state lives in NBIO/PCIe hardware registers. Some fields are static or firmware-initialized capability state, such as capability IDs, versions, next pointers, vendor IDs, supported link speeds, ACS/DPC/AER capability bits, Data Link Feature support, ESM-supported data-rate bitmaps, CCIX support, and lane equalization capability fields. Some fields are live status, such as negotiated link speed/width, equalization completion/failure, AER status, DPC trigger state, RP PIO first-error pointer, TLP header/prefix logs, margining ready/status, and ESM status. Others are writable controls, including PCI command enables, bridge reset/control, PM control, MSI enablement and addresses, PCIe device/link/root controls, AER masks and severity, ACS controls, L1 PM substate controls, DPC controls, CCIX/ESM controls, 16 GT/s equalization presets, and margining lane commands.

Persistence depends on the device power/reset domain. Writable hardware register values can survive normal runtime until reset, FLR, suspend/resume, hot reset, GPU reset, or firmware reinitialization. Sticky error/status registers may require specific clear semantics that this generated header does not describe.

## Dependencies And Integration Points

The immediate dependency is the matching generated offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`. This shift/mask header says which bits matter; the offset header says where the registers are located.

Integration points include:

- AMDGPU NBIO register access code that selects ASIC-generation-specific register headers.
- PCIe bridge/root-port initialization paths that program command, status, bus number, memory/I/O window, interrupt, bridge-control, PM, MSI, and PCIe capability fields.
- PCIe link management and diagnostics that inspect link speed/width, ASPM, retrain state, equalization phases, lane error status, 16 GT/s equalization status, parity mismatch status, and per-lane transmit presets.
- RAS, AER, DPC, and Root Port PIO handling paths that decode status, mask, severity, source ID, first-error pointer, header log, and prefix log fields.
- Isolation and virtualization-sensitive policy code that interprets ACS capability/control fields.
- Power-management code that configures L1 PM substates and related restore/threshold timing fields.
- CCIX and ESM capability handling that discovers supported rates, enables ESM, selects data rates/timeouts, tracks calibration, and configures retimer/link reach fields.
- Lane margining tooling or diagnostics that uses the port readiness bits and per-lane receiver/type/payload command/status fields.

A reference search in this repository found the sampled field names primarily in generated headers and the matching offset/default files rather than ordinary C call sites. That is expected for generated ASIC register definitions: many macros exist for hardware completeness even if only a subset is currently referenced by compiled driver code.

## Risks

The primary risk is silent hardware misprogramming from a wrong bit mask or shift. A single incorrect field can enable the wrong PCI command bit, decode a status bit as a different error, mask or unmask the wrong AER/DPC condition, select an invalid ESM rate, corrupt a lane preset, or send a margining command to the wrong receiver/type/payload field.

The repetition across lanes and rates is a major maintenance hazard. The per-lane PCIe equalization and margining groups repeat nearly identical definitions for many lanes, so copy-generation mistakes may only affect one lane and appear only on certain link widths. The ESM capability registers are especially sensitive because each bit represents a 0.1 GT/s step; an off-by-one shift would advertise or select the wrong data rate.

Several registers mix 8-bit, 16-bit, and 32-bit-style fields in a C macro namespace without encoding access width or write semantics. Consumers must use the hardware-specified access width and preserve reserved bits. Error/status fields may be sticky or write-one-to-clear, and log registers may have capture side effects; this header only supplies bit geometry and cannot prevent unsafe writes.

The chunk boundary itself is a documentation/reconciliation risk. It begins mid-`BIFPLR4_1_LANE_13_MARGINING_LANE_CNTL` and ends mid-`BIFPLR5_1_LANE_6_MARGINING_LANE_CNTL`, so any per-file merged report must stitch adjacent chunks to avoid treating incomplete opening and closing register groups as complete schemas.

## Test Signals

Useful validation signals are mostly build and hardware integration signals:

- The AMDGPU tree builds with NBIO 7.2.0 headers included and all referenced generated macro names resolve.
- Register-offset and shift/mask pairs remain synchronized between `nbio_7_2_0_offset.h`, this header, and related generated default headers.
- PCIe enumeration on supported AMD hardware reports plausible bridge windows, PCIe capabilities, MSI capability, AER/DPC/ACS/L1 PM substate capability, and link speed/width values compared with `lspci -vv` and kernel PCIe logs.
- Link training and retraining tests show expected equalization completion bits, per-lane preset behavior, no lane swaps in lane error/parity status, and stable negotiated speed/width across reset and resume.
- AER/DPC/RP PIO fault-injection or hardware-error tests decode status, severity, source ID, first-error pointer, header log, and prefix log fields consistently with kernel PCIe reporting and hardware documentation.
- ESM/CCIX validation, where supported by the platform, shows correct rate capability bitmaps, enable/status transitions, calibration completion, retimer/reach handling, and 20/25 GT/s per-lane presets.
- Lane margining diagnostics report port ready/software-ready status and per-lane command/status payloads without cross-lane or field-offset mismatches.
