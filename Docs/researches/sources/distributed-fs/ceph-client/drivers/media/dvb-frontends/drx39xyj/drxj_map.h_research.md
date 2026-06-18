# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj_map.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004063`: lines 1-3808, `Docs/researches/chunks/subset-b-004063_research.md`
- `subset-b-004064`: lines 3809-7747, `Docs/researches/chunks/subset-b-004064_research.md`
- `subset-b-004065`: lines 7748-11615, `Docs/researches/chunks/subset-b-004065_research.md`
- `subset-b-004066`: lines 11616-15055, `Docs/researches/chunks/subset-b-004066_research.md`

## Chunk Research

### subset-b-004063: lines 1-3808

# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj_map.h lines 1-3808

## Scope

This chunk is the first 3,808 lines of the generated DRXJ register map header. The full file has 15,055 lines; this chunk starts at the license/header guard and ends in the first ORX FWP register block at `ORX_FWP_IQM_FRQ_W__W`. It is generated from `reg_map` by `IDF:x 1.3.0` and explicitly warns not to hand-edit it.

The chunk contains no C functions, structs, or executable branches. Its purpose is to publish compile-time register metadata for the DRX39xxJ demodulator driver: register addresses (`__A`), field widths (`__W`), masks (`__M`), reset/default or preset values (`__PRE`), bit offsets (`__B`), and named encoded values for hardware modes. Under `_REGISTERTABLE_`, it can also expose `drxj_map[]` and `drxj_map_info[]` from `<registertable.h>`, but the normal Linux driver path uses the preprocessor constants directly.

## Register Map Families In This Chunk

- Lines 56-100: `ATV_COMM_*` common analog-TV block controls, status/mailbox/interrupt registers, and the magic key value `0xFABA`.
- Lines 102-523: `ATV_TOP_*` analog-TV top block, including common exec/state/mailbox/interrupt registers; carrier recovery, equalizer, rotation, modulation, video standard, video amplitude/peak, sync slice, SIF gain/test points, standby, SFR override, and analog output format registers.
- Lines 525-536: `ATV_AFT_*` automatic frequency tuning exec/test definitions.
- Lines 538-669: `AUD_COMM_*` and `AUD_TOP_*` audio top-level exec, mailbox, transfer FIFO control/status, timer, and demod TBO selection registers.
- Lines 671-1327: `AUD_DEM_*` and `AUD_DSP_*` audio demodulator/DSP control, status, thresholds, I2S, AVC, FM/NICAM, RDS, firmware revision, DC level, and sync-output registers.
- Lines 1328-1362: `AUD_XFP_*` and `AUD_XDFP_*` audio DRAM/PRAM windows.
- Lines 1364-1421: `FEC_COMM_*` and `FEC_TOP_*`, including FEC exec/interrupt routing and annex selection.
- Lines 1423-2617: `FEC_DI_*`, `FEC_RS_*`, and `FEC_OC_*`, covering data input, Reed-Solomon measurement/error counters, output controller status, DTO/TMD/RCN/SNC/OCR controls, MPEG input/output pin mode/inversion fields, and FEC RAM windows.
- Lines 2618-3593: `IQM_*`, covering common IQ manager control, frequency/rate correction, rotator, channel filter taps, power measurements, analog-front-end monitor/ADC/AGC/standby registers, and rotator RAM.
- Lines 3594-3808: start of `ORX_*`, including ORX common/top controls, OOB receiver ADC interface controls, and the start of front-wave processor parameters.

## Important API Surface

The exported API is the naming convention itself:

