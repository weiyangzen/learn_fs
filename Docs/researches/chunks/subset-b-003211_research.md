# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 123882-126303

## Scope

This chunk is a generated AMD NBIO 7.2.0 register shift/mask segment. It contains only preprocessor field-layout macros and register-family comments; there are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the middle of the `BIFPLR5_1_LANE_6_MARGINING_LANE_CNTL` definitions, covers the rest of `BIFPLR5_1` PCIe lane margining and CCIX/ESM fields, then begins the generated `// addressBlock: nbio_pcie0_bifplr6_cfgdecp` block. The `BIFPLR6_1` portion describes a PCIe bridge/root-port style configuration space from vendor/device/class registers through DPC, RP PIO, ESM, Data Link Feature, 16 GT/s PHY capability, and per-lane 16 GT/s equalization definitions. The range ends at the `BIFPLR6_1_LANE_15_EQUALIZATION_CNTL_16GT` comment, before that lane's field macros are complete.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield half of AMD's generated NBIO register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk primarily supports PCIe configuration-space and high-speed-link management for NBIO 7.2.0. The `BIFPLR5_1` section covers PCIe lane margining, CCIX capability and transaction-control fields, CCIX ESM data-rate capability/status/control fields, and per-lane ESM TX presets for 20 GT/s and 25 GT/s. The `BIFPLR6_1` section maps a full root-port configuration decode block, including standard PCI bridge fields, PM/PCIe/MSI capabilities, virtual-channel resources, serial number, AER, secondary PCIe equalization, ACS, multicast, L1 PM substates, DPC/RP PIO containment and logging, ESM capability bitmaps, Data Link Feature exchange, and 16 GT/s PHY equalization state.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The `BIFPLR5_1` lane-margining families define control/status fields for lanes 6 through 15. Each lane exposes receiver number, margin type, usage model, and margin payload fields, with matching status readback masks. The first lines are the tail of lane 6 control; adjacent chunks are needed for the complete lane 6 control register.

The `BIFPLR5_1` CCIX families describe the CCIX enhanced capability list/header, ESM support metadata, required ESM speed support bits for 2.5, 5, 8, 16, 20, and 25 GT/s, ESM current data-rate and calibration-complete status, and ESM control fields for two data-rate selectors, calibration request, enable, phase 2/3 timeout extension, link reach, retimer presence, and quick-equalization timeout selection. The transaction capability/control pair exposes optimized TLP format support and enablement.

The `BIFPLR5_1_ESM_LANE_*_EQUALIZATION_CNTL_20GT` and `..._25GT` groups repeat uniformly for lanes 0 through 15. Each lane has downstream-port and upstream-port TX preset fields, encoded as low and high nibbles. These definitions are signal-integrity sensitive because they represent equalization presets for CCIX/ESM operation at 20 and 25 GT/s.

The `BIFPLR6_1` standard PCI bridge/configuration families include vendor/device IDs, command/status, revision/class-code bytes, cache-line/latency/header/BIST, primary/secondary/subordinate bus numbers, IO/memory/prefetchable bridge windows, ROM base, interrupt line/pin, bridge controls, subsystem IDs, and capability pointers. These are the base fields used to enumerate and program the root-port-like PCIe function.

The `BIFPLR6_1` PM and PCIe capability groups cover power-management capability/status-control, PCIe device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and PCIe capability version 2 fields. Important behaviors represented here include payload size, max read request size, relaxed ordering, no-snoop, FLR, error reporting enables, PME, ASPM/link disable/retrain/common-clock controls, negotiated link speed/width, slot hotplug/power bits, root error signaling, completion timeout, ARI, AtomicOp, ID-based ordering, LTR, OBFF, ten-bit tags, emergency power reduction, and FRS.

The interrupt and extended capability groups include MSI control/address/data fields, SSID, MSI mapping, vendor-specific enhanced capability headers/data, virtual-channel capabilities and VC0/VC1 resource controls, device serial number, AER status/mask/severity/control/header-log/root-error/source-ID/TLP-prefix-log fields, secondary PCIe link control and lane error status, per-lane secondary equalization controls, ACS capability/control, multicast addressing and receive/block vectors, L1 PM substate capability/control, and DPC/RP PIO fields.

The late `BIFPLR6_1` DPC/RP PIO/ESM/DLF/16GT groups describe downstream port containment capability/control/status, DPC error source ID, root-port PIO status/mask/severity/system-error/exception bitmaps for config/IO/memory UR/CA/CTO conditions, PIO header and prefix logs, PCIe ESM capability/status/control and dense data-rate support bitmaps, Data Link Feature exchange support/status, and 16 GT/s PHY enhanced capability fields. The 16 GT/s section includes equalization-complete/phase-success/request status bits, parity mismatch status registers, and lane 0 through lane 14 TX preset controls; lane 15 is only introduced in this chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public surface is the generated macro namespace.

The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry. They do not encode register addresses, reset values, access widths, read/write permissions, write-one-to-clear behavior, sequencing requirements, firmware ownership, or hardware side effects. Consumers must combine these macros with sibling generated address/default metadata and AMDGPU bitfield/register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and the relevant SOC15/NBIO/SMN/PCIe access path.

## Control Flow

This header has no local runtime control flow. Runtime use follows the generated-register pattern:

