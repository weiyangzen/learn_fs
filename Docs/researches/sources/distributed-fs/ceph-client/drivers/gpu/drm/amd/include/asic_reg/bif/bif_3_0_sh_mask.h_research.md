# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001475`: lines 1-3812, `Docs/researches/chunks/subset-b-001475_research.md`
- `subset-b-001476`: lines 3813-7580, `Docs/researches/chunks/subset-b-001476_research.md`
- `subset-b-001477`: lines 7581-8127, `Docs/researches/chunks/subset-b-001477_research.md`

## Chunk Research

### subset-b-001475: lines 1-3812

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h

Chunk: `subset-b-001475`
Covered source range: lines 1-3812 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h`

## Purpose

This chunk is the front portion of AMD's generated BIF 3.0 register field mask header. It does not implement executable logic; it provides C preprocessor constants that describe bit masks and bit shifts for fields in the BIF/NBIF register block used by older AMD GPU ASIC support code.

The header pairs with `bif_3_0_d.h`, which provides register addresses such as `mmBACO_CNTL`, `ixPB0_PIF_CNTL`, and `ixPB0_TX_LANE*_CTRL_REG0`. This file supplies the field-level constants used to compose, extract, and poll values inside those registers.

The covered range includes:

- top-level BIF/BACO control and status fields;
- bus number, device/function, framebuffer aperture, config aperture, MM index/data, interrupt, debug, reset, scratch, SSA, XDMA, and BIOS scratch field definitions;
- PB0 physical bus interface, PLL, RX, TX, lane, override, power, sequence, and debug fields for lanes 0-15;
- the beginning of equivalent PB1 global/debug/override/status field definitions.

The source range ends at line 3812 in the middle of the PB1 global SCI status override block. Later chunks must complete the PB1 family and the rest of the header before producing a final file-level report.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or exported symbols in this chunk. The API surface is entirely macro constants.

The naming convention is consistent:

- `<REGISTER>__<FIELD>_MASK` is the bit mask to isolate or update the field in a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` is the right-shift count for the field.
- Register names are shared with address macros in `bif_3_0_d.h` and related generation-specific `*_d.h` files.

The chunk contains 3,788 `#define` lines in the assigned range. Excluding the include guard, almost all constants are field masks or shifts. There is one incomplete mask/shift pair at the range boundary: `PB1_GLB_SCI_STAT_OVRD_REG4__FREQDIV_14_MASK` appears at line 3812 and its matching shift is outside this work item.

Important register families in this range include:

- `BACO_CNTL`, `BF_ANA_ISO_CNTL`, `BIF_BACO_DEBUG`, and `BIF_BACO_DEBUG_LATCH`: BACO power-state entry/exit, isolation, reset, power-good, and debug latch fields.
- `BIF_BUSNUM_*` and `BIF_DEVFUNCNUM_*`: bus/device/function capture, list, mask, and autoupdate fields used when BIF filters or tracks host PCI identity.
- `BIF_RESET_EN`: enables and timing fields for soft reset, PHY/PIF/reset-to-config, hot reset, link-disable/down reset, driver reset, strap-valid reset, BIF core reset, and FLR for functions 0-2.
- `BUS_CNTL`, `CONFIG_*`, `MM_INDEX`, `MM_DATA`, `MM_CFGREGS_CNTL`: host aperture, VGA, BIOS ROM, posted/nonposted behavior, config space, and indirect MM register access controls.
- `BIF_FB_EN`, `BIF_XDMA_*`, `BIF_SSA_*`, `HDP_*_COHERENCY_FLUSH_CNTL`: fields around framebuffer access, XDMA apertures, system static aperture windows, and coherency flush controls.
- `INTERRUPT_CNTL` and `INTERRUPT_CNTL2`: interrupt-handler dummy reads, interrupt delay, non-snoop requests, and GPIO/IH interrupt routing.
- `BIF_PERFMON_CNTL` and `BIF_PERFCOUNTER*_RESULT`: performance counter enable, reset, selector, and result fields.
- `PB0_*`: a large generated block for physical bus interface instance 0, including global controls, SCI status overrides, PIF controls, lane pairing, lane power overrides, sequence status, PLL control/override/status, RX/TX global and per-lane controls, TX coefficient accept tables, and TX/RX lane status fields.
- `PB1_*`: the start of a matching physical bus interface instance 1 block, covering DFT, jitter injection, global controls, overrides, and initial SCI status override fields.

