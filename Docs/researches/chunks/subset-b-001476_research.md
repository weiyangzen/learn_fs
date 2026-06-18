# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h lines 3813-7580

## Scope And Purpose

This chunk is part of AMDGPU's generated BIF 3.0 register field mask header. It does not contain executable functions, data structures, or storage. Instead, it defines C preprocessor constants that describe bit masks and right-shift values for hardware register fields in the Bus Interface (BIF), PCIe PHY/PIF, PCIe link controller, PCIe port, performance counter, interrupt, error, and PRBS diagnostic blocks.

The practical purpose is to give AMDGPU code a single compile-time contract for extracting and updating fields in 32-bit MMIO registers. Driver code combines the `*_MASK` constants with the paired `*__SHIFT` constants when reading, modifying, or writing registers through helpers such as `RREG32_PCIE()`, `WREG32_PCIE()`, `RREG32_PCIE_PORT()`, and ASIC-specific indirect register accessors. Because these values encode hardware layout, correctness depends on exact numeric masks and shifts rather than on local control flow.

Within this range the dominant register family is `PB1_*`, covering PHY block 1 PIF controls, lane power controls, PLL controls, RX adaptation/equalization, TX coefficients and overrides, and lane SCI status overrides. The chunk then transitions into `PCIE_*` and `PCIEP_*` fields for PCIe bus/config/control/error handling, dynamic power allocation, flow-control credits, link training, link speed/width control, port state, performance counters, and PRBS error counters.

## Important APIs, Types, And Macros

There are no functions or C types in this chunk. The important API surface is the macro naming convention:

- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for a field in a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- Callers typically read a register, isolate a field with `value & FIELD_MASK`, and normalize it with `>> FIELD__SHIFT`; updates clear the mask and OR in `new_value << FIELD__SHIFT`.

The first large family is `PB1_PIF_*`. It includes `PB1_PIF_CNTL`, `PB1_PIF_CNTL2`, `PB1_PIF_PAIRING`, `PB1_PIF_PDNB_OVERRIDE_0` through `_15`, `PB1_PIF_PWRDOWN_0` through `_3`, `PB1_PIF_SC_CTL`, `PB1_PIF_SEQ_STATUS_0` through `_15`, and `PB1_PIF_TXPHYSTATUS`. These fields describe receiver detection overrides, PIF serial configuration, PLL binding, electrical-idle detection timing, lane grouping, per-lane TX/RX powerdown overrides, PLL power state in low-power states, sequencer status, and PHY TX status.

The `PB1_PLL_*` macros describe LC and ring-oscillator PLL control and override state: `PB1_PLL_LC0_CTRL_REG0`, `PB1_PLL_LC0_OVRD_REG0/1`, `PB1_PLL_RO0_CTRL_REG0`, `PB1_PLL_RO0_OVRD_REG0/1`, `PB1_PLL_RO_GLB_CTRL_REG0`, and per-PLL SCI status override registers. These expose divider, frequency mode, lock, calibration, reset, and power-on fields used by low-level PCIe/PHY bring-up and power-management sequences.

The `PB1_RX_*` macros cover receiver-global and per-lane configuration. Global registers describe GEN1/GEN2/GEN3 adaptation mode, CDR gain/time, LEQ/DFE/FOM settings, DLL and clock-power LUT entries, and override enable/value pairs for RX clocks, DLL, frontend, idle detect, termination, and adaptation state. Per-lane `PB1_RX_LANE<n>_CTRL_REG0` fields cover backup/debug/test controls, while `PB1_RX_LANE<n>_SCI_STAT_OVRD_REG0` exposes lane-specific `RXPWR`, preset hints, electrical-idle detect, FOM request/enable, and response mode.

The `PB1_TX_*` macros cover transmitter-global coefficient acceptance tables, lane skew, TX global control and override fields, and per-lane TX control/override/SCI status fields. Important field groups include TX calibration enable, swing/pre/de-emphasis values, PRBS enable, power-on and data-enable overrides, TX margin, deemphasis, coefficient ID, and coefficient value. These are tightly related to link equalization and PHY debug.

The `PCIE_*` macro families define higher-level PCIe controller state. `PCIE_CNTL`, `PCIE_CNTL2`, `PCIE_CONFIG_CNTL`, `PCIE_CI_CNTL`, and `PCIE_CFG_CNTL` cover ordering, payload/read-request sizing, hidden-register decode, completion allocation, arbitration, memory light-sleep/shutdown, and malformed/error behavior. `PCIE_ERR_CNTL`, `PCIE_INT_CNTL`, and `PCIE_INT_STATUS` expose error injection/reporting and interrupt enable/status bits. `PCIE_F0_DPA_*` fields describe Dynamic Power Allocation capability, latency indication, and substate power allocations.

