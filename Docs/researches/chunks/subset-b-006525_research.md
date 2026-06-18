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