## Control Flow

The header has no runtime control flow. Its only compile-time control structure is the include guard:

- `#ifndef BIF_3_0_SH_MASK_H`
- `#define BIF_3_0_SH_MASK_H`

At runtime, these constants participate in control flow in code that reads, modifies, writes, or polls hardware registers. For example, the power-management BACO code uses `BACO_CNTL__BACO_EN_MASK`, `BACO_CNTL__BACO_POWER_OFF_MASK`, `BACO_CNTL__BACO_MODE_MASK`, and related shift constants in command tables that sequence BACO entry and exit. The macros become part of operations such as:

- read a register;
- clear the field mask;
- shift a field value into position;
- OR it into the register value;
- write the register back;
- poll until `(register & mask)` matches an expected value.

The PB0/PB1 PIF, PLL, RX, and TX fields are similarly intended for low-level link bring-up, lane power management, training/debug overrides, electrical idle detection, PLL power/frequency mode reporting, transmitter coefficient handling, and per-lane status inspection.

## State And Persistence Behavior

The header itself has no mutable state and no persistence behavior. It defines numeric constants compiled into whichever translation units include it.

The state affected by these constants is hardware state in memory-mapped or indexed BIF registers. Writes using these masks can persist in device registers until changed by the driver, firmware, reset, BACO transition, PCIe link event, or power-management flow. Scratch-register masks such as `BIF_SCRATCH*`, `BIOS_SCRATCH_*`, and `PB0_PIF_SCRATCH` expose fields whose values may intentionally survive across parts of driver/firmware handoff or diagnostic flows, depending on register retention rules outside this header.

Because the constants are generated from hardware register descriptions, correctness depends on exact mask and shift values matching the ASIC's register specification. A wrong constant does not fail locally; it can silently set the wrong bit in persistent hardware state.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The header is consumed alongside BIF address headers, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_d.h`
- other generation-specific BIF/NBIF `*_d.h` and `*_sh_mask.h` headers

Known integration points visible in the tree include:

- `drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c`, which includes `bif/bif_3_0_sh_mask.h`;
- BACO power-management flows such as `ci_baco.c`, `fiji_baco.c`, `smu7_baco.c`, and newer generation variants that use same-named BACO field masks for command-table read/modify/write and wait operations;
- register helper macros and accessors in AMDGPU/PowerPlay code that expect the `<REG>__<FIELD>_MASK` and `<REG>__<FIELD>__SHIFT` naming style.

The header is architecture-specific. It should be included only in code paths that operate on hardware matching BIF 3.0 register layouts or compatibility layers that deliberately reuse these definitions. Adjacent ASIC generations may share names while changing fields, masks, or register addresses.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Since these are plain numeric macros, the compiler cannot validate that a mask belongs to the register being accessed or that the matching shift is used.

Mask/shift pairs must remain synchronized. A copy/paste or generator error in either half can make field extraction and updates incorrect. This matters especially for multi-bit fields such as reset delay selectors, lane pairing, PLL divider/frequency modes, RX/TX power states, and TX coefficient fields.

The chunk boundary is in the middle of a generated field family. Line 3812 includes `PB1_GLB_SCI_STAT_OVRD_REG4__FREQDIV_14_MASK` without its matching shift in this range, so any analysis of PB1 is incomplete until later chunks are merged.

Many PB0 definitions are repeated per lane and per lane group. Off-by-one lane numbering, lexicographic ordering (`10` before `1` in some generated blocks), or accidental use of `PB0` fields against `PB1` registers can be hard to detect in review.

Several fields control destructive or disruptive hardware behavior: BACO power-off/isolation/reset, BIF reset enables, PIF power overrides, PLL override controls, RX/TX frontend power, lane reset, and debug/test modes. Incorrect writes can hang the PCIe link, break device resume, or require a full GPU reset.

The file relies on `L`-suffixed hexadecimal constants. They are intended for 32-bit register values, but callers should avoid signed arithmetic surprises and should use the driver's normal unsigned register types when combining masks.

Generated headers are usually not unit-tested directly. Regression risk is highest when regenerating from a new register database, manually editing a field, or mixing headers from different ASIC generations.

## Test Signals

Useful validation is mostly build, register-access, and hardware behavior coverage:

- Compile coverage for translation units that include `bif_3_0_sh_mask.h`, especially legacy DPM and PowerPlay paths.
- Static checks that every `_MASK` in the generated header has a matching `__SHIFT` and that no duplicate macro names have conflicting values. The assigned range intentionally has one incomplete pair at the boundary.
- Consistency checks against `bif_3_0_d.h`: field macro register prefixes should map to address macros with the same register names.
- BACO enter/exit tests on supported ASICs, validating `BACO_CNTL` mode transitions, power-good fields, isolation controls, reset enable behavior, and recovery after resume.
- PCIe link bring-up, link speed change, ASPM/L0s/L1 transitions, FLR, hot reset, link-down reset, and driver reset tests that exercise `BIF_RESET_EN`, `PB0_PIF_*`, `PB0_PLL_*`, `PB0_RX_*`, and `PB0_TX_*` fields.
- Runtime register readback tests for representative single-bit and multi-bit fields to confirm mask/shift extraction returns expected values after controlled writes.
- Suspend/resume and low-power tests that verify scratch, BACO, PIF power, PLL power, and RX/TX lane state do not regress.
- Hardware debug or lab validation for per-lane PB0/PB1 fields, because lane-indexed constants can compile cleanly while targeting the wrong physical lane.

### subset-b-001476: lines 3813-7580

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

### subset-b-001477: lines 7581-8127

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h lines 7581-8127

## Purpose

This chunk is the closing register-field mask/shift section for the AMD BIF 3.0 generated header. It defines C preprocessor constants that describe bit layouts for PCIe/BIF registers rather than executable code. The paired address header is `bif_3_0_d.h`; this file supplies the per-field `*_MASK` and `*__SHIFT` values used with those register addresses.

The covered range starts in the middle of the PCIe PRBS error-counter definitions and then covers the tail of the BIF register map:

- PCIe PRBS checker/counter fields, receive L0s FTS detection, and PCIE/PCIEP scratch or reserved registers.
- PCIe link-control and function strap fields, including function enablement and advertised PCIe capabilities for functions F0-F2.
- PCIe receive-side controls, error/unsupported-request ignore controls, completion timeout controls, receive credits, sequence numbers, NAK counters, and last-TLP capture registers.
- PCIe transmit-side controls, requester ID, sequence/replay status, advertised and initialized flow-control credits, and credit error/status fields.
- WPR reset policy bits, peer frame-buffer offset windows, peer register ranges, slave hang/credit controls, SMBus pad controls, and the BACO SMBus dummy register.

The final `#endif` closes the `BIF_3_0_SH_MASK_H` include guard. The chunk therefore completes the generated BIF 3.0 mask header and should be reconciled with preceding chunks for a full per-file view.

## Important APIs, Types, And Functions

There are no functions, structs, or runtime APIs in this chunk. The important interface is the set of macro names and their stable generated naming convention:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask for a field.
- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for extracting or inserting that field.
- Full-width registers use `0xffffffffL` masks and shift `0`, such as PRBS error counters, `PCIE_RX_LAST_TLP*`, `PCIE_TX_LAST_TLP*`, scratch registers, and `SMBUS_BACO_DUMMY`.
- Multi-bit fields preserve their hardware width, for example `PCIE_RX_CNTL__RX_RCB_CPL_TIMEOUT_MASK`, `PCIE_TX_REPLAY__TX_REPLAY_TIMER_MASK`, `PCIE_STRAP_MISC__STRAP_MAX_PASID_WIDTH_MASK`, and peer range start/end address fields.

The macros in this chunk are meaningful only alongside BIF 3.0 register address macros from `bif_3_0_d.h`, such as `ixPCIE_RX_CNTL`, `ixPCIE_TX_CNTL`, `ixPCIE_PRBS_MISC`, `ixPCIE_STRAP_F0`, `mmPEER0_FB_OFFSET_LO`, `mmSLAVE_HANG_ERROR`, `mmSMBCLK_PAD_CNTL`, and `mmSMBUS_BACO_DUMMY`.

Key groups in this range:

- PRBS diagnostics: `PCIE_PRBS_ERRCNT_3` through `PCIE_PRBS_ERRCNT_9`, `PCIE_PRBS_FREERUN`, `PCIE_PRBS_HI_BITCNT`, `PCIE_PRBS_LO_BITCNT`, `PCIE_PRBS_MISC`, `PCIE_PRBS_STATUS1`, `PCIE_PRBS_STATUS2`, and `PCIE_PRBS_USER_PATTERN`.
- PCIe port and strap configuration: `PCIE_P_RCV_L0S_FTS_DET`, `PCIEP_STRAP_LC`, `PCIEP_STRAP_MISC`, `PCIE_STRAP_F0` through `PCIE_STRAP_F7`, `PCIE_STRAP_I2C_BD`, `PCIE_STRAP_MISC`, `PCIE_STRAP_MISC2`, and `PCIE_STRAP_PI`.
- Receive path: `PCIE_RX_CNTL`, `PCIE_RX_CNTL2`, `PCIE_RX_CNTL3`, `PCIE_RX_CREDITS_ALLOCATED_*`, `PCIE_RX_EXPECTED_SEQNUM`, last-TLP capture, NAK counters, and `PCIE_RX_VENDOR_SPECIFIC`.
- Transmit path: `PCIE_TX_ACK_LATENCY_LIMIT`, `PCIE_TX_CNTL`, `PCIE_TX_CREDITS_*`, `PCIE_TX_REPLAY`, `PCIE_TX_REQUESTER_ID`, `PCIE_TX_REQUEST_NUM_CNTL`, `PCIE_TX_SEQ`, and `PCIE_TX_VENDOR_SPECIFIC`.
- BIF fabric/support registers: `PCIE_WPR_CNTL`, `PEER[0-3]_FB_OFFSET_{HI,LO}`, `PEER_REG_RANGE[0-1]`, `SLAVE_HANG_ERROR`, `SLAVE_HANG_PROTECTION_CNTL`, `SLAVE_REQ_CREDIT_CNTL`, `SMBCLK_PAD_CNTL`, `SMBDAT_PAD_CNTL`, and `SMBUS_BACO_DUMMY`.

## Control Flow

This header has no control flow. All behavior comes from compile-time macro substitution in source files that include it. Callers typically read a 32-bit hardware register, mask and shift a field out, or construct a value by shifting an input and applying the mask before writing the register through AMDGPU register-access helpers.

The order of definitions follows the generated register-map order. The assigned range begins with `PCIE_PRBS_ERRCNT_3__PRBS_ERRCNT_3__SHIFT`; the matching `PCIE_PRBS_ERRCNT_3__PRBS_ERRCNT_3_MASK` appears immediately before this chunk. That line-boundary split is important for merge reconciliation because the `ERRCNT_3` field is incomplete if reviewed from this chunk alone.

## State And Persistence Behavior

The header itself stores no software state and performs no hardware access. The persistent state affected by users of these macros is the BIF/PCIe hardware register state on Sea Islands-era AMD GPUs:

- Strap fields describe or override link/function capability exposure, including ACS, AER, MSI, VC, BAR, DPA, ATS, page request, PASID, power management, link configuration, lane reversal, and FLR support.
- RX/TX control fields can alter how the PCIe block handles malformed TLPs, unsupported requests, completion timeouts, NAK generation, relaxed ordering/no-snoop behavior, flow-control updates, replay timers, and requester IDs.
- Credit fields expose or configure posted, non-posted, and completion header/data credits, both allocated on RX and advertised/initialized/status on TX.
- Peer FB offsets and peer register ranges define windows used for peer access routing or aperture translation.
- Slave hang/error and request-credit fields persistently tune BIF access crediting and hang detection until reset or later driver/firmware reprogramming.
- SMBus pad-control fields persist pad mode, selection, slew, Schmitt trigger, wake, and drive/control bits for the SMB clock/data pins.

Because these are raw bit definitions, there is no locking, allocation, reference counting, or validation here. Ordering, concurrency, and register side effects are controlled entirely by the driver code that uses the macros.

## Dependencies And Integration Points

This file depends on the AMD ASIC register-generation contract: every mask and shift must match the BIF 3.0 hardware specification and the address macros in `bif_3_0_d.h`. The suffixes `ix` and `mm` in the paired address header distinguish indirect-indexed PCIe register spaces from direct MMIO registers; these mask definitions are shared by both access styles according to the register named in the macro.