- `<REGISTER>__A`: hardware address used with access helpers such as `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, `drxdap_fasi_write_block()`, and atomic 32-bit helpers in `drxj.c`.
- `<REGISTER>__W`: field/register width in bits. The driver uses this mainly as documentation and for register-table tooling; runtime masking generally uses `__M`.
- `<REGISTER>__M`: full-register or bit-field mask. These masks are used directly when extracting status and constructing values, for example FEC RS error mantissa/exponent fields, FEC output pin inversion fields, audio FIFO status, and IQM AGC values.
- `<REGISTER>__PRE`: hardware preset/default value. The driver writes many `__PRE` values during initialization or mode transitions, so these constants are part of the device configuration contract.
- `<REGISTER>_<FIELD>__B`: bit offset for a field.
- `<REGISTER>_<FIELD>__W`, `__M`, `__PRE`: per-field width, mask, and preset.
- `<REGISTER>_<FIELD>_<NAME>` or `<REGISTER>_<NAME>`: encoded enum-like values for hardware modes.

High-value constants in this chunk include:

- Execution states shared across blocks: `*_COMM_EXEC_STOP`, `*_COMM_EXEC_ACTIVE`, and `*_COMM_EXEC_HOLD`.
- Unlock keys: `ATV_COMM_KEY_KEY`, `ATV_TOP_COMM_KEY_KEY_KEY`, and `ORX_TOP_COMM_KEY_KEY`, all using `0xFABA`.
- Analog video/audio modes: `ATV_TOP_STD_MODE_*`, `ATV_TOP_STD_VID_POL_*`, `ATV_TOP_MOD_CONTROL_*`, `ATV_TOP_AF_SIF_ATT_*`, `ATV_TOP_STDBY_*`, and `ATV_TOP_OUT_CONF_*`.
- Audio standard selection/status: `AUD_DEM_WR_STANDARD_SEL_STD_SEL_*`, `AUD_DEM_RD_STANDARD_RES_STD_RESULT_*`, `AUD_DEM_RD_STATUS_*`, and RDS counters/data.
- Audio DSP controls: `AUD_DSP_WR_VOLUME`, `AUD_DSP_WR_SRC_I2S_MATR_*`, `AUD_DSP_WR_AVC_*`, `AUD_DSP_WR_QPEAK_*`, `AUD_DEM_WR_I2S_CONFIG2_*`, `AUD_DSP_WR_AV_SYNC_*`, and firmware revision reads.
- FEC measurement/status: `FEC_RS_NR_BIT_ERRORS_*`, `FEC_RS_NR_SYMBOL_ERRORS_*`, `FEC_RS_NR_PACKET_ERRORS_*`, `FEC_RS_NR_FAILURES_*`, and `FEC_OC_SNC_FAIL_COUNT/PERIOD`.
- FEC output configuration: `FEC_OC_IPR_MODE_*`, `FEC_OC_IPR_INVERT_*`, `FEC_OC_OCR_*`, `FEC_OC_DTO_*`, `FEC_OC_TMD_*`, and `FEC_OC_RCN_*`.
- IQM tuning and signal quality: `IQM_FS_RATE_*`, `IQM_RC_RATE_*`, `IQM_RC_STRETCH_*`, `IQM_RT_*`, `IQM_CF_OUT_ENA_*`, `IQM_CF_TAP_RE0..27`, `IQM_CF_TAP_IM0..27`, `IQM_CF_POW*`, `IQM_AF_AGC_IF`, and `IQM_AF_AGC_RF`.
- Analog front-end hardware mode bits: `IQM_AF_ADC_CONF_*`, `IQM_AF_CLKNEG_*`, `IQM_AF_CLP_*`, `IQM_AF_SNS_*`, `IQM_AF_PGA_GAIN`, `IQM_AF_PDREF`, and `IQM_AF_STDBY_*`.
- OOB receiver setup: `ORX_TOP_MDE_W_RATE_*`, `ORX_TOP_AIF_CTRL_W_*`, `ORX_FWP_AAG_*`, `ORX_FWP_PFI_*`, `ORX_FWP_SRC_DGN_W_*`, and Nyquist coefficient address/data registers.

## Control Flow And Runtime Use

This header has no runtime control flow; it is a data declaration layer for hardware access. Runtime flow appears in `drxj.c`, which includes this header and passes these constants into DAP/FASI I2C helpers.

The effective control flow pattern is:

1. A caller selects a device mode or reads a frontend metric.
2. `drxj.c` writes `*_COMM_EXEC__A` registers with `STOP`, `ACTIVE`, or `HOLD` values for the relevant hardware blocks.
3. It writes configuration registers using the `__A` addresses and encoded values/masks from this header.
4. It reads status/counter registers and masks fields with `__M` values before reporting Linux DVB status, BER, SNR, signal strength, or audio/OOB state.

Examples visible in the driver integration:

- Power-down paths write `ATV_COMM_EXEC__A`, `IQM_COMM_EXEC__A`, `IQM_FS_COMM_EXEC__A`, `IQM_FD_COMM_EXEC__A`, `IQM_RC_COMM_EXEC__A`, `IQM_RT_COMM_EXEC__A`, `IQM_CF_COMM_EXEC__A`, and `AUD_COMM_EXEC__A` to `STOP`.
- QAM and other receive paths configure FEC output and IQM using constants from this chunk, including `FEC_OC_OCR_INVERT__A`, `FEC_OC_FCT_USAGE__A`, `FEC_OC_TMD_*`, `FEC_OC_RCN_*`, `FEC_OC_SNC_*`, `IQM_FS_ADJ_SEL__A`, `IQM_RC_ADJ_SEL__A`, `IQM_CF_ADJ_SEL__A`, and `IQM_CF_OUT_ENA__A`.
- Signal-strength logic reads `IQM_AF_AGC_IF__A` and `IQM_AF_AGC_RF__A` and masks with `IQM_AF_AGC_IF__M` and `IQM_AF_AGC_RF__M`.
- BER/error reporting reads `FEC_RS_NR_BIT_ERRORS__A`, `FEC_RS_NR_SYMBOL_ERRORS__A`, `FEC_RS_NR_PACKET_ERRORS__A`, `FEC_RS_NR_FAILURES__A`, and `FEC_OC_SNC_FAIL_COUNT__A`, then applies masks and field shifts from this header.
- OOB setup writes `ORX_COMM_EXEC__A`, `ORX_TOP_MDE_W__A`, `ORX_FWP_AAG_LEN_W__A`, `ORX_FWP_AAG_THR_W__A`, `ORX_FWP_PFI_A_W__A`, `ORX_FWP_NYQ_ADR_W__A`, and `ORX_FWP_NYQ_COF_RW__A`. Later ORX/SCU registers are outside this chunk but are part of the same OOB initialization flow.

## State And Persistence Behavior

The header itself has no mutable software state and no persistence. The state it describes lives in hardware registers and RAM windows on the demodulator. The constants define how driver code mutates or observes that hardware state.

State-sensitive areas:

- `*_COMM_EXEC`, `*_COMM_STATE`, `*_COMM_MB`, `*_COMM_INT_*` define block lifecycle, mailbox control/observe routing, and interrupt state.
- `ATV_TOP_*` contains analog video/audio path configuration, standby bits, equalizer coefficients, and output formatting. Some values are mirrored in `drxj.h` state fields such as shadows of `ATV_TOP_EQU0..3`, `ATV_TOP_VID_PEAK`, and `ATV_TOP_NOISE_TH`.
- `AUD_*` registers define audio standard detection, thresholds, RDS data availability, I2S output, volume, AVC, sync, and audio firmware revision observations.
- `FEC_RS_*` and `FEC_OC_*` hold measurement counters and output-controller state that persist until reset/measurement rollover or explicit reconfiguration.
- `IQM_*` registers hold front-end frequency/rate correction, channel-filter tap coefficients, power measurement, ADC/AGC/standby state, and rotator delay RAM.
- `ORX_*` registers configure OOB receiver mode, ADC format, front-wave filtering, PFI coefficients, and Nyquist coefficient access.

Because hardware state outlives a single helper call, safe sequencing matters: the driver often stops a block, writes many parameters, then restarts it. Directly writing one of these addresses without the expected stop/configure/start sequence can leave the demodulator in an inconsistent acquisition state.

## Dependencies And Integration Points

- Primary consumer: `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj.c`, which includes `drxj_map.h` and uses these constants for low-level demodulator register I/O.
- Public/private state definitions: `drxj.h` references several `ATV_TOP_*` registers as shadowed fields in the demodulator state.
- Generic frontend integration: `drx39xxj.h`, `drx_driver.h`, and Linux DVB frontend APIs expose higher-level tuning/status controls that eventually map down to these registers.
- Access path: the values are consumed by FASI/DAP helper functions using the demodulator I2C address. Audio registers have special handling through audio transfer FIFO control registers such as `AUD_TOP_TR_CTR__A` and `AUD_TOP_TR_RD_REG__A`.
- Optional register-table tooling: `_REGISTERTABLE_` enables declarations for `drxj_map[]` and `drxj_map_info[]`; this is not the normal in-kernel path but matters for generated-map diagnostics or external tooling.
- Cross-chunk dependency: later sections of `drxj_map.h` define SIO, SCU, QAM, OFDM, VSB, and later ORX/NSU/DDC registers. This chunk already participates in flows that use those later constants, especially OOB and QAM setup.

## Risks And Edge Cases

- Generated-file drift: hand edits are risky. The driver contains local DJCOMBO patches and duplicate/override constants in `drxj.c`, which means regenerating this file without reconciling those patches can silently change behavior.
- Address correctness is critical. A single wrong `__A` value can write to the wrong hardware block over I2C; there is no compile-time protection beyond symbol names.
- Mask and shift consistency is critical. Many values are pre-shifted masks or encoded values, not plain unshifted enums. Mixing shifted constants with raw numeric fields can corrupt adjacent bits.
- Width/sign ambiguity: several registers hold signed or fixed-point values in unsigned `u16` transfers, including FEC error mantissa/exponent fields, IQM taps, AGC values, and OOB gain/coefficients. Callers must preserve the hardware representation.
- Audio register access is special. `DRXJ_ISAUDWRITE()` in `drxj.c` routes some audio addresses through transfer-FIFO protocol; using generic read/write assumptions for `AUD_*` can fail or deadlock if FIFO status bits are ignored.
- Hardware sequencing risk: `*_COMM_EXEC_ACTIVE/STOP/HOLD`, key registers, and standby registers are not independent configuration flags. Wrong order can leave ATV/AUD/FEC/IQM/ORX inactive, held, or using stale coefficients.
- Register aliases exist. For example, some audio read addresses overlap in the demod map; code must use the intended mask and semantic symbol for interpretation.
- The chunk boundary splits the ORX FWP block after `ORX_FWP_IQM_FRQ_W__W`, so later fields for that register and subsequent ORX blocks must be researched in later chunks before producing a whole-file summary.

## Test And Validation Signals

Useful validation for changes around this map is mostly integration or hardware-backed:

- Build signal: the DRX39xxJ driver must compile with `drxj.c` including this header; missing or renamed constants will fail compilation.
- Register access smoke tests: attaching a supported DRX39xxJ demodulator should allow init/open, firmware load, and block activation without I2C errors.
- Analog TV/audio paths: tune analog standards and verify `ATV_TOP_*` configuration, audio standard detection results from `AUD_DEM_RD_STANDARD_RES__A`, audio status bits from `AUD_DEM_RD_STATUS__A`, volume/I2S/AV-sync controls, and RDS reads.
- Digital/QAM paths using this chunk: verify QAM acquisition and stable FEC lock after writes to `FEC_*` and `IQM_*`; read BER/uncorrected blocks through `FEC_RS_*` and `FEC_OC_SNC_*`.
- Signal-strength path: compare `IQM_AF_AGC_IF/RF` based signal strength against known RF input levels.
- OOB path: verify mode selection for 1544 kbps, 2048 kbps, and 3088 kbps using `ORX_TOP_MDE_W_RATE_*`, PFI/Nyquist coefficient writes, and ORX activation.
- Regression checks should include endianness/word-oriented I2C transfers because DAP/FASI helpers split addresses and 16-bit data around this map's address constants.

## Chunk Notes For Merge Lane

This chunk should be merged with later `drxj_map.h` chunks to produce the final source-tree-aligned file report. For this chunk, the important whole-file signals are that `drxj_map.h` is a generated hardware register contract, not algorithmic driver logic; it is tightly coupled to `drxj.c` access helpers and to hardware state sequencing. Later chunks are needed to cover SIO/SCU/QAM/OFDM/VSB and the rest of ORX before any final per-file report can claim whole-file coverage.

### subset-b-004064: lines 3809-7747

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

### subset-b-004065: lines 7748-11615

# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj_map.h lines 7748-11615

## Scope

This chunk is a generated register-map slice from `drxj_map.h`, covering line 7748 through line 11615. It is not executable logic; it defines preprocessor constants that encode hardware/firmware register addresses, widths, masks, reset/default values, bit positions, and enumerated values for the Trident/Hauppauge DRX-J frontend driver.

The chunk begins in the SCU RAM out-of-band receiver (`SCU_RAM_ORX_*`) region at address `0x831F06`, continues through ATV, QAM, VSB, SCU command mailbox/version registers up to `0x831FFF`, then enters SIO host/serial/pad register regions from `0x400000`, `0x410000`, `0x420000`, `0x430000`, `0x440000`, `0x450000`, `0x460000`, and `0x7F0000`. The next merge lane should treat this as a partial register-map report for the larger generated header.

## Purpose

The purpose of this chunk is to expose symbolic names for memory-mapped register contracts used by `drxj.c` and related driver code when programming the DRX-J demodulator firmware through DAP/FASI access helpers. The definitions let the C code use names such as `SCU_RAM_COMMAND__A`, `SCU_RAM_PARAM_0__A`, `SCU_RAM_QAM_FSM_RTH__A`, or `SIO_PDR_GPIO_CFG__A` instead of raw register addresses and bit masks.

Every top-level register follows the generated naming pattern:

- `*_A`: absolute register address.
- `*_W`: field/register width in bits.
- `*_M`: mask for valid bits.
- `*_PRE`: generated reset/default/preload value.
- Nested `*_B`, `*_W`, `*_M`, `*_PRE`: bitfield offset, width, mask, and preload within a register.
- Leaf constants without suffixes: legal enum values already shifted into their target bit positions when the associated mask is not zero-based.

## Important Register Groups

### SCU RAM ORX and ATV window, lines 7748-8453

The chunk starts with OOB receiver RAM status and control registers around `0x831F06` to `0x831F47`. These include MER minimum, RF/IF gain actual/min/max, analog and digital gain loop parameters, frequency/phase/timing/equalizer lock thresholds, lock windows, lock masks, frequency gain correction presets for 1544/2048/3088 kbps, and reset controls for carrier phase/timing/kernel loops. The reset fields use boolean-style enum values such as `DISABLE` and `ENABLE`.

The ATV section begins at `SCU_RAM_ATV_STANDARD__A` (`0x831F48`) and includes standard selection values for MN, B, G, DK, L, LP, I, and FM; detection enable and threshold; lock/sync status bits; AGC mode fields; AMS max reference defaults by TV standard; active AM extrema; video gain high/low; SIF gain; rate/LO/IIR control; and AGC integrator limits/thresholds. Many `SCU_RAM_ATV_RSV_*` entries are reserved address holders that preserve the generated memory layout.

### SCU RAM QAM configuration, lines 8454-9336

The QAM write/configuration region starts at `SCU_RAM_QAM_PARAM_ANNEX__A` (`0x831F74`) and defines:

- Annex selection: A, B, C, D.
- Constellation selection: unknown, QAM16, QAM32, QAM64, QAM128, QAM256.
- Interleave selection, including many `I*_J*` combinations, `UNKNOWN`, and `AUTO`.
- Symbol recovery rate high/low words and alternate rate high/low words.
- Equalizer center tap and reserved write slots.
- QAM FSM tuning registers for hum timeout, median/radius averaging, LC average offsets, target/override state, amplitude/rate/frequency/phase/median/cluster thresholds, and rate/frequency/count limits.
- Loop-control coefficient banks for CA, CP, CI, EP, EI, CF, and CF1 coarse/medium/fine tuning.
- Signal power and CMA equalizer radii `SCU_RAM_QAM_EQ_CMA_RAD0..5`.
- `SCU_RAM_QAM_CTL_ENA__A`, a 16-bit enable bitmap for QAM blocks such as AMP, ACQ, EQU, SLC, LC, AGC, FEC, AXIS, FMHUM, EQTIME, and EXTLCK.

This is one of the most actively used parts of the chunk. `drxj.c` writes QAM set-point tables by calling `drxdap_fasi_write_block()` at `SCU_RAM_QAM_EQ_CMA_RAD0__A` and many `drxj_dap_write_reg16()` calls against `SCU_RAM_QAM_FSM_*`, `SCU_RAM_QAM_LC_*`, and `SCU_RAM_QAM_SL_SIG_POWER__A`.

### SCU RAM QAM read/status and events, lines 9285-9836

The read/status QAM block defines active constellation/interleave, QAM lock, event occurrence masks, event schedule masks, tasklet schedule/run masks, active symbol rate words, AGC target-power offset, FSM state/current and new state, FSM lock flags, rate/frequency variation, error state, error lock flags, equalizer lock, equalizer state, and reserved read locations.

`SCU_RAM_QAM_LOCKED__A` splits into an internal lock progression level (`NOT_LOCKED`, `AMP_OK`, `RATE_OK`, `FREQ_OK`, `UPRIGHT_OK`, `PHNOISE_OK`, `TRACK_OK`, `IMPNOISE_OK`) and a coarser locked result (`NOT_LOCKED`, `DEMOD_LOCKED`, `LOCKED`, `NEVER_LOCK`). The event registers expose pre/post BER, packet fail, PRBS, lock in/out, FIFO full/empty, grab/change, FSM change, timer, clip, sense, power, median, MER, loop, frequency wrap, SER, Viterbi/symbol lock in/out, syncword, equalizer lock in/out, MPEG lock in/out, and reserved bits.

### SCU RAM VSB, command mailbox, and version, lines 9843-10157

The VSB block starts at `SCU_RAM_VSB_CTL_MODE__A` (`0x831FD7`) with AGC and monitor mode bits, notch threshold, reserved slots, AGC power target, outer-loop cycle, field number, and segment number. `drxj.c` writes `SCU_RAM_VSB_AGC_POW_TGT__A` during VSB/AGC setup, so width and mask correctness matter for tuner behavior.

The generic SCU mailbox appears at `SCU_RAM_PARAM_15__A` through `SCU_RAM_PARAM_0__A`, followed by `SCU_RAM_COMMAND__A`, `SCU_RAM_VERSION_HI__A`, and `SCU_RAM_VERSION_LO__A`. `SCU_RAM_PARAM_0__A` enumerates ATV/QAM `SET_ENV` parameters and result codes (`RESULT_OK`, `RESULT_UNKCMD`, `RESULT_UNKSTD`, `RESULT_INVPAR`, `RESULT_SIZE`). `SCU_RAM_PARAM_1__A` enumerates `GET_LOCK` results. `SCU_RAM_COMMAND__A` enumerates standard demod commands (`RESET`, `SET_ENV`, `SET_PARAM`, `START`, `GET_LOCK`, `GET_PARAM`, `HOLD`, `RESUME`, `STOP`), QAM IRQ/debug/admin commands, auxiliary atomic access, and high-byte standard selectors for ATV, QAM, VSB, OFDM, OOB, and TOP.

`drxj.c` uses these mailbox definitions in `scu_command()`: it polls `SCU_RAM_COMMAND__A` for ready state, writes `SCU_RAM_PARAM_0..4__A` according to parameter length, writes the combined command word, waits for readiness again, reads `SCU_RAM_PARAM_0..3__A` for results, and maps fixed result codes from `SCU_RAM_PARAM_0_*` to `-EINVAL` or `-EIO`. Because this command path is a firmware ABI, any address, mask, or enum change can break standard selection, lock polling, and error handling.

### SIO communication, host register access, debug, serial, and pad regions, lines 10158-11615

After the SCU RAM window, the chunk defines SIO-side blocks:

- `SIO_COMM_*` at `0x400000`: command execution, state, mailbox, and interrupt request/status/mask/sticky registers.
- `SIO_TOP_*` at `0x410000`: top-level execution, unlock/update key, and JTAG ID words.
- `SIO_HI_RA_RAM_*` at `0x420010`: host-interface register-access slave slots S0/S1, CRC/access flags, bank/block/address buffers, command/result/parameter mailbox registers, I2C control, and virtual-bank mapping entries/offsets.
- `SIO_HI_IF_*` at `0x430000` and `0x440000`: trap breakpoints/stack registers and high-interface execution/debug stack/breakpoint controls.
- `SIO_CC_*` at `0x450000`: clock/control PLL mode, lock, clock delay/invert, powerdown level, soft reset, and update key.
- `SIO_SA_*` at `0x460000`: serial-access execution, interrupts, prescaler, TX/RX data/length/command/status.
- `SIO_PDR_*` at `0x7F0000`: pad-ring/pin-drive register controls for monitoring, feedback, SMA RX/TX, UIO inputs/outputs, PWM outputs, OOB pins, GPIO/IRQ, and MPEG transport stream pins through `SIO_PDR_MD3_CFG__A`.

These SIO definitions are primarily low-level hardware interface constants. They connect to DAP/FASI, serial access, pad configuration, and hardware bring-up paths elsewhere in the driver or adjacent chunks of the generated map.

## APIs, Types, and Functions

This chunk defines no C functions, structs, or callable APIs. Its effective API is the set of macros consumed by driver routines. Important consumers visible outside the chunk include:

- `scu_command()` in `drxj.c`, which depends on `SCU_RAM_PARAM_*__A`, `SCU_RAM_COMMAND__A`, command enums, result-code enums, and standard selector bit values.
- QAM setup functions in `drxj.c`, which use `SCU_RAM_QAM_EQ_CMA_RAD0__A`, `SCU_RAM_QAM_FSM_*__A`, `SCU_RAM_QAM_LC_*__A`, and `SCU_RAM_QAM_SL_SIG_POWER__A` for constellation-specific tuning.
- VSB/AGC setup in `drxj.c`, which uses `SCU_RAM_VSB_AGC_POW_TGT__A`.
- OOB setup in `drxj.c`, which uses adjacent ORX/SCU command constants; this chunk includes the later ORX loop and reset fields plus OOB-capable `SCU_RAM_COMMAND_STANDARD_OOB`.

The concrete access APIs are in `drxj.c` and related support code, not in this header slice: `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, and `drxdap_fasi_write_block()` use the `_A` constants as hardware addresses and the surrounding enum values as payloads.

