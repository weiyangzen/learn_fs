# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 52501-54982

## Scope

This chunk covers lines 52501-54982 of the generated-style AMD DCE 12.0 register shift/mask header. It contains only C preprocessor constants for bit positions and already-positioned masks. There are no structs, functions, inline helpers, branches, or executable statements in this slice.

The slice starts in the tail of the `DC_COMBOPHYPLLREGS6` PLL register family, then defines the full `UNIPHY8`, `COMBOPHYCMREGS8`, `COMBOPHYTXREGS8`, and `COMBOPHYPLLREGS8` display PHY families, then begins the `DSI0` and `DSI1` MIPI DSI display-interface register families. The chunk ends inside `DSI1_DISP_DSI_DLN0_PHY_ERROR`, so the final per-file merge should reconcile that register with the following chunk.

## Purpose

The purpose of this header region is to publish field-level metadata for low-level AMDGPU display driver code programming DCE 12.0 memory-mapped registers. Each register field appears as a `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pair. Callers combine these constants with companion register-address headers and AMDGPU register access macros to encode, decode, poll, clear, or acknowledge hardware register bits.

The covered hardware domains are:

- COMBOPHY PLL instance 6 tail fields for loop, voltage-regulator, observation, and DFT readout.
- UNIPHY8 macro reserved registers `DCIO_UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159`, each modeled as a full-width reserved field.
- COMBOPHY common instance 8 controls for fuses, lane power management, TX control, TMDS/DisplayPort mode behavior, lane resets, calibration code, and RFU registers.
- COMBOPHY TX instance 8 per-lane controls for four lanes, including command-bus TX settings, margin/de-emphasis, global TX controls, and lane RFU slots.
- COMBOPHY PLL instance 8 frequency, bandwidth, calibration, loop, VREG, observation, and DFT fields.
- DSI0 and the first part of DSI1 MIPI DSI controller fields, including enable/reset, mode programming, DMA command/data windows, command mode, readback, trigger, external TE/reset, lane CRC, ULPS/stop controls, error reporting, timers, PHY clock timing, EOT, BIST, interrupt masking, clock control/status, FIFOs, tearing-effect control, lane status, perf controls, readback count, and command-memory power controls.

## Important Macro Families

`DC_COMBOPHYPLLREGS6_*` at the beginning is a continuation from the prior chunk. It includes PLL loop fields such as feedback slip disable, TDC/NCTL clock selection, PRBS enable, clock gate enable, and phase offset, plus `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT`. These fields are relevant to PHY PLL stability, analog observation, sticky-lock handling, and design-for-test readback.

`DCIO_UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` are repetitive full-register definitions. Each exposes a single `UNIPHY_MACRO_CNTL_RESERVED` field at shift 0 with mask `0xFFFFFFFFL`. Their value is mostly structural: they preserve generated register-map coverage for the UNIPHY8 decode region even when the fields are reserved or undocumented for normal driver programming.

`DC_COMBOPHYCMREGS8_COMMON_*` describes the common PHY-side configuration for instance 8. `COMMON_FUSE1/2/3` expose calibration/fuse controls such as spare fuses, PLL REFCLK/VCO mode fuses, receiver termination, lane-mode margin/de-emphasis values, and RDAC/termination references. `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, and `COMMON_LANE_RESETS` define lane power, TX bus isolation, data enable, TMDS/DP link mode, and per-lane reset/powerdown controls. `COMMON_ZCALCODE_CTRL` and `COMMON_DISP_RFU1` through `RFU7` cover impedance calibration and reserved-for-future-use fields.

`DC_COMBOPHYTXREGS8_*_LANE0` through `LANE3` repeats the same TX register layout per physical lane. `CMD_BUS_TX_CONTROL_LANE*` contains TX enable, high-impedance, and bus isolation controls. `MARGIN_DEEMPH_LANE*` carries transmit margin and de-emphasis settings. `CMD_BUS_GLOBAL_FOR_TX_LANE*` includes boost, calibration, CDR, driver current, bypass, and slew/mode control fields. The `TX_DISP_RFU*_LANE*` registers are full-width RFU slots for each lane.

