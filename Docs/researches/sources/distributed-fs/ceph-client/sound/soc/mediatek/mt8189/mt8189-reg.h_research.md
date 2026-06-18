# Research: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-reg.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006524`: lines 1-4363, `Docs/researches/chunks/subset-b-006524_research.md`
- `subset-b-006525`: lines 4364-8767, `Docs/researches/chunks/subset-b-006525_research.md`
- `subset-b-006526`: lines 8768-10773, `Docs/researches/chunks/subset-b-006526_research.md`

## Chunk Research

### subset-b-006524: lines 1-4363

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

### subset-b-006525: lines 4364-8767

# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-reg.h lines 4364-8767

## Scope

This chunk covers the middle register-field macro block of the MT8189 ALSA SoC AFE register header. It starts inside the ETDM cowork field definitions, then describes TDM/DPTX/HDMI output controls, CBIP bus-monitor fields, memory-interface control/status fields for many DL and VUL paths, ETDM input memory interfaces, multi-channel monitor registers, and secure/protection/domain sideband registers. The chunk ends in `AFE_SECURE_SRAM_CON0` after defining non-secure SRAM read/write enable bits down through SRAM bank 2.

The content is declarative C preprocessor metadata. Each hardware field is represented as a shift macro, an unshifted mask macro, and a shifted mask macro, following the local pattern `FIELD_SFT`, `FIELD_MASK`, and `FIELD_MASK_SFT`.

## Purpose

The macros provide the bit-level hardware contract used by MT8189 ASoC driver code when programming the audio front end through regmap. They are paired with register-offset macros later in the same header and with data-driven memif descriptors in `mt8189-afe-pcm.c`.

The chunk's main responsibilities are:

- Route and format control for ETDM/TDM/HDMI/DPTX playback paths.
- Base/current/end pointer field definitions for DMA-like audio memory interfaces.
- Runtime enable, sample-rate, burst-length, high-definition mode, mono, alignment, and buffer clear fields for DL and VUL memifs.
- Read-only monitor fields for current pointers, sample data, buffer state, pending memory requests, and CBIP decoder/mux state.
- Secure-world, non-secure-world, HPROT, HDOMAIN, and register-mask sideband controls for audio paths and SRAM regions.

## Important APIs, Types, and Macros

