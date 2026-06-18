# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj_map.h lines 3809-7747

## Scope And Purpose

This chunk is part of the generated DRX-J register map for the Trident/Hauppauge `drx39xyj` DVB frontend driver. It contains C preprocessor constants only: register addresses, register widths, masks, reset/default values, bit offsets, bit-field masks, and symbolic enum values. There are no executable functions, data structures, or local control-flow statements in this slice.

The covered range starts at the tail of the `ORX_FWP_IQM_FRQ_W` definition and then defines major hardware/firmware control surfaces for:

- OOB receiver (`ORX_*`) equalizer, DDC, controller, NSU/tuner analog controls, and test controls.
- QAM demodulator (`QAM_*`) top-level mode selection, feed-forward and decision-feedback equalizers, slicer, loop controller, Viterbi decoder, synchronizer, and Viterbi RAM base addresses.
- SCU firmware/control (`SCU_*`) command execution state and high RAM variables for AGC, FEC measurement accumulation, GPIO, host/target transfer buffers, ATV helpers, and OOB receiver status/target-mode fields.

The file header says this file is generated and should not be edited manually. Its role is to provide a stable symbolic ABI between `drxj.c` and the device firmware/register map. Driver code includes this header and passes the `__A` address macros, masks, and symbolic values into low-level DAP/FASI accessors such as `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, `drxj_dap_atomic_read_reg32()`, `drxdap_fasi_write_reg32()`, and `drxdap_fasi_write_block()`.

## Register Macro Conventions

Most register definitions follow a generated naming convention:

- `NAME__A` is the device address.
- `NAME__W` is the logical bit width.
- `NAME__M` is the whole-register mask.
- `NAME__PRE` is the reset or preferred initialization value.
- `NAME_FIELD__B`, `NAME_FIELD__W`, `NAME_FIELD__M`, and `NAME_FIELD__PRE` describe a subfield's bit offset, width, mask, and default.
- Further indented `NAME_FIELD_SYMBOL` macros encode legal field values or named operating modes.

The suffixes embedded in names also matter. `_W` registers are generally writable control/configuration points, `_R` registers are read/status or telemetry points, and `_RW` registers are writable/readable coefficient memories. The generated constants themselves do not enforce access direction; correctness depends on callers using the right DAP/FASI read or write helper and applying masks before modifying subfields.

## Important APIs, Types, And Macro Families

OOB equalizer and receiver blocks:

- `ORX_EQU_COMM_EXEC`, `ORX_EQU_COMM_MB`, `ORX_EQU_COMM_INT_REQ`, `ORX_EQU_COMM_INT_STA`, `ORX_EQU_COMM_INT_MSK`, and `ORX_EQU_COMM_INT_STM` define an equalizer command/interrupt surface. `COMM_EXEC` supports `STOP`, `ACTIVE`, and `HOLD`; mailbox fields expose control/observe bits and three-bit control/observe mux fields; interrupt bits distinguish FFF and FBF read completion/status.
- `ORX_EQU_FFF_*` defines feed-forward equalizer configuration: gain scale, LMS update enable, step/learning/rewrite controls, and eleven complex 12-bit coefficients `C0` through `C10` split into real/imaginary `*_RE_RW` and `*_IM_RW` words. The default has `C4RE` preloaded with `0x400`, marking the center/main tap.
- `ORX_EQU_FBF_*` defines a feedback equalizer with LMS update, step/learning/rewrite controls, and six complex 12-bit coefficients `C0` through `C5`.
- `ORX_EQU_ERR_*`, `ORX_EQU_MER_*`, and `ORX_EQU_SYN_LEN_W` expose equalizer error-vector selection/timing, in-phase/quadrature decision and channel error readbacks, MER readout/low-detection threshold, and sync length.
- `ORX_DDC_COMM_*` defines DDC command/interrupt registers. `ORX_DDC_DEC_MAP_W` describes quadrant rotation mappings plus coherent versus differential decoding, and `ORX_DDC_OFO_SET_W` packs phase, `CRXHITIME`, inversion, and disable bits.
- `ORX_CON_*` defines carrier/timing controller controls: load/reset bits for CPH/CTI/KRN/KRP, readbacks for phase/frequency/amplitude/timing, K-factor controls, acquisition/weight-limit thresholds, delay/loop constants, and timing acquisition time.
- `ORX_NSU_*` exposes analog and tuner-side controls: standby bits for ADC, amplifier, bias, PLL, PD, IF/RF TAGC, and baseband analog paths; LO frequency/mode/power; threshold and tuner RF/IF gain; BPF; and bit-swap mapping. Some standby symbols encode different A1/A2 silicon polarity naming for the same bit value, so callers must select values according to chip revision.
- `ORX_TST_COMM_EXEC` and `ORX_TST_AOX_TST_W` provide a small test block.

QAM common, top-level, and equalizer blocks:

- `QAM_COMM_*` defines the QAM-wide command, mailbox, and interrupt registers. Interrupt request bits target slicer (`SL`), loop controller (`LC`), Viterbi decoder (`VD`), and synchronizer (`SY`).
- `QAM_TOP_ANNEX` selects Annex A/B/C/D and defaults to Annex B. `QAM_TOP_CONSTELLATION` selects none, QPSK, QAM8, QAM16, QAM32, QAM64, QAM128, or QAM256 and defaults to QAM64.
- `QAM_FQ_*` defines the feed-forward QAM equalizer. `QAM_FQ_MODE` has tap reset, LMS update, and tap drain bits. `MU_FACTOR`, `LA_FACTOR`, center-tap index/value, and 24 complex 12-bit tap entries `TAP_RE_EL0..23` and `TAP_IM_EL0..23` follow. The center tap default appears at element 19 with `0x600`.
- `QAM_SL_*` defines the slicer block. It has command/mailbox/interrupt controls, slicer mode selection for loop controller, DQ, and Viterbi paths (`RECT`, `ONET`, `RAD`), rotation disable bits, DFE disable, radius mixing, tilt compensation, K factor, median-filter settings, alpha, phase limit, MTA length, median-error readback, and error power.
- `QAM_DQ_*` defines the decision-feedback/adaptive equalizer. `QAM_DQ_MODE` has tap reset/LMS/drain controls plus feedback mode selection (`CMA`, `RADIUS`, `DFB`, `TRELLIS`). It defines MU/LA factors, `CMA_RATIO` presets for QPSK through QAM1024, quality weighting controls/functions, raw limit, and 28 complex tap entries `TAP_RE_EL0..27` and `TAP_IM_EL0..27`.
- `QAM_LC_*` defines the QAM loop controller. It exposes command/mailbox/interrupt bits for ready, overflow, and frequency-wrap signals; enable bits for amplitude/frequency/rate loops; loop coefficients `CA`, `CF`, `CF1`, `CP`, `CI`, `EP`, `EI`; a sparse quality table (`QUAL_TAB0`, `1`, `2`, `3`, `4`, `5`, `6`, `8`, `9`, `10`, `12`, `15`, `16`, `20`, `25`); equalizer timing; LPF factors; rate limit; symbol frequency; MTA length; accumulator readbacks; amplitude; radial error; frequency offset; and phase error.
- `QAM_VD_*` defines the Viterbi decoder command/mailbox/interrupt/status space, lock status, unlock control, min/max voting rounds, traceback depth, measurement period/prescale, fixed-mantissa-plus-exponent telemetry for delta path metric and error counts, and relock count.
- `QAM_SY_*` defines the synchronizer command/mailbox/interrupt/status space, sync timeout, sync low/acquisition/high water marks, unlock request, and control-word register.
- `QAM_VD_ISS_RAM__A`, `QAM_VD_QSS_RAM__A`, and `QAM_VD_SYM_RAM__A` are base addresses for Viterbi-related RAM regions.

SCU and firmware RAM blocks:

- `SCU_COMM_EXEC`/`SCU_COMM_STATE` and `SCU_TOP_COMM_EXEC`/`SCU_TOP_COMM_STATE` define SCU execution state and 16-bit status. `SCU_TOP_MWAIT_CTR` controls monitor-wait selection and ready/NMI behavior.
- `SCU_LOW_RAM__A` and `SCU_HIGH_RAM__A` expose low/high SCU RAM base windows.
- `SCU_RAM_AGC_*` is a dense set of firmware RAM variables for AGC behavior: RF max, fast-sense/clip delays, cycle counters/lengths, RF sense deviation min/max, gain integrator fields, min/max gain limits, gain reduction, clip/sense sums and direction controls, IF/RF accumulators, target levels, cutoff current, IF/RF gain min/max, and clip-control mode.
- `SCU_RAM_FEC_MEAS_COUNT`, `SCU_RAM_FEC_ACCUM_CW_CORRECTED_LO/HI`, and `SCU_RAM_FEC_ACCUM_PKT_FAILURES` are FEC measurement counters or accumulators used by runtime BER/error measurement setup.
- `SCU_RAM_GPIO` packs GPIO0/GPIO1/GPIO3 states plus lock indicators into a 15-bit word.
- `SCU_RAM_INHIBIT_1`, `SCU_RAM_INHIBIT_2`, `SCU_RAM_HTOL_BUF_0/1`, `SCU_RAM_TR_SHORT_BUF_0/1`, and `SCU_RAM_TR_LONG_BUF_0..31` are firmware coordination buffers and inhibit flags.
- `SCU_RAM_ATV_*` covers analog-TV firmware variables such as AMS min/max, field count, AAGC fast/LP2, black-peak level/reliability/MTA/reference/min/max/count/extra-count, and PAGC/BPC minimum KI values.
- `SCU_RAM_ORX_RF_RX_FREQUENCY_VALUE`, `SCU_RAM_ORX_RF_RX_DATA_RATE`, `SCU_RAM_ORX_SCU_STATE`, `SCU_RAM_ORX_SCU_LOCK`, and `SCU_RAM_ORX_TARGET_MODE` expose OOB receiver frequency, data-rate/spectrum mode, SCU state machine state, lock bits, and target data-rate mode. The OOB data-rate symbols encode 2048 kbps, 1544 kbps, and 3088 kbps with regular/inverted spectrum variants and alternate values for 2048 kbps.

## Control Flow And Runtime Behavior

This chunk has no direct control flow. Its runtime behavior is indirect: the macros define numeric constants consumed by `drxj.c` during tune, lock, equalization, spectrum inversion, AGC, and measurement operations.

QAM setup uses these constants in staged hardware programming. `set_qam()` maps frontend standard and constellation into `QAM_TOP_ANNEX_*` and QAM constellation values, then stops communication/execution blocks before programming the demodulator. Constellation-specific helpers write quality function tables starting at `QAM_DQ_QUAL_FUN0__A` and related SCU QAM RAM fields. Viterbi measurement setup derives a measurement period from `QAM_TOP_CONSTELLATION_QAM64` or `QAM_TOP_CONSTELLATION_QAM256`, then writes `QAM_VD_MEASUREMENT_PERIOD__A` and `QAM_VD_MEASUREMENT_PRESCALE__A`.

QAM spectrum/image flipping uses the equalizer and loop-control macros as an operational sequence. The driver freezes frequency control by writing `QAM_LC_CF__A` and `QAM_LC_CF1__A`, freezes DQ/FQ updates through `QAM_DQ_MODE__A` and `QAM_FQ_MODE__A`, clears loop gains such as `QAM_LC_CI__A`, `QAM_LC_EP__A`, and `QAM_FQ_LA_FACTOR__A`, flips the IQM rate offset, negates the imaginary DQ taps using `QAM_DQ_TAP_IM_EL0__A + 2 * i` for 28 taps, negates the imaginary FQ taps using `QAM_FQ_TAP_IM_EL0__A + 2 * i` for 24 taps, then restores the equalizer mode.

AGC configuration code writes many `SCU_RAM_AGC_*` addresses directly when setting IF/RF AGC behavior. It updates target levels, min/max values, accumulator words, KI fields, polarity bits, gain-speed reduction fields, clip/sense thresholds, and direction controls. Subfield masks such as `SCU_RAM_AGC_KI_DGAIN__M`, `SCU_RAM_AGC_KI_RF__M`, `SCU_RAM_AGC_KI_IF__M`, `SCU_RAM_AGC_KI_INV_RF_POL__M`, and `SCU_RAM_AGC_KI_INV_IF_POL__M` are used in read-modify-write sequences.

OOB setup maps user/channel OOB mode and spectrum inversion into `SCU_RAM_ORX_RF_RX_DATA_RATE_*` parameter values before issuing an SCU `DEMOD_SET_ENV` command. The selected value also feeds a local mode index, so these generated numeric encodings are not only register payloads; driver logic interprets their high bits to choose runtime handling.

Interrupt and mailbox macros define expected polling/notification surfaces for hardware blocks, but this header does not provide interrupt handlers. Callers must explicitly write request bits, mask/status/sticky-mask registers, and mailbox muxes in the right sequence for the block they are controlling.

## State And Persistence Behavior

The state represented by this chunk is hardware and firmware state, not Linux kernel object state. Values written through these addresses persist in the demodulator until overwritten, reset, or reinitialized by firmware/driver mode changes. The `__PRE` macros encode generated defaults or preferred reset values and are important for initialization tables, but the header itself does not apply them.

QAM and ORX equalizer tap arrays are stateful adaptive filters. The driver can reset/update/drain taps through mode bits and can inspect or modify tap memories directly. Because the tap registers are contiguous and the driver performs offset arithmetic from element-zero addresses, the generated address ordering for `QAM_DQ_TAP_*` and `QAM_FQ_TAP_*` is part of the runtime contract.

SCU RAM variables are firmware-owned working state. AGC accumulators, FEC counters, GPIO/lock words, transfer buffers, ATV variables, and OOB SCU state are shared between host driver code and embedded firmware. Some are configuration inputs, some are telemetry outputs, and some are mailbox/buffer words. The header cannot distinguish all ownership semantics beyond naming and access suffixes, so callers must follow the firmware command protocol.

Measurement counters are reset and sampled by driver code. For example, FEC accumulation counters are zeroed before measurement windows, and QAM VD period/prescale fields determine how later error counters should be interpreted. Non-atomic multi-register reads can yield mixed-period data unless the caller uses the driver's atomic helpers or follows documented freeze/read protocols.

## Dependencies And Integration Points

This header is included by `drxj.c`. The actual I/O path is provided by low-level DRX DAP/FASI helpers that take these generated addresses and transfer 16-bit, 32-bit, or block payloads over the device access bus, usually backed by I2C.

The `_REGISTERTABLE_` conditional at the top of the file declares `drxj_map[]` and `drxj_map_info[]` if a register-table build mode is enabled. This chunk does not define those arrays; it only contributes macros used by normal driver builds and possibly by register-table tooling.

Frontend integration flows through higher-level `drxj.c` tuning and configuration functions. Linux DVB-facing choices such as standard, constellation, interleaving, mirror/spectrum inversion, OOB mode, AGC settings, and BER measurement periods are translated into these generated register values before being written to the device.

The generated names also integrate with the firmware command protocol. Some `SCU_RAM_*` addresses are direct RAM variables, while OOB/QAM setup uses SCU command parameters whose numeric values come from this map. Changing a macro value without regenerating the rest of the firmware/register artifacts would break that protocol.

## Risks And Edge Cases

- This file is generated. Manual edits risk desynchronizing driver constants from the firmware/register specification and from any optional register-table metadata.
- The chunk starts mid-definition for `ORX_FWP_IQM_FRQ_W`; its `__A` and `__W` lines are in the prior chunk. Merge/reconciliation should preserve that cross-chunk boundary.
- Mask and shift mistakes in caller code can corrupt adjacent bit fields. Several registers pack unrelated controls into the same word, such as SCU AGC KI fields, mailbox control/observe bits, and OOB DDC decode mapping.
- Some symbols have chip-revision or polarity-sensitive meanings. `ORX_NSU_AOX_STDBY_W_*` includes A1/A2 names where ON/OFF meanings can invert for the same bit value.
- Equalizer tap arrays rely on contiguous address layout. Loops that use `QAM_DQ_TAP_IM_EL0__A + 2 * i` and `QAM_FQ_TAP_IM_EL0__A + 2 * i` assume the generated register map remains real/imag interleaved at one-word spacing.
- Width macros are not type-safe. Many registers are narrower than 16 bits but are accessed with 16-bit helpers, so values must be masked. Some QAM Viterbi counters use fixed mantissa/exponent packing inside a 16-bit word, not plain linear counters.
- SCU RAM is shared with firmware. Host writes to firmware-owned state at the wrong time can fight the SCU state machine, invalidate lock acquisition, or produce inconsistent measurement data.
- OOB data-rate symbols encode both data rate and spectrum inversion. The driver also derives a mode index from high bits, so changing those constants affects both command payload and host logic.
- Interrupt status/mask/sticky-mask registers are block-specific and similar-looking. Accidentally mixing `INT_STA`, `INT_MSK`, and `INT_STM` addresses can either lose events or leave interrupts masked/sticky.
- `__PRE` values are generated defaults, not necessarily safe runtime writes in every mode. Some defaults are calibration-like center taps or thresholds that should only be applied during a controlled reset/init sequence.

## Test And Validation Signals

- Build the `drx39xyj` frontend with this header included by `drxj.c`; compile failures catch missing or renamed macros used by QAM, OOB, AGC, and measurement paths.
- Exercise QAM Annex A/B/C tune flows and verify that `QAM_TOP_ANNEX_*`, `QAM_TOP_CONSTELLATION_*`, QAM communication stop/start, and SCU command setup all program successfully.
- Tune QAM16/QAM32/QAM64/QAM128/QAM256 paths and verify that quality-function block writes starting at `QAM_DQ_QUAL_FUN0__A` and constellation-dependent Viterbi measurement periods are accepted by hardware.
- Test spectrum inversion/image-flip behavior. Confirm DQ/FQ update freeze, tap imaginary negation across 28 DQ and 24 FQ taps, and equalizer mode restoration do not break lock.
- Validate AGC setup for IF and RF modes by checking writes to `SCU_RAM_AGC_*` fields, read-modify-write masking of KI/polarity bits, and resulting signal-strength/lock behavior.
- Exercise OOB mode A, B grade A, and B grade B with regular and inverted spectrum. Confirm `SCU_RAM_ORX_RF_RX_DATA_RATE_*` values produce the intended SCU command behavior and lock states.
- Read QAM VD and FEC measurement counters after controlled measurement windows and verify period/prescale handling, saturation limits, fixed mantissa/exponent decoding, and counter reset behavior.
- Check interrupt paths, if enabled by surrounding driver code, by toggling mask/sticky-mask registers for QAM SL/LC/VD/SY and ORX equalizer/DDC blocks and confirming expected status bits.
- Compare generated macro addresses against any vendor register-table output or `_REGISTERTABLE_` tooling when regenerating `drxj_map.h`.

## Cross-Chunk Notes

This chunk is one segment of a much larger generated register map. Earlier chunks define preceding ATV/FEC/IQM/QAM/ORX symbols, and later chunks continue additional `SCU_RAM_ORX_*` lock, timing, reset, and firmware variables after `SCU_RAM_ORX_TARGET_MODE`. The final per-file report should treat this file as a generated hardware ABI rather than hand-written driver logic and should merge adjacent chunks by register block rather than by line count alone.