## Control Flow and State Behavior

There is no runtime control flow inside the header. The state model encoded by the constants is hardware/firmware state:

- SCU RAM `PARAM_*` and `COMMAND` registers form a persistent command mailbox while the demodulator firmware processes commands. Driver code writes parameter registers, writes a command word, then waits until firmware clears/returns the command register to ready.
- QAM tuning registers persist programmed thresholds, loop gains, equalizer radii, and enable bits in demodulator RAM. Status registers expose active constellation/interleave, lock phase, FSM state, event occurrence flags, and equalizer state.
- ORX/ATV/VSB registers persist standard-specific gain, lock, frequency, timing, equalizer, and AGC state.
- SIO registers persist host-interface routing, serial access, clock/reset/power, pad drive, UIO, PWM, and transport pin configuration.

Because this is generated hardware ABI data, persistence is in the device/firmware register file, not in kernel memory. The macros themselves are compile-time constants.

## Dependencies and Integration Points

The file is guarded by `__DRXJ_MAP__H__` and optionally exposes `drxj_map[]` and `drxj_map_info[]` under `_REGISTERTABLE_` with `<registertable.h>`. Normal driver compilation mostly consumes the macro definitions.

Integration depends on:

- The DRX-J firmware register layout matching these generated addresses and bit encodings.
- Kernel I2C/DAP/FASI helpers issuing correctly sized 16-bit register accesses and block writes.
- Higher-level DVB frontend control paths translating standards, constellations, symbol rates, interleave modes, OOB modes, and lock polling into the command/register values defined here.
- Adjacent chunks of `drxj_map.h` defining earlier SCU RAM, QAM, AGC, ORX, and DAP symbols referenced by the same functions.