Direct include points in this source tree include AMDGPU Sea Islands components such as `amdgpu/si.c`, `amdgpu/gfx_v6_0.c`, `amdgpu/gmc_v6_0.c`, `amdgpu/dce_v6_0.c`, and `pm/legacy-dpm/si_dpm.c`. Those files can combine BIF 3.0 address constants, these masks, and AMDGPU register helpers to program GPU initialization, power management, PCIe link behavior, memory controller/BIF aperture setup, display bring-up, and diagnostics.

The chunk also has cross-generation relevance. Similar fields appear in later `bif_*`, `nbif_*`, and `nbio_*` mask headers, sometimes with changed field names or extra bits. Code that is generic across ASIC generations must include the correct generation header and avoid assuming BIF 3.0 masks match newer NBIF/NBIO layouts.

## Risks And Edge Cases

The primary risk is silent register-field drift. A wrong mask or shift compiles cleanly but can program the wrong hardware bit, misread status, or leave a field unchanged. This is especially risky for control fields that suppress PCIe errors or timeouts, such as `RX_IGNORE_*`, `RX_PCIE_CPL_TIMEOUT_DIS`, `RX_RCB_CPL_TIMEOUT`, `TX_REPLAY_TIMER`, and `TX_FC_UPDATE_TIMEOUT_DIS`.

Strap fields are capability-sensitive. Incorrect function strap bits can advertise unsupported capabilities, hide required capabilities, or change function enumeration behavior for MSI, AER, ACS, ATS, PASID, page-request, BAR, power-management, virtual-channel, lane, and FLR support. Since many strap values are latched or firmware-influenced, driver writes may be constrained by timing or platform policy.

Several counters and capture registers are full-width fields. Code should not shift these values unnecessarily or treat them as signed quantities. Conversely, narrow fields such as peer offsets, credit counts, requester ID bus/device/function fields, and SMBus pad controls require proper mask/shift handling to avoid clobbering neighboring bits.

The chunk includes reserved-register masks (`PCIEP_RESERVED`, `PCIE_RESERVED`, and reserved `PCIE_STRAP_F3` through `F7`). These should not be interpreted as safe writable feature fields; full-width masks on reserved registers are generated descriptions, not permission to write arbitrary values.

Peer offset and range registers can affect address-routing behavior. Programming `PEER*_FB_OFFSET_LO__PEER*_FB_EN`, high/low offset fields, or `PEER_REG_RANGE*` with stale values can expose the wrong aperture or break peer access paths.

The first line of this chunk is a continuation of the previous PRBS counter field. Any automated extraction or review process that reasons about complete fields must merge adjacent chunks or tolerate a split mask/shift pair at the line boundary.

## Test Signals

Useful validation is mostly compile-time, register-dump, and hardware-behavior oriented:

- Build coverage for the Sea Islands AMDGPU paths that include `bif_3_0_sh_mask.h`; missing or renamed macros should fail compilation in `si.c`, `gfx_v6_0.c`, `gmc_v6_0.c`, `dce_v6_0.c`, or `si_dpm.c`.
- Static register-map checks can compare every `REGISTER__FIELD_MASK`/`__SHIFT` pair against the generated BIF 3.0 source data and against paired addresses in `bif_3_0_d.h`.
- PCIe link bring-up and resume should keep expected negotiated width/speed, requester ID, completion behavior, replay/NAK behavior, and flow-control credit status after initialization.
- PCIe error-handling tests should observe expected AER/UR/completion-timeout behavior when RX ignore bits are enabled or disabled by the driver or firmware policy.
- PRBS diagnostics should show sane lock, bit-count, free-run, user-pattern, and per-lane error-counter behavior when exercising PCIe PHY test modes.
- Peer aperture tests should verify that `PEER[0-3]_FB_OFFSET_{HI,LO}` and `PEER_REG_RANGE[0-1]` route only the intended windows and that disabling `PEER*_FB_EN` blocks the corresponding path.
- SMBus/BACO tests should confirm that `SMBCLK_PAD_CNTL`, `SMBDAT_PAD_CNTL`, and `SMBUS_BACO_DUMMY` accesses do not regress BACO or board-management sideband behavior.

## Cross-Chunk Notes

The final per-file research should merge this tail with earlier chunks that define the rest of `bif_3_0_sh_mask.h`, including BACO, BIF bus numbering, BIOS scratch, config aperture, interrupt, performance counter, PCIe PHY/link, and the beginning of the PRBS register set. This chunk supplies the closing PCIe RX/TX, strap, peer-window, hang-protection, SMBus pad, and final include-guard context.
