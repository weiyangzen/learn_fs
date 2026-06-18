# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 92668-94991

## Scope

This chunk is part of a generated AMD NBIO 7.2.0 register shift/mask header. It contains C preprocessor constants only: `__SHIFT` values and pre-shifted `_MASK` values for PCIe/NBIO register fields. There are no functions, structs, control-flow statements, allocations, locks, persistence calls, or direct MMIO accesses in this range.

The requested range starts in the tail of `BIFP2_PCIE_RX_CNTL`, beginning with completion-prefix/PASID/TPH-related receive-control masks, and ends inside `BIFP3_PCIE_LINK_MANAGEMENT_MASK`, after the link-management event mask field values. Adjacent chunks own the beginning of `BIFP2_PCIE_RX_CNTL` and the following `BIFP3_PCIE_LINK_MANAGEMENT_CNTL` fields.

## Purpose

The file gives AMDGPU/NBIO code symbolic names for hardware bit positions and masks. Driver code pairs these macros with register offset definitions, typically from the matching `nbio_7_2_0_offset.h`, to read, decode, or update specific fields in NBIO PCIe port registers without embedding numeric bit constants at call sites.

This chunk covers two closely related hardware surfaces:

- The second half of the `BIFP2` PCIe port directory/control block, mostly receive path, error injection, link control, link training, equalization, power management, straps, performance/debug, clock-gating, and save/restore fields.
- The beginning and middle of the `BIFP3` PCIe port directory/control block, starting at `// addressBlock: nbio_pcie0_bifp3_pciedir_p`, covering port/transaction transmit registers, flow-control accounting, CCIX fields, receive path control, error handling, link control, training, equalization, and link-management status/mask fields.

## Important APIs, Types, And Macros

This chunk exposes macros, not callable APIs or C types. The naming pattern is consistent:

- `BIFP*_REGISTER__FIELD__SHIFT` gives the field's least-significant bit index.
- `BIFP*_REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Register comments such as `//BIFP3_PCIE_RX_CNTL` delimit logical hardware registers.
- `BIFP2` and `BIFP3` prefixes distinguish separate PCIe port instances or blocks with largely repeated layouts.

Important `BIFP2` groups in this range include:

- Receive-path controls: `BIFP2_PCIE_RX_CNTL`, `BIFP2_PCIE_RX_CNTL3`, expected sequence number, vendor-specific receive data/status, and allocated posted/non-posted/completion receive credits.
- Error injection and error status helpers: physical-layer and transaction-layer error injection registers, NAK counters, captured LTR threshold values, private AER surprise-down mask/trigger bits, and BCH ECC controls.
- Link control and training: `BIFP2_PCIE_LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_STATE0` through `LC_STATE5`, and link-management status/mask/control registers.
- Link equalization and high-speed tuning: `LC_CNTL2` through `LC_CNTL12`, bandwidth-change control, CDR/lane controls, forced 8 GT/s coefficients, best equalization settings, force-request coefficients, scheduled RX equalization, ESM controls, 16 GT/s settings, 3x3 coefficient search, preset logic, SRIS/SRNS controls, RX recover, and fine-grain clock-gate overrides.
- Power, ordering, straps, and save/restore: L1 PM substate controls, port order, strap registers, HPGI/private HPGI, host counter descriptor, TX clock performance counters, and `LC_SAVE_RESTORE_1` through `LC_SAVE_RESTORE_3`.

Important `BIFP3` groups in this range include:

- Port and transmit controls: reserved/scratch registers, `PCIEP_PORT_CNTL`, `PCIE_TX_CNTL`, requester ID, vendor-specific transmit fields, request-number controls, sequence/replay counters, ACK latency, NOP DLLP, skid control, and transmit advertised/initial/status credit registers.
- Flow-control and CCIX: FC P/NP/CPL fields, VC1 flow-control mirrors, FCU thresholds, CCIX port controls, CCIX stacked base/limit, and CCIX misc status.
- Receive and error handling: `PCIE_ERR_CNTL`, receive control and PASID/TPH/error ignore bits, expected sequence number, receive vendor fields, receive allocated credits, physical/transaction error injection, NAK counters, captured LTR thresholds, and private AER surprise-down fields.
- Link control and training: `LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_STATE0` through `LC_STATE5`, `LINK_MANAGEMENT_CNTL2`, `LC_CNTL2` through `LC_CNTL7`, bandwidth-change/CDR/lane controls, forced coefficients, best equalization settings, force-request coefficients, SRIS/SRNS, RX recover, ESM, scheduled equalization, and link-management enablement.
- Link-management events: `BIFP3_PCIE_LINK_MANAGEMENT_STATUS` exposes update/failure/status bits for speed, width, partner support, power-down completion, bandwidth, link power state, bandwidth hints, equalization requests, partner ESM requests, low-speed immediate requests, and ESM PLL setup. `BIFP3_PCIE_LINK_MANAGEMENT_MASK` mirrors those bits as interrupt/event masks.

## Control Flow

There is no executable control flow in this chunk. The effective flow is supplied by code that includes this generated header:

1. Driver code selects an NBIO/PCIe register offset from the matching offset header.
2. It reads or writes the register through AMDGPU register-access helpers for the relevant MMIO/config space aperture.
3. It uses the `*_MASK` and `*__SHIFT` macros here to isolate, compose, or test individual hardware fields.
4. Hardware state transitions, posted-write ordering, polling loops, interrupt handling, and clear semantics occur in the caller and in hardware, not in this header.

Because the chunk is a compile-time hardware schema, all sequencing requirements are implicit in the surrounding NBIO/PCIe driver code and the ASIC programming guide.

## State And Persistence Behavior

The header itself owns no state and persists nothing. It describes stateful hardware registers whose values may be strap-derived, firmware-initialized, driver-programmed, volatile status, sticky status, or write-one-to-clear depending on the register.

Stateful surfaces represented by these masks include:

- PCIe receive-path policy bits for unsupported requests, completion timeout handling, PASID/prefix handling, TPH behavior, and receive credit accounting.
- Link training and link-state-machine state, including speed/width changes, FTS counts, ASPM/L1/L23 behavior, reset/link-disable controls, RX detection, and autonomous link-management transitions.
- Equalization state and tuning inputs, including per-rate coefficients, presets, best-measured equalization settings, figure-of-merit fields, request coefficients, ESM fields, and scheduled RX equalization.
- Error and diagnostic state, including injected physical/transaction errors, NAK counters, AER surprise-down controls, BCH ECC, FC/credit counters, captured LTR thresholds, and link-management update/failure status.
- Power-management, clock-gating, strap, HPGI, performance-counter, and save/restore-related hardware configuration.

The macros do not encode access type. Callers must know which fields are read-only, read/write, sticky, clear-on-write, write-one-to-clear, reserved, or only valid in specific link states.

## Dependencies And Integration Points

Primary integration points are:

- The matching NBIO 7.2.0 offset header, which supplies the register addresses corresponding to these field names.
- AMDGPU NBIO, PCIe link-management, power-management, reset, firmware/PSP initialization, error-handling, and debug/diagnostic code that includes ASIC-specific register headers.
- Linux PCIe concepts mirrored in the hardware fields: transaction layer credits, DLLP/TLP errors, completion timeouts, AER-like reporting, ASPM/L1 substates, LTR, PASID/prefix handling, flow control, lane equalization, lane width/speed negotiation, and interrupt/event masking.
- Generated register-header infrastructure shared across AMD ASIC revisions. Similar prefix and field patterns are expected in neighboring NBIO revisions and in companion offset headers.

The chunk has a structural boundary at `// addressBlock: nbio_pcie0_bifp3_pciedir_p`. Callers must use masks with offsets from the same logical block. Mixing `BIFP2` masks with `BIFP3` offsets is only safe when the hardware documentation explicitly guarantees identical field layout and the caller intentionally targets that port.

## Risks

- Incorrect shift or mask constants can corrupt adjacent hardware bits during read-modify-write operations.
- Many fields affect PCIe link bring-up, retraining, ASPM/L1 behavior, equalization, ESM, SRIS/SRNS, and RX recovery. Bad writes can produce intermittent link failures or performance regressions rather than obvious compile-time errors.
- Error/status fields may be sticky or write-one-to-clear. Treating masks as ordinary read/write fields can lose diagnostics, fail to clear interrupts, or accidentally acknowledge events.
- The range begins and ends mid-register group. Automated analysis that treats this chunk as complete ownership of `BIFP2_PCIE_RX_CNTL` or `BIFP3_PCIE_LINK_MANAGEMENT_MASK` can miss sibling fields in adjacent chunks.
- `BIFP2` and `BIFP3` contain many visually similar repeated register groups. Copying a mask from the wrong prefix or lane/rate group can silently target the wrong port or field.
- Several masks cover private, debug, strap, save/restore, error-injection, and clock-gating controls. These are sensitive integration points and should not be programmed casually outside documented initialization, diagnostics, or validation flows.

## Test Signals

Useful validation signals for changes involving this chunk:

- Build coverage: AMDGPU/NBIO code including this header compiles without duplicate macro definitions, missing macro names, or preprocessor syntax errors.
- Static consistency: each visible `__SHIFT` has the expected companion `_MASK`; masks align with their shifts and field widths; repeated BIFP2/BIFP3 groups stay structurally consistent.
- Offset/header consistency: register names and block prefixes match the corresponding address definitions in `nbio_7_2_0_offset.h`.
- Register-dump decoding: decoded field names, bit positions, and masks match vendor register documentation or known-good NBIO 7.2.0 dumps.
- Runtime PCIe signals: link speed/width negotiation, equalization completion, ASPM/L1 transitions, SRIS/SRNS behavior, RX recovery, LTR capture, flow-control counters, and link-management event reporting behave as expected on supported hardware.
- Error-path signals: injected physical/transaction errors, NAK counters, completion-timeout behavior, AER surprise-down events, and link-management masks/status bits are decoded and cleared correctly by diagnostics.