The link-controller macros are especially important for runtime PCIe management. `PCIE_LC_SPEED_CNTL` exposes current and target data rate, GEN2/GEN3 strap support, SW/HW speed-change control, speed-change attempts and status, partner support observation, and recovery/equalization behavior. `PCIE_LC_LINK_WIDTH_CNTL` exposes link-width requests/readback, renegotiation, upconfigure support, dynamic lane power state, and reconfiguration triggers. `PCIE_LC_STATUS1/2` report detected and operating link width, reversal, inactive lanes, and lanes being turned on. `PCIE_LC_CNTL*`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, and `PCIE_LC_BEST_EQ_SETTINGS` describe ASPM/L0s/L1 behavior, illegal-state handling, hotplug, enhanced hotplug, speed/width recovery, Gen3 coefficient search/forcing, equalization parameters, and training-control policy.

The tail of the chunk defines PCIe physical-layer and observability registers: `PCIE_P_CNTL`, `PCIE_P_BUF_STATUS`, `PCIE_P_DECODER_STATUS`, `PCIE_P_MISC_STATUS`, `PCIE_P_PORT_LANE_STATUS`, `PCIE_PERF_*`, `PCIEP_HW_DEBUG`, `PCIEP_PORT_CNTL`, `PCIE_PORT_INDEX/DATA`, `PCIE_PRBS_CLR`, and `PCIE_PRBS_ERRCNT_*`. These support symbol alignment/deskeW error reporting, overflow/underflow/decode errors, indirect port access, performance-event selection and counters by clock domain, port PME/hotplug/power-fault behavior, PRBS checker clearing, and per-lane PRBS error counts.

## Control Flow

This header chunk has no runtime control flow. It participates in caller control flow by supplying field definitions used in read-modify-write sequences throughout AMDGPU and legacy DPM code.

A typical consumer flow is:

1. Read an MMIO or indirect PCIe register with a register address macro from the matching `bif_3_0_d.h`-style header.
2. Use this header's `*_MASK` and `*__SHIFT` pair to decode status or to prepare a new field value.
3. Clear a field with `reg &= ~FIELD_MASK`.
4. Insert the shifted field with `reg |= value << FIELD__SHIFT`.
5. Write the register back, often after checking link state, ASIC family, power-management state, or PCIe capability state.

Examples visible elsewhere in the source tree include PCIe link speed and width management using `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE_MASK`, `PCIE_LC_STATUS1__LC_DETECTED_LINK_WIDTH_MASK`, `PCIE_LC_LINK_WIDTH_CNTL__LC_RECONFIG_NOW_MASK`, `PCIE_LC_CNTL4__LC_REDO_EQ_MASK`, and `PB1_PIF_PWRDOWN_*` lane/PLL power fields. This chunk therefore shapes control flow indirectly: bad constants can make otherwise correct driver branches read the wrong status bit, leave a write-one control bit unset, or corrupt unrelated fields.

## State And Persistence Behavior

The chunk itself stores no state. All persistence is in hardware registers outside normal kernel memory. The macros describe persistent device state such as PCIe link speed, link width, lane reversal, ASPM/L-state behavior, RX/TX power state, PLL lock or override state, interrupt status, error counters, and performance counters.

Register writes using these macros can persist until a later driver write, firmware action, link retrain, hot reset, suspend/resume transition, BACO/power-gating transition, or full device reset. Some fields are status-only from the driver's perspective, while others are control or override fields that can directly change PCIe PHY behavior. Debug/status fields such as `PB1_HW_DEBUG`, `PB1_PIF_HW_DEBUG`, `PCIE_HW_DEBUG`, `PCIEP_HW_DEBUG`, `PCIE_LC_STATE*`, and `PCIE_PRBS_ERRCNT_*` provide snapshots or counters rather than Linux-owned memory state.

Because the header does not indicate access semantics, callers must know from hardware documentation or established driver sequences whether a field is read-only, write-one-to-clear, self-clearing, sticky, strap-derived, or safe only during specific link states. This is an important integration point: the masks are necessary but not sufficient for safe state transitions.

## Dependencies And Integration Points

This header depends only on the C preprocessor and the surrounding AMDGPU ASIC register-header layout. It is intended to be included with matching BIF 3.0 register address definitions so that names such as `ixPCIE_LC_SPEED_CNTL`, `ixPCIE_LC_STATUS1`, `ixPB1_PIF_PWRDOWN_0`, or indirect PCIe port indexes point at the register whose fields are defined here.

Primary integration points are low-level AMDGPU PCIe, ASIC initialization, power-management, and diagnostics code:

- ASIC PCIe helpers read link speed, link width, reversal, and retraining status using the `PCIE_LC_*` fields.
- Power-management paths update ASPM, L0s/L1 behavior, lane power state, PLL power state, and dynamic lane behavior through `PCIE_LC_CNTL*`, `PCIE_LC_LINK_WIDTH_CNTL`, and `PB1_PIF_PWRDOWN_*`.
- Link training and equalization paths use `PCIE_LC_SPEED_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, and the PB1 TX/RX coefficient and FOM fields.
- Interrupt and error handling consult or program `PCIE_ERR_CNTL`, `PCIE_INT_CNTL`, and `PCIE_INT_STATUS`.
- Debug and validation tooling can inspect `PCIE_LC_STATE*`, `PCIE_P_*` status fields, performance counters, and PRBS error counters.
- Register access helper macros such as `RREG32_PCIE`, `WREG32_PCIE`, and port-indirect variants provide the actual I/O behavior; this header only supplies the bit layout.

The file lives under a Ceph source mirror path, but the code content is AMDGPU Linux kernel driver register metadata. There is no Ceph filesystem logic in this chunk.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift can corrupt neighboring bits in a register, especially for packed link-controller fields such as `LC_LINK_WIDTH`, `LC_DYN_LANES_PWR_STATE`, `LC_CURRENT_DATA_RATE`, `LC_TARGET_LINK_SPEED_OVERRIDE`, TX/RX coefficient fields, and per-lane power override values.

Several fields are control bits that can affect link stability. Incorrect use of `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_RECONFIG_NOW`, `LC_REDO_EQ`, `LC_GO_TO_RECOVERY`, `LC_SET_QUIESCE`, `LC_RESET_LINK`, PIF powerdown fields, or RX/TX override enables can force retraining, quiesce traffic, power down lanes, or leave the PHY in an unexpected diagnostic state.

Lane-indexed definitions are repetitive and vulnerable to copy/generation errors. The chunk defines many fields for lanes 0-15 across RX lane status, TX lane status, PIF PDNB overrides, PIF sequence status, PRBS counters, and TX/RX power/override controls. A swapped lane suffix or field offset would only fail on certain widths, reversed links, or specific failing lanes.

There are paired enable/value override fields throughout the PHY macros. Writing a value field without the corresponding override enable may have no effect; enabling an override with a stale value can force an unintended power, clock, data, or calibration state.

Status and sticky error fields require caller-specific clearing semantics. The header names `PCIE_INT_STATUS`, `PCIE_ERR_CNTL`, `PCIE_P_BUF_STATUS`, `PCIE_P_DECODER_STATUS`, `PCIE_P_MISC_STATUS`, and PRBS counters, but does not encode whether fields are read-only, write-one-to-clear, latched, or reset by a separate clear register.

The requested line range ends on `PCIE_PRBS_ERRCNT_3__PRBS_ERRCNT_3_MASK`; its paired `PCIE_PRBS_ERRCNT_3__PRBS_ERRCNT_3__SHIFT` appears on the next source line outside this chunk. The merge/reconciliation lane should account for that boundary so the final per-file report does not imply the field pair is absent from the source file.

## Test Signals

Useful validation signals are indirect and hardware-oriented:

- Build coverage for AMDGPU configurations that include BIF 3.0 headers. Missing or renamed macros should fail compilation in PCIe and power-management code.
- PCIe link reporting should show sane current speed and width values decoded from `PCIE_LC_SPEED_CNTL` and `PCIE_LC_STATUS1`.
- Link retrain and speed-change paths should complete without timeouts when using `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_RECONFIG_NOW`, `LC_RENEGOTIATE_EN`, and related status bits.
- Suspend/resume, runtime power management, BACO-like transitions, and ASPM changes should not leave lanes powered incorrectly or reduce link width unexpectedly.
- Error and interrupt paths should report expected correctable, non-fatal, fatal, miscellaneous, link-bandwidth, and power-state-change status when triggered by hardware or tests.
- Diagnostic tests using PRBS, performance counters, debug buses, lane reversal, and equalization should show per-lane counters and status changing in the expected lane/register positions.
- Regression symptoms from bad constants include link stuck at a lower generation, failed width upconfigure, retraining loops, GPU disappearance after suspend/resume, AER noise, underflow/overflow status stuck high, PRBS errors on the wrong lane, or inability to clear/observe expected interrupt status.

## Cross-Chunk Notes

Earlier chunks of `bif_3_0_sh_mask.h` define the beginning of the same generated register-mask namespace, including BACO, BIF, PCIe, and the first part of the PB1/PIF/PHY register fields. Later lines continue the PRBS counter definitions after the boundary at line 7580 and then complete the rest of the header. The final per-file document should treat this file as a generated hardware register layout contract, not as algorithmic driver code.
