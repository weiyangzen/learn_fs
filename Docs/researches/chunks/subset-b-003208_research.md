# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 116618-119033

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains 2,168 `#define` lines, including paired `__SHIFT` and `_MASK` macros for hardware register fields, plus 246 register or address-block comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `BIFPLR2_1_ESM_LANE_12_EQUALIZATION_CNTL_25GT` register, covers the tail of the `BIFPLR2_1` 25 GT ESM/CCIX translation definitions, then enters `// addressBlock: nbio_pcie0_bifplr3_cfgdecp`. Most of the chunk defines the `BIFPLR3_1` PCI/PCIe bridge configuration and extended-capability field layout. It ends after the complete `BIFPLR3_1_ESM_LANE_1_EQUALIZATION_CNTL_20GT` field masks, immediately before `BIFPLR3_1_ESM_LANE_2_EQUALIZATION_CNTL_20GT`.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO register interface. For each hardware register field it exposes:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

This chunk describes the PCIe configuration-space image for the `BIFPLR3_1` root-port/bridge-like block, including conventional PCI bridge registers, PCI power management, MSI and SSID capabilities, PCIe capability registers, virtual channel and multicast resources, advanced error reporting, secondary PCIe capability, ACS, L1 PM substates, downstream port containment, root-port PIO reporting, enhanced speed mode, lane equalization, lane margining, and CCIX capability/control/status fields. The first lines also finish `BIFPLR2_1` 25 GT ESM equalization presets and CCIX optimized TLP translation enablement.

Although this path is under a `ceph-client` source mirror, the file is AMDGPU hardware metadata. It has no direct distributed filesystem behavior.

## Important Macro Families

The `BIFPLR2_1` tail at the beginning of the range covers:

- 25 GT ESM lane equalization control for lanes 12-15. Each lane has downstream-port and upstream-port TX preset fields at shifts 0 and 4 with `0x0f`/`0xf0` masks.
- `BIFPLR2_1_PCIE_CCIX_TRANS_CAP` and `BIFPLR2_1_PCIE_CCIX_TRANS_CNTL`, which expose optimized CCIX TLP-format support and enable bits.

The `BIFPLR3_1` address block starts at line 116643 and defines a PCI/PCIe configuration register map:

- Conventional PCI bridge fields: vendor/device ID, command/status, revision and class-code bytes, cache line and latency, header and BIST, primary/secondary/subordinate bus numbers, I/O and memory base/limit windows, prefetchable base/limit upper dwords, ROM base, interrupt line/pin, bridge control, and vendor/adapter capability fields.
- Power management fields: PM capability-list metadata, PME version/clock/DSI/AUX-current support, D1/D2 support, PME support, current power state, PME enable/status, data select/scale, bridge extension, bus power/clock control, and B2/B3 support.
- PCIe capability fields: `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_*`, `ROOT_*`, and second-generation `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and slot capability/control/status 2 fields.
- MSI and subsystem fields: MSI capability header, message control, 32-bit and 64-bit message address/data registers, subsystem vendor/device IDs, and MSI mapping capability.
- Vendor-specific and virtual-channel fields: vendor-specific enhanced capability headers, VC port capability/control/status, VC0 and VC1 resource capabilities, TC/VC maps, arbitration select/load/table offset fields, and negotiation-pending/resource-status bits.
- Advanced Error Reporting: uncorrectable error status/mask/severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress block, TLP prefix block, and poisoned-TLP egress block. Correctable error status/mask fields, ECRC and multi-header controls, header logs, TLP prefix logs, root error command/status, and error source IDs are also defined.
- Secondary PCIe and equalization fields: secondary capability header, `LINK_CNTL3`, lane error status, and normal PCIe lane 0-15 equalization controls with downstream/upstream TX preset and RX preset hint fields.
- ACS fields: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated peer-to-peer support, and egress vector size/control bits.
- Multicast fields: multicast capability and control, group count, BAR/base addresses, receive/block vectors, untranslated-block vectors, and overlay BAR fields.
- L1 PM substate fields: L1.1/L1.2 ASPM and PCI PM support/enables, common-mode restore timing, power-on scale/value, and LTR threshold values.
- DPC and RP PIO fields: DPC trigger reason/support/control/status, RP extension and PIO log support, containment interrupt enable/status, error source ID, PIO status/mask/severity/system-error/exception bits, and PIO header/prefix logs.
- PCIe Enhanced Speed Mode fields: ESM capability-list/header fields, minimum time in electrical idle, ESM enable, and dense support bitmaps in `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7` for 8.0 GT/s through 28.0 GT/s selections.
- Data Link Feature and PHY 16 GT fields: DLF capability/status, 16 GT link capability/control/status, local and retimer parity mismatch statuses, and lane 0-15 16 GT equalization controls.
- Lane margining: margining capability/list/status and lane 0-15 control/status registers, each repeating receiver number, margin type, usage model, and payload fields.
- CCIX and CCIX ESM fields: CCIX capability-list/header fields, ESM support and reach/capability/timing fields, required/optional ESM capability masks for 2.5, 5, 8, 16, 20, and 25 GT, current data-rate/calibration status, ESM enable/calibration/control, timeout controls, reach/retimer selectors, and the first two 20 GT ESM lane equalization control registers.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace, consisting of untyped integer preprocessor constants, mostly with an `L` suffix.

These macros do not include register addresses, reset defaults, read/write permissions, write-one-to-clear behavior, firmware ownership, ordering requirements, or side-effect rules. Consumers must combine them with the companion address metadata in `nbio_7_2_0_offset.h`, for example matching `BIFPLR3_1_VENDOR_ID__VENDOR_ID_MASK` with `regBIFPLR3_1_VENDOR_ID` and `regBIFPLR3_1_VENDOR_ID_BASE_IDX`. Runtime users typically access fields through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or NBIO/PCIe-specific accessors selected by the calling code.

## Control Flow

This header has no local runtime control flow. The implied runtime flow is external:

1. AMDGPU code selects a `BIFPLR2_1_*` or `BIFPLR3_1_*` register address from generated offset metadata.
2. It reads a register value or composes a new value through an NBIO, SOC15, or PCIe configuration access path.
3. It uses the `__SHIFT` and `_MASK` constants from this header to decode a field, update a field while preserving unrelated bits, or test a status/capability bit.
4. Hardware then performs the actual behavior: PCIe bridge decode, command/status reporting, interrupt/MSI delivery, link training, equalization, lane margining, error latching/reporting, DPC containment, L1 PM transitions, ACS routing policy, multicast/VC mapping, CCIX ESM calibration, or enhanced speed mode selection.

Several represented flows are asynchronous to software. Link status, equalization completion, lane margining status, ESM calibration completion, AER/DPC status, RP PIO logs, and PME or interrupt status can change due to hardware events outside the CPU-side control path.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO/PCIe configuration registers. Persistence depends on the GPU and PCIe reset domains, platform firmware initialization, hot/warm/fundamental reset behavior, function-level reset where supported, AMDGPU initialization and suspend/resume restore, and explicit software writes.

Represented state includes static identifiers and capabilities, bridge resource windows, command/control enables, interrupt routing, MSI target/data values, negotiated link status, advertised and selected link features, lane equalization presets, margining controls/statuses, error status/mask/severity latches, diagnostic header and prefix logs, L1 PM timing controls, DPC containment state, RP PIO exception classification, ACS policy, VC/multicast routing resources, CCIX capabilities, ESM data rate selection, calibration state, and lane presets for 20 GT and 25 GT operation.

Call sites must not infer write semantics from the mask geometry alone. Some fields are read-only capabilities, some are live status bits, some are sticky status bits, some are write-one-to-clear, and some are ordinary software-owned controls. The hardware specification and the register access path decide those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with sibling generated files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h` supplies matching `regBIFPLR3_1_*` addresses and `*_BASE_IDX` constants for the register names defined here. Spot checks show entries such as `regBIFPLR3_1_VENDOR_ID`, `regBIFPLR3_1_PCIE_UNCORR_ERR_STATUS`, `regBIFPLR3_1_PCIE_ESM_CAP_1`, and `regBIFPLR3_1_ESM_LANE_0_EQUALIZATION_CNTL_20GT`.
- Other generated NBIO revision headers, such as `nbio_7_7_0_sh_mask.h`, carry homologous `BIFPLR3_1_*` field layouts and are useful for detecting cross-generation drift.
- Common AMDGPU register helper macros provide field extraction and insertion; this file only provides constants used by those helpers.

