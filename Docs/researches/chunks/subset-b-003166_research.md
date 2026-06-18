# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 14800-17218

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2 shift/mask header. It defines C preprocessor constants for decoding and programming bitfields in the `BIFPLR0_*` PCI/PCIe bridge and root-port register view. The macros describe field geometry only: each register field receives a zero-based `__SHIFT` constant and a pre-shifted `_MASK` constant. There are no functions, structs, enums, runtime algorithms, Ceph paths, or distributed-filesystem semantics in this source range despite the repository mirror path.

The range contains 2,171 `#define` entries across 248 commented register blocks. There are 1,083 field `__SHIFT` definitions and 1,088 field `_MASK` definitions. The five-mask surplus is a chunk-boundary artifact: the range starts at the tail of `BIFPLR0_COMMAND`, where the shifts and first six masks are in the previous chunk. The range ends at the comment for `BIFPLR0_ESM_LANE_12_EQUALIZATION_CNTL_20GT`; its fields are in the next chunk.

At a high level this chunk covers the main `BIFPLR0` PCI bridge/root-port configuration layout, PCIe capability and error-reporting fields, per-lane PCIe equalization fields, access control and multicast controls, L1 PM substates, Downstream Port Containment and root-port PIO diagnostics, Equalization Service Mode capability bitmaps, data-link feature exchange, 16 GT/s PHY/equalization fields, lane margining control/status fields for lanes 0-15, CCIX ESM capability/control fields, and the start of 20 GT/s ESM per-lane equalization controls.

## Important APIs, Types, and Macros

There are no APIs in the usual function-call sense. The interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used when extracting or composing a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

The first visible lines finish `BIFPLR0_COMMAND` masks for parity error response, address stepping, SERR, fast back-to-back, and interrupt disable. The command register's shifts and earlier masks are outside this chunk.

The standard PCI and PCI-to-PCI bridge-like fields include:

- `BIFPLR0_STATUS`, revision/class/prog-interface/cache/latency/header/BIST fields.
- Bus numbering, I/O base/limit, memory base/limit, prefetchable memory base/limit, upper address, capability pointer, ROM base, interrupt line/pin, bridge control, and extension control fields.
- Vendor capability, subsystem/adapter ID, and power-management capability/status-control fields, including PME status/enable, selected power state, no-soft-reset, data select/scale, and bridge extension bits.

The PCIe capability fields include:

- `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` fields for device type, slot implementation, interrupt message, payload/read request sizing, relaxed ordering, no-snoop, error-reporting enables, FLR, captured slot power, and transaction/error status bits.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` fields for supported/current speed and width, ASPM, exit latencies, clock power management, surprise-down and active-link reporting, retraining, common clock, bandwidth notifications, and data-link active state.
- Slot and root-control/status blocks for hotplug-style events, power/attention controls, PME requestor/status, and root SERR policy.
- PCIe 2.0+ blocks such as `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, covering completion timeout, ARI forwarding, AtomicOp, ID ordering, LTR, OBFF, ten-bit tags, E2E TLP prefixes, target link speed, compliance, de-emphasis, DRS, crosslink, and equalization status.

Interrupt and identification capability macros cover MSI message control/address/data fields, SSID capability fields, and MSI mapping capability bits. Vendor-specific enhanced capability fields expose VSEC ID/revision/length and two scratch dwords.

The virtual-channel section defines `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status fields, and VC0/VC1 resource capability/control/status fields. These macros describe arbitration capability/table offsets, TC/VC mapping, load controls, VC enable bits, negotiation pending status, and resource assignment status.

Advanced Error Reporting is represented by `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header logs, root error command/status, error source ID, and TLP prefix logs. Fields include common PCIe AER categories such as data-link protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, replay rollover, replay timeout, advisory nonfatal, and corrected internal error.

The secondary/link training and lane-equalization section defines:

- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS`.
- `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, each with downstream/upstream TX presets and RX preset hints.

Isolation, multicast, low-power, and containment fields include:

- ACS enhanced capability, ACS capability, and ACS control bits for source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct translated P2P.
- Multicast capability/control/address/receive/block/overlay BAR fields.
- L1 PM substate capability/control fields for PCI PM L1.1/L1.2, ASPM L1.1/L1.2, common-mode restore time, threshold values/scales, and T_POWER_ON values.
- DPC capability/control/status fields and root-port PIO status/mask/severity/system-error/exception/header-log/prefix-log fields.

