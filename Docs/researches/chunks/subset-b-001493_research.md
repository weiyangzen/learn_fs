# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 16995-21114

## Scope And Purpose

This chunk is part of AMDGPU's generated BIF 5.1 register field mask header. It contains only C preprocessor constants, not executable code. Each definition describes a bit mask or right-shift for a field in AMD PCIe/BIF registers, primarily for device/function namespaces `D3F2`, `D3F3`, and the start of `D3F4`.

The practical purpose is to provide a compile-time bit-layout contract for driver code that reads, decodes, modifies, or writes PCIe and BIF hardware registers. The matching address header, `bif_5_1_d.h`, provides register addresses; this header provides the field packing. Callers combine `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` with low-level MMIO or PCIe-port access helpers to avoid hard-coding bit positions in runtime logic.

The range starts in the middle of `D3F2_PCIE_LC_N_FTS_CNTL` at `LC_N_FTS`, covers the rest of the `D3F2` PCIe link-controller/configuration capability space, covers a large and more complete `D3F3` function block, and ends at the beginning of `D3F4_STATUS`. It includes 2060 complete mask/shift field pairs within the requested line range.

Although this repository path sits under a Ceph source mirror, the content of this chunk is Linux AMDGPU hardware metadata. There is no distributed filesystem or Ceph client logic here.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The important API is the generated macro naming convention:

- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- Consumers normally use `(reg & FIELD_MASK) >> FIELD__SHIFT` to decode a field, and clear/insert fields with `reg = (reg & ~FIELD_MASK) | ((value << FIELD__SHIFT) & FIELD_MASK)`.

The `D3F2` portion begins with link-controller fields and then enumerates PCI/PCIe configuration and capability registers. Important groups include `D3F2_PCIE_LC_SPEED_CNTL`, `D3F2_PCIE_LC_CDR_CNTL`, `D3F2_PCIE_LC_LANE_CNTL`, `D3F2_PCIE_LC_FORCE_COEFF`, `D3F2_PCIE_LC_FORCE_EQ_REQ_COEFF`, and `D3F2_PCIE_LC_STATE0` through `D3F2_PCIE_LC_STATE5`. These describe link speed negotiation, Gen2/Gen3 capability straps, software/hardware speed-change gating, current data rate, equalization coefficient forcing, corrupted/disabled lanes, CDR test fields, and recent link-controller state history.

The `D3F2` configuration-register families include conventional PCI header fields such as `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class code fields, BIST, bus numbers, I/O and memory base/limit windows, bridge control, interrupt line/pin, and subsystem ID capability fields. They also cover PCI Express capability registers such as `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, `ROOT_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, and `SLOT_STATUS2`.

The error and advanced-capability portion for `D3F2` includes `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header/TLP-prefix log registers, root error command/status, error source ID, VC capability/control/status, vendor-specific enhanced capability headers, device serial number fields, ACS capability/control, and multicast (`PCIE_MC_*`) registers. These constants describe AER reporting, isolation/security controls, virtual-channel resources, multicast groups, and diagnostic log extraction.

The `D3F3` portion repeats much of the standard PCI/PCIe capability map and adds substantial controller-internal state. `D3F3_PCIE_PORT_INDEX` and `D3F3_PCIE_PORT_DATA` define the indirect port access aperture. `D3F3_PCIEP_HW_DEBUG`, `D3F3_PCIEP_PORT_CNTL`, `D3F3_PCIEP_RESERVED`, and `D3F3_PCIEP_SCRATCH` expose debug bits, hotplug/PME/power-fault control, completion payload policy, scratch storage, and reserved port metadata.

