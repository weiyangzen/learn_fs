# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-reg.h lines 1-4363

## Scope

This chunk covers lines 1-4363 of `sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-reg.h`, the first part of the MediaTek MT8189 ALSA SoC audio register-definition header. The full header continues after this range with more bitfield definitions and the register-address map, so this is a chunk-level report only. In this range the file provides an include guard, one small enum for memory-interface prefetch-buffer sizing, and a large set of register field shift/mask macros for the first audio-top, IRQ, ADDA, MTKAIF, and ETDM blocks.

## Purpose

The chunk is the symbolic hardware contract for MT8189 audio front-end control fields. It lets the rest of the driver program register fields through readable names instead of raw bit positions. Most macros follow the pattern:

- `<FIELD>_SFT`: bit shift.
- `<FIELD>_MASK`: unshifted field mask.
- `<FIELD>_MASK_SFT`: mask already shifted into register position.

The header itself does not execute code. Its correctness directly controls how `regmap_write()` and `regmap_update_bits()` calls in the MT8189 AFE, ADDA, PCM, and I2S DAI drivers affect silicon state.

## Important APIs, Types, and Defines

The only type-like API in this chunk is an anonymous enum:

- `MT8189_MEMIF_PBUF_SIZE_32_BYTES`, `64_BYTES`, `128_BYTES`, `256_BYTES`, and `MT8189_MEMIF_PBUF_SIZE_NUM`. `mt8189-afe-pcm.c` uses this to choose a memory-interface prefetch buffer size, returning 256 bytes for periods longer than 10 ms and 32 bytes otherwise.

Major macro groups in this chunk:

- Audio top power and clock gating: `PDN_MTKAIFV4`, `PDN_FM_I2S`, `PDN_HW_GAIN01`, `PDN_HW_GAIN23`, `PDN_STF`, `PDN_CM0`, `PDN_CM1`, `PDN_PCM0`, `PDN_DL0_*`, `PDN_UL*`, `PDN_DMIC*`, `PDN_ETDM_*`, `PDN_GENERAL*_ASRC`, `PDN_APLL_TUNER*`, and `CG_*`.
- Audio engine and test generation: `AUDIO_*_EN_ON`, `MULTI_USER_*`, `AFE_SINEGEN_CON*`, sine frequency/amplitude/domain/mode fields, and tie-constant registers.
- APLL and SPM/resource control: tuner config/monitor fields, `AFE_*_REQ` resource requests, `SPM_RESOURCE_CONTROL_ACK`, top IP/version/monitor fields, and default delay-select fields.
- Connectivity I2S and PCM: `AFE_CONNSYS_I2S_*` monitor/control fields, `AFE_PCM0_INTF_CON0/1`, PCM sync/format/clock/loopback fields, FIFO overrun/glitch monitors, and PCM top IP version.
- IRQ controller: enable masks for MCU, DSP, DSP2, and SCP targets; normal/custom IRQ status bits; IRQ clear/miss-flag clear; per-IRQ 0-26 domain, sample-rate, enable, count, miss-flag, and count-monitor fields; and custom IRQ0 fields.
- Hardware gain: common `AFE_GAIN0..3` field definitions for target sync, timeout, trigger, on/off, sample-per-step, selected domain/sample-rate, target/current left/right values, and up/down step sizes.
- ADDA downlink: `AFE_ADDA_DL_*` source, gain, predistortion, SDM/DC-compensation, test, monitor, dither, auto-reset, HBF coefficient, no-load-enhancement, DEM/IDWA, side-tone, and channel-merge fields.
- ADDA uplink: `AFE_ADDA_UL0_*` and `AFE_ADDA_UL1_*` source controls, DMIC/AMIC clock mode selection, IIR/filter coefficients, ULCF coefficients, debug monitors, proximity selection, and uplink phase synchronization fields.
- MTKAIF and MTKAIFv4: MTKAIF monitor select/status, MTKAIF0/1 TX/RX config, sync-word handling, protocol/8-to-5 options, loopback, FIFO response, v4 TX/RX enable/input-mode/four-channel options, sync-word tables, and monitor fields.
- ETDM input/output: ETDM_IN0/1 and ETDM_OUT0/1/4 common fields for enable, sync mode, slave/master mode, format, LRCK/BCK polarity, bit/word length, channel count, timing, clock source, relatch, repack, lane/channel start pairs, AFIFO, monitor status, and the beginning of ETDM cowork selection.

