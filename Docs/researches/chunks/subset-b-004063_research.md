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