- `ETDM_OUT*_DATA_SEL`, `ETDM_OUT*_SYNC_SEL`, `ETDM_OUT*_SLAVE_SEL`, `ETDM_IN*_SLAVE_SEL`, `ETDM_IN*_SYNC_SEL`, and `ETDM_IN*_SDATA*_SEL`: field macros for ETDM cowork routing. The chunk begins mid-`ETDM_0_3_COWORK_CON0`, then covers `ETDM_0_3_COWORK_CON1` and `ETDM_4_7_COWORK_CON0`.
- `DPTX_CHANNEL_ENABLE`, `DPTX_REGISTER_MONITOR_SELECT`, `DPTX_16BIT`, `DPTX_CHANNEL_NUMBER`, and `DPTX_ON`: DPTX enable/format/monitor fields used by the TDM DAI when the DPTX route is selected.
- `TDM_EN`, `BCK_INVERSE`, `LRCK_INVERSE`, `DELAY_DATA`, `LEFT_ALIGN`, `WLEN`, `CHANNEL_NUM`, `CHANNEL_BCK_CYCLES`, `DAC_BIT_NUM`, and `LRCK_TDM_WIDTH`: `AFE_TDM_CON1` fields that encode TDM frame format. `AFE_TDM_CON2` adds stereo-pair source mapping, loopback, sine-generator, and fixed-value controls. `AFE_TDM_CON3` adds output clock-domain/sample-rate selection, monitor selection, async FIFO reset, and update selection.
- `HDMI_O_0` through `HDMI_O_7`: `AFE_HDMI_CONN0` channel mux fields. `mt8189-dai-tdm.c` exposes these as ALSA SOC enum controls named `HDMI_CH*_MUX`.
- `AFE_HDMI_OUT_*` fields: MSB/low base, current, and end pointer fields plus `HDMI_OUT_ON`, `HDMI_CH_NUM`, burst settings, buffer-clear bits, alignment, normal mode, and HD mode.
- `AFE_CBIP_CFG0` and CBIP monitor fields: bus/interface configuration and error/monitor selectors for decoder and slave mux diagnostics. Important fields include APB timeout toggles, async FIFO thresholds, decoder error enable/status, source flags, and register monitor selectors.
- `AFE_MEMIF_CON0` and `AFE_MEMIF_ONE_HEART`: common memif controls for interrupt-once modes and one-heart behavior. They sit before per-memif field groups.
- `AFE_DL*` groups: downlink memory interfaces `DL0..DL8`, `DL23..DL25`, plus `DL_24CH`. Each ordinary DL group defines base/current/end pointer fields, right/left channel monitor fields, `*_CON0` playback control fields, and for `DL0..DL8` a `*_MON0` status register. `DL_24CH` has multi-channel-specific `CH_NUM`, per-channel monitor registers `AFE_DL_24CH_CH0_MON` through `CH7_MON`, and no ordinary left/right monitor pair in this chunk.
- `AFE_VUL*` groups: uplink/capture memory interfaces `VUL0..VUL10`, `VUL24`, and `VUL25`. They mirror the base/current/end pointer shape and use `*_CON0` fields for enable, memory burst length, domain/sample-rate selection, full-buffer clear, sign extension, mono, alignment, normal mode, and HD mode. VUL monitors expose `MEM_HW_WEN`, pending request, full-buffer state, sync enable flags, and memory address difference.
- `AFE_VUL_CM0` and `AFE_VUL_CM1`: channel-mixer capture interfaces with base/current/end fields and richer `*_CON0` flags such as channel shift mode, forced no-mask-extra behavior, ultra threshold, odd/even use, AXI request lengths, sign extension, extra update, free-run, odd interrupt selection, and odd interrupt flag.
- `AFE_ETDM_IN0` and `AFE_ETDM_IN1`: ETDM input memory interface fields. Their `*_CON0` blocks include soft reset, write-clear, update-word, status-update selection, frame-size timing selection, sync/packed-mode options, enable, mono, high-definition, and source interface selection fields.
- `AFE_SECURE_CON0` and `AFE_SECURE_CON1`: per-channel read/write enable maps for non-secure and secure access. Each packs read and write enable bits for channels 0 through 15 into alternating bit positions.
- `AFE_SE_SECURE_CON0..3`: per-engine secure-bit selectors for DL, VUL, HDMI, SPDIF, TDM input, ETDM input, and microphone-related paths.
- `AFE_SE_PROT_SIDEBAND0..3` and `AFE_SE_DOMAIN_SIDEBAND0..9`: sideband HPROT and HDOMAIN maps for the same audio engines. The HPROT maps are one bit per path; the HDOMAIN maps are four bits per path.
- `AFE_PROT_SIDEBAND*_MON` and `AFE_DOMAIN_SIDEBAND*_MON`: full-width readback fields for sideband monitor registers.
- `AFE_SECURE_CONN0`, `AFE_SECURE_CONN_ETDM1`, and `AFE_SECURE_CONN_ETDM2`: secure mask controls for selected AFE connection/control registers, including PCM, CONNSYS I2S, MRGIF, DAIBT, TDM, TDMIN, MRKAIF, ADDA UL/DMIC, SPDIF input loopback, and ETDM cowork masks.
- `AFE_SECURE_SRAM_CON0`: non-secure read/write enable fields for SRAM banks. This chunk defines banks 15 down to 2 and continues beyond the chunk for banks 1 and 0.

## Control Flow and Integration

There is no executable control flow in this chunk. Runtime behavior emerges when other driver code combines these constants with register offsets and regmap operations.

