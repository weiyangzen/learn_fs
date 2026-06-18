# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 82593-84945

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in NBIO/BIF PCIe registers. The matching offset names live in `nbio_7_7_0_offset.h`; this file supplies the field layout used after a driver reads or writes a register value.

The range contains 2,353 source lines, 2,177 `#define` entries, and 174 register-comment/address-block markers. It starts inside the `BIFP4_0_PCIE_RX_CNTL` register, continues through the tail of the `BIFP4_0` PCIe port block, then enters `addressBlock: nbio_pcie0_pciedir` and covers the opening `BIF0` PCIe-directory block through the first fields of `BIF0_SWRST_COMMAND_0`.

At a high level, the chunk covers:

- `BIFP4_0` receive controls, sequence/vendor status, receive credit allocation, physical and transaction error injection, NAK counters, link-control state/history, link training, width/speed negotiation, 8/16/32 GT/s equalization coefficient controls, L1 PM substates, link-management masks, BCH/ECC control, save/restore fields, transmit replay/ack/credit controls, and flow-control status for VC0/VC1.
- The beginning of `BIF0` PCIe-directory controls, including reserved/scratch registers, NAK counters, global PCIe control/config/debug, RX sideband and completion policy, common AER masking, client-interface controls, bus/PM controls, link-state history and status, WPR reset policy, last received TLP snapshots, I2C debug/register access windows, configuration decode control, CLKREQ mapping, physical-lane controls/status, SDP attribute overrides, performance counters, strap registers, PRBS diagnostics, and software-reset controls.

The file is not executable code and has no Ceph or distributed-filesystem behavior despite its mirrored path. It is a generated hardware ABI description consumed by low-level AMDGPU register-access code.

## Important APIs, Types, And Macros

There are no functions, structs, typedefs, enums, or runtime objects in this chunk. The public surface is entirely macro based:

- `<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for that field in a 32-bit register value.
- Some field names intentionally contain `MASK`, producing generated names such as `BIF0_NBIO_CLKREQb_MAP_CNTL2__PCIE_CLKREQB_0_CNTL_MASK_MASK` and `BIF0_PCIE_PRBS_MISC__PRBS_CHK_ERR_MASK_MASK`.

Important register families in the `BIFP4_0` portion include:

- Receive and error policy: `BIFP4_0_PCIE_RX_EXPECTED_SEQNUM`, `BIFP4_0_PCIE_RX_VENDOR_SPECIFIC`, `BIFP4_0_PCIE_RX_CNTL3`, receive credit allocation registers, `BIFP4_0_PCIEP_ERROR_INJECT_PHYSICAL`, `BIFP4_0_PCIEP_ERROR_INJECT_TRANSACTION`, and `BIFP4_0_PCIEP_NAK_COUNTER`.
- Link control and training: `BIFP4_0_PCIE_LC_CNTL`, `LC_TRAINING_CNTL`, `LC_LINK_WIDTH_CNTL`, `LC_N_FTS_CNTL`, `LC_SPEED_CNTL`, `LC_SPEED_CNTL2`, `LC_STATE0` through `LC_STATE5`, `LC_CNTL2` through `LC_CNTL12`, `LC_BW_CHANGE_CNTL`, `LC_CDR_CNTL`, and `LC_LANE_CNTL`.
- Equalization and high-speed tuning: `LC_FORCE_COEFF`, `LC_BEST_EQ_SETTINGS`, `LC_FORCE_EQ_REQ_COEFF`, plus the `*_COEFF2` and `*_COEFF3` variants for newer speed families. These expose pre-cursor, cursor, post-cursor, FS/LF, and forced-equalization request fields, including 32 GT/s fields.
- Power and save/restore: `LC_L1_PM_SUBSTATE` through `LC_L1_PM_SUBSTATE5`, `LC_FINE_GRAIN_CLK_GATE_OVERRIDES`, `LC_SAVE_RESTORE_1`, and `LC_SAVE_RESTORE_2`.
- Transmit and flow control: `PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, `PCIE_TX_ACK_LATENCY_LIMIT`, `PCIE_TX_CREDITS_FCU_THRESHOLD`, vendor-specific/NOP DLLP transmit controls, outstanding non-posted request control, advertised and initial P/NP/CPL credits, transmit credit status, and `PCIE_FC_*`/`PCIE_FC_*_VC1` flow-control fields.

Important register families in the `BIF0` portion include:

- Core PCIe controls and RX policy: `BIF0_PCIE_CNTL`, `CONFIG_CNTL`, `DEBUG_CNTL`, `RX_CNTL2/4/5`, `COMMON_AER_MASK`, `CNTL2`, `CI_CNTL`, `BUS_CNTL`, and `RX_AD`. These fields control lock/write behavior, sideband arbitration, completion and timeout handling, ATS/PASID/page-request unsupported-request policy, ordering/attribute overrides, power gating, AER masking, VDM/drop/UR behavior, and client-interface arbitration.
- Link history, status, and physical layer: `LC_STATE6` through `LC_STATE11`, `LC_STATUS1`, `LC_STATUS2`, `P_CNTL`, `P_BUF_STATUS`, `P_DECODER_STATUS`, `P_MISC_STATUS`, and `P_RCV_L0S_FTS_DET`.
- Debug and sideband access: scratch/reserved registers, last-TLP snapshot dwords, I2C register address/data, config-hidden-register enables, CLKREQ mapping, SDP controls, and SWUS/RC slave attribute override registers.
- Performance counters: global count enable/reset/shadow controls, `PERF_CNTL_TXCLK1` through `TXCLK6`, matching counter dwords, and event-port select registers for LC/CI traffic.
- Strap and capability controls: `PCIE_STRAP_F0`, `STRAP_NTB`, `STRAP_MISC`, `STRAP_MISC2`, `STRAP_PI`, and `STRAP_I2C_BD`. These expose feature straps for MSI, VC, DSN, AER, ACS, BAR, power, DPA, ATS, page request, PASID, ECRC, multicast, atomic ops, ARI, SR-IOV, MSI map, DLF, 16/32 GT/s support, margining, NPEM, clock PM, compliance, TPH, DRS/FRS/RTR, and debug I2C.
- PRBS and reset diagnostics: PRBS clear/status/freerun/misc/user pattern, low/high bit counters, 16 PRBS error counters, `SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, and the start of `SWRST_COMMAND_0`.

## Control Flow And Runtime Behavior

This header has no executable control flow. Runtime behavior is implied by code that includes the generated NBIO 7.7.0 headers:

1. A caller selects a register offset from `nbio_7_7_0_offset.h`, such as `regBIFP4_0_PCIE_LC_CNTL`, `regBIF0_PCIE_PERF_COUNT_CNTL`, or `regBIF0_SWRST_COMMAND_STATUS`.
2. The caller reads or writes that register through AMDGPU's NBIO/MMIO/SMN/config access path for the detected ASIC.
3. The caller decodes fields with `(value & FIELD_MASK) >> FIELD__SHIFT` or performs a read-modify-write using the masks in this file.
4. Hardware performs the actual PCIe link training, flow-control, reset, power, error-reporting, diagnostic, or performance-counter behavior.

The hardware flows represented here include PCIe receive filtering and unsupported-request policy, poisoned/error handling, enhanced atomic/ATS/PASID/page-request behavior, completion timeout policy, NAK/replay accounting, LTSSM/link-state history capture, link width and speed negotiation, L0s/L1/L1-substate power transitions, CLKREQ mapping, equalization coefficient forcing, save/restore across low-power transitions, transmit replay and ack-latency control, posted/non-posted/completion credit advertisement, flow-control update tracking, PRBS link diagnostics, strap-controlled feature exposure, and software-triggered BIF/port resets.

## State And Persistence

The header itself owns no mutable state, performs no I/O, allocates no memory, and persists nothing. It is a compile-time description of bit layouts.

The state described by these macros lives in NBIO/BIF hardware registers. Some fields are mostly static or firmware/strap-derived, such as feature straps, capability enable straps, speed-support straps, I2C debug enablement, and some reserved or identity-adjacent values. Other fields are live control state, including RX error/UR/drop policy, AER masking, client-interface ordering and credit policy, link training knobs, link-speed-change controls, L1 substate timing, clock-gating overrides, transmit replay/credit settings, performance-counter event selects, PRBS test mode, and software-reset commands.

Status and log fields include expected/acknowledged sequence numbers, NAK counters, link-state history and current width/inactive-lane status, speed-change status/failure status, BCH/ECC status, TX credit errors, last received TLP snapshots, physical-layer overflow/underflow/decode/deskew/symbol-unlock status, performance-counter full flags and counts, PRBS lock/error/bit/error counters, and reset-complete/wait/PERST/link-reset status. This generated header does not encode reset defaults, read-only/write-only access rules, write-one-to-clear semantics, polling delays, or side effects.

Persistence across FLR, hot reset, link reset, GPU reset, BACO, suspend/resume, runtime power transitions, or firmware save/restore is defined by hardware and higher-level driver code, not by this header. The presence of `LC_SAVE_RESTORE_*` field definitions signals hardware save/restore surfaces, but the macros do not specify when values are captured, restored, or invalidated.

## Dependencies And Integration Points

The direct dependency is the paired generated offset header:

- `nbio_7_7_0_offset.h` supplies register offsets and base indices.
- This `nbio_7_7_0_sh_mask.h` chunk supplies masks and shifts for fields in those registers.

The semantic dependencies are the AMD NBIO 7.7.0 register specification and PCI Express behavior for link training/status, replay and flow control, virtual channels, completion timeout, ATS/PASID/page request, atomics, LTR/TPH-adjacent policy, ASPM/L1 substates, DPC/AER-adjacent error handling, PRBS testing, and reset sequencing.

Likely integration points include:

- AMDGPU NBIO 7.7 bring-up code that initializes PCIe link, reset, and power-management behavior.
- Link-management paths that read LTSSM history/status, force retraining or speed changes, manage width negotiation, tune equalization coefficients, and validate 16/32 GT/s behavior.
- Error handling and diagnostics paths that inspect NAK/replay/credit counters, last TLP logs, AER masks, RX drop/UR policy, physical-layer error status, and PRBS results.
- Power-management paths that program L0s/L1/L1-substate, CLKREQ mapping, clock-gating overrides, save/restore fields, and physical-lane powerdown behavior.
- Performance/debug tooling that programs `BIF0_PCIE_PERF_*` event selectors and reads the paired counters.
- Firmware/board configuration paths that consume or audit strap values controlling advertised PCIe features such as MSI, ACS, ATS, PASID, SR-IOV, DLF, high-speed support, margining, and FRS/DRS/RTR.
- Reset handling that uses `BIF0_SWRST_COMMAND_STATUS`, `BIF0_SWRST_GENERAL_CONTROL`, and `BIF0_SWRST_COMMAND_0` with hardware-specific ordering and polling.

A repository search in this source mirror found these exact field names only in the generated header and matching offset definitions, which is typical for large ASIC-register dumps: consumers often reach them via generated include conventions and local register helper macros rather than through many direct references in nearby C files.

## Risks

The primary risk is silent hardware misprogramming. These macros are compile-time constants; pairing a `BIFP4_0` mask with a `BIF0` offset, a different port number, or another NBIO generation can compile cleanly while decoding or programming the wrong bits.

Chunk boundaries split logical registers. The first lines are the tail masks for `BIFP4_0_PCIE_RX_CNTL`, whose earlier shifts and masks are in the previous chunk. The final line range stops inside `BIF0_SWRST_COMMAND_0`, before the full register group and the following `BIF0_SWRST_COMMAND_1` fields. Audits for complete register coverage must include adjacent chunks.

Generated names with repeated `MASK` suffixes are easy to mishandle in scripts. They are not typos by themselves; they come from field names that include `MASK`. Renaming or normalizing them would break generated ABI compatibility.

Read-modify-write discipline matters. Many registers mix writable controls with status, reserved, sticky, or write-one-to-clear fields. This header does not describe access policy, so callers must preserve reserved bits and follow hardware sequencing from the NBIO specification and existing AMDGPU conventions.

Link-training and equalization fields are platform sensitive. Fields for speed changes, 16/32 GT/s coefficients, L1 substates, lane reversal, inactive lanes, CLKREQ, and PRBS diagnostics can depend on board routing, retimers, firmware policy, link partner behavior, and power state. Normal boot testing may not exercise the dangerous combinations.

Reset fields have high blast radius. `BIF0_SWRST_*` controls can reset ports, configuration state, PHY, core, register, sticky, global, and SDP credit domains. Incorrect writes may drop the PCIe link, lose config state, or prevent recovery without a wider GPU/platform reset.

## Test Signals

Useful validation signals include:

- The AMDGPU tree builds with NBIO 7.7.0 headers included, proving macro names resolve for generated consumers.
- Generator or static checks verify that every complete register group in this chunk has matching offsets in `nbio_7_7_0_offset.h`, while allowing the known partial boundary groups at `BIFP4_0_PCIE_RX_CNTL` and `BIF0_SWRST_COMMAND_0`.
- Hardware register dumps on NBIO 7.7 systems decode plausible link status, negotiated width, inactive lanes, LTSSM history, sequence numbers, NAK/replay counters, credit values, and flow-control state.
- PCIe link tests cover speed changes, retraining, L0s/L1/L1 substate entry and exit, CLKREQ behavior, width negotiation, equalization, 16/32 GT/s coefficient handling, and recovery after failed speed/equalization attempts.
- Error-path tests or forced-error diagnostics exercise RX ignore/drop/UR policy, AER/common mask behavior, poisoned/completion-timeout handling, NAK/replay behavior, TX credit error bits, and last-TLP capture.
- PRBS validation checks lock, bit-count completion, polarity, user pattern, and per-lane error counters with expected pass/fail behavior.
- Performance-counter validation programs `BIF0_PCIE_PERF_CNTL_*` event selects, enables global counting, snapshots counters, and confirms count/reset/full/shadow behavior.
- Reset and power-management testing verifies that SWRST command/status bits, link-reset type bits, save/restore fields, straps, and writable PCIe controls are restored or reinitialized by higher-level code after FLR, hot reset, link reset, GPU reset, suspend/resume, and runtime power transitions.