The integration surface is PCIe/NBIO behavior in AMDGPU: device and bridge setup, BAR/window/resource decode, link capability and link-status reporting, link retraining and equalization, lane margining diagnostics, AER/DPC and root-port PIO handling, MSI setup, ASPM/L1 PM substate policy, ACS/IOMMU isolation, virtual-channel and multicast configuration, CCIX and enhanced speed mode support, register dumps, and hardware bring-up scripts.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while targeting the wrong hardware bits, causing incorrect PCIe capabilities, broken resource windows, missed or misclassified errors, unsafe ACS policy, or link-training instability.
- The range starts and ends mid-family. The previous chunk is needed for the first half of `BIFPLR2_1_ESM_LANE_12_EQUALIZATION_CNTL_25GT`; the next chunk is needed for `BIFPLR3_1_ESM_LANE_2_EQUALIZATION_CNTL_20GT` and the rest of the BIFPLR3 20 GT/25 GT ESM lane families.
- Per-lane families repeat across lanes 0-15. A one-lane generation error can be invisible on narrow links and only surface on wider link widths or lane-specific margining/equalization tests.
- Error, DPC, and RP PIO status/log registers may be sticky or write-one-to-clear. Generic read-modify-write sequences can accidentally clear diagnostics or preserve stale error state if they rely only on masks.
- Bridge base/limit, command, ACS, multicast, and VC fields affect routing and isolation. Incorrect writes can block legitimate DMA, expose peer-to-peer traffic, confuse enumeration, or break IOMMU expectations.
- Link control, equalization, margining, CCIX, ESM, retimer, and L1 PM fields are link-partner and platform sensitive. Writes may require strict sequencing, polling, quiescence, or retraining windows not represented in this header.
- Dense ESM capability bitmaps use one bit per 0.1 GT/s step across multiple registers. Off-by-one assumptions in decoding can report or select the wrong data rate.
- Capability fields should not be treated as programmable policy. Writes to read-only capability bits may be ignored, while writes to control bits can have immediate hardware side effects.

## Test Signals

- Build AMDGPU with NBIO 7.2.0 support enabled. Compile-time coverage catches missing or renamed macros referenced by consumers.
- Run generated-header consistency checks: every field should have compatible `__SHIFT` and `_MASK` values, repeated lane 0-15 families should match except for lane number, and masks within each register should not overlap unexpectedly.
- Cross-check this shift/mask chunk against `nbio_7_2_0_offset.h` so each `BIFPLR3_1_*` layout has a matching register address and base index.
- Compare homologous `BIFPLR3_1_*` families with adjacent NBIO generation headers to catch accidental field drift that is not explained by hardware revision changes.
- On supported hardware, validate PCIe enumeration, bridge window assignment, MSI delivery, negotiated link width and speed, equalization state, lane error status, suspend/resume, and reset recovery.
- Exercise diagnostics where available: AER correctable/uncorrectable injection or observation, DPC containment, RP PIO logs, lane margining, L1 PM substate transitions, ACS policy, VC/multicast programming, CCIX capability reporting, and ESM calibration/status reporting.
- For write paths using these masks, inspect register traces to confirm reserved bits are preserved, sticky bits are cleared intentionally, per-lane writes stay within active/implemented lanes, and link-sensitive fields are not changed while training or calibration is active unless the hardware sequence requires it.