`DC_COMBOPHYPLLREGS8_*` is the complete PLL instance 8 field set. `FREQ_CTRL0/1/2/3` cover fractional and integer feedback/divider controls, refclk divider, VCO pre-divider, fractional-N enable, spread-spectrum enable, frequency-jump behavior, TDC resolution, and DPLL configuration. `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT` define loop bandwidth, calibration, lock detection, analog/digital observation, regulator behavior, PRBS/test controls, and full-width DFT data.

`DSI0_DISP_DSI_*` is a broad MIPI DSI controller register set. Key groups include:

- `CTRL` and `STATUS` for DSI enable, video/command mode enable, data-lane and clock-lane enables, PHY enables, clock resets, CRTC selection, ECC/CRC checks, busy bits, FIFO state, overflow/underflow status, trigger state, and clear bits.
- `VIDEO_MODE_*` for virtual channel, destination format, traffic mode, low-power behavior during blanking/sync regions, sync/data packet types, payload lengths, pixel datatype, and blanking packet datatype.
- `COMMAND_MODE_*`, `DMA_*`, `DENG_DATA_LENGTH`, `CMD_FIFO_*`, and software trigger registers for command-mode packet construction, DMA command/data addressing, DCS commands, FIFO control, and software-driven command/BTA/reset events.
- `ACK_ERROR_REPORT`, `RDBK_DATA*`, `RDBK_DATATYPE*`, and `RDBK_NUM` for MIPI ACK/error packet classification and readback payload capture.
- `TRIG_CTRL`, `EXT_MUX`, `EXT_TE_PULSE_DETECTION_CTRL`, `EXT_RESET`, and `TE_CTRL` for command trigger source selection, external tearing-effect muxing/polarity/timing, external reset, and TE filtering.
- `LANE_CRC_*`, `PIXEL_CRC_CTRL`, `LANE_CTRL`, `DLN0_PHY_ERROR`, `LANE_STATUS`, and timer/PHY-clock timing registers for lane CRC/readback, ULPS request/exit, force-stop, high-speed clock request, PHY error state, lane stop/ULPS status, low-power/high-speed timers, and D-PHY timing.
- `MIPI_BIST_*` for built-in self-test frame/block size, LFSR mode/init/seed, start, status, and expected/generated CRC.
- `ERROR_INTERRUPT_MASK`, `INTERRUPT_CTRL`, `CLK_CTRL`, `CLK_STATUS`, `DENG_FIFO_STATUS`, `DENG_FIFO_CTRL`, `PERF_CTRL`, `HSYNC_LENGTH`, and `CMD_MEM_PWR_CTRL` for interrupt masking/ack, DSI/byte/escape clock request/enable/status, data-engine FIFO watermarks, performance counters, sync-length programming, and command-memory power gating.

`DSI1_DISP_DSI_*` repeats the same initial DSI register layout as DSI0 from `CTRL` through `LANE_CTRL`, and this chunk includes the beginning of `DLN0_PHY_ERROR`. The naming and masks mirror DSI0 for the covered range, enabling callers to select the DSI instance by macro prefix.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions. The exported interface is the macro namespace itself:

- `REGISTER__FIELD__SHIFT` gives the low-bit offset for an encoded register field.
- `REGISTER__FIELD_MASK` gives the already shifted field mask.
- Some hardware fields naturally end with `_MASK`, producing names such as `*_ERR_ESC_MASK__SHIFT` and `*_ERR_ESC_MASK_MASK`; these are intentional generated symbols, not double-application mistakes.
- Clear/ack fields often share a bit position and mask with the corresponding status field, for example `*_OVERFLOW` and `*_OVERFLOW_CLR` or DSI ACK error bits and their `_CLR` forms.