## Control Flow and Runtime Use

There is no local control flow in this chunk. Control flow appears in consumers that include `mt8189-reg.h` through `mt8189-afe-common.h`:

- `mt8189-dai-adda.c` uses audio-top and ADDA fields in DAPM supplies and stream setup. For playback it builds `AFE_ADDA_DL_SRC_CON0` values from rate, output mode, mute, voice-mode, and gain fields, then writes source, gain, predistortion, SDM, dither, and auto-reset registers. Capture widgets use `AFE_ADDA_UL0_SRC_CON0`, `UL_SRC_ON_TMP_CTL_SFT`, `UL_AP_DMIC_ON_SFT`, FIFO reset fields, and the top-level `PDN_UL0_ADC`/`PDN_DMIC*` gates.
- `mt8189-dai-i2s.c` uses ETDM input/output fields as the I2S/TDM DAI programming model. DAPM supplies toggle `REG_ETDM_IN_EN_SFT` and `OUT_REG_ETDM_OUT_EN_SFT`. Hardware-parameter paths program initial count/point, LRCK reset, clock source, sample-rate timing, relatch domain, bit length, word length, AFIFO settings, format, and ETDM cowork selection.
- `mt8189-afe-pcm.c` uses the enum values for memory interface prefetch sizing and lists IRQ register addresses as readable/regmap-visible registers. The address constants for these register names are outside this chunk, but the bitfields here define how those addresses are interpreted.
- DAPM and PCM setup code rely on the polarity encoded by ALSA supply macros: many power-down fields are active-low at the widget level because writing `1` to a `PDN_*` bit powers a block down, while DAPM enable paths typically request the powered state.

## State and Persistence Behavior

The header keeps no C runtime state, but it defines persistent hardware state:

- Audio-top `PDN_*` and `CG_*` fields gate clocks and functional blocks until changed or reset. Incorrect values can leave ADDA, PCM, MTKAIF, ETDM, ASRC, hardware gain, side-tone, or channel-merge blocks unavailable.
- SPM request/ack fields represent shared power-resource votes for source clocks, APSRC, VRF18, infra, and DDR. These fields are coordination points with platform power management.
- IRQ enable/status/miss/count fields persist as interrupt-controller state and diagnostics. Clear bits and miss-flag clear bits must be used with the correct masks to avoid dropping or retaining stale IRQs.
- ADDA downlink/uplink fields hold sample-rate modes, gain values, filter coefficients, dither/SDM configuration, mute state, loopback/test state, and DMIC/AMIC clock selections across stream setup until explicitly reprogrammed.
- MTKAIF and ETDM fields persist protocol timing, sync words, FIFO response modes, format, channel mapping, clock source, AFIFO behavior, and monitor selections. These settings must match external codec and pad clocking.
- Full-width coefficient fields (`0xffffffff` masks) expose raw filter/tap payload registers where driver code must preserve exact 32-bit values.

## Dependencies and Integration Points

Primary dependencies:

- Linux regmap: all field macros are meant for `regmap_write()`, `regmap_update_bits()`, and readable/volatile register tables in the MT8189 platform driver.
- ALSA SoC DAPM/DAI/PCM code: widgets, routes, and hardware-parameter callbacks use these masks and shifts to turn blocks on/off and derive register values from sample-rate, channel, and format parameters.
- MT8189 audio hardware ABI: every bit position and mask must match the SoC register manual.
- Later chunks of the same header: this chunk has field definitions but not the matching register-address `#define`s for many named registers, which appear after line 4363.

