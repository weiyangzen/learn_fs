# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 70872-73204

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It contains C preprocessor constants only: `#define` names ending in `__SHIFT` or `_MASK` that describe bit positions and bit masks for NBIO PCIe/BIF port registers. There are no functions, structs, enums, branches, allocation sites, or runtime side effects in this range.

The requested range starts inside the tail of `BIFP4_PCIEP_ERROR_INJECT_PHYSICAL`, then covers the rest of the BIFP4 PCIe port register field map. It fully covers the `nbio_pcie0_bifp5_pciedir_p` address block and begins the `nbio_pcie0_bifp6_pciedir_p` address block, ending partway through `BIFP6_PCIEP_ERROR_INJECT_TRANSACTION`. In total, the range contains 2,182 `#define` entries grouped by 147 comment markers.

The purpose of these definitions is to let NBIO, PCIe, and diagnostics code manipulate hardware registers by symbolic field names instead of hard-coded bit arithmetic. The companion NBIO offset/SMN headers provide register addresses; this `*_sh_mask.h` file provides the field layout needed by helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`.

## Register Areas Covered

The BIFP4 portion continues the physical-layer error injection register and then covers transaction-layer error injection, NAK counters, captured LTR control/status and threshold values, link-control registers, link-training controls, lane-width controls, speed controls, link-state status registers, link-management status/mask/control registers, strap registers, L1 power-management substate controls, BCH ECC controls, HPGI controls, descriptor fields, and a TXCLK performance counter control.

The BIFP5 block is complete for this slice. It starts with reserved/scratch and port-control registers, then covers TX request control, requester ID, vendor-specific fields, request-number and replay/sequence tracking, advertised and initial flow-control credits, credit status and FCU thresholds, port lane status, posted/non-posted/completion flow-control credit registers, error control, RX control, expected sequence number, RX vendor-specific data/status, RX control 3, allocated RX credits, physical and transaction error injection, NAK counters, LTR capture, link-control/training/width/speed/state registers, link-management status/mask/control, strap and L1 PM substate controls, BCH ECC, HPGI, descriptor, and TXCLK perf count control.

The BIFP6 block begins another structurally similar PCIe port instance. This chunk covers BIFP6 reserved/scratch, port control, TX/RX flow-control and request handling, error control, allocated RX credits, physical-layer error injection, and the first half of transaction-layer error-injection shifts through `ERROR_INJECT_TL_UNEXPECTED_CMPLT`. The remaining BIFP6 transaction masks and later BIFP6 link-control/link-management fields fall outside this chunk and must be reconciled by adjacent chunk research.

## Important APIs, Types, And Constants

This file exposes macros rather than C APIs. The externally visible contract is the generated naming convention:

- `BIFP{4,5,6}_<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `BIFP{4,5,6}_<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for the same field.
- `BIFP4`, `BIFP5`, and `BIFP6` identify separate PCIe/BIF port instances. Repeated register names intentionally describe separate hardware blocks, not duplicate software symbols.

Important field families in this range include:

- Error injection: physical-layer lane, framing, SKP parity/LFSR, loopback underflow/overflow, deskew, 8b/10b disparity/decode, SKP ordered-set, invalid ordered-set identifier, and bad sync-header injection; transaction-layer flow-control, replay rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion-timeout injection.
- Link control and training: `LC_RESET_LINK`, L0s/L1 inactivity timers, L1/L23 entry/exit behavior, ASPM/PMI interactions, receiver-idle gating, training control state, compliance receive, speed-change initiation, autonomous change/upconfigure disable, hardware link-disable state, and recovery/equalization timing knobs.
- Link width and speed: negotiated/read link width, reconfiguration triggers, renegotiation/upconfiguration support, dynamic lane power state, lane reversal/equalization handling, target link speed, speed-change attempt counters, equalization phase timers, degraded-link handling, Gen2/Gen3 training flags, and EIEOS/EQ behavior.
- Link state and management: six `LC_STATE*` registers for internal state readback, link-management interrupt/status/mask/control fields for hot reset, speed change, link bandwidth notifications, lane-width changes, link-autonomous bandwidth state, link-disable events, and EQ request/complete states.
- Flow control and credits: TX advertised/init credits for posted, non-posted, and completion traffic, credit-consumed/limit/status fields, FCU thresholds, RX allocated credits, and per-class flow-control credit readbacks.
- RX/TX control: requester ID fields, request counters, replay sequence, ACK latency, RX ignore controls for PCIe protocol errors, RCB completion/FLR timeout controls, TPH/PASID-related ignore fields, one-shot NAK generation, and vendor-specific RX data/status.
- Power and low-power behavior: captured LTR thresholds, L1 PM substate timers and entry/exit controls, L1.1/L1.2 enable/status, idle-to-RX turnoff controls, refclk request/ack timing, and strap fields that control link-capability, lane, ASPM, L0s/L1, lane reversal, and clock/power-gating behavior.
- Diagnostics and platform hooks: NAK counters, HPGI request/command/interrupt/status fields, BCH ECC correction/uncorrectable status, hcnt descriptor, and TXCLK performance counter event/count fields.

## Control Flow

This header chunk has no direct control flow. Runtime control flow appears when AMDGPU code includes the header and uses these constants to read, decode, update, or write NBIO registers. Typical use is:

1. Select a register address from `nbio_7_0_offset.h` or `nbio_7_0_smn.h`.
2. Read the register with a helper such as `RREG32_SOC15` or `RREG32_PCIE`, or prepare a value for write.
3. Extract a field with the generated mask/shift, often through `REG_GET_FIELD`.
4. Preserve unrelated bits and update a field with `REG_SET_FIELD`, then write through `WREG32_SOC15` or `WREG32_PCIE`.

The ordering in this file follows the generated hardware register map, not software execution. The repeated BIFP4/BIFP5/BIFP6 sections represent parallel PCIe port instances with similar layout. Code may program one port instance or another depending on ASIC wiring, board configuration, firmware state, virtualization mode, or diagnostics path.

## State And Persistence Behavior

The macros are compile-time constants and do not store state. The state described by the macros lives in NBIO/BIF PCIe hardware registers.

Some described fields are software-controlled configuration state: link reset/training controls, speed-change controls, ASPM and L1/L23 policy, error-reporting disables, RX ignore controls, LTR threshold masks, HPGI command fields, and error-injection enables. Other fields are hardware-observed state: link state readbacks, negotiated link width/speed, NAK counters, credit status, RX expected sequence numbers, captured LTR status, link-management interrupts, BCH ECC status, and HPGI status.

Persistence is controlled by GPU reset, PCIe link reset, BACO/runtime power transitions, suspend/resume, and ASIC power-domain behavior. The header itself provides no save/restore mechanism and does not encode reset values or access semantics. Driver code using these masks must still know whether a field is read-only, write-one-to-clear, sticky until reset, reserved, strap-derived, or safe for read/modify/write.

## Dependencies And Integration Points

This header is included directly by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Those files combine NBIO 7.0 masks with the sibling generated headers `nbio_7_0_default.h`, `nbio_7_0_offset.h`, and `nbio_7_0_smn.h`.

Observed integration patterns in nearby code include:

- `nbio_v7_0.c` uses NBIO masks to decode strap fields, configure memory-controller access, doorbell ranges, interrupt behavior, medium-grain clock gating/light sleep, and NBIO register initialization.
- `soc15.c` includes this header as part of the SOC15 ASIC support layer and uses related PCIe register masks to program/read PCIe performance counters and replay/NAK counts.
- Register field helpers (`REG_GET_FIELD`, `REG_SET_FIELD`, `WREG32_FIELD15`) depend on the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names matching the helper's token-pasting expectations.
- Linux PCIe integration depends indirectly on these definitions through AMDGPU's link training, power management, AER/diagnostic, reset, interrupt, and performance telemetry paths.

The BIFP port fields align with PCI Express concepts: transaction/data-link/physical layer errors, ASPM and L1 substate power management, LTR, link equalization and speed changes, flow-control credits, NAK/replay accounting, hot reset, link-bandwidth management, and vendor-specific port diagnostics.

## Risks And Edge Cases

Generated-register drift is the primary risk. If a single shift or mask differs from the NBIO 7.0 register database, code may silently program the wrong bit, clear a reserved bit, fail to train or retrain the PCIe link, suppress or inject the wrong error, misread link status, or corrupt flow-control settings. Because BIFP4/BIFP5/BIFP6 blocks are intentionally repetitive, accidental template or copy/paste drift can be difficult to distinguish from an intended per-port exception.

Read/modify/write safety is a major concern. Many registers combine software controls, hardware status, reserved fields, sticky status, and write-one-to-clear bits. Mask constants alone do not indicate access type. Code that writes a full value instead of preserving unrelated bits can disturb link training, power-management policy, error reporting, or flow-control credit accounting.

Error-injection fields are especially sensitive. The physical and transaction injection registers can intentionally create protocol errors that may trigger AER, link recovery, replay storms, device reset, or system-level PCIe error handling. Test or debug code must be tightly gated and must avoid leaving injection bits set across reset or resume paths.

Power-management fields are platform-sensitive. LTR thresholds, ASPM/L1/L1.1/L1.2 controls, refclk request timing, receiver standby, and lane power-state controls can affect idle power, wake latency, hotplug behavior, and link stability. Changes should be validated on real hardware across multiple root complexes and firmware configurations.

Chunk boundaries are meaningful. This range starts after the BIFP4 physical error-injection shifts and most masks have already begun in the previous chunk, and it ends before BIFP6 transaction error-injection masks and the rest of BIFP6 link-management fields. The final per-file report should merge adjacent chunks before claiming complete coverage of BIFP4 or BIFP6.

## Test Signals

There are no unit tests for these generated macros in this header. Useful validation signals are build, static comparison, and hardware behavior:

- Build AMDGPU/SOC15/NBIO 7.0 code to catch missing, renamed, or malformed generated macro symbols and helper token-pasting failures.
- Compare the generated header against the authoritative AMD NBIO 7.0 register database or regeneration output, with special focus on repeated BIFP4/BIFP5/BIFP6 symmetry and intentional per-port exceptions.
- Run PCIe link bring-up, retraining, speed-change, hot-reset, suspend/resume, runtime power management, and BACO scenarios on NBIO 7.0 hardware; watch for link-width/speed regressions, training timeouts, ASPM instability, and AMDGPU reset messages.
- Use PCIe/AER diagnostics or controlled validation-only error injection to confirm physical and transaction error bits map to expected hardware behavior and are cleared/restored safely.
- Check replay/NAK counters, PCIe performance counters, link-management status/mask behavior, and debug register dumps against expected values during heavy DMA, graphics, SDMA, video, and KFD queue workloads.
- Validate LTR and L1 substate behavior with platform power-management tooling; failures may appear as elevated idle power, wake latency problems, or intermittent link recovery events.