The map was generated from `reg_map` by `IDF:x 1.3.0` in 2010; manual edits are explicitly discouraged in the file header.

## Risks

- Address or enum drift is high impact: driver writes would target the wrong firmware registers, especially for the SCU mailbox and QAM tuning tables.
- Some enum constants are pre-shifted to their bit positions, for example command standard selectors and QAM lock result values. Treating them as unshifted field values would produce invalid command words or status comparisons.
- Reserved registers are part of the address layout. Removing or renumbering them can break block writes and generated-table alignment even when the names look unused.
- Many widths are narrower than 16 bits despite 16-bit access helpers. Callers must respect masks when composing values; invalid high bits may be ignored, latched, or interpreted as reserved hardware controls.
- `SCU_RAM_COMMAND__A` command codes reuse low-byte values across QAM IRQ, debug, admin, and auxiliary command spaces. Correct high-byte standard/context bits are required to disambiguate.
- Status/event bits are hardware-driven and may be clear-on-read or sticky depending on firmware behavior not visible in this chunk. Tests should avoid assuming ordinary RAM semantics unless confirmed elsewhere.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware/firmware tests:

- Build coverage: compile the `drx39xyj` driver with this header and ensure all referenced macros resolve.
- SCU command smoke tests: exercise reset, set environment, start, get lock, and stop paths; verify `scu_command()` sees `SCU_RAM_COMMAND__A` return ready and maps `SCU_RAM_PARAM_0_*` errors correctly.
- QAM tune tests: tune QAM16/32/64/128/256 paths and verify the driver writes the expected FSM, LC, CMA radius, and signal power values without DAP write errors.
- Lock/status tests: read `SCU_RAM_QAM_LOCKED__A`, FSM state, lock flags, event occurrence registers, and equalizer lock/state while tuning to known-good and no-signal inputs.
- VSB setup tests: verify `SCU_RAM_VSB_AGC_POW_TGT__A` programming in VSB mode and check field/segment counters progress.
- SIO/bring-up tests: check JTAG ID, PLL lock, soft reset/update key, serial access, UIO/PWM, and pad-drive configuration where the board design exposes those paths.