Important integration files observed in the MT8189 directory:

- `mt8189-afe-common.h` includes this header and exposes it to the MT8189 driver modules.
- `mt8189-afe-pcm.c` consumes `MT8189_MEMIF_PBUF_SIZE_*` and IRQ/register visibility definitions.
- `mt8189-dai-adda.c` programs ADDA playback/capture, DMIC, MTKAIF, pad-top, gain, SDM, and filter controls.
- `mt8189-dai-i2s.c` programs ETDM-backed I2S input/output DAIs and ETDM cowork relationships.

## Risks and Edge Cases

- Numeric drift is the main risk. A one-bit error in `_SFT`, `_MASK`, or `_MASK_SFT` can silently program the wrong hardware field while still compiling.
- Many generic macro names are intentionally reused for multiple same-layout registers, such as `UPPER_BOUND`, `APLL_DIV`, `RESERVE_RG`, `TUNER_MON`, gain fields, and ETDM common fields. This works only because definitions are identical; non-identical duplicates would create preprocessor warnings or incorrect consumers.
- Several fields have active-low or power-down semantics (`PDN_*`, FIFO reset, soft reset, clear bits). Tests must verify both enable and disable paths because a value that looks like "on" in code may be hardware "power down".
- ETDM input/output blocks reuse common field names across IN0/IN1 and OUT0/OUT1/OUT4. DAI code assumes these blocks share the same layout. Any SoC revision-specific layout divergence would require separate names or conditional code.
- IRQ0-26 macros are highly repetitive. Copy/paste mistakes in domain, sample-rate, count, clear, or miss-flag fields can affect only one IRQ line and may be missed by broad playback/capture smoke tests.
- Full-width coefficient and monitor fields are easy to mask incorrectly if driver code uses shifted masks where raw payloads are expected.
- The chunk ends at the start of `ETDM_0_3_COWORK_CON0`; remaining cowork fields and all register address definitions are cross-chunk dependencies for a full-file report.

## Test Signals

Useful validation signals for this chunk:

- Build the MT8189 audio driver with warnings enabled to catch duplicate macro mismatches, missing field names, and invalid references after edits.
- Boot/probe with regmap debug enabled and confirm the AFE regmap marks IRQ, ADDA, MTKAIF, and ETDM registers readable/writable according to the full header.
- PCM playback through ADDA should exercise `AFE_ADDA_DL_SRC_CON0/1`, SDM/DC-compensation, predistortion, mute/gain, and `PDN_DL0_*` gating fields.
- PCM capture through ADDA and AP DMIC should exercise `AFE_ADDA_UL0/UL1_SRC_CON*`, DMIC clock/phase fields, FIFO reset, `PDN_UL0_ADC`, and `PDN_DMIC*` gating.
- I2S/ETDM input and output streams should validate sample-rate timing, format, bit/word length, channel count, master/slave polarity, AFIFO, and cowork selection fields on ETDM_IN0/IN1 and ETDM_OUT0/OUT1/OUT4.
- IRQ tests should enable selected MCU/DSP/SCP IRQ targets, trigger period interrupts, read count monitors, and verify clear/miss-flag behavior for normal and custom IRQ paths.
- Hardware-gain, side-tone, channel-merge, and NLE paths need targeted mixer/control tests because these fields are not always covered by simple playback/capture.
- Suspend/resume tests should confirm power/resource request bits, clock gates, and programmed DAI formats are restored or safely reinitialized by the consuming driver code.

## Open Cross-Chunk References

- Lines after 4363 continue ETDM cowork definitions and later define register-address macros such as `AFE_ADDA_DL_SRC_CON0`, `ETDM_IN0_CON0`, `ETDM_OUT0_CON0`, and `AFE_IRQ0_MCU_CFG0`.
- The final per-file report should merge this field-layout chunk with the later address-map chunks so every field group is tied to its concrete register offsets and regmap access policy.