Because these are global preprocessor symbols, the field names are part of the ABI between generated register metadata and the low-level display driver code. Any rename or mask change can break build-time references or, worse, compile while programming the wrong hardware bit.

## Control Flow

This chunk has no direct control flow. The runtime sequences are implemented by callers using these constants. Typical flows implied by the fields are:

1. Configure PHY/PLL values by masking and shifting frequency, bandwidth, calibration, VREG, or loop-control fields, then poll lock/ready/observation bits through the corresponding register family.
2. Program DSI controller mode: select video or command mode, enable lanes/PHY/clock lane, release DSI clock resets, set CRTC source and packet checking, and then enable the interface.
3. Program MIPI video-mode packetization and timings by writing virtual-channel, datatype, payload, blanking, traffic-mode, and sync fields.
4. Program command-mode DMA and command FIFO offsets, lengths, pitches, dimensions, DCS command controls, and trigger source selection, then issue hardware or software triggers.
5. Monitor DSI status, FIFO, lane, timeout, error, and clock-status fields; clear sticky status or interrupt bits using the matching `_CLR` or ack fields.
6. Enter or exit lane low-power states through ULPS request/exit bits, force TX stop controls, clock-lane high-speed request, timer values, and lane status polling.
7. Exercise diagnostics through lane/pixel CRC, MIPI BIST, readback data registers, DFT outputs, and PHY observation selectors.

The important ordering rules are external hardware rules rather than C code in this header. In particular, resets, PLL changes, DSI clock requests, lane enable/ULPS transitions, BTA/readback, and interrupt clear/ack behavior must be sequenced by the caller against the DCE register specification.

## State and Persistence

The header stores no software state. It describes persistent hardware state held in DCE display registers until reset, power-gated, reprogrammed, or updated by hardware side effects.

State domains visible in this slice include:

- PHY/PLL analog state: calibration codes, loop bandwidth, regulator configuration, lock detection, observation muxes, PRBS/test state, and DFT readout.
- PHY lane state: lane powerdown/reset, TX enable/high-Z/isolation, TMDS/DP mode selection, transmit margin/de-emphasis, driver current, and per-lane RFU state.
- DSI mode state: controller enable, video versus command mode, lane enables, PHY enables, reset state, CRTC routing, ECC/CRC checking, and interleave/pre-trigger behavior.
- DSI packetization state: MIPI virtual channel, traffic mode, datatype values, payload lengths, blanking packet types, command-mode packet types, DMA offsets and dimensions, FIFO thresholds, and null packet values.
- DSI status and error state: busy bits, FIFO empty/full/overflow/underflow, TE abort/contention, ACK/error-report bits, readback data, timeout status, lane PHY error bits, interrupt mask/status/ack, and clock status.
- DSI power/timing state: low-power and high-speed timers, clock timing, EOT packet behavior, command-memory power control, and ULPS/force-stop controls.

Many status fields are sticky until explicitly cleared. The paired `_CLR` and ack macros show write-one-to-clear or write-one-to-ack style behavior, but the header does not encode access type. Callers must avoid normal read/modify/write patterns that accidentally set clear bits or preserve stale clear bits.

## Dependencies and Integration Points

This header depends only on the C preprocessor and companion generated AMD DCE register headers for addresses, offsets, and block instances. It integrates with the AMDGPU DRM display stack under `drivers/gpu/drm/amd`, especially low-level display, clock, PHY, link, and panel/DSI programming paths.

Likely integration points include:

- Register accessor macros that take an address macro plus `*_MASK` and `*__SHIFT` values.
- Display PHY/UNIPHY initialization code selecting COMBOPHY instance 8 and lane 0-3 fields.
- PLL programming and diagnostics for COMBOPHY PLL instances 6 and 8.
- MIPI DSI panel bring-up, command-mode transfer, video-mode transfer, BTA/readback, TE synchronization, reset handling, and lane power-state management.
- Interrupt handling and diagnostics for DSI error/status, FIFO, timeout, lane, and clock events.
- Hardware validation paths using DSI BIST, CRC, DFT, and observation registers.

