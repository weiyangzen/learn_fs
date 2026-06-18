# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 68540-70871

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It defines C preprocessor constants for bit positions and masks used to access PCIe BIF port register fields in the `nbio_pcie0` register space. The content is data-like hardware description, not executable code: every declaration is a `#define` for a `__SHIFT` or `_MASK` constant.

The line range starts inside the `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` register, continues through the rest of the BIFP2 PCIe link-controller and port-management registers, covers the complete `addressBlock: nbio_pcie0_bifp3_pciedir_p`, and begins `addressBlock: nbio_pcie0_bifp4_pciedir_p` through the physical error-injection masks. These macros are consumed by driver code that pairs shift/mask constants from this header with register-offset constants from companion generated headers and AMDGPU register access helpers.

## Register Areas Covered

The BIFP2 section begins with physical-layer error injection fields for lane, framing, SKP parity/LFSR, loopback underflow/overflow, deskew, 8b/10b disparity/decode, SKP ordered-set, invalid OS identifier, and bad sync header faults. It then defines transaction-layer error injection fields for flow-control errors, replay-number rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout. This is followed by NAK counters and captured LTR threshold/status fields.

Most of the BIFP2 body describes link-controller controls and status: `PCIE_LC_CNTL`, training control, link width control, FTS count, speed control, LC state registers 0 through 5, link-management status/mask/control, bandwidth-change controls, CDR and lane controls, LC control extensions 2 through 7, equalization coefficient forcing/best-settings registers, strap fields, L1 PM substates, port order, BCH ECC, HPGI/private HPGI state, descriptor count, and TX clock performance counting.

The BIFP3 address block is a full repeated port block. It starts at `nbio_pcie0_bifp3_pciedir_p` and covers reserved/scratch/port control, TX controls and requester/vendor-specific fields, request numbering, sequence/replay/ack-latency registers, advertised/initial/current TX credit registers, lane status, flow-control credit visibility, PCIe error control, RX controls, expected sequence number, vendor-specific RX fields, RX control 3, allocated RX credits, physical and transaction error injection, NAK counters, captured LTR, link-controller controls/status, strap fields, L1 substates, HPGI, descriptors, and TX clock performance counting.

The BIFP4 section starts another repeated port block. In this chunk it includes reserved/scratch/port control, TX control/requester/vendor/request-number/sequence/replay/ack-latency fields, TX credit advertise/init/status/FCU thresholds, port lane status, FC P/NP/CPL fields, PCIe error control, RX controls, expected sequence number, vendor-specific RX fields, RX control 3, allocated RX credits, and the beginning of physical error injection. Later BIFP4 link-controller and management registers are outside this chunk.

## Important APIs, Types, And Constants

There are no functions, structs, enums, callbacks, or runtime APIs in this range. The exported interface is the macro naming convention:

- `BIFP{N}_<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `BIFP{N}_<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit register mask for that field.
- `BIFP2`, `BIFP3`, and `BIFP4` identify repeated PCIe BIF port instances. The field layouts are intentionally very similar across ports, but the macro prefixes bind each definition to a distinct hardware register instance.

Important field families in this chunk include link training and power-management controls (`LC_TRAINING_CNTL`, `LC_POWER_STATE`, L0s/L1/L23 entry and wake controls), link width and reconfiguration controls (`LC_LINK_WIDTH`, `LC_RECONFIG_NOW`, upconfigure/renegotiate controls, lane power state), link speed controls (`LC_GEN2_EN_STRAP`, `LC_GEN3_EN_STRAP`, target speed override, software/hardware speed-change forcing, current data rate, advertised data rate), interrupt-style link-management status/mask bits, and bandwidth hint/control fields.

The TX/RX credit and flow-control fields expose advertised, initialized, allocated, and current/error credit state for posted, non-posted, and completion classes. The error-control fields include reporting disable, ECRC/LCRC generation or drop behavior, AER header-log timeout, slave-buffer halt status/reset, and immediate error-message sending. The RX controls include ignore bits for multiple TLP/config/completion/error classes, NAK-on-FIFO-full, one-shot NAK generation, flow-control initialization from registers, completion timeout controls, PASID/prefix error ignore controls, TPH disable, and FLR timeout disable.

## Control Flow

