# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 108786-111115

## Scope

This chunk covers generated shift and mask macros for the AMD NBIO 7.7.0 PCIe register map. It starts in the middle of the `BIFP4_1_PCIE_LC_CNTL8` field set, continues through the remaining `BIFP4_1` PCIe link-control and transmit/flow-control definitions, covers the full `nbio_pcie1_bifp5_pciedir_p` address block, and ends in the `nbio_pcie1_pciedir` block after the first half of `BIF1_PCIE_LC_STATE7`.

The file is not executable driver logic. It defines preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. Register addresses and base-index macros live in the sibling `nbio_7_7_0_offset.h` header; this header supplies the bit positions used by AMDGPU register access helpers.

## Purpose

The purpose of this section is to provide the bit-level ABI between AMDGPU NBIO/PCIe code and NBIO 7.7.0 hardware. Driver code can use these masks with helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related NBIO accessors to configure PCIe link training, equalization, ASPM/L1 substates, save/restore state, transmit replay/credit behavior, error injection, and status/debug collection.

The chunk is mostly organized by repeated PCIe port instances. `BIFP4_1_*` definitions finish one port instance. `BIFP5_*` repeats the same broad register families for another physical PCIe directory port. `BIF1_*` begins a core PCIe directory block with receive, completion, bus-control, and link-state history fields.

## Important Macro Families

### BIFP4_1 Link Control Tail

The opening `BIFP4_1_PCIE_LC_*` definitions continue link-control fields for a PCIe port. The covered controls include:

- `LC_CNTL8`, `LC_CNTL9`, `LC_CNTL10`, `LC_CNTL11`, and `LC_CNTL12`, covering equalization timing, loopback equalization, receiver-detect reset behavior, L1/L1.2 refclk request policy, link disable timing, low-speed link detect, training bits, FOM settling controls, data-stream SKP handling, and Gen4/16GT or Gen5/32GT-oriented behavior.
- `LC_FORCE_COEFF2`, `LC_FORCE_EQ_REQ_COEFF2`, `LC_FORCE_COEFF3`, and `LC_FORCE_EQ_REQ_COEFF3`, which expose forced pre-cursor, cursor, post-cursor, full-swing, and low-frequency equalization request fields for 16GT and 32GT rates.
- `LC_FINE_GRAIN_CLK_GATE_OVERRIDES`, which disables selected dynamic/output clock-gating paths for transmit mux, symbol mux, packet generator, and LTSSM logic.
- `LC_SAVE_RESTORE_1` and `LC_SAVE_RESTORE_2`, which define an indexed save/restore command interface with enable, direction, index, acknowledge, done, fast-restore, speed-selection, and data fields.
- `LC_SPEED_CNTL2`, which holds speed-change inhibit/abort knobs, auto speed-change control, directed speed-change policy, Gen4/Gen5 ordered-set behavior, and failed speed-change handling.

These fields are hardware state-machine controls rather than normal software state. Many are policy bits read by LTSSM, equalization, ASPM, or power-management hardware during link transitions.

### BIFP4_1 Transmit and Flow Control

The `BIFP4_1_PCIE_TX_*` and `BIFP4_1_PCIE_FC_*` groups define transaction-layer transmit behavior:

- `TX_SEQ` and `TX_REPLAY` expose sequence number, replay timer, replay buffer pointer, and replay timeout/count fields.
- `TX_ACK_LATENCY_LIMIT` and `TX_CREDITS_FCU_THRESHOLD` tune ACK/NAK latency limits and flow-control update thresholds for posted, non-posted, and completion traffic.
- `TX_VENDOR_SPECIFIC`, `TX_NOP_DLLP`, and `TX_REQUEST_NUM_CNTL` control vendor-specific DLLP/NOP behavior and request numbering.
- `TX_CREDITS_ADVT_*`, `TX_CREDITS_INIT_*`, and `TX_CREDITS_STATUS` describe advertised, initialized, and current credit values for posted, non-posted, and completion header/data paths.
- `FC_P`, `FC_NP`, `FC_CPL`, and their `VC1` variants expose flow-control credit data/header fields for the default virtual channel and VC1.

These masks are integration points for PCIe reliability and throughput tuning. Incorrect credit or replay manipulation can produce link stalls, excessive replay, or protocol-level errors.

### BIFP5 PCIe Port Register Map