The ESM and high-speed PHY portion includes:

- `PCIE_ESM_CAP_LIST`, headers, status, control, and `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`. These are dense capability bitmaps enumerating ESM data-rate points from low single-digit rates through `ESM_28P0G`.
- Data Link Feature capability/status fields for local and remote DLF support and exchange/valid bits.
- 16 GT/s PHY enhanced capability, reserved link cap/control dwords, 16 GT/s equalization status, local/retimer parity mismatch status, and `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`.
- PCIe lane margining enhanced capability, port capability/status, and lane 0-15 margining control/status fields. Each lane control/status block uses receiver number, margin type, usage model, and payload fields.
- CCIX capability headers plus CCIX ESM required/optional capability, status, and control fields, including supported ESM rates, calibration complete, selected data rates, enable/calibration request, extended equalization timeouts, link reach target, retimer presence, and quick equalization timeout selection.
- 20 GT/s ESM lane equalization controls for lanes 0-11 are complete in this chunk; lane 12 starts only as a register comment at the final line and continues in the next chunk.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It contributes compile-time constants to code that reads or writes NBIO/BIF PCI configuration registers. Runtime behavior is implied by consumers that combine these masks with register offsets from `nbio_7_2_0_offset.h` and with AMDGPU register access helpers.

The implied hardware flows are:

1. PCI/PCIe initialization and enumeration code reads identity, class, bridge window, BAR/ROM, capability pointer, interrupt, PM, and PCIe capability fields.
2. Bring-up code programs command enables, bridge controls, payload/read request sizes, link policy, ASPM/L1 substate policy, MSI/MSI mapping, VC resources, ACS isolation, multicast windows, and data-link feature exchange.
3. Error handling and RAS paths read AER status, root error status, source ID, header logs, TLP prefix logs, DPC status, and root-port PIO logs, then use mask/severity/control fields to classify, report, or contain faults.
4. Link training, equalization, margining, CCIX, and ESM paths use the per-lane and data-rate fields to negotiate or diagnose high-speed PCIe links across 8 GT/s, 16 GT/s, 20 GT/s, 25 GT/s, and CCIX-related modes.

The file itself does not perform hardware access, validate values, sequence reset/retrain operations, clear write-one-to-clear status bits, or persist policy. Those semantics belong to the AMDGPU driver paths and the NBIO 7.2 hardware specification.

## State and Persistence

The header owns no mutable state, allocates no memory, persists no data, and performs no I/O. The represented state lives in NBIO/BIF PCI configuration-space and enhanced-capability registers.

State categories represented by this chunk include:

- Enumeration and bridge-window state: status/class/header fields, bus numbers, I/O and memory decode windows, ROM base, capability pointer, interrupt line/pin, and bridge control bits.
- Power and link policy: PM state, PME, ASPM, L1 PM substates, LTR/OBFF, completion timeout controls, target link speed, de-emphasis, common clock, retraining, and clock power management.
- Error-observation and containment state: AER status/mask/severity, root error command/status, source IDs, header/prefix logs, DPC controls/status, and root-port PIO status/mask/severity/log registers.
- Isolation and routing state: ACS capability/control, ARI forwarding bits in device control 2, multicast group/window/block settings, virtual-channel resource controls, and data-link feature exchange state.
- Signal-integrity and high-speed link state: equalization presets, lane error status, 16 GT/s parity mismatch status, lane margining control/status, ESM data-rate capability bitmaps, CCIX ESM controls, and per-lane 20 GT/s preset fields.

Persistence across GPU reset, PCI reset, FLR, D3 transitions, suspend/resume, or runtime power transitions is not specified by this header. A wrong shift or mask value would persist in the compiled driver until the generated header is corrected and rebuilt.

## Dependencies and Integration Points

The direct companion in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies the address/offset side of the same NBIO 7.2 register map. The inspected directory does not contain `nbio_7_2_0_default.h` or `nbio_7_2_0_smn.h`, so this chunk's local integration is primarily with the offset header and the AMDGPU code that includes generated ASIC register headers.

Likely integration areas include:

- NBIO 7.2 ASIC initialization and low-level register access paths.
- PCIe root port or bridge configuration code that manages bus windows, command/status, PM, link, slot, root, MSI, and virtual-channel state.
- PCIe error handling, AER, DPC, RAS, and recovery paths.
- Link training, equalization, lane margining, CCIX, and ESM diagnostics or setup paths.
- Power-management code for ASPM, L1 substates, D-states, PME, LTR, OBFF, and emergency power reduction.
- DMA isolation and fabric routing paths that depend on ACS, ARI, multicast, and peer-to-peer controls.