This chunk has no direct control flow. It participates in control flow only through code that performs register read/modify/write operations. A typical consumer reads a 32-bit NBIO register, clears a field with `~*_MASK`, inserts the shifted field value with `(value << *_SHIFT) & *_MASK`, and writes the result back through AMDGPU's MMIO or indexed-register access path.

The file ordering follows the generated hardware register map, not program execution order. Within each register group, `__SHIFT` constants appear before corresponding `_MASK` constants. BIFP3 repeats the same conceptual sequence as surrounding BIF port blocks, while BIFP2 and BIFP4 are partial in this chunk because the chunk boundaries fall inside their generated address-block coverage.

## State And Persistence Behavior

The header itself contains no mutable software state and persists nothing. The described state lives in NBIO PCIe hardware registers. Some fields are software-programmed controls, including reset/link-training controls, speed/width renegotiation controls, ASPM and L1 substate controls, error reporting masks, RX ignore behavior, MSI-like interrupt/status masking for link-management events, and error injection controls. Other fields are hardware-owned status or counters, including LC state fields, NAK counters, link-management status, current data rate, lane status, credit status, expected sequence number, and captured LTR thresholds.

Persistence and side effects are hardware-defined. Many status bits may be latched, write-one-to-clear, self-clearing, strap-derived, or reset by link state transitions. The shift/mask macros do not encode access type, reset value, volatility, self-clear behavior, or sequencing requirements. Any driver write path using these constants must preserve unrelated/reserved bits unless companion register documentation explicitly permits a full-register write.

## Dependencies And Integration Points

This header is one generated member of the AMDGPU ASIC register interface. Register address headers provide offsets, this `*_sh_mask.h` header provides bit layouts, and driver C code supplies access primitives, synchronization, and hardware sequencing. The chunk integrates with AMDGPU NBIO, PCIe link management, GPU reset and recovery, runtime power management, error handling, and ASIC bring-up or diagnostics code.

The field names map closely to PCIe concepts: link training state machine, ASPM/L1 substates, lane width negotiation, Gen2/Gen3 speed negotiation, flow-control credits, DLLP/TLP replay/NAK behavior, completion timeouts, ECRC/LCRC handling, latency tolerance reporting, and physical/transaction-layer error injection. Because the macros are port-specific, consumers must select the correct BIFP instance for the physical port or virtualized topology being inspected or programmed.

## Risks And Edge Cases

The main risk is register-map drift. A wrong shift or mask in this generated header can silently program the wrong hardware bit, clear adjacent status, disable error reporting, force unsafe link retraining, or misdecode link/credit/error telemetry. Repeated BIFP blocks increase review difficulty because near-identical definitions are expected, but an incorrect prefix or copied field can still target the wrong port.

Chunk boundaries are material for later merge work. This range starts after the `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` comment and begins with its remaining field definitions; the earlier BIFP2 registers are in previous chunks. Conversely, this range ends before completing BIFP4 physical error injection and before BIFP4 transaction error injection, link-controller, strap, L1 substate, and HPGI definitions. File-level conclusions about all BIF ports must reconcile adjacent chunk reports.

Error-injection and error-control fields are especially sensitive. Test or diagnostic code that writes the `ERROR_INJECT_*`, LCRC/ECRC generation, RX ignore, or reporting-disable bits can mask real PCIe problems or intentionally create link faults. These paths should be guarded by debug/validation-only policy and sequenced with recovery handling. Credit, sequence, NAK, and link-management status fields should also be treated as volatile hardware state, so stale snapshots can mislead diagnostics.

## Test Signals

There are no unit tests in this header. Useful validation signals are build, static, and hardware-facing:

- Full kernel or AMDGPU builds catch malformed macro names, missing companion definitions, or syntax regressions.
- Generated-header diffs should be compared against the authoritative NBIO 7.0 register database, especially across BIFP2/BIFP3/BIFP4 repetition and this chunk's partial boundaries.
- Register dumps decoded with these masks should match expected link width, speed, LC state, LTR, credit, NAK, and error-control state on known boards.
- Link retraining, ASPM/L1 substate, reset/recovery, and runtime-power tests can reveal incorrect control masks through failed transitions or unexpected link-down behavior.
- PCIe AER/error-injection validation can exercise transaction/physical error-injection, RX ignore, ECRC/LCRC, completion-timeout, and reporting-disable fields, while checking that recovery and telemetry decode the intended bits.
