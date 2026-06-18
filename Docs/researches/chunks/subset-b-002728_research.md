# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_6_0_sh_mask.h lines 4470-9119

## Purpose

This chunk is the middle generated register-field mask slice for AMD GMC 6.0. It exports C preprocessor constants for memory-controller, memory-IO, power-management, request-buffer, sequencer, and training registers. Each field is represented as a `REGISTER__FIELD_MASK` and, normally, a matching `REGISTER__FIELD__SHIFT` value for composing or decoding 32-bit MMIO register values.

The range starts inside the `MC_IO_DEBUG_DQB2L_OFSCAL_D0` field list, continues through the remaining DQB2L entries, complete DQB3, EDC, WCDR, WCK, and `MC_IO_DEBUG_UP_0..159` debug value tables, then covers pad/PHY control, memory clock power management, PMG mode-register controls, read arbitration groups, RPB request-buffer controls, and a large block of memory-sequencer control/timing/status/training masks. It ends in the first part of `MC_SEQ_TRAIN_WAKEUP_MASK`; the remaining fields are in the next chunk.

This file is declarative hardware binding data. It has no executable code, but the constants are part of the Southern Islands / GMC 6.0 register ABI used by AMDGPU display, graphics, power-management, and memory-controller bring-up paths.

## Major Register Areas Covered

The first section defines memory-IO debug lane masks. The `MC_IO_DEBUG_DQB2L_*`, `MC_IO_DEBUG_DQB3_*`, `MC_IO_DEBUG_DQB3H_*`, `MC_IO_DEBUG_DQB3L_*`, `MC_IO_DEBUG_EDC_*`, `MC_IO_DEBUG_WCDR_*`, and `MC_IO_DEBUG_WCK_*` families expose four byte-wide `VALUE0..VALUE3` fields at shifts 0, 8, 16, and 24. These cover clock select, miscellaneous, offset calibration, RX equalization, RX phase, RX VREF calibration, TX boost pull-down/pull-up, TX phase, TX self settings, CDR phase-size, dynamic RX power management, and EDC/WCDR equalization power-management fields for D0/D1 channels.

`MC_IO_DEBUG_UP_0..159` is a dense debug table with the same four 8-bit `VALUE*` fields per register. It appears to map a generated register-index space used by the memory-controller IO debug loader rather than hand-authored driver logic. In the GMC 6.0 firmware load path, `gmc_v6_0.c` writes firmware-provided index/data pairs to `MC_SEQ_IO_DEBUG_INDEX` and `MC_SEQ_IO_DEBUG_DATA`; these `MC_IO_DEBUG_*` masks document the bit layout of those indexed payload registers.

The pad and PHY control section covers `MC_IO_DPHY_STR_CNTL_D0/D1`, `MC_IO_PAD_CNTL`, `MC_IO_PAD_CNTL_D0/D1`, RX control for DPHY0/1 and D0/D1, TX control for APHY and DPHY, `MCLK_PWRMGT_CNTL`, `MC_MEM_POWER_LS`, `MC_NPL_STATUS`, and `MC_PHY_TIMING*`. These masks describe low-level electrical and timing controls: data/command/address delay sync, fall-out behavior, read strobe forcing/delay, VREF enable/select, clock delay selection, power-off controls, GDDR power-on, drive strengths, RX comparator/equalization and CDR controls, TX pull-up/pull-down strengths, TX slew, dynamic power management, DLL/pad timing, and memory clock gating or switching state.

The PMG and mode-register section covers `MC_PMG_AUTO_CFG`, `MC_PMG_AUTO_CMD`, `MC_PMG_CFG`, `MC_PMG_CMD_MRS*`, and `MC_PMG_CMD_EMRS`. These fields describe memory power-management automation, self-refresh and DPM wake behavior, mode-register reset/command construction, MRS wait counters, YCLK and ACPI acknowledgement behavior, RX power state, and ZQ calibration send controls.

The read arbitration and request-buffer section covers `MC_RD_CB`, `MC_RD_DB`, `MC_RD_HUB`, `MC_RD_TC0/TC1`, `MC_RD_GRP_EXT/GFX/LCL/OTH/SYS`, and `MC_RPB_*`. The masks provide per-client or per-traffic-class read-request controls, grouping, weights, queue IDs, BIF/XPB ordering controls, read/write combine and switch controls, performance counter selection, debug fields, and effective-control/status bits for the request path between clients and the memory controller.

The sequencer section starts with bit/byte remap (`MC_SEQ_BIT_REMAP_B0..B3_D0/D1`, `MC_SEQ_BYTE_REMAP_D0/D1`) and then covers DRAM timing and command state. `MC_SEQ_CAS_TIMING*`, `MC_SEQ_RAS_TIMING*`, `MC_SEQ_MISC_TIMING*`, `MC_SEQ_PMG_TIMING*`, `MC_SEQ_CNTL*`, `MC_SEQ_DRAM*`, `MC_SEQ_CMD`, `MC_SEQ_FIFO_CTL`, `MC_SEQ_MPLL_OVERRIDE`, and `MC_SEQ_CG` fields encode memory-type/timing controls, low-power variants, queue and FIFO controls, command issue state, PLL override, clock gating, DRAM configuration, and error insertion hooks.

