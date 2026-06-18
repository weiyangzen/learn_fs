# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 106479-108785

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains 2,188 `#define` field-layout macros and 117 register/address-block comments. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts at the tail of `BIFP3_1_PCIEP_NAK_COUNTER`, covers the `BIFP3_1` PCIe link-control and transaction/flow-control layout through `BIFP3_1_PCIE_FC_CPL_VC1`, then begins the next generated address block, `nbio_pcie1_bifp4_pciedir_p`, covering `BIFP4_1` PCIe port, RX/error-injection, NAK-counter, and link-control layouts. It ends after the first four `SHIFT` definitions for `BIFP4_1_PCIE_LC_CNTL8`, so the following chunk is required for that register's remaining shifts and masks.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO register interface. Every field is represented by a pair of preprocessor constants:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position for extracting or encoding the field.
- `<REGISTER>__<FIELD>_MASK`, the already-shifted register mask for isolating or preserving the field.

This chunk describes PCIe/BIF pipe instances `BIFP3_1` and `BIFP4_1`. The `BIFP3_1` section is mostly link-control and transmit/flow-control metadata: link training, link width, speed negotiation, FTS counts, link state snapshots, bandwidth-change controls, CDR/lane controls, equalization coefficients, fine-grain clock gating overrides, save/restore controls, L1 PM substate controls, link management event masks, strap-derived link/misc settings, BCH ECC controls, transmit sequence/replay/ACK latency settings, advertised and initialized credits, current credit status, and VC0/VC1 flow-control counters. The `BIFP4_1` section repeats the same generated pattern for another PCIe port instance, beginning with port/requester/lane status and RX/error-injection controls before entering its link-control families.

## Important Macro Families

The `BIFP3_1` link-control families cover:

- `PCIE_LC_CNTL`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_N_FTS_CNTL`, and `PCIE_LC_SPEED_CNTL`: link reset, L0s/L1/L23 behavior, power-state handling, training-state controls, reconfiguration and renegotiation controls, lane power-state handling, advertised/current data rates, target-link speed controls, speed-change attempts, and Gen2/Gen3/Gen4/Gen5 strap-derived capability bits.
- `PCIE_LC_STATE0` through `PCIE_LC_STATE5`: hardware-observed link state, lane counts, lane reversals, receive/deskew/electrical-idle state, equalization state, power-management state, and other link-training diagnostics.
- `PCIE_LC_CNTL2` through `PCIE_LC_CNTL12`: electrical-idle filtering, safe-mode or recovery behavior, compliance controls, alternate protocol and ESM-related controls, link-management event behavior, PLL and receiver-detection handling, retimer/equalization support, clock-gating overrides, lane masks, loopback/equalization controls, and other timing or workaround bits.
- `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_LINK_MANAGEMENT_MASK`, and save/restore registers: link-speed/width event notification masks, software-visible link-management event masking, equalization setting persistence, and restore-needed signaling.

The `BIFP3_1` power, strap, and reliability families cover:

- `PCIE_LC_L1_PM_SUBSTATE` through `PCIE_LC_L1_PM_SUBSTATE5`: L1.1/L1.2 override bits, CLKREQ filtering, `T_POWER_ON` scaling/value fields, FCH target-address fields, LTR thresholds, CM restore timing, powerdown/defer/abort controls, and reference-clock/electrical-idle behaviors around L1 substates.
- `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, and `PCIEP_STRAP_LC2`: strap-derived FTS/TS counts, skip interval, receiver-detect bypass, compliance disable/force, lane reversal and negotiation straps, software-controlled margining, RTM presence detection, automatic speed-negotiation disables, ESM mode/reach/recalibration/calibration-time straps, and miscellaneous features such as end-to-end prefix, extended format, OBFF, LTR, and CCIX.
- `PCIEP_BCH_ECC_CNTL`: BCH ECC enable, error threshold, and status fields for this PCIe block.

The `BIFP3_1` transmit and flow-control families cover:

- `PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, and `PCIE_TX_ACK_LATENCY_LIMIT`: transmit sequence number, replay-buffer sequence state, replay pointer and rollover status, latency-limit fields, and ACK/NACK enable or timeout controls.
- `PCIE_TX_CREDITS_FCU_THRESHOLD`, `PCIE_TX_CREDITS_ADVT_*`, `PCIE_TX_CREDITS_INIT_*`, and `PCIE_TX_CREDITS_STATUS`: posted, non-posted, and completion header/data credits, advertised/init credit values, infinite-credit indicators, and credit status counters.
- `PCIE_TX_VENDOR_SPECIFIC`, `PCIE_TX_NOP_DLLP`, and `PCIE_TX_REQUEST_NUM_CNTL`: vendor-specific DLLP payloads, NOP DLLP generation, and request-number policy.
- `PCIE_FC_P`, `PCIE_FC_NP`, `PCIE_FC_CPL`, and their `_VC1` variants: flow-control counter layouts for posted, non-posted, and completion traffic across virtual channels.

The `BIFP4_1` families in this chunk cover:

- Port metadata: `PCIEP_RESERVED`, `PCIEP_SCRATCH`, `PCIEP_PORT_CNTL`, `PCIE_TX_REQUESTER_ID`, and `PCIE_P_PORT_LANE_STATUS`, including scratch/reserved storage, port-level controls, requester ID fields, and per-lane status.
- Error and RX controls: `PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_VENDOR_SPECIFIC`, `PCIE_RX_CNTL3`, `PCIE_RX_CREDITS_ALLOCATED_*`, `PCIEP_ERROR_INJECT_PHYSICAL`, `PCIEP_ERROR_INJECT_TRANSACTION`, and `PCIEP_NAK_COUNTER`. These define CRC/parity/reporting controls, RX flow behavior, expected sequence numbers, received credit allocations, physical/transaction-layer error injection knobs, and NAK received/generated counters.
- Link-control and power-management registers matching the `BIFP3_1` pattern through `PCIE_LC_L1_PM_SUBSTATE5` and `PCIEP_BCH_ECC_CNTL`. The range then begins `PCIE_LC_CNTL8` with FOM time, equalization search traversal, lock-in response, and the first ESM rate timer field.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The macros are untyped integer literals, usually with an `L` suffix, and encode only bit positions and bit masks.

These definitions do not include register addresses, reset values, access permissions, write-one-to-clear behavior, polling sequences, or side-effect rules. Consumers must combine them with sibling generated NBIO address/default headers and the AMDGPU register helpers used by the surrounding driver, such as field extraction/composition helpers and SOC15/NBIO read-modify-write accessors.

## Control Flow

This header has no local runtime control flow. Runtime flow is supplied by AMDGPU code that includes the generated NBIO headers:

1. Driver code selects a `BIFP3_1_*` or `BIFP4_1_*` register address from sibling generated metadata.
2. It reads a register, decodes fields with these `__SHIFT` and `_MASK` constants, or composes a write value while preserving unrelated bits.
3. The decoded or programmed values participate in PCIe link bring-up, link speed/width management, equalization, ASPM/L1 substate policy, error reporting, NAK/error diagnostics, transmit credit accounting, flow-control handling, suspend/resume save/restore, or board bring-up debug.

The field names imply asynchronous hardware flows outside this header: link training and retraining, speed-change attempts, bandwidth-change notifications, lane reversal and reconfiguration, L0s/L1/L23 entry and exit, L1.1/L1.2 entry and wake, FTS and TS exchange, error injection and capture, replay and NAK handling, equalization searches, loopback tests, BCH ECC status updates, and credit updates for posted/non-posted/completion traffic.

## State And Persistence Behavior

The header owns no state and persists nothing. It names hardware-visible state in NBIO PCIe registers. The actual state is owned by the GPU's PCIe/NBIO block and is affected by BIOS or firmware initialization, strap sampling, PCIe reset, GPU reset, link retraining, power-state transitions, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable controls, strap-derived capability fields, advertised link settings, current link and lane status, event masks, error masks/status, error-injection enables, NAK counters, transmit replay and ACK latency controls, credit advertisement/init/status counters, L1 substate timing and address settings, saved equalization settings, restore-needed status, clock-gating override bits, and BCH ECC threshold/status fields. Some fields are live status; others may be sticky, write-one-to-clear, write-trigger, or temporarily valid only during a link-management sequence, but those semantics are not encoded in the shift/mask file.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.7.0 register database and must stay synchronized with sibling generated headers:

- `nbio_7_7_0_offset.h` and/or `nbio_7_7_0_smn.h` provide register address metadata for the same `BIFP3_1` and `BIFP4_1` register names.
- `nbio_7_7_0_default.h` provides reset/default values where generated.
- AMDGPU SOC15/NBIO/PCIe helper code provides the actual register read, write, and read-modify-write paths.

Integration points include PCIe link initialization, dynamic link speed and width changes, ASPM and L1 PM substate policy, high-speed equalization and loopback diagnostics, lane reversal/reconfiguration, transmit replay and credit management, RX credit accounting, AER-like error monitoring, error injection tests, NAK counter diagnostics, BCH ECC threshold/status handling, suspend/resume save/restore, GPU reset recovery, and low-level debug or validation tools that dump NBIO PCIe state.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing callers to read or write the wrong PCIe field. Symptoms may be link-training failures, incorrect speed/width negotiation, broken ASPM/L1 behavior, missed link-management events, incorrect error injection, or misleading diagnostics.
- The chunk starts after the beginning of `BIFP3_1_PCIEP_NAK_COUNTER` and ends in the middle of `BIFP4_1_PCIE_LC_CNTL8`; merge/reconciliation must join adjacent chunks before treating either boundary register as complete.
- Link control and equalization fields are timing-sensitive. Writes generally need ordered sequences, delay/polling loops, and timeout handling that are not visible in this header.
- L1 PM substate fields include timing values, FCH target address pieces, CLKREQ handling, and electrical-idle behavior. Incorrect programming can break low-power entry/exit, suspend/resume, or wake behavior.
- Error-injection fields should only be used in controlled diagnostics. Accidentally enabling physical-layer or transaction-layer injection can create real PCIe errors and destabilize the device.
- Status, counter, replay, NAK, and ECC fields may be live or sticky. Read/clear ordering and rollover behavior must be understood from hardware documentation and call-site conventions.
- Transmit credit and flow-control fields affect PCIe data movement. Incorrect writes can cause throughput collapse, stalls, protocol errors, or virtual-channel-specific failures.
- Many register families are mechanically repeated across `BIFP3_1` and `BIFP4_1`; a single lane, virtual-channel, or port-instance typo in generated data may affect only one topology path and be hard to catch with generic boot tests.
- Writers must preserve reserved and unrelated fields unless hardware documentation explicitly permits a full-register overwrite.

## Test Signals

- Build AMDGPU with NBIO 7.7.0 support enabled. Compile-time coverage catches missing or renamed symbols consumed by driver code.
- Run generated-header consistency checks: every field should have compatible `__SHIFT` and `_MASK` values, masks should fit a 32-bit register, repeated `BIFP3_1`/`BIFP4_1` register families should align where the hardware block is cloned, and repeated posted/non-posted/completion or VC0/VC1 credit fields should follow the same layout pattern.
- Cross-check each register name in this chunk against sibling address/default headers so field layouts map to known registers and expected reset values.
- On supported hardware, validate PCIe enumeration, negotiated speed and width, link retraining, ASPM/L1 substate entry and exit, suspend/resume, GPU reset recovery, and any board-specific lane reversal or width reconfiguration.
- Exercise diagnostics that read link state, NAK counters, replay state, ACK latency, RX/TX credits, BCH ECC status, and link-management masks, confirming decoded values match hardware traces or firmware expectations.
- For error-injection users, run controlled physical-layer and transaction-layer injection tests and confirm expected status bits, counters, interrupts, recovery behavior, and clean disable/restore sequencing.
- For any code that writes these fields, inspect register traces for correct read-modify-write preservation, correct use of masks and shifts, and no writes to adjacent fields when manipulating link, credit, power, or error controls.