The `nbio_pcie1_bifp5_pciedir_p` address block repeats a complete port-level PCIe map for `BIFP5`. Important groups include:

- Port and requester identity: `PCIEP_RESERVED`, `PCIEP_SCRATCH`, `PCIEP_PORT_CNTL`, `PCIE_TX_REQUESTER_ID`, `PCIE_TX_SKID_CTRL`, and `PCIE_P_PORT_LANE_STATUS`.
- Error and receive controls: `PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_RX_CNTL3`, `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_VENDOR_SPECIFIC`, `PCIEP_NAK_COUNTER`, and receive credit allocation registers.
- Error injection and AER: `PCIEP_ERROR_INJECT_PHYSICAL`, `PCIEP_ERROR_INJECT_TRANSACTION`, `PCIE_AER_PRIV_UNCORRECTABLE_MASK`, and `PCIE_AER_PRIV_TRIGGER`.
- LTR capture: `PCIEP_RX_CAPTURED_LTR_CTRL_STATUS` and `PCIEP_RX_CAPTURED_LTR_THRESHOLD_VALUES`, which expose captured latency tolerance reporting control/status and threshold values.
- Link controller state and policy: `LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_STATE0` through `LC_STATE5`, `LC_CNTL2` through `LC_CNTL12`, `LC_BW_CHANGE_CNTL`, `LC_CDR_CNTL`, `LC_LANE_CNTL`, and `LC_LINK_MANAGEMENT_MASK`.
- Equalization and coefficients: `LC_FORCE_COEFF`, `LC_BEST_EQ_SETTINGS`, `LC_FORCE_EQ_REQ_COEFF`, plus the `COEFF2` and `COEFF3` variants for higher rates.
- Strap and low-power behavior: `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, `PCIEP_STRAP_LC2`, and `LC_L1_PM_SUBSTATE` through `LC_L1_PM_SUBSTATE5`.
- BCH ECC, HPGI/HCNT, and performance counters: `PCIEP_BCH_ECC_CNTL`, `PCIEP_HPGI_PRIVATE`, `PCIEP_HPGI`, `PCIEP_HCNT_DESCRIPTOR`, and `PCIEP_PERF_CNTL_COUNT_TXCLK*`.
- Transmit and flow-control families matching the earlier `BIFP4_1` definitions.

The BIFP5 block is the most substantial part of this chunk. It mirrors the same generated naming convention for a distinct PCIe port, so consumers must pair these field masks with the matching `regBIFP5_*` address macros rather than cross-port addresses.

### BIF1 Core PCIe Directory Fields

The final `nbio_pcie1_pciedir` block begins the `BIF1` PCIe directory map. The covered portion includes:

- `BIF1_PCIE_RESERVED`, `BIF1_PCIE_SCRATCH`, `BIF1_PCIE_RX_NUM_NAK`, and `BIF1_PCIE_RX_NUM_NAK_GENERATED`, which provide reserved/scratch and NAK accounting fields.
- `BIF1_PCIE_CNTL`, with hardware init write-lock, hot-plug delay, unsupported-request reporting, malformed atomic operation handling, NP memory write behavior, RCB ordering/error handling, ATS-related receive behavior, TX completion debug, LTR UR handling, and completion ordering enable.
- `BIF1_PCIE_CONFIG_CNTL` and `BIF1_PCIE_DEBUG_CNTL`, providing dynamic clock latency and debug-port selection fields.
- `BIF1_PCIE_RX_CNTL5`, `RX_CNTL4`, and `RX_CNTL2`, covering sideband arbitration, enhanced atomic UR behavior, ATS relaxed-ordering disable, completion timeout reference speed, overflow handling, NAK counter mode, endpoint UR filtering for PASID/ATS/page request/invalidate completion cases, RCB latency counting, slave completion memory low-power controls, and FLR extension mode.
- `BIF1_PCIE_COMMON_AER_MASK`, `BIF1_PCIE_CNTL2`, `BIF1_PCIE_CI_CNTL`, and `BIF1_PCIE_BUS_CNTL`, covering AER private masks, link-state enable bits for RCB/master/slave paths, slave memory power saving/shutdown/deep-sleep controls, completion allocation/order policy, DPC/CTO behavior, arbitration, and PMI status/interrupt controls.
- `BIF1_PCIE_LC_STATE6` and the start of `BIF1_PCIE_LC_STATE7`, which store packed previous LTSSM/link-controller state history entries.

## Control Flow

There is no C control flow in this chunk. Runtime sequencing is implicit in the hardware protocols described by the registers:

- Link training, width negotiation, speed changes, equalization, loopback, and ASPM/L1 substate entry/exit are controlled by LTSSM and link-controller hardware that samples these bitfields.
- Save/restore registers form a small command/acknowledge protocol: software selects direction and index, places or reads data, enables the operation, and observes acknowledge/done/status fields.
- Error injection fields act as command-like debug controls and should only be used in controlled diagnostic paths.
- TX replay and credit status fields reflect transaction-layer state that is continuously updated by hardware and consumed by debug, recovery, or tuning code.

Any driver function using these macros must preserve reserved bits and respect register-specific read/modify/write requirements because the header does not encode access type, volatility, write-one-to-clear behavior, or sequencing constraints.

## State and Persistence

The state described here is hardware register state, not persisted kernel memory. Some fields are persistent configuration until reset or reprogramming, including strap-derived overrides, link training policy, flow-control thresholds, power-management controls, and clock-gating overrides. Other fields are live counters or status snapshots, including replay counts, NAK counts, credit status, lane status, LTR capture, BCH ECC status, and LTSSM previous-state history.

Save/restore fields are explicitly stateful and indexed. They can preserve equalization or link-related settings across low-power transitions when the surrounding driver and hardware use the acknowledge/done handshake correctly. Scratch registers may provide temporary firmware/driver communication state, but persistence is limited to the hardware reset domain.

## Dependencies and Integration Points

This header depends on the generated NBIO register-address header for matching `reg*` symbols and on AMDGPU register helper macros for bitfield composition and extraction. It is normally included indirectly by NBIO, PCIe, and SOC15 code rather than used as a standalone interface.

Integration points include:

- AMDGPU NBIO initialization and PCIe bring-up paths that configure requester IDs, port policy, hot-plug delay, lane width, link speed, and ASPM behavior.
- Power-management code coordinating clock gating, L1/L1.1/L1.2 substates, refclk request behavior, link disable, and save/restore.
- PCIe error handling, AER/DPC, recovery, and debug code that reads receive error controls, NAK/replay counters, AER masks/triggers, and link-state history.
- Performance and validation tooling that samples TXCLK performance counters, credit status, flow-control values, lane state, and equalization results.
- Hardware validation paths that use error injection, loopback equalization, forced coefficients, and debug-port selection.

The generated prefixes matter. `BIFP4_1`, `BIFP5`, and `BIF1` fields target different address blocks or port instances; sharing a mask name pattern does not mean the same register address should be used.

## Risks

- Mispaired register addresses and masks across `BIFP4_1`, `BIFP5`, and `BIF1` can silently write the wrong port or decode a field with the wrong layout.
- Forced equalization coefficients, speed-change bits, loopback controls, and training timers can destabilize PCIe link training or recovery when set outside silicon-specific workarounds.
- ASPM, L1 substate, refclk request, and clock-gating fields interact with platform firmware and board electrical constraints; aggressive settings can cause resume failures, link drops, or intermittent device disappearance.
- TX credit, replay, ACK latency, and NOP DLLP controls are protocol-sensitive. Incorrect writes can induce replay storms, timeout behavior, or deadlocked flow control.
- Error injection and AER trigger bits should not be reachable from normal runtime paths because they can intentionally create physical or transaction-layer faults.
- Some field names imply status or handshakes, but this generated header does not document read/write side effects. Callers must rely on hardware programming guides or existing AMDGPU access sequences.

## Test Signals

Useful validation signals for code using this chunk include:

- Successful GPU probe and PCIe enumeration with expected requester ID, link width, and link speed.
- Stable suspend/resume, runtime power management, ASPM L1/L1.1/L1.2 entry/exit, and reset recovery on systems that exercise NBIO 7.7.0.
- No increase in PCIe AER, DPC, NAK, replay, completion timeout, unsupported-request, or malformed transaction reports after field changes.
- Correct LTSSM/link history and lane-status readings when debugging link-width or link-training issues.
- Passing hardware validation for loopback/equalization paths when forced coefficient or error-injection fields are used.
- Register readback tests that verify `SHIFT` and `MASK` pairs cover the intended bit ranges and do not overlap reserved bits when composed with standard AMDGPU field helpers.