The TDM DAI is the most direct user of the TDM/DPTX/HDMI fields. In `mt8189-dai-tdm.c`, `mtk_dai_tdm_hw_params()` calculates MCLK/BCLK requirements from ALSA PCM parameters, writes `AFE_TDM_CON1` using `LEFT_ALIGN_SFT`, `WLEN_SFT`, `CHANNEL_NUM_SFT`, `CHANNEL_BCK_CYCLES_SFT`, and `LRCK_TDM_WIDTH_SFT`, optionally programs DPTX channel enable/count/word-length fields, writes `AFE_TDM_CON2` for channel-pair mapping, and updates `HDMI_CH_NUM` in `AFE_HDMI_OUT_CON0`. `mtk_dai_tdm_trigger()` enables and disables `HDMI_OUT_ON`, `DPTX_ON`, and `TDM_EN` around PCM start/stop and resume/suspend events.

The memory-interface fields are consumed through descriptor macros in `mt8189-afe-pcm.c`. `MT8189_DL_MEMIF`, `MT8189_MULTI_DL_MEMIF`, and `MT8189_UL_MEMIF` build `struct mtk_base_memif_data` entries from register names and bit fields such as `AFE_DL0_BASE`, `AFE_DL0_BASE_MSB`, `DL0_ON_SFT`, `DL0_SEL_FS_SFT`, `DL0_HD_MODE_SFT`, `DL0_HALIGN_SFT`, `DL0_PBUF_SIZE_SFT`, `DL0_MINLEN_SFT`, `AFE_VUL0_CON0`, and similar per-id macros. The resulting `memif_data[MT8189_MEMIF_NUM]` table covers DL0-DL8, DL23-DL25, DL_24CH, HDMI, VUL0-VUL10, VUL24/VUL25, VUL_CM0/VUL_CM1, and ETDM_IN0/ETDM_IN1.

Regmap volatility also depends on this chunk's register families. `mt8189_is_volatile_reg()` marks current pointer registers, monitor registers, CBIP monitor registers, sideband monitor registers, and selected CON0 registers as volatile. That prevents regcache from treating hardware-updated status and pointer fields as stable cached values.

The security and sideband field definitions integrate with platform security setup rather than ordinary PCM data movement. The chunk exposes the fields needed to classify each AFE path as secure/non-secure, set HPROT and HDOMAIN metadata, and mask selected connection-control registers from secure or non-secure access. The actual policy values are not encoded here; the macros only define where those values live.

## State and Persistence Behavior

The header itself has no mutable software state. The fields represent persistent or live hardware state in the AFE register map:

- Base/end pointer registers persist the programmed DMA buffer window until rewritten or reset. They are split into low address fields and 9-bit MSB fields, so callers must program both parts consistently for high physical addresses.
- Current pointer registers and data monitor registers are live hardware status and are treated as volatile by the regmap configuration.
- `*_ON`, `TDM_EN`, `DPTX_ON`, and `HDMI_OUT_ON` bits gate active hardware paths. Incorrect sequencing can leave a memif, serial output, or DPTX path running against stale buffer configuration.
- Buffer clear bits such as `*_SW_CLEAR_BUF_EMPTY` and `*_SW_CLEAR_BUF_FULL` are command-like state changes, not ordinary cached configuration.
- `MEM_REQ_PENDING`, `BUF_EMPTY`, `BUF_FULL`, `ENABLE_SYNC_MEM`, `ENABLE_SYNC_AGENT`, and `MEM_ADDR_DIFF` expose transient synchronization and FIFO/buffer conditions.
- Secure/protection/domain sideband registers are system policy state. Their effects can cross subsystem boundaries because they influence bus attributes and access permissions for audio engines and SRAM banks.

## Dependencies