## Open Questions for Merge Lane

- The source chunk starts after earlier ORX definitions, so merge should combine this with prior chunks before making whole-file statements about ORX command parameters.
- Many SIO definitions in this slice may be consumed outside the visible `SCU_RAM_*` search set. A final per-file report should include a full-symbol usage pass for `SIO_*` across the directory.
- Hardware side effects such as clear-on-read, write-one-to-clear, or sticky event semantics are not documented by the generated names alone and should be inferred only if adjacent driver code or vendor docs confirm them.

### subset-b-004066: lines 11616-15055

# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj_map.h lines 11616-15055

## Scope And Purpose

This chunk covers the final part of the generated DRX-J register map header. The file is generated from Trident's `reg_map` input and is included by `drxj.c`; it does not implement executable logic. Instead, it publishes preprocessor constants that the DRX39xyJ DVB frontend driver uses to address demodulator hardware registers through the DAP/FASI access helpers.

The assigned line range starts in the middle of the SIO pad-driver register definitions, continues through SIO GPIO function-selection registers, defines the VSB demodulator communication and top-level control/status map, defines two VSB sysctrl RAM windows used for equalizer/feed-forward/leak/gain tuning tables, and ends with three VSB RAM aperture base addresses for TCMEQ, FCPRE, and EQTAP data.

The constants follow a consistent generated convention:

- `*_A` is the hardware address used by `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, `drxdap_fasi_write_block()`, and similar accessors.
- `*_W` is the bit width of the full register or subfield.
- `*_M` is the unshifted or shifted mask for the register/subfield.
- `*_PRE` is the power-on/reset or preferred default value emitted by the generator.
- Nested field constants add `_*FIELD*__B`, `__W`, `__M`, and `__PRE` for bit position, width, mask, and reset/default.

This chunk is not Ceph-specific despite the mirrored source tree path. It is media frontend hardware-description data for the DRX39xyJ demodulator.

## Important Register Blocks And Macros

SIO pad-driver and GPIO function map:

- `SIO_PDR_MD4_CFG__A` through `SIO_PDR_MD7_CFG__A` define remaining MPEG transport data pad configuration registers at `0x7F002F` through `0x7F0032`. The chunk begins just after `SIO_PDR_MD3_CFG__A`, so the final report should merge this with the preceding chunk for the complete MPEG data-pad set.
- Each MPEG data pad configuration register has `MODE`, `DRIVE`, `KEEP`, and `UIO` fields. In this chunk the full pad register width is 9 bits, mask `0x1FF`, and default/preferred value is typically `0x50`.
- `SIO_PDR_I2C_SCL1_CFG__A`, `SIO_PDR_I2C_SDA1_CFG__A`, `SIO_PDR_I2C_SDA2_CFG__A`, and `SIO_PDR_I2C_SCL2_CFG__A` describe I2C pad configuration registers. Their defaults use `MODE__PRE 0x1` and full-register `__PRE 0x11`, distinguishing them from MPEG data pads.
- `SIO_PDR_VSYNC_CFG__A`, `SIO_PDR_SMA_RX_CFG__A`, `SIO_PDR_SMA_TX_CFG__A`, `SIO_PDR_I2S_CL_CFG__A`, and `SIO_PDR_I2S_DA_CFG__A` define video sync, smart-antenna, and I2S pad registers with the same `MODE`/`DRIVE`/`KEEP`/`UIO` shape.
- `SIO_PDR_GPIO_GPIO_FNC__A`, `SIO_PDR_IRQN_GPIO_FNC__A`, `SIO_PDR_MSTRT_GPIO_FNC__A`, `SIO_PDR_MERR_GPIO_FNC__A`, `SIO_PDR_MCLK_GPIO_FNC__A`, `SIO_PDR_MVAL_GPIO_FNC__A`, `SIO_PDR_MD0_GPIO_FNC__A` through `SIO_PDR_MD7_GPIO_FNC__A`, `SIO_PDR_SMA_RX_GPIO_FNC__A`, and `SIO_PDR_SMA_TX_GPIO_FNC__A` define 2-bit GPIO function selectors at `0x7F0050` through `0x7F005F`.

VSB communication registers:

- `VSB_COMM_EXEC__A` at `0x1C00000` exposes the VSB firmware/subsystem execution control state. It provides symbolic values `VSB_COMM_EXEC_STOP`, `VSB_COMM_EXEC_ACTIVE`, and `VSB_COMM_EXEC_HOLD`.
- `VSB_COMM_MB__A` defines a 16-bit VSB mailbox register.
- `VSB_COMM_INT_REQ__A`, `VSB_COMM_INT_STA__A`, `VSB_COMM_INT_MSK__A`, and `VSB_COMM_INT_STM__A` define the VSB interrupt request/status/mask/sticky-mask style registers. The request and status registers expose single-bit subfields for `COMM_INT_REQ` and `COMM_INT_STA`.

VSB top-level control and status registers:

- `VSB_TOP_COMM_EXEC__A`, `VSB_TOP_COMM_MB__A`, `VSB_TOP_COMM_INT_REQ__A`, `VSB_TOP_COMM_INT_STA__A`, `VSB_TOP_COMM_INT_MSK__A`, and `VSB_TOP_COMM_INT_STM__A` repeat the communication pattern for the VSB top block at base `0x1C10000`.
- Clock and carrier tracking gain registers include `VSB_TOP_CKGN1ACQ__A`, `VSB_TOP_CKGN1TRK__A`, `VSB_TOP_CKGN2ACQ__A`, `VSB_TOP_CKGN2TRK__A`, `VSB_TOP_CKGN3__A`, `VSB_TOP_CYGN1ACQ__A`, `VSB_TOP_CYGN1TRK__A`, `VSB_TOP_CYGN2ACQ__A`, `VSB_TOP_CYGN2TRK__A`, and `VSB_TOP_CYGN3__A`.
- State-machine and mux/control registers include `VSB_TOP_SYNCCTRLWORD__A`, `VSB_TOP_MAINSMUP__A`, `VSB_TOP_EQSMUP__A`, `VSB_TOP_SYSMUXCTRL__A`, `VSB_TOP_CYSMSTATES__A`, `VSB_TOP_EQSMRSTCTRL__A`, `VSB_TOP_EQSMTRNCTRL__A`, `VSB_TOP_EQSMRCA1CTRL__A`, `VSB_TOP_EQSMRCA2CTRL__A`, `VSB_TOP_EQSMDDM1CTRL__A`, `VSB_TOP_EQSMDDM2CTRL__A`, `VSB_TOP_SYSSMRSTCTRL__A`, `VSB_TOP_SYSSMCYCTRL__A`, `VSB_TOP_SYSSMTRNCTRL__A`, `VSB_TOP_SYSSMEQCTRL__A`, `VSB_TOP_SYSSMAGCCTRL__A`, and `VSB_TOP_SYSSMCTCTRL__A`.
- Signal-quality and lock-status registers include `VSB_TOP_SNRTH_RCA1__A`, `VSB_TOP_SNRTH_RCA2__A`, `VSB_TOP_SNRTH_DDM1__A`, `VSB_TOP_SNRTH_DDM2__A`, `VSB_TOP_SNRTH_PT__A`, `VSB_TOP_SNR__A`, `VSB_TOP_LOCKSTATUS__A`, `VSB_TOP_MEASUREMENT_PERIOD__A`, `VSB_TOP_NR_SYM_ERRS__A`, `VSB_TOP_ERR_ENERGY_L__A`, and `VSB_TOP_ERR_ENERGY_H__A`.
- Equalizer/AGC/tap-control registers include `VSB_TOP_EQCTRL__A`, `VSB_TOP_PREEQAGCCTRL__A`, `VSB_TOP_PREEQAGCPWRREFLVLHI__A`, `VSB_TOP_PREEQAGCPWRREFLVLLO__A`, `VSB_TOP_CORINGSEL__A`, `VSB_TOP_BEDETCTRL__A`, `VSB_TOP_LBAGCREFLVL__A`, `VSB_TOP_UBAGCREFLVL__A`, `VSB_TOP_AGC_TRUNCCTRL__A`, `VSB_TOP_BEAGC_*`, `VSB_TOP_CFAGC_*`, `VSB_TOP_FIRSTLARGFFETAP*`, `VSB_TOP_SECONDLARGFFETAP*`, `VSB_TOP_FIRSTLARGDFETAP*`, and `VSB_TOP_SECONDLARGDFETAP*`.
- Notch and burst-noise related registers include `VSB_TOP_SMALL_NOTCH_CONTROL__A`, `VSB_TOP_NOTCH1_BIN_NUM__A`, `VSB_TOP_NOTCH2_BIN_NUM__A`, `VSB_TOP_NOTCH_START_BIN_NUM__A`, `VSB_TOP_NOTCH_STOP_BIN_NUM__A`, `VSB_TOP_NOTCH_TEST_DURATION__A`, `VSB_TOP_RESULT_LARGE_PEAK_BIN__A`, `VSB_TOP_RESULT_LARGE_PEAK_VALUE__A`, `VSB_TOP_RESULT_SMALL_PEAK_BIN__A`, `VSB_TOP_RESULT_SMALL_PEAK_VALUE__A`, `VSB_TOP_NOTCH_SWEEP_RUNNING__A`, `VSB_TOP_NOTCH_SCALE_1__A`, `VSB_TOP_NOTCH_SCALE_2__A`, `VSB_TOP_BNFIELD__A`, `VSB_TOP_CLPLASTNUM__A`, `VSB_TOP_BNSQERR__A`, `VSB_TOP_BNTHRESH__A`, and `VSB_TOP_BNCLPNUM__A`.
- Phase/lock accumulation registers include `VSB_TOP_PHASELOCKCTRL__A`, `VSB_TOP_DLOCKACCUM__A`, `VSB_TOP_PLOCKACCUM__A`, `VSB_TOP_CLOCKACCUM__A`, `VSB_TOP_DCRMVACUMI__A`, and `VSB_TOP_DCRMVACUMQ__A`.
- `VSB_TOP_PHASELOCKCTRL__A` is one of the more important multi-field controls in this range. Its subfields include force-polarity and force-PLL bits for D, P, and C paths plus `IQSWITCH`.

VSB sysctrl RAM and RAM windows:

- `VSB_SYSCTRL_RAM0_*` begins at `0x1C20000` and runs through `VSB_SYSCTRL_RAM0_FIRRCA1GAIN8__A` at `0x1C2007F`.
- `VSB_SYSCTRL_RAM1_*` begins at `0x1C30000` and runs through `VSB_SYSCTRL_RAM1_DFEDDM2GAIN__A` at `0x1C30035`.
- RAM0 contains 12-entry sequences for FFE train leak ratios, FFE RCA1/RCA2 train/data leak ratios, FFE DDM1/DDM2 train/data leak ratios, FIR train gains, and the first eight FIR RCA1 gain words.
- RAM1 continues FIR RCA1 gains 9-12, defines FIR RCA2 gain words 1-12, FIR DDM1/DDM2 gain words 1-12, and then defines aggregate DFE leak-ratio and gain controls for RCA1/RCA2/DDM1/DDM2 train/data paths.
- Most RAM0 leak-ratio definitions are 12-bit fields (`__W 12`, `__M 0xFFF`). FIR gain words are 15-bit composite words with separate 7-bit train and data gain subfields at bit 0 and bit 8. This is reflected in subfield pairs such as `*_FIRRCA1TRAINGAIN*` and `*_FIRRCA1DATAGAIN*`.
- `VSB_TCMEQ_RAM__A` at `0x1C40000`, `VSB_FCPRE_RAM__A` at `0x1C50000`, and `VSB_EQTAP_RAM__A` at `0x1C60000` define larger RAM apertures with one generated subfield each (`TCMEQ_RAM`, `FCPRE_RAM`, and `EQTAP_RAM` respectively).

## Runtime Control Flow And Usage

The header contributes constants to runtime flows in `drxj.c`.

For MPEG/output pad handling, `ctrl_set_cfg_mpeg_output()` and related output-control logic write SIO PDR registers to switch MPEG transport stream pads between input, serial output, and parallel output. The code uses address macros such as `SIO_PDR_MD4_CFG__A` through `SIO_PDR_MD7_CFG__A` and field-position macros such as `SIO_PDR_MD0_CFG_DRIVE__B` and `SIO_PDR_MD0_CFG_MODE__B` to compose the pad values. When the transport output is disabled or serial-only, the driver writes zero to unused MD pad configuration registers, effectively tri-stating those pins.

For smart-antenna and UIO-related pin control, the driver writes pad config and GPIO function selector registers such as `SIO_PDR_SMA_TX_CFG__A`, `SIO_PDR_SMA_RX_CFG__A`, `SIO_PDR_GPIO_CFG__A`, `SIO_PDR_IRQN_CFG__A`, and the function selectors in this chunk. This lets higher-level smart-antenna or GPIO configuration code decide whether a pin is controlled as a hardware function or general-purpose I/O.

For 8VSB setup, `set_vsb()` first stops the VSB communication executor through `VSB_COMM_EXEC__A` along with FEC and IQM executors, resets/configures the demodulator through SCU commands, writes VSB top-level parameters such as CF/BE AGC gain shifts, carrier tracking gains, burst/noise thresholds, SNR thresholds, equalizer control, and measurement period, then restarts the VSB executor with `VSB_COMM_EXEC_ACTIVE`.

For VSB equalizer and leak/gain initialization, `set_vsb_leak_n_gain()` writes two packed byte tables with `drxdap_fasi_write_block()`. The first block starts at `VSB_SYSCTRL_RAM0_FFETRAINLKRATIO1__A`; the second starts at `VSB_SYSCTRL_RAM1_FIRRCA1GAIN9__A`. Those start addresses depend on the contiguous generated ordering in this chunk. The comments in the initializer arrays line up one-for-one with the RAM0/RAM1 symbols defined here.

For link-quality reporting, the VSB measurement helpers read:

- `VSB_TOP_NR_SYM_ERRS__A` to report pre-Viterbi BER-related symbol error counts.
- `VSB_TOP_ERR_ENERGY_H__A` to calculate VSB MER.
- `VSB_TOP_MEASUREMENT_PERIOD__A` is written during VSB setup so later count calculations use the same measurement window.

There are no C functions, call graphs, locking paths, or allocation paths inside this header itself. Its control-flow role is indirect: it determines which physical register or RAM location each `drxj.c` access reaches.

## State And Persistence Behavior

The constants in this chunk model persistent hardware state rather than software-owned memory state.

SIO pad configuration state persists in the demodulator registers until changed by the driver, hardware reset, or power-state transition. The generated `__PRE` values document expected reset/default states, but runtime code often overwrites them depending on transport-output mode, smart-antenna mode, or low-power/safe pad handling.

VSB `COMM_EXEC` state persists in hardware and gates whether the VSB processing subsystem is stopped, active, or held. The runtime sequence deliberately stops VSB while mode setup and RAM table writes occur, then restarts it after IQM/FEC/VSB configuration is complete. A stale or incorrect `COMM_EXEC` value can leave the VSB datapath inactive even though frontend software state says a standard has been selected.

VSB top-level register state stores live acquisition/tracking, equalizer, AGC, burst-noise, notch, phase-lock, and measurement configuration. Some registers are write-only or tuning-oriented from the driver's perspective; others are status/measurement registers sampled after the demodulator is running.

VSB sysctrl RAM0/RAM1 state stores table-driven equalizer leak and gain parameters loaded by the driver. The tables are not mirrored as a C struct after the block write; the durable copy for the running demodulator is in hardware RAM. Because `drxdap_fasi_write_block()` writes raw bytes to the generated base address, table length, byte order (`DRXJ_16TO8()` packing), and address continuity are the persistence contract.

The generated `__M`, `__B`, and `__W` values are also a form of static state contract. They encode the hardware layout expected by hand-written bit composition in `drxj.c`. If these constants drift from the silicon/firmware register map, the driver can silently set the wrong bits while still compiling cleanly.

## Dependencies And Integration Points

Direct code dependency:

- `drxj.c` includes `drxj_map.h` and consumes the generated constants throughout mode setup, pad configuration, VSB setup, quality measurement, firmware control, and low-power transitions.

Hardware access dependency:

- Address macros feed the DRX DAP/FASI access helpers, primarily `drxj_dap_read_reg16()`, `drxj_dap_write_reg16()`, `drxdap_fasi_write_reg32()`, and `drxdap_fasi_write_block()`.
- Block writes to `VSB_SYSCTRL_RAM0_*` and `VSB_SYSCTRL_RAM1_*` assume the target addresses are word-addressed and contiguous in the order emitted by this header.

Frontend integration:

- The VSB register block is used when the selected standard is `DRX_STANDARD_8VSB`.
- VSB setup is coordinated with IQM and FEC register blocks outside this chunk. `set_vsb()` stops VSB/FEC/IQM executors, applies IQM filter and ADC/AGC setup, configures FEC output behavior, writes VSB thresholds/gains, and then restarts IQM, VSB, and FEC.
- Signal-quality APIs exposed through the DVB frontend ultimately depend on VSB measurement registers from this chunk when the frontend is operating in 8VSB mode.

Generated map integration:

- The optional `_REGISTERTABLE_` path at the top of the header declares generated register-table metadata, though this chunk only contains the generated `#define` output. The line range relies on the header guard and include established at the top of the file.
- The chunk starts mid-register for `SIO_PDR_MD3_CFG`; the final per-file report should merge this chunk with the preceding chunk to avoid treating the MD3 field list as orphaned.