The sequencer microcontroller and status portion includes `MC_SEQ_IO_DEBUG_INDEX/DATA`, `MC_SEQ_IO_RDBI/REDC/RWORD*`, `MC_SEQ_MISC*`, performance counters, PMG command registers for low-power modes, page-gating hardware/software controls, read-control framing for D0/D1, reserved sequencer state, RX framing for bytes/DBI/EDC, `MC_SEQ_STATUS_M/S`, and `MC_SEQ_SUP_*` supervisor program/status registers. These masks support memory-controller firmware loading, sequencer state inspection, and low-level training/debug flows.

The final part covers training and wakeup controls. `MC_SEQ_TCG_CNTL` defines a training command generator with reset/start/load FIFO, MOP, burst/data count, auto-refresh, DBI, valid-pointer masking, done, and channel-enable fields. `MC_SEQ_TIMER_RD/WR` define full-width counters. `MC_SEQ_TRAIN_CAPTURE`, `MC_SEQ_TRAIN_WAKEUP_CLEAR`, `MC_SEQ_TRAIN_WAKEUP_CNTL`, `MC_SEQ_TRAIN_WAKEUP_EDGE`, and the beginning of `MC_SEQ_TRAIN_WAKEUP_MASK` describe wakeup/capture events for auto-refresh, command/data FIFO readiness, read/write EDC, memory-clock frequency changes, software wakeup, timers, training state-machine completion, DPM, allow-stop signals, idle, and PHY power gating. `MC_SEQ_TRAIN_EDC_THRESHOLD*` and `MC_SEQ_TRAIN_TIMING` provide EDC retrain status/threshold and train timing fields.

## Important APIs, Types, and Functions

There are no functions, types, structs, or enums in this chunk. The exported API is the generated macro namespace:

- `REGISTER__FIELD_MASK` gives the bit mask to preserve, clear, test, or encode a field.
- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- Full-register fields such as sequencer timers, status words, program words, and debug data use `0xffffffffL` masks with shift 0.
- Repeated debug-register families use four byte fields: `VALUE0`, `VALUE1`, `VALUE2`, and `VALUE3`.