The `D3F3` transmit/receive and flow-control groups include `PCIE_TX_CNTL`, `PCIE_TX_REQUESTER_ID`, `PCIE_TX_REQUEST_NUM_CNTL`, `PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, `PCIE_TX_ACK_LATENCY_LIMIT`, `PCIE_TX_CREDITS_*`, `PCIE_TX_CREDITS_STATUS`, `PCIE_TX_CREDITS_FCU_THRESHOLD`, `PCIE_RX_CNTL`, `PCIE_RX_CNTL3`, `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_CREDITS_ALLOCATED_*`, `PCIE_FC_P`, `PCIE_FC_NP`, and `PCIE_FC_CPL`. These fields control requester IDs, outstanding non-posted requests, replay and ACK timers, advertised and initialized credits, credit error/status bits, receive error filtering, completion timeouts, PASID/prefix-related unsupported-request behavior, and allocated receive credits.

The `D3F3` error-injection and link-controller groups are especially sensitive. `D3F3_PCIEP_ERROR_INJECT_PHYSICAL` and `D3F3_PCIEP_ERROR_INJECT_TRANSACTION` expose physical-layer and transaction-layer fault injection fields. `D3F3_PCIE_ERR_CNTL` controls error reporting, ECRC/LCRC generation and dropping, AER header-log timing, slave-buffer halt status/reset, immediate error-message sending, and poisoned advisory behavior. `D3F3_PCIE_LC_CNTL`, `LC_CNTL2`, `LC_CNTL3`, `LC_CNTL4`, `LC_CNTL5`, `LC_CNTL6`, `LC_BW_CHANGE_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_FORCE_COEFF`, `LC_FORCE_EQ_REQ_COEFF`, `LC_BEST_EQ_SETTINGS`, and `LC_STATE0` through `LC_STATE5` describe ASPM/L0s/L1/L23 handling, link resets, quiesce/recovery triggers, Gen3 equalization policy, lane-width reconfiguration, N_FTS timing, speed-change attempts, partner capability observations, and link-state history.

The `D3F3` lane and capability groups include `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, `PCIE_LANE_ERROR_STATUS`, `PCIE_P_PORT_LANE_STATUS`, VC resources, AER logs, ACS, multicast, MSI mapping/message fields, PMI, slot/root controls, and strap/status helpers such as `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, `PCIEP_BCH_ECC_CNTL`, `PCIEP_HPGI_PRIVATE`, and `PCIEP_HPGI`.

The `D3F4` portion starts with port-index/data, debug, port control, TX/RX/credit/error/link-controller fields, physical and transaction error injection, strap/HPGI/BCH-ECC fields, and then enters standard PCI identification and command/status fields. The requested range ends after `D3F4_STATUS__CAP_LIST__SHIFT`; remaining `D3F4_STATUS` fields continue in the next source chunk.

## Control Flow

This header chunk has no direct control flow. It influences control flow in callers by defining how runtime register values are interpreted. A PCIe helper might read a `D3F3_PCIE_LC_SPEED_CNTL` register, decode `LC_CURRENT_DATA_RATE`, branch on the current link generation, set `LC_TARGET_LINK_SPEED_OVERRIDE`, and then set `LC_INITIATE_LINK_SPEED_CHANGE`. Another path might inspect `D3F3_PCIE_LC_LINK_WIDTH_CNTL__LC_LINK_WIDTH_RD`, decide whether link width is degraded, and request reconfiguration with `LC_RECONFIG_NOW` or `LC_RENEGOTIATE_EN`.

The same pattern applies to error handling and diagnostics. AER code or validation tooling can decode uncorrectable/correctable status fields, root error status, header logs, and TLP prefix logs; link validation code can decode per-lane equalization controls and lane error status; hardware test paths can program `PCIEP_ERROR_INJECT_PHYSICAL` or `PCIEP_ERROR_INJECT_TRANSACTION`; flow-control debug paths can inspect advertised, initialized, allocated, and current credit status fields.

Because the macros are generated constants, branch behavior remains in the consuming C files. This chunk's role is to make those branches target the intended bits. A wrong mask or shift would not fail locally in this header; it would make otherwise valid caller control flow observe the wrong state or write the wrong control bit.

## State And Persistence Behavior

The chunk itself stores no state and persists nothing in kernel memory. The state described by the macros is hardware state in PCIe/BIF registers: link speed and width, link-controller state history, ASPM and low-power transition policy, CDR and equalization settings, N_FTS timing, lane disable/corruption state, slot/root/device capability and status fields, AER status and masks, VC and multicast controls, TX/RX flow-control credits, replay/sequence counters, error-injection controls, hotplug/PME/power-fault status, BCH ECC status, and strap-derived configuration.

Persistence semantics belong to the hardware registers and are not encoded in the macro names. Some fields are read-only status, some are writable controls, some are sticky error/status bits, some may be write-one-to-clear, some are strap-derived, and some are self-clearing commands. Driver code must combine these mask/shift constants with hardware documentation or established AMDGPU register sequences to know when a write is safe and whether a read value survives link retraining, FLR, suspend/resume, BACO-like power transitions, hot reset, or full device reset.

Several fields can alter persistent device behavior until the next reset or driver write. Examples include PCI command enable bits, AER masks/severity, ACS controls, VC resource controls, RX ignore/error policy, TX credit/replay policy, link speed/width overrides, ASPM/L-state policy, hotplug/PME enables, and error-injection controls.

## Dependencies And Integration Points

This chunk depends only on the C preprocessor, but it is meaningful only with the rest of the AMDGPU register-header set. The matching `bif_5_1_d.h` address definitions identify the registers, and AMDGPU register-access helpers perform the actual MMIO or indirect PCIe-port reads and writes. Consumers generally include generated ASIC headers through AMDGPU's device-specific register access layers rather than using these masks as standalone definitions.

Integration points include:

- PCIe link management code that reads and writes `PCIE_LC_SPEED_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_STATUS`-style state from adjacent chunks, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_TRAINING_CNTL`, and `PCIE_LC_CNTL*`.
- Power-management and suspend/resume paths that adjust ASPM/L0s/L1/L23 behavior, lane power state, quiesce/recovery handling, and Gen3 equalization behavior.
- PCI/PCIe configuration-space handling that decodes command/status, bridge windows, MSI/MSI mapping, PMI, slot/root/device/link capabilities, and enhanced capability list pointers.
- Error handling and diagnostics that consume AER status/mask/severity, root error status, header logs, TLP prefix logs, ECRC/LCRC generation controls, and `PCIE_ERR_CNTL`.
- Validation and manufacturing paths that use physical/transaction error injection, per-lane equalization controls, lane error status, debug registers, scratch registers, and BCH ECC status.
- Flow-control and transaction-layer debug paths that inspect TX/RX credits, replay counters, sequence numbers, requester IDs, completion timeout policy, and receive ignore rules.
- Hotplug and platform notification paths that interact with `PCIEP_HPGI`, `PCIEP_HPGI_PRIVATE`, slot capability/control/status, PME, and power-fault fields.