Integration is exact-symbol based. `BIFPLR0_*` masks must be paired with the matching `BIFPLR0` offsets/register accesses; using similarly shaped fields from a different NBIO block or endpoint/function would silently decode or program the wrong hardware view.

## Risks

- Chunk boundaries split definitions. This range begins mid-`BIFPLR0_COMMAND` and ends at the `BIFPLR0_ESM_LANE_12_EQUALIZATION_CNTL_20GT` comment; adjacent chunks are required for complete pair accounting.
- The file is generated and repetitive. Manual edits or ad hoc fixes can easily break a shift/mask pair, duplicate a symbol, or desynchronize this header from `nbio_7_2_0_offset.h`.
- Many fields have identical names across status, mask, severity, command, and control registers. Confusing AER status with mask or severity can hide errors, misclassify fatality, or corrupt diagnostics.
- Link control fields directly affect PCIe training and stability. Incorrect masks for speed, width, ASPM, de-emphasis, equalization, DRS, L1 substates, or ESM controls can cause link training failures, bandwidth regressions, or resume failures.
- ACS, multicast, ARI, ID ordering, TLP prefix, and peer-to-peer fields affect routing and isolation. Wrong programming can create DMA isolation problems or break virtualization/peer-to-peer assumptions.
- MSI/MSI mapping fields and root error interrupt message fields influence interrupt delivery. Incorrect offset/BIR or message-number decoding can produce missing or misrouted interrupts.
- Lane equalization and margining definitions are dense per-lane repetitions. Off-by-one lane use or mixing lane status/control macros can make signal-integrity diagnostics misleading.
- CCIX and ESM rate bitmaps are dense and non-linear in places. Consumers should avoid assuming a simple continuous bit-to-rate transform unless it matches the hardware specification.
- Several full-dword log or reserved fields use `0xFFFFFFFFL`. Consumers should keep normal unsigned 32-bit register handling to avoid width/sign surprises.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware-facing coverage:

- Build AMDGPU configurations that include NBIO 7.2 generated headers to catch malformed or duplicate macro definitions.
- After adjacent chunks are merged, verify each field has matching `__SHIFT` and `_MASK` definitions. Expected local exceptions are the initial `BIFPLR0_COMMAND` masks and the final empty `BIFPLR0_ESM_LANE_12_EQUALIZATION_CNTL_20GT` boundary.
- Cross-check `BIFPLR0_*` register names against `nbio_7_2_0_offset.h` so field macros have corresponding address macros where expected.
- Decode PCI config-space/register dumps from NBIO 7.2 hardware and compare command/status, bridge windows, PM, PCIe capability, MSI, VC, AER, DPC, ACS, multicast, L1 PM, DLF, margining, CCIX, and ESM fields against expected hardware values.
- Exercise AER/DPC/root-port PIO paths with controlled correctable, uncorrectable, and containment scenarios; confirm status/mask/severity/source/log fields decode correctly.
- Exercise link retraining, ASPM/L1 substate transitions, suspend/resume, D3/D0 transitions, and high-speed equalization paths; confirm link status, equalization, parity mismatch, and margining fields decode consistently.
- Validate ACS/multicast/peer-to-peer behavior in IOMMU and virtualization scenarios, especially where isolation controls and P2P redirects are enabled.
- Validate MSI/MSI-map and root error interrupt routing by checking message data/address and interrupt message-number fields under error and PME events.

## Chunk Boundary Notes

Lines 14800-14804 contain only the final five masks from `BIFPLR0_COMMAND`; the matching shifts and earlier command masks are in the previous work item. Lines 14805-15755 cover the standard PCI/PCIe, MSI, VC, and AER blocks through TLP prefix logs. Lines 15756-16050 cover secondary PCIe link control, lane equalization, ACS, multicast, and L1 PM substate blocks. Lines 16051-16220 cover DPC and root-port PIO diagnostics. Lines 16221-16654 cover ESM capability bitmaps. Lines 16655-17157 cover DLF, 16 GT/s PHY/equalization, lane margining, and CCIX ESM fields. Lines 17158-17217 cover 20 GT/s ESM lane equalization controls for lanes 0-11; line 17218 starts the lane 12 block, whose fields continue in the next chunk.