## Risks And Edge Cases

- This is generated hardware metadata. Manual edits are risky because a single bad address, mask, width, or bit position can redirect a hardware write without producing a compiler error.
- The assigned range starts mid-definition, after the `SIO_PDR_MD3_CFG__A` full-register lines and before the final MD3 field lines. Any standalone reading of this chunk should not infer that MD3 is incomplete in the real header; it is only incomplete in this line slice.
- SIO PDR writes often require a hardware unlock sequence outside this chunk. `drxj.c` writes `SIO_TOP_COMM_KEY__A` before changing PDR registers. Code that uses these SIO address macros without the correct key sequence may see writes ignored or partially applied.
- Several pad registers share the same shape but not the same reset defaults. Copying values between MPEG data, I2C, smart-antenna, I2S, and GPIO pads can break electrical behavior, bus ownership, or board-level pin muxing.
- MPEG serial/parallel output code writes MD pad groups in loops expanded by hand. Missing one of `SIO_PDR_MD4_CFG__A` through `SIO_PDR_MD7_CFG__A`, or using an MD0 field shift for a register whose layout later changes, would cause only some transport bits to drive correctly.
- VSB sysctrl RAM writes rely on table-size and register-map alignment. If a table in `set_vsb_leak_n_gain()` is extended, shortened, or reordered without matching this generated RAM map, all later leak/gain fields in the block can be shifted into the wrong hardware locations.
- The `DRXJ_16TO8()` packed constants written to the RAM windows must match the access layer's byte order. The register map exposes 12-bit/15-bit logical fields, but the runtime writes byte arrays.
- Measurement registers such as `VSB_TOP_NR_SYM_ERRS__A` and `VSB_TOP_ERR_ENERGY_H__A` are meaningful only after VSB measurement-period setup and demodulator startup. Reads while stopped, reset, or on another standard can report stale or meaningless values.
- Some `__PRE` values are not the values used by runtime tuning. For example, `set_vsb()` writes tuned thresholds and gains after reset. Tests should not assume generated `__PRE` is the post-configuration state.
- `VSB_COMM_EXEC__A` and `VSB_TOP_COMM_EXEC__A` have similar names and execution-state values but different addresses. Confusing top-level and subsystem communication registers can stop/start the wrong hardware block.
- The large RAM aperture macros `VSB_TCMEQ_RAM__A`, `VSB_FCPRE_RAM__A`, and `VSB_EQTAP_RAM__A` expose wide memory regions through a single generated base. Access code must know the valid length and element width from surrounding driver/firmware contracts, not from this header alone.