1. AMDGPU or low-level diagnostic code selects a `BIFPLR5_1_*` or `BIFPLR6_1_*` register address from companion generated metadata.
2. The code reads a 16-bit or 32-bit hardware/config-space value, then applies the `*_MASK` and `*__SHIFT` constants to decode a field.
3. For writable controls, the code composes a new value with the same masks while preserving unrelated and reserved bits, then writes the hardware register through the appropriate access path.

The field names imply hardware flows outside the header: PCI enumeration, bridge-window programming, PME and D-state transitions, MSI routing, link retraining and equalization, lane margining, ESM calibration/data-rate changes, AER reporting and clearing, ACS isolation, VC negotiation, multicast windowing, L1.1/L1.2 power entry/exit timing, DPC containment, RP PIO logging, DLF exchange, and 16 GT/s equalization/parity status.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration and capability registers. Persistence depends on the GPU reset domain, PCIe hot/warm reset, link retrain, power gating, firmware/BIOS initialization, suspend/resume restore, and explicit driver writes.

Represented state includes capability descriptors, negotiated link state, error-status latches, interrupt enables, bridge aperture configuration, PM/D-state controls, MSI programming, VC/ACS/multicast policy, lane margining commands and readbacks, CCIX/ESM data-rate and calibration controls, DPC containment status, RP PIO logs, DLF advertised/remote-supported features, and 16 GT/s equalization/parity status. Some fields are status or write-one-to-clear at the hardware/specification level, so the mask definitions alone are not enough to infer safe read-modify-write behavior.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with sibling headers:

- `nbio_7_2_0_offset.h` and related generated address headers provide register offsets or SMN addresses for the same `BIFPLR5_1_*` and `BIFPLR6_1_*` names.
- `nbio_7_2_0_default.h`, where available for a register, provides reset/default values.
- AMDGPU SOC15/NBIO register helpers and PCIe config-space access paths apply these masks and shifts at runtime.

Semantic dependencies come from the PCI, PCIe, AER, ACS, MSI, VC, L1 PM Substates, DPC, RP PIO, Data Link Feature, CCIX, and ESM specifications. The generated names mirror those architectural fields, but legality checks, ordering, timeouts, and side-effect handling are the responsibility of driver code and hardware documentation.

Integration points are PCIe/NBIO bring-up, enumeration, reset and resume restore, power management, link training/retraining, error handling, virtualization/isolation policy, debug register dumps, and hardware diagnostics. High-speed equalization and lane-margining fields are especially tied to platform firmware and board-specific signal-integrity assumptions.

## Risks And Edge Cases

- The chunk starts and ends mid-family: lane 6 margining control is incomplete at the start, and lane 15 16 GT/s equalization control is incomplete at the end. Adjacent chunks are required for complete per-register analysis.
- Generated shift/mask drift can compile successfully while decoding the wrong bit or programming the wrong hardware field, leading to enumeration failures, unstable PCIe links, broken power management, missing interrupts, or misreported error status.
- Many fields are repeated across lanes or capability blocks. Copy/generation errors can be lane-specific and may only appear at certain negotiated widths or data rates.
- Error-status, DPC, RP PIO, AER, slot-status, PME, and link-status fields may have write-one-to-clear, sticky, or asynchronous behavior. Generic read-modify-write code can accidentally clear events or preserve stale state if it ignores the hardware semantics.
- Controls for bridge windows, ACS, VC, MSI, AER masks/severity, DPC, AtomicOp, IDO/LTR/OBFF, link retraining, L1 PM substates, lane margining, ESM data-rate changes, and equalization presets affect isolation, DMA visibility, interrupt delivery, containment, power, and link stability.
- Reserved fields such as `BIFPLR6_1_LINK_CAP_16GT__RESERVED_MASK` and `BIFPLR6_1_LINK_CNTL_16GT__RESERVED_MASK` must be preserved unless the hardware documentation says otherwise.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` rely on the established AMDGPU unsigned register-helper types to avoid signedness or truncation surprises.

## Test Signals

- Build coverage for AMDGPU translation units that include `nbio_7_2_0_sh_mask.h`; this catches missing or renamed generated symbols used by consumers.
- Generated-header consistency checks: every field should have a compatible `__SHIFT`/`_MASK` pair, masks should align with shifts, and repeated lane families should differ only by lane number and expected prefix.
- Cross-header checks that `BIFPLR5_1_*` and `BIFPLR6_1_*` register names in this slice have matching address metadata and expected defaults in the NBIO 7.2.0 generated headers.
- Runtime PCIe config-space validation on NBIO 7.2.0 hardware using `lspci -vvxxx`, AMDGPU debug register dumps, or firmware traces: vendor/device IDs, bridge apertures, PM state, MSI, link speed/width, AER masks/status, ACS/VC/multicast state, L1 PM substate controls, and DPC/RP PIO state should decode consistently.
- Link-training and power tests around retrain-link, equalization completion, lane error/parity status, 16 GT/s preset fields, CCIX/ESM calibration and data-rate transitions, L1.1/L1.2 entry/exit timing, suspend/resume, and GPU reset recovery.
- Error-path validation through injected or observed AER/DPC/RP PIO conditions, checking that software reports, masks, clears, and logs the intended fields without touching unrelated status.
- Lane-margining and high-speed ESM diagnostics should verify receiver number, margin type, usage model, payload/status, per-lane TX presets, retimer/reach controls, and calibration-complete behavior against hardware expectations.