- The register offsets named in comments here are defined later in `mt8189-reg.h`; this chunk defines field positions, not the numeric register addresses.
- The field macros depend on the Linux regmap access pattern used by the MT8189 ASoC driver, especially `regmap_write()` and `regmap_update_bits()`.
- ALSA SoC TDM playback depends on these constants through `mt8189-dai-tdm.c` and its DAPM routes, controls, hardware-parameter handling, and trigger callbacks.
- ALSA PCM memory-interface setup depends on these constants through `mt8189-afe-pcm.c` descriptor macros and `memif_data`.
- `mt8189-afe-common.h` provides the memif and DAI ids that select which field family is used at runtime.
- Security-related fields likely depend on platform firmware, secure monitor, or board policy code deciding which paths should be secure, non-secure, protected, or assigned to which domain. That policy code is outside this chunk.

## Risks and Edge Cases

- The chunk begins inside an ETDM cowork register block and ends inside `AFE_SECURE_SRAM_CON0`; reconciliation with adjacent chunks is required for complete field coverage of those two boundary registers.
- Many field names are generated-style and repetitive. A single wrong suffix, shift, or mask silently misprograms hardware because call sites build values by token pasting in descriptor macros.
- Split pointer programming is high risk: base/end/current registers use a low 28-bit field shifted by 4 plus a separate 9-bit MSB field. Address alignment, physical address width, and ordering must match the SoC data sheet.
- DL and VUL families are similar but not identical. DL paths use empty-buffer clear/status semantics, while VUL paths use full-buffer clear/status semantics and write-sign/right-mono fields. Copying DL programming into VUL code, or the reverse, can invert the buffer condition being handled.
- Some memifs are sparse or special-purpose: DL23-DL25, VUL24/VUL25, VUL_CM0/VUL_CM1, ETDM_IN0/IN1, HDMI, and DL_24CH do not have exactly the same monitor/control fields as DL0-DL8 or VUL0-VUL10.
- `OUT_ON_USE_VUL24` and `OUT_ON_USE_VUL25` in the VUL24/VUL25 controls indicate extra routing/ownership semantics beyond ordinary capture enable. Treating those as ordinary VULs may miss route coupling.
- The `VUL_CM*` controls include command/status-like odd interrupt and extra-update fields. These are more than plain sample format controls and may need strict write ordering.
- Security sideband errors can be severe. Incorrect `AFE_SE_SECURE_CON*`, `AFE_SE_PROT_SIDEBAND*`, `AFE_SE_DOMAIN_SIDEBAND*`, `AFE_SECURE_CONN*`, or `AFE_SECURE_SRAM_CON*` values can expose protected audio paths, block legitimate PCM operation, or cause bus faults.
- Several monitor macros reuse generic names such as `AFE_DOMAIN_SIDEBAN0_MON_SFT` under multiple monitor-register comments. That is legal as repeated identical macro definitions only if the preprocessor sees matching values, but it makes name-to-register traceability weaker.
- The CBIP decoder/mux monitor fields are diagnostic-oriented. Misclassifying them as stable cached registers would hide transient bus errors; misusing selectors can report the wrong bus path.

## Test Signals

Useful validation for this chunk is mostly build-time, regmap, and hardware-route oriented:

- Build the MT8189 ASoC driver with warnings enabled to catch duplicate, missing, or token-paste-incompatible field macros.
- Exercise TDM playback with 2, 4, 6, and 8 channel configurations and verify that `AFE_TDM_CON1`, `AFE_TDM_CON2`, `AFE_DPTX_CON`, and `AFE_HDMI_OUT_CON0` reflect the expected format, channel-pair, DPTX, and channel-count values.
- Start/stop TDM and TDM_DPTX PCM streams and check that `HDMI_OUT_ON`, `DPTX_ON`, and `TDM_EN` toggle in the order expected by `mtk_dai_tdm_trigger()`.
- Open representative playback and capture memifs and verify base/end/current pointer programming for DL0, DL8, DL24, DL_24CH, HDMI, VUL0, VUL10, VUL24, VUL_CM0, and ETDM_IN0.
- Confirm regmap volatility behavior by reading current pointer and monitor registers repeatedly during active streams; values should come from hardware rather than regcache.
- Validate buffer clear and monitor behavior by observing `BUF_EMPTY` on DL paths and `BUF_FULL` on VUL paths across underrun/overrun-style tests.
- Exercise ALSA mixer controls for `HDMI_CH*_MUX` and verify the `HDMI_O_*` fields in `AFE_HDMI_CONN0`.
- Run secure/non-secure policy tests, where available, by toggling representative secure bits, HPROT bits, HDOMAIN nibbles, connection masks, and SRAM read/write enables under the platform's secure firmware expectations.
- Probe CBIP monitor registers during normal operation and forced/error-injection scenarios to confirm decoder error flags, source flags, and mux monitor selectors are not stale.