The immediate companion dependency is `gmc_6_0_d.h`, which supplies register offsets such as `mmMC_SEQ_TRAIN_WAKEUP_CNTL`, `mmMC_SEQ_SUP_CNTL`, `mmMC_SEQ_IO_DEBUG_INDEX`, and `mmMC_SEQ_IO_DEBUG_DATA`. Including C files combine these offsets with the mask constants through raw `RREG32`/`WREG32` operations or through generic AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` where applicable.

## Control Flow

This header has no runtime control flow. Its effective flow is compile-time macro expansion:

1. A GMC 6.0 consumer includes the generated register offset and mask headers.
2. Driver code selects a register by offset and a field by `REGISTER__FIELD_*` macro.
3. The driver reads, tests, clears, or writes a 32-bit MMIO value using `RREG32`, `WREG32`, or a register-field helper.
4. Hardware interprets the selected bit fields as memory-controller, PHY, PMG, request-buffer, sequencer, or training state.

The most visible runtime flow from this chunk appears in `amdgpu/gmc_v6_0.c`. During memory-controller firmware loading, the driver checks `MC_SEQ_SUP_CNTL__RUN_MASK`, writes supervisor control values to reset and make the sequencer writable, streams firmware IO debug index/data pairs through `MC_SEQ_IO_DEBUG_INDEX` and `MC_SEQ_IO_DEBUG_DATA`, writes sequencer program words through `MC_SEQ_SUP_PGM`, returns the engine to active state, then polls `MC_SEQ_TRAIN_WAKEUP_CNTL__TRAIN_DONE_D0_MASK` and `MC_SEQ_TRAIN_WAKEUP_CNTL__TRAIN_DONE_D1_MASK` until both memory channels report training completion or the device timeout expires.

Other flows are implied by the register groups: memory timing setup writes DRAM, CAS/RAS, miscellaneous timing, and PHY fields; display and graphics clients rely on read-group/request-buffer fields for memory request priority and ordering; power-management paths can program PMG, memory clock, and sequencer page-gating controls; diagnostics can read status, wakeup capture, EDC retrain, performance counter, and debug fields.

## State and Persistence Behavior

The header stores no state. It names fields in GPU hardware registers, and those hardware registers retain or lose state according to the ASIC's reset, suspend, resume, dynamic power management, and memory-training sequences.

Persistent or semi-persistent state represented by this range includes memory PHY electrical tuning, pad enable and power-off bits, drive strengths, RX/TX phase/equalization/VREF controls, memory clock power-management state, mode-register command data, DRAM timing values, sequencer microcode program/control state, request-buffer ordering and queue controls, and page-gating or clock-gating settings. Firmware-provided IO debug arrays written during initialization can materially affect memory training and signal integrity.

Transient and status state includes `MC_NPL_STATUS`, RPB performance counter status, sequencer status master/slave fields, supervisor program/status fields, training wakeup captures, training wakeup clear bits, EDC retrain status/in-progress bits, training timers, and TCG done bits. The macro names alone do not identify read-clear, write-one-to-clear, sticky, or side-effect semantics. Callers must rely on the register programming sequence, hardware documentation, and existing AMDGPU initialization flows.

## Dependencies and Integration Points

This generated header depends only on the C preprocessor, but it must stay synchronized with the GMC 6.0 register-offset header and with AMD's source register database. It is included directly by `amdgpu/gmc_v6_0.c`, `amdgpu/gfx_v6_0.c`, `amdgpu/si.c`, `amdgpu/dce_v6_0.c`, `pm/legacy-dpm/si_dpm.c`, and `display/dc/resource/dce60/dce60_resource.c`.

Important integration points for this chunk are:

- GMC 6.0 memory-controller initialization in `amdgpu/gmc_v6_0.c`, especially sequencer firmware loading, IO debug index/data programming, and polling `MC_SEQ_TRAIN_WAKEUP_CNTL` training-done bits.
- Southern Islands graphics and display code that shares the same generated register namespace and may combine GMC masks with graphics, display, and memory arbitration setup.
- Legacy DPM code that can interact with memory-clock power management, PMG, self-refresh, memory clock switching, and low-power timing fields.
- Firmware and VBIOS data paths that provide IO debug tables and memory-timing values consumed by the driver and interpreted through these register layouts.
- Hardware diagnostics, bring-up, and RAS-style tooling that need to decode sequencer status, request-buffer counters, EDC retraining state, and wakeup captures.

## Risks and Edge Cases

The main risk is silent hardware misprogramming if any generated mask or shift drifts from the actual GMC 6.0 register specification. A wrong bit in this chunk can alter memory PHY training, DRAM timing, page/clock gating, request ordering, or sequencer firmware control without necessarily causing a compile error.

The chunk is heavily repetitive. Debug families repeat the same four `VALUE*` byte fields across DQB, EDC, WCDR, WCK, and 160 `MC_IO_DEBUG_UP_*` registers. Sequencer byte/bit remap, RX framing, D0/D1, and low-power/non-low-power variants also repeat with small name changes. Reviewers should treat generation drift, skipped entries, duplicated entries, or off-by-one register-family ranges as realistic hazards.

Several constants use `0xffffffffL` or high-bit masks such as `0x80000000L`. Callers must use unsigned 32-bit register semantics and avoid sign-extension assumptions from the `L` suffix on platforms where `long` width differs.

Many fields are not ordinary configuration bits. Wakeup clear, training command-generator start/reset, DRAM error insertion, supervisor program/control, mode-register commands, page-gating controls, memory-clock controls, and PHY power-off fields can have immediate hardware side effects. The header does not encode valid sequencing, required delays, timeout policy, or whether a status bit is sticky.

This chunk starts mid-register and ends mid-family. `MC_IO_DEBUG_DQB2L_OFSCAL_D0` begins before line 4470, and `MC_SEQ_TRAIN_WAKEUP_MASK` continues after line 9119. Any final per-file report should merge chunks 1 and 3 before making complete-header claims.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Kernel builds with Southern Islands AMDGPU, display, and legacy DPM enabled should compile without missing `gmc_6_0_sh_mask.h` macro names.
- Static comparison against AMD's generated GMC 6.0 register database should verify every `MASK`/`SHIFT` pair, especially repeated `MC_IO_DEBUG_UP_0..159`, D0/D1, low-power, and wakeup-clear/capture/mask families.
- Field round-trip checks can validate representative masks: `MC_SEQ_TRAIN_WAKEUP_CNTL__TRAIN_DONE_D0/D1`, `MC_SEQ_SUP_CNTL__RUN`, `MC_IO_PAD_CNTL_D1__TXPWROFF_CLK`, `MC_PMG_CFG__ZQCL_SEND`, `MC_RPB_CONF__RPB_*_PCIE_ORDER`, and `MC_SEQ_TCG_CNTL__DONE`.
- Hardware boot tests on GMC 6.0 devices should verify successful memory-controller firmware load, IO debug table programming, memory training completion on both D0 and D1, VRAM sizing, and stable display scanout.
- Suspend/resume and DPM tests should exercise memory clock switching, self-refresh, page/clock gating, PMG wake paths, and restoration of sequencer/PHY state.
- Stress tests should include VRAM bandwidth, display under memory pressure, graphics workloads, and fault/retrain diagnostics where available, watching for training timeouts, EDC retrain status changes, request-buffer stalls, or sequencer status errors.