The function prefixes matter. `D3F2`, `D3F3`, and `D3F4` identify separate device/function register namespaces with heavily repeated layouts but not always identical coverage. Callers must use the function-specific address and mask names together; mixing `D3F3_*` masks with `D3F4_*` register addresses because the field names look similar can silently target wrong or absent fields.

## Risks And Edge Cases

The dominant risk is silent hardware misprogramming. These definitions compile as constants, so a bad mask, bad shift, or wrong namespace selection usually shows up only as bad hardware behavior: incorrect link speed reporting, failed link retraining, degraded link width, unexpected ASPM behavior, unhandled AER events, broken hotplug notification, malformed credit accounting, or failure to clear/observe sticky status.

Link-controller control bits have high blast radius. Misusing `LC_RESET_LINK`, `LC_GO_TO_RECOVERY`, `LC_SET_QUIESCE`, `LC_REDO_EQ`, `LC_RECONFIG_NOW`, `LC_RENEGOTIATE_EN`, `LC_INITIATE_LINK_SPEED_CHANGE`, speed override fields, or dynamic lane-power fields can retrain or reset the link, disrupt traffic, or leave the GPU behind a nonfunctional PCIe path.

Error-injection fields are dangerous outside controlled validation. `PCIEP_ERROR_INJECT_PHYSICAL`, `PCIEP_ERROR_INJECT_TRANSACTION`, and the LCRC/ECRC generation bits in `PCIE_ERR_CNTL` can intentionally create PCIe errors. Leaving those fields enabled in production paths could cause AER storms, data-transfer failures, or device removal.

The repeated `D3F2`/`D3F3`/`D3F4` and per-lane definitions are vulnerable to generation, copy, and boundary mistakes. Per-lane equalization fields repeat for lanes 0-15; lane error status and lane-width fields can be especially hard to validate on narrow links. Some `D3F2` and `D3F3` blocks include full PCIe capability definitions, while the `D3F4` block in this chunk is incomplete because the requested range ends mid-status-register.

Capability/status fields do not describe access semantics. Conventional PCI status bits, AER status, root error status, hotplug status, BCH ECC status, and link-controller status may be read-only, sticky, write-one-to-clear, reset-on-read, or self-clearing depending on the register. The header gives bit positions only; incorrect clearing policy in callers can lose evidence or fail to acknowledge hardware.

The requested range starts at line 16995 after earlier `D3F2_PCIE_LC_N_FTS_CNTL` fields and ends at line 21114 after `D3F4_STATUS__CAP_LIST__SHIFT`. Adjacent chunks must be reconciled for complete per-register coverage of those boundary registers.

## Test Signals

Useful validation is mostly build- and hardware-oriented:

- Compile AMDGPU configurations that include BIF 5.1 generated headers. Missing or renamed macros should surface as compiler errors in PCIe, power-management, and diagnostics code.
- On supported hardware, verify reported PCIe link generation and width before and after runtime PM, suspend/resume, and explicit retraining. Bad `LC_SPEED_CNTL` or `LC_LINK_WIDTH_CNTL` constants can appear as a link stuck at a lower generation or width.
- Exercise ASPM and low-power transitions and watch for hangs, AER noise, resume failures, or unexpected link resets tied to `PCIE_LC_CNTL*` and training-control fields.
- Validate AER paths by checking uncorrectable/correctable status, root error status, header/TLP-prefix logs, and masks/severity against expected injected or observed events.
- In controlled validation only, use error-injection fields to confirm physical-layer and transaction-layer error reporting paths fire and clear as expected.
- Inspect TX/RX flow-control credit registers, replay counters, expected sequence numbers, and requester IDs during stress traffic to catch field-position errors in credit or transaction-layer macros.
- Test hotplug/PME/power-fault and HPGI status/enables where platform support exists.
- Validate lane-specific equalization and lane-error reporting on x1, x4, x8, and x16 configurations, including lane reversal where available, because copy/prefix mistakes often appear only on particular lane widths.

## Cross-Chunk Notes

This is one slice of a very large generated header. Earlier lines define the beginning of `D3F2_PCIE_LC_N_FTS_CNTL`; later lines complete `D3F4_STATUS` and continue the generated BIF 5.1 mask namespace. The final per-file report should treat `bif_5_1_sh_mask.h` as generated hardware register metadata, not as algorithmic AMDGPU logic, and should merge this chunk with adjacent chunks before drawing conclusions about complete register coverage.