### subset-b-006526: lines 8768-10773

# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-reg.h lines 8768-10773

## Scope

This chunk covers the tail of the MT8189 AFE register-definition header. It is macro-only C preprocessor content: bit shifts, unshifted masks, shifted masks, MMIO register offsets, and final range/status constants. There are no functions, structs, or executable control-flow blocks in this slice, but the definitions are consumed by the MT8189 ALSA SoC AFE driver through regmap reads, writes, update masks, volatile-register classification, IRQ dispatch, and hardware capability bounds.

## Purpose

The chunk defines several hardware-facing groups:

- Secure SRAM and secure/non-secure audio interconnect permission fields.
- Secure and normal input mask windows and secure output select windows for the AFE interconnect fabric.
- Mask-monitor registers for selected interfaces such as PCM0, CONNSYS I2S, MTKAIF, and ADDA uplink paths.
- GASRC0 asynchronous sample-rate-converter control, frequency calibration, coefficient SRAM, debug, and IP-version fields.
- The main AFE register offset map from top-level clock/control blocks through gain, ADDA, ETDM, TDM/HDMI, connection matrix, memory interface, secure control, ASRC/GASRC, SoundWire phase, and IRQ blocks.
- Final driver constants: `AFE_MAX_REGISTER`, `AFE_IRQ_STATUS_BITS`, `AFE_IRQ_CNT_SHIFT`, and `AFE_IRQ_CNT_MASK`.

This file is the source of truth for numeric offsets and bit layouts. Driver code should use these names instead of hard-coded offsets so the register map remains auditable and regmap can enforce the right address bounds.

## Important Definitions

The secure SRAM definitions at the start of the chunk finish non-secure SRAM write/read enable bits and then define `AFE_SECURE_SRAM_CON1` secure bits. Each SRAM slot has paired write/read enables, numbered 0 through 15, packed as alternating bits. For the secure register, `SRAM_WRITE_EN0_S_SFT` starts at bit 0 and `SRAM_READ_EN15_S_SFT` ends at bit 31. These macros are likely used with `regmap_update_bits()` style operations where the `_MASK_SFT` value provides the shifted one-bit mask and `_SFT` provides the bit position for composed values.

The secure interconnect input masks are expressed as 32-bit windows:

- `SECURE_INTRCONN_I0_I31_S_*` through `SECURE_INTRCONN_I224_I256_S_*`.
- `NORMAL_INTRCONN_I0_I31_S_*` through `NORMAL_INTRCONN_I224_I256_S_*`.

Each mask macro covers a full 32-bit register. The labels show that the connection fabric has secure and non-secure classification windows for AFE inputs. The last range name uses `I224_I256`, but the mask is still `0xffffffff`; callers should treat the name as a hardware naming convention rather than proof that bit 32 exists in that specific register.

Secure output selection registers mirror the input-window pattern with `SECURE_INTRCONN_O0_O31_S_*` through `SECURE_INTRCONN_O224_O256_S_*`. These define full-width security selection masks for output endpoints.

The mask-monitor fields, such as `AFE_PCM0_INTF_CON1_MASK_MON_*`, `AFE_CONNSYS_I2S_CON_MASK_MON_*`, `AFE_MTKAIF0_CFG0_MASK_MON_*`, and `AFE_ADDA_UL0_SRC_CON0_MASK_MON_*`, are full-width monitor fields. They expose hardware-observed mask state rather than narrow configuration fields.

The `AFE_GASRC0_NEW_CON*` fields describe one generic ASRC instance in detail:

- `AFE_GASRC0_NEW_CON0` controls ASRC enable, channel-set enable, stream clear, coefficient SRAM control, mono/16-bit format, input/output frequency selectors, IIR enable/stage, and special clocking/heart-beat behavior.
- `AFE_GASRC0_NEW_CON1` through `CON4` provide four 24-bit `ASM_FREQ_*` fields.
- `AFE_GASRC0_NEW_CON5` selects input/output sample-rate domains, calibration clock/LRCK sources, calibration result source, and soft reset.
- `AFE_GASRC0_NEW_CON6` controls frequency calibration enable, auto restart, debounce/glitch filtering, max gate width, calibration source, result compensation, auto-tune controls, running status, and autorst detection.
- `AFE_GASRC0_NEW_CON7` through `CON9` expose 24-bit denominator/result/record values.
- `AFE_GASRC0_NEW_CON10` and `CON11` are coefficient SRAM data/address fields.
- `AFE_GASRC0_NEW_CON12` is ring-debug read data.
- `AFE_GASRC0_NEW_CON13` and `CON14` define high/low thresholds for frequency-calibration auto reset.
- `AFE_GASRC0_NEW_IP_VERSION` is a full-width version register.

The offset map begins at `AUDIO_TOP_CON0` and continues to `AFE_CUSTOM_IRQ_MCU_DSP_WLA_EN`. It includes repeated register families for gains, ADDA downlink/uplink, digital microphones, MTKAIF, ETDM/TDM, connection matrix, memory interfaces, secure controls, ASRC/GASRC instances, SoundWire uplink-source phase control, and common/custom IRQ blocks. `AFE_MAX_REGISTER` aliases the last defined offset so the regmap configuration can reject addresses beyond the known hardware map.

## Register-Map Integration

The chunk is integrated through `mt8189-afe-pcm.c`. The regmap configuration uses `AFE_MAX_REGISTER` as `.max_register` and `.num_reg_defaults_raw`, with 32-bit registers, 4-byte stride, 32-bit values, and flat caching. This makes the final offset in this chunk part of the driver's addressability contract.

Several registers from this chunk are explicitly classified as volatile in the PCM driver. The volatile set includes monitor registers, ASRC/GASRC status/result registers, IRQ enable/config registers, and selected memory-interface controls. For GASRC0, the driver marks `AFE_GASRC0_NEW_CON0`, `CON6`, `CON8`, `CON9`, `CON10`, `CON11`, `CON12`, and `IP_VERSION` as volatile. This matters because stale regcache values would be unsafe for live calibration, coefficient-SRAM, debug, and IP-version state.

The IRQ handler uses the final `AFE_IRQ_STATUS_BITS` mask when intersecting status and enable registers:

- `AFE_IRQ_MCU_STATUS & AFE_IRQ_MCU_EN & AFE_IRQ_STATUS_BITS`.
- `AFE_CUSTOM_IRQ_MCU_STATUS & AFE_CUSTOM_IRQ_MCU_EN & AFE_IRQ_STATUS_BITS`.

Only enabled and in-range interrupt bits are allowed to drive `snd_pcm_period_elapsed()` and IRQ clearing. The `0x7ffffff` mask means bits 0 through 26 are accepted for the common status path, matching the `AFE_IRQ0_MCU_CFG*` through `AFE_IRQ26_MCU_CFG*` offsets in this chunk.

## Control Flow

This header chunk has no runtime control flow by itself. It enables control flow in the driver in three main ways:

- Register writes and updates use the offset macros to route operations to hardware blocks.
- Bitfield macros let callers set, clear, or test packed control fields without manual shifts.
- Volatile-register and IRQ-handler switch/loop logic in the PCM driver depends on these numeric constants to decide which values must be read from hardware and which interrupts require ALSA period callbacks.

For secure routing and memory protection, higher-level driver code is expected to program sideband, secure connection, secure SRAM, and secure/non-secure input/output masks in a sequence consistent with the SoC's power and trust-domain state. This chunk only names the controls; ordering requirements live in the consuming driver or firmware contract.

