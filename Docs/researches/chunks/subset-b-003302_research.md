# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 104156-106478

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains 2,181 `#define` field-layout macros and 138 register or address-block comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the middle of `BIFP1_1_PCIE_LC_L1_PM_SUBSTATE`, after the corresponding shift macros and early masks were emitted in the previous chunk. It then covers the remainder of the `BIFP1_1` PCIe link-control and transmit/flow-control directory fields, a complete cloned `addressBlock: nbio_pcie1_bifp2_pciedir_p` register-field block for `BIFP2_1`, and the beginning of `addressBlock: nbio_pcie1_bifp3_pciedir_p` through `BIFP3_1_PCIEP_ERROR_INJECT_TRANSACTION`. The final line is only the `BIFP3_1_PCIEP_NAK_COUNTER` comment; the counter field macros begin on the next line outside this chunk.

Although the source tree path is under a `ceph-client` mirror, this file is AMDGPU hardware metadata. It has no direct distributed-filesystem logic.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.7.0 register interface. For each hardware register field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit used to encode or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the already-shifted register mask used to isolate or preserve that field.

This chunk describes PCIe BIF port-directory fields for NBIO PCIe instance 1. The dominant theme is low-level PCIe port behavior: LTSSM/link training, negotiated width and speed, ASPM/L1 substate handling, reference-clock request policy, receiver/transmitter error handling, retry/NAK and credit accounting, equalization coefficients and presets for 8/16/32 GT/s paths, loopback and margin-style diagnostics, save/restore handshakes, and strap-derived capability configuration.

## Important Macro Families

The `BIFP1_1` tail starts with the remaining L1 PM substate masks, including L1.1/L1.2 abort/defer behavior, wake and power-gate exit controls, auxiliary reference-clock counter handling, restore timing, LTR threshold fields, FCH target address/delay fields, and L1SS electrical-idle handling. It then covers high-speed link-control fields (`LC_CNTL8` through `LC_CNTL12`), save/restore fields, 16 GT/s and 32 GT/s force/equalization coefficient controls, fine-grain link clock-gate overrides, transmitter sequence/replay controls, ACK latency limits, credit FCU thresholds, TX vendor/NOP/request-number controls, advertised and initial posted/non-posted/completion credits, TX credit status, and posted/non-posted/completion flow-control counters for VC0 and VC1.

The `BIFP2_1` block is the complete repeated PCIe port-directory layout for another BIF port. It includes:

- Basic per-port controls: reserved/scratch storage, `PCIEP_PORT_CNTL`, requester ID bus/device/function and validation fields, physical lane status, error-control policy, receiver-control policy, expected sequence number, RX vendor data/status, RX PASID/atomic/poison handling, allocated RX credits, physical and transaction error injection controls, and NAK counters.
- Link-control state machine programming: `PCIE_LC_CNTL`, training control, link-width control, N_FTS programming, speed control, six link-state registers, bandwidth-change controls, CDR and lane controls, and `LC_CNTL2` through `LC_CNTL7`. These fields cover lane reversal, active lane selection, receiver detect, link number, hold-training states, poll/config/defer/recovery masks, speed-change commands, failed-speed counters, auto-speed negotiation, deskew/EIEOS behavior, TS1/TS2 and SKP handling, FTS counts, ESM/Gen3+ equalization handling, and dynamic lane/power transitions.
- Equalization and high-rate controls: forced coefficient fields, best equalization settings, equalization-request coefficient fields, acceptable presets, loopback equalization, 16 GT/s and 32 GT/s coefficient forcing, no-equalization-needed or bypass-to-high-rate negotiation, transmitter precoding request/status, link safe-recover controls, phase timing controls, and live deskew/recovery options.
- Power-management and straps: link-management masks for L0/L0s/L1/L2/L3 and recovery paths, strap LC and miscellaneous capability fields, L1 PM substate controls and timing, reference-clock request/deassertion policy, L1SS powerdown behavior, common-mode restore timing, and BCH ECC control/status.
- Transmit and flow-control accounting: TX sequence and replay numbers, ACK latency timers, FCU threshold controls, vendor/NOP DLLP fields, request-number controls, advertised and initial credit counts for posted/non-posted/completion traffic, current credit-status counters, and VC0/VC1 flow-control posted/non-posted/completion counters.

The `BIFP3_1` start repeats the same generated pattern for the next port instance, but this chunk only includes the early portion: reserved/scratch, port control, requester ID, lane status, error control, receiver control, expected sequence number, vendor-specific RX data, RX control 3, RX allocated credit counters, and physical/transaction error injection masks. The `BIFP3_1_PCIEP_NAK_COUNTER` field definitions are outside this range.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are preprocessor integer literals, mostly with an `L` suffix, and describe bit geometry only.

The macros must be paired with generated address metadata from `nbio_7_7_0_offset.h`; for example, the sibling offset header maps `regBIFP2_1_PCIE_RX_CNTL`, `regBIFP2_1_PCIE_LC_CNTL*`, and `regBIFP3_1_PCIEP_NAK_COUNTER` to NBIO register offsets and base indices. Runtime code is expected to consume these definitions through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the appropriate NBIO/PCIe indirect accessors.

This header does not define register addresses, reset values, access permissions, write-one-to-clear behavior, sequencing constraints, or ownership rules.

## Control Flow

This chunk has no local runtime control flow. Runtime flow is supplied by AMDGPU code that includes the generated NBIO headers:

1. The driver selects a `BIFP1_1`, `BIFP2_1`, or `BIFP3_1` register address from sibling generated metadata.
2. It reads a register and extracts fields with the `__SHIFT` and `_MASK` macros, or composes a write value while preserving unrelated and reserved bits.
3. The decoded or programmed values affect PCIe link bring-up, speed/width negotiation, ASPM and L1 substate policy, clock request behavior, error reporting, credit flow control, equalization, loopback, diagnostics, suspend/resume restore, or reset recovery.

The field names imply several asynchronous hardware flows outside the header: LTSSM transitions, receiver detect, link disable/retrain, autonomous speed change, bandwidth-change interrupts, equalization phases, lane reversal and lane-off changes, reference-clock request/acknowledge handshakes, L1.1/L1.2 entry/exit timing, safe-recover flows, replay and NAK handling, credit updates, and injected or real physical/transaction errors.

## State And Persistence Behavior

The header owns no state and persists nothing. It names hardware-visible state in NBIO PCIe port-directory registers. Persistence is controlled by GPU reset domains, PCIe resets, firmware or BIOS initialization, link retraining, power-management transitions, suspend/resume restore paths, and explicit AMDGPU writes.

Represented state includes writable control bits, strap-derived capabilities, live link-state encodings, status latches, counters, credit accounting fields, sequence/replay numbers, error masks and injection selectors, advertised capabilities, L1SS timing/policy fields, equalization coefficients, per-rate preset selection, save/restore handshake controls, and clock-gating overrides. Many of these fields are not ordinary software variables: they may be read-only hardware status, write-one-to-clear latches, sticky debug state, strap sampled values, or fields with side effects when written.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.7.0 register database and must remain synchronized with sibling generated headers:

- `nbio_7_7_0_offset.h` provides register offsets and base indices for the same `BIFP*` register names.
- Other NBIO generation families in this directory provide comparable layouts for related ASIC revisions, but consumers must not mix revisions.
- AMDGPU SOC15/NBIO/PCIe helper code provides the actual read, modify, write, polling, reset, and debug paths that use these shifts and masks.

Integration points include PCIe port initialization, requester ID programming, GPU PCIe link training, Gen speed negotiation, width and lane-management policy, ASPM/L1SS power management, reference-clock request handling, link bandwidth management, error logging and injection, AER-adjacent debugging, credit-flow diagnostics, loopback tests, equalization tuning, suspend/resume save/restore, and GPU reset recovery. The repeated `BIFP1_1`, `BIFP2_1`, and `BIFP3_1` prefixes show that this metadata is cloned per PCIe BIF port; code that selects a port instance must pair the right address macro with the matching field macro prefix.

## Risks And Edge Cases

- The range begins and ends mid-register-family. Whole-file reconciliation must merge the prior `BIFP1_1_PCIE_LC_L1_PM_SUBSTATE` fields and the following `BIFP3_1_PCIEP_NAK_COUNTER` fields before treating either register as complete.
- Generated shift/mask drift can compile cleanly while causing the driver to read or write the wrong PCIe control bit. Effects can include failed link training, wrong negotiated speed or width, broken L1SS behavior, missed error status, invalid credit accounting, or unstable equalization.
- The port instances are mechanically repeated. Accidentally combining a `regBIFP2_1_*` address with a `BIFP1_1_*` or `BIFP3_1_*` field macro may produce plausible-looking but incorrect register operations.
- Link training, equalization, safe-recover, loopback, and speed-change fields are timing-sensitive. Writes generally need ordered sequencing, polling, and timeout behavior that this shift/mask file cannot express.
- Error injection fields can intentionally corrupt physical- or transaction-layer behavior. They should be confined to controlled diagnostics and must not leak into normal runtime initialization.
- RX ignore/error-mask controls can suppress protocol errors, unsupported requests, poisoned traffic, PASID errors, completion timeout signaling, or DPC-style triggers. Incorrect policy can hide real faults.
- L1SS and reference-clock controls interact with platform firmware, board wiring, CLKREQ#/REFCLK behavior, and remote endpoint support. Incorrect settings can cause hangs during idle entry/exit or resume.
- Credit and flow-control fields are narrow counters split by posted, non-posted, completion, and VC class. Misinterpreting units or fields can lead to false diagnostics rather than direct software-visible memory corruption.
- Many fields likely include reserved or hardware-owned bits adjacent to writable controls. Consumers should use read/modify/write preservation unless hardware documentation explicitly allows full-register writes.

## Test Signals

- Build AMDGPU with NBIO 7.7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: each `__SHIFT` should have a compatible `_MASK`, masks should fit a 32-bit register field, and repeated `BIFP1_1`/`BIFP2_1`/`BIFP3_1` families should match except where the chunk boundary intentionally truncates a family.
- Cross-check every register family in this chunk against `nbio_7_7_0_offset.h` so each field layout maps to a known register offset and base index.
- On supported hardware, validate PCIe enumeration, requester ID behavior, negotiated link speed and width, retrain/link-disable flows, autonomous speed changes, bandwidth-change status, ASPM and L1.1/L1.2 entry/exit, CLKREQ#/REFCLK behavior, suspend/resume, and GPU reset recovery.
- Exercise error paths with controlled injection or fault observation: physical-layer errors, transaction-layer errors, NAK/replay behavior, receiver ignore policy, completion timeouts, poisoned traffic, PASID/atomic handling, and status clear behavior.
- For equalization and high-speed diagnostics, compare 8/16/32 GT/s preset/coefficient programming, bypass/no-equalization-needed negotiation, transmitter precoding state, loopback equalization status, and safe-recover completion against firmware or board expectations.
- For any code writing these fields, inspect register traces to confirm correct address/prefix pairing, read/modify/write preservation of unrelated bits, and restoration of temporary debug or clock-gating overrides.