## Test Signals

Build and static checks:

- Compile the DRX39xyJ frontend with `drxj.c` including this generated header; undefined-symbol or duplicate-macro failures catch broken generated output or include ordering.
- Use warnings/static analysis to catch shifts that exceed the destination width when composing values from `__B` and `__M` constants.
- Verify no local patch modifies `drxj_map.h` manually unless it regenerates the map from the authoritative source.

SIO pad and output tests:

- Enable MPEG transport output in serial mode and verify only MD0 is driven while MD1-MD7 are tri-stated through the SIO PDR addresses in this chunk.
- Enable MPEG transport output in parallel mode and verify MD0-MD7, MCLK, MVAL, MSTRT, and MERR all drive with the expected pad mode and drive strength.
- Disable MPEG output and verify the PDR registers return to input/tri-state values.
- Exercise smart-antenna/GPIO direction changes and confirm `SIO_PDR_SMA_RX_CFG__A`, `SIO_PDR_SMA_TX_CFG__A`, and corresponding GPIO function selectors produce the expected pin behavior.
- Probe I2C pad-related defaults carefully on hardware variants that use secondary I2C pins, since their `__PRE` values differ from the MPEG and generic GPIO pad defaults.

VSB setup and operation tests:

- Tune an 8VSB channel and trace register writes to confirm `VSB_COMM_EXEC__A` is stopped before VSB setup/RAM writes and set active after setup.
- Confirm the VSB sysctrl RAM block writes begin at `VSB_SYSCTRL_RAM0_FFETRAINLKRATIO1__A` and `VSB_SYSCTRL_RAM1_FIRRCA1GAIN9__A` with byte counts matching the initializer arrays.
- Validate that VSB lock acquisition still succeeds after writing tuned values to `VSB_TOP_CFAGC_GAINSHIFT__A`, `VSB_TOP_CYGN*`, `VSB_TOP_BNTHRESH__A`, `VSB_TOP_CLPLASTNUM__A`, `VSB_TOP_SNRTH_*`, `VSB_TOP_EQCTRL__A`, `VSB_TOP_BEDETCTRL__A`, and `VSB_TOP_LBAGCREFLVL__A`.
- Read `VSB_TOP_NR_SYM_ERRS__A`, `VSB_TOP_ERR_ENERGY_H__A`, and related measurement registers after a stable VSB lock and compare reported BER/MER against known signal conditions.
- Force weak-signal, burst-noise, and notch-heavy RF scenarios to exercise the threshold and notch-control registers defined in this range.

Regression signals:

- A failure to start VSB demodulation after otherwise successful SCU/IQM/FEC setup points to `VSB_COMM_EXEC__A` sequencing or VSB top-level register writes.
- Incorrect transport stream pin behavior with a working demodulator points to SIO PDR mode/drive/function selector constants.
- Good lock but bad BER/MER reporting points to measurement-period, symbol-error, or error-energy register definitions.
- Hardware that locks only before `set_vsb_leak_n_gain()` changes may indicate a RAM block-write length, address, or byte-order mismatch against the `VSB_SYSCTRL_RAM0/1` map.

## Cross-Chunk Notes

The preceding chunk contains the beginning of the SIO PDR register family, including the full definitions for some MPEG and GPIO pad registers referenced by `drxj.c`. This chunk should be merged with that context for a complete description of transport-output pad handling.

Earlier `drxj_map.h` chunks define ATV, QAM, IQM, FEC, SCU, and other SIO registers that are configured in the same `drxj.c` mode-transition paths. The VSB setup flow depends on those other blocks: IQM and FEC are stopped/configured alongside VSB, then all relevant executors are restarted.

Later per-file reconciliation should preserve that `drxj_map.h` is a generated register-address contract, not a normal implementation unit. The most important behavioral findings come from how `drxj.c` consumes these constants.