The parallel `DSI0` and `DSI1` prefix structure is an instance-selection mechanism. The merge lane should check the following chunk for the rest of `DSI1` and determine whether all DSI0 fields are repeated for DSI1.

## Risks

The main risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can write reserved bits, acknowledge the wrong interrupt, clear sticky error state unexpectedly, enable the wrong lane, or leave the display PHY in an unstable mode.

Reserved and RFU registers are especially sensitive. The `UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED*`, `COMMON_DISP_RFU*`, and `TX_DISP_RFU*_LANE*` full-width masks preserve register-map shape but should not be treated as freely writable feature controls without hardware documentation.

Repeated instance and lane layouts create copy/generation hazards. DSI0 and DSI1, four COMBOPHY TX lanes, and many reserved UNIPHY slots are almost identical. A one-character prefix or lane-number mismatch can direct a caller at the wrong register field while remaining syntactically valid.

Status/clear aliases require care. Several fields define both a state bit and a `_CLR` bit at the same mask. Generic helper code that reads a register, modifies unrelated bits, and writes the entire value back can inadvertently clear errors or interrupts if it preserves a read value containing set status bits.

Clock, reset, PLL, and ULPS fields are timing-sensitive. Misordering DSI clock enables, reset release, PLL calibration/lock polling, D-PHY timing, lane stop/ULPS transitions, or command triggers can cause hangs, FIFO underflow, packet errors, or panels failing to respond rather than a clean software failure.

Type width is also relevant. Full-width masks use `0xFFFFFFFFL`; callers should use unsigned 32-bit arithmetic or existing register helpers to avoid sign-extension or truncation issues on unusual host/compiler combinations.

## Test Signals

Useful validation signals for this chunk are mostly build, static, and hardware-integration tests:

- Compile coverage for AMDGPU display translation units that include `dce_12_0_sh_mask.h` and reference COMBOPHY8 or DSI0/DSI1 fields.
- Generated-header consistency checks ensuring every `__SHIFT` has a matching `_MASK`, masks align with shifts, and repeated DSI/lane families match expected widths.
- Diff checks against the authoritative DCE 12.0 register database, especially around the chunk boundaries for `DC_COMBOPHYPLLREGS6` and `DSI1_DISP_DSI_DLN0_PHY_ERROR`.
- Display PHY/link smoke tests that exercise COMBOPHY lane enable, reset, margin/de-emphasis, PLL frequency/calibration, and observation/DFT readback.
- MIPI DSI panel tests covering video mode, command mode, DMA command transfer, BTA/readback, external reset, TE triggering, and clock/reset sequencing on both DSI0 and DSI1 where hardware exposes both instances.
- Error-path tests or register readback diagnostics for DSI FIFO overflow/underflow, ACK error report bits, timeout status, lane PHY errors, interrupt mask/ack behavior, and clear-on-write semantics.
- Diagnostics using DSI lane/pixel CRC and MIPI BIST expected/generated CRC fields to confirm that encoded masks land in the intended bits.
- Power-management tests around DSI command-memory power control, DSI/byte/escape clock request/status, lane ULPS request/exit, and force-stop transitions.

## Cross-Chunk Notes

The beginning of this chunk depends on the previous chunk for the start of `DC_COMBOPHYPLLREGS6_LOOP_CTRL`. The end of this chunk stops after the first `DSI1_DISP_DSI_DLN0_PHY_ERROR__DLN0_ERR_CONTENTION_LP1__SHIFT` definition, before the remaining masks and later DSI1 registers. The final per-file research should merge this with adjacent chunks before drawing conclusions about the complete COMBOPHY6 and DSI1 register families.