## State And Persistence

All definitions in this chunk represent either hardware register addresses or hardware bitfields. The persistent state is the AFE hardware state behind those addresses, not any C object in the header. Some registers are ordinary cached configuration state under regmap, while monitors, counters, calibration outputs, current pointers, and IRQ status fields are live hardware state and must be treated as volatile by consuming code.

Memory-interface offsets define base/current/end pointer registers for downlink (`AFE_DL*`), uplink (`AFE_VUL*`), ETDM input, and HDMI output paths. These values persist in hardware while a stream is configured and running, and the current-pointer/monitor registers change as DMA progresses. Secure controls and connection masks persist as hardware security/routing state until reset or reprogrammed.

IRQ configuration and count registers persist interrupt period, enable, delay, and count state. The final `AFE_IRQ_CNT_SHIFT` and `AFE_IRQ_CNT_MASK` constants describe a 24-bit count field used by IRQ counter/config handling.

## Dependencies

The chunk depends on Linux kernel conventions rather than local helper functions:

- C preprocessor macro expansion.
- Linux `BIT()` and regmap-style update/read APIs in consuming C files.
- ALSA SoC MediaTek AFE driver data structures that map memory interfaces, IRQ IDs, and register addresses to runtime stream behavior.
- Hardware documentation or generated register descriptions for MT8189 AFE; the naming and repeated pattern strongly indicate an auto-generated or register-database-derived header.

No include-time dependencies are introduced in this chunk beyond the surrounding header guard ending at line 10773.

## Risks And Edge Cases

Register offset drift is the largest risk. If any offset in this chunk diverges from the SoC register map, the driver can write to the wrong hardware block. This is especially risky in the secure-control, memory-interface, and IRQ regions because a wrong write can break access control, DMA buffer bounds, or interrupt delivery.

Mask/shift misuse is another common risk. Many fields provide both `_MASK` and `_MASK_SFT`; callers must use `_MASK_SFT` when passing a shifted mask to `regmap_update_bits()` and use `_SFT` when constructing shifted values. Accidentally shifting `_MASK_SFT` again or passing unshifted `_MASK` for nonzero fields can silently configure the wrong bits.

The full-width secure/non-secure interconnect mask definitions and monitor definitions use `0xffffffff`. Callers need to avoid C signedness pitfalls when storing or printing these values; they should remain unsigned 32-bit register values.

The repeated GASRC register blocks define five instances in the offset map (`GASRC0` through `GASRC4`), but detailed bitfield definitions in this chunk are only named for `GASRC0`. If the hardware layout is shared across instances, consumers may reuse the `GASRC0` field masks with other GASRC instance offsets, but that coupling is implicit and should be verified before adding new code.

`AFE_MAX_REGISTER` is tied to the last listed custom IRQ enable register. Adding later hardware registers requires updating this macro; otherwise regmap may reject valid accesses or fail to allocate enough flat-cache space.

IRQ masking with `AFE_IRQ_STATUS_BITS` intentionally ignores bits above 26 in common/custom status handling. If future IRQ definitions use higher bits, this mask must be updated together with IRQ data tables and clear logic.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage for macro names referenced by MT8189 AFE sources.
- Regmap probe success with `.max_register = AFE_MAX_REGISTER`; failures or invalid-register warnings indicate offset/bounds issues.
- Playback and capture smoke tests that exercise `AFE_DL*`, `AFE_VUL*`, ETDM, HDMI, and IRQ period callbacks.
- Interrupt tests confirming only enabled bits within `AFE_IRQ_STATUS_BITS` cause `snd_pcm_period_elapsed()` and that IRQ clear registers are updated correctly.
- Suspend/resume or power-domain tests verifying secure routing, SRAM access enables, and volatile monitor/calibration registers are not restored from stale cache incorrectly.
- Hardware register dumps comparing key offsets in this header against the MT8189 register manual, especially secure-control, GASRC, memory-interface, and IRQ ranges.
