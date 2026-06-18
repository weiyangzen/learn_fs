# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 27464-30059

## Scope

This chunk is part of the generated DCN 3.1.6 register shift/mask header used by the AMD display driver. It covers hardware bitfield definitions for output-pixel-processing and output-data-merge related display blocks:

- The tail of `dce_dc_opp_abm0_dispdec`, then complete ABM replicas for `ABM1`, `ABM2`, and `ABM3`.
- Four repeated OPP pipe slices, each with display pattern generator (`DPGx`), formatter (`FMTx`), OPP buffer (`OPPBUFx`), OPP pipe control, and OPP pipe CRC registers.
- DSC remap/forwarding blocks `DSCRM0` through `DSCRM2`.
- OPP top-level clock and ABM selection registers.
- OPP performance monitor register masks for `DC_PERFMON16`.
- ODM input blocks for `ODM0`, `ODM1`, `ODM2`, and the beginning of `ODM3`.

The file contains no functions or runtime code. Its purpose is to expose C preprocessor constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` so register access helpers in the AMD DC code can compose, write, read, and decode DCN 3.1.6 MMIO register fields without hard-coded bit arithmetic at call sites.

## Important API Surface

The exported API is a generated macro namespace. Each register field appears as a pair of constants:

- `...__SHIFT` gives the low bit index for the field.
- `..._MASK` gives the already-positioned mask for the field.

The important register families in this chunk are:

- `ABM[0-3]_BL1_PWM_*` and `ABM[0-3]_DC_ABM1_*`: adaptive backlight management, PWM brightness levels, ambient/user/target/current/final duty-cycle fields, ambient contrast enhancement (`ACE`) curve fields, histogram (`HG`) and luma statistics (`LS`) fields, sample-rate controls, read-progress/missed-frame flags, and master-lock bits.
- `DPG[0-3]_*`: display pattern generator enable, mode, dynamic range, bit depth, active dimensions, ramp controls, RGB/YCbCr pattern colors, segment offsets, and double-buffer-pending status.
- `FMT[0-3]_*`: formatter clamp ranges, dynamic expansion, pixel encoding, subsampling, dither/truncation controls, random dither seeds, clamp enable/color format, 4:2:0 memory low-power controls, and 4:2:2 edge handling.
- `OPPBUF[0-3]_*`: OPP buffer active width, segmentation, overlap, pixel repetition, double-buffer pending, 3D dummy-data/vertical-active spacing, and segment padded pixels.
- `OPP_PIPE[0-3]_OPP_PIPE_CONTROL`: per-pipe clock enable/on status and digital bypass control.
- `OPP_PIPE_CRC[0-3]_*`: per-pipe CRC enable/configuration, one-shot pending state, CRC mask, and result fields for A/R/G/B/C components.
- `DSCRM[0-2]_DSCRM_DSC_FORWARD_CONFIG`: DSC forwarding enable, OPP-pipe source selection, double-buffer pending, and enable status.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`: OPP clock gating/test clock selection, ABM clock-on status for ABM0-3, and backlight PWM source selection.
- `DC_PERFMON16_*`: performance counter event selection, count modes, hardware start/stop/off controls, active state, interrupt enable/status/ack fields, counter state slots 0-7, current-value high/low reads, and read selector.
- `ODM[0-3]_OPTC_*`: ODM input soft reset, underflow interrupt/status/clear fields, double-buffer pending, input/output segment counts, segment source selectors, DSC data format, DSC bytes per pixel, segment/DSC slice widths, input clock control, memory selection/status, and spare register fields. The chunk ends after `ODM3_OPTC_DATA_SOURCE_SELECT`, so the remaining ODM3 fields are in the next chunk.

## Control Flow and State Behavior

There is no direct control flow in this header, but the bitfields model several hardware sequencing patterns that driver code must observe:

- ABM writes are synchronized with lock and double-buffer fields. The `ABM1_HGLS_REG_LOCK`, `ABM1_ACE_LOCK`, `ABM1_BL_MASTER_LOCK`, `*_REG_UPDATE_PENDING`, `*_UPDATE_AT_FRAME_START`, `*_FRAME_START_DISP_SEL`, `*_READBACK_DB_REG_VALUE_EN`, and `*_IGNORE_MASTER_LOCK_EN` fields indicate that parts of ABM state are latched at frame boundaries and may have readback-vs-shadow behavior.
- ABM statistics are frame-derived hardware state. `LS_SUM_OF_LUMA`, `LS_MIN_MAX_LUMA`, filtered min/max, pixel counts, min/max value counts, and `HG_RESULT_1` through `HG_RESULT_24` are hardware-produced measurements. Sample-rate controls can enable counting, reset frame counters, and set frame-count periods.
- `ACE_CNTL_MISC` and `HGLS_REG_READ_PROGRESS` expose missed-frame and clear bits. Code using these fields needs write-one-style clear behavior awareness from the register spec and should not treat status and clear bits as ordinary persistent configuration.
- DPG, FMT, OPPBUF, DSCRM, and ODM fields include double-buffer-pending bits. These are hardware state signals used to confirm whether a programmed update has latched, especially around timing-sensitive mode changes.
- OPP pipe CRC has both continuous and one-shot modes. The `ONE_SHOT_PENDING` field and result registers imply a sequence of enable/configure, wait for completion/pending clear, then read result fields.
- Performance monitor fields encode a small state machine. `PERFMON_STATE`, per-counter `PERFCOUNTER_CNTx_STATE`, active bits, interrupt status/ack bits, run-enable selectors, and current-value reads define runtime sampling behavior, not static configuration.
- ODM input-global fields carry underflow status/current-status/interrupt/clear fields and input soft reset. These are critical display-pipeline health and recovery controls.

## Dependencies and Integration Points

This header is paired with the DCN 3.1.6 offset header, usually `dcn_3_1_6_offset.h`, whose register-address macros share the same register names. Runtime access typically flows through AMD DC register helpers and register lists that combine an offset macro with the corresponding field shift/mask macros from this file.

Downstream integration points include:

- Display Core resource and hardware-sequencer code that initializes OPP/FMT/DPG/ODM blocks during mode set, pipe bring-up, stream enable, DSC routing, and pipe split/ODM combine.
- ABM/backlight code that configures adaptive brightness, luma/histogram collection, sample cadence, and PWM output source selection.
- CRC debug/test paths that program OPP pipe CRC and read component results for validation.
- Performance/debug paths that program `DC_PERFMON16` to count selected display events and acknowledge generated counter interrupts.
- DMUB/DCN 3.1.6 setup tables that include this generated ASIC header to access the right field layout for this hardware revision.

The macro naming and bit positions are an ABI-like contract between generated register headers and the rest of the kernel display driver. Adjacent chunks define previous and later address blocks in the same register namespace; the final per-file research should merge them as one generated hardware register map.

## Risks and Edge Cases

- Field-name repetition across instances is intentional. ABM, DPG, FMT, OPPBUF, OPP pipe, CRC, and ODM instances differ mainly by numeric prefix. A copy/paste or generator error in one instance can silently program the wrong field for only one pipe.
- Some fields are status or acknowledge/clear controls, not normal read-write configuration. Examples include ABM missed-frame clear bits, perfmon interrupt acks, ODM underflow clear, and many `*_PENDING` or `*_STATUS` fields. Generic read-modify-write code can accidentally clear or preserve hardware state incorrectly if it does not know field semantics.
- The `MASK` constants are already shifted. Callers must not shift them again when using common `REG_SET`, `REG_GET`, or field-preparation helpers.
- Several registers pack signed or scaled values into 10-, 11-, 12-, 14-, 16-, 24-, or full 32-bit fields. Bounds errors in callers can truncate brightness levels, ACE slopes/offsets, active dimensions, DSC slice widths, CRC masks, or performance event selectors.
- Lock/update-at-frame-start fields mean mode-set and backlight changes can be asynchronous. Tests that read immediately after a write may observe old shadow state unless they select readback behavior or wait for update-pending bits.
- The chunk boundary cuts `ODM3` in the middle of its register group. Any generated documentation or analysis must reconcile with `subset-b-001909` before treating ODM3 coverage as complete.
- These constants are ASIC-specific. Reusing them for a different DCN revision can produce valid C that writes invalid hardware bit positions.

## Test Signals

Useful validation signals for code paths using this chunk include:

- Build coverage for DCN 3.1.6 display code, ensuring every referenced register field macro resolves with the matching offset macro.
- Mode-set tests across four OPP pipes that exercise FMT pixel encoding/subsampling, DPG patterns, OPPBUF segmentation, and ODM segment/source programming without underflow.
- Backlight/ABM tests that verify PWM level changes, ABM enable/bypass, sample-rate updates, histogram/luma statistic reads, and missed-frame clear behavior.
- DSC/ODM tests that enable DSCRM forwarding and ODM DSC data format/bytes-per-pixel/slice-width fields, then confirm double-buffer pending clears and no ODM underflow status remains set.
- CRC tests that configure each `OPP_PIPE_CRC[0-3]` path in one-shot and continuous modes and compare stable result registers for known DPG output.
- Perfmon tests that select a display event, enable counting/interrupts, observe `PERFCOUNTER_ACTIVE`/state fields, read high/low/current values, and acknowledge interrupt status without leaving counters armed.
