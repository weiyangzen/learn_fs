# subset-b-006518 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-afe-pcm.c

Purpose: implements the MT8173 ASoC AFE platform driver, including FE memory DAIs for DL1/VUL/HDMI, BE DAIs for I2S and HDMI/TDM output, DMA hardware limits, memif and IRQ register metadata, runtime PM, clock setup, and component registration.

Important APIs/types/functions: defines register offsets and bitfields for AFE, I2S, HDMI, TDM, memif, and IRQ blocks; `struct mt8173_afe_private` stores clock handles; `mt8173_afe_i2s_fs` maps PCM rates to hardware FS fields; `mt8173_afe_set_i2s`, `mt8173_afe_set_i2s_enable`, `mt8173_afe_i2s_*` configure and power the I2S BE; `mt8173_afe_hdmi_*` configures I2S3/TDM/HDMI routing and trigger-time enable; `mt8173_memif_fs` and `mt8173_irq_fs` provide common FE callbacks; `memif_data` and `irq_data` describe DMA base/current/end, sample-rate, mono, enable, MSB, IRQ count/en/clear fields; `mt8173_afe_irq_handler` calls `snd_pcm_period_elapsed`; runtime PM hooks gate clocks and AFE registers; `mt8173_afe_pcm_dev_probe` builds the AFE object and registers platform, PCM DAI, and HDMI DAI components.

Control flow: probe sets a 33-bit DMA mask, allocates `mtk_base_afe` and private clock state, optionally attaches reserved memory or enables preallocation, maps MMIO/regmap, initializes clocks, allocates memif/IRQ arrays, assigns fixed memif-to-IRQ usage, enables runtime PM, registers the generic PCM platform plus two component instances, and requests the AFE IRQ. PCM open/hw_params behavior is largely delegated through `mtk_afe_fe_ops` using the memif/IRQ metadata. I2S startup ungates 22M/24M clocks, prepare sets MCLK rates and I2S input/output formats, shutdown disables I2S and re-powers down 22M/24M when inactive. HDMI startup enables I2S3 clocks, prepare computes TDM channel mapping and HDMI channel count, trigger writes HDMI connection routes and toggles HDMI/TDM enable.

State and persistence: persistent driver state is devm-managed `afe`, memif/IRQ tables, regmap, clock pointers, runtime PM state, and the register backup list used by common suspend/resume helpers. Hardware state persists in MMIO registers while powered; runtime suspend disables AFE, powers down the AFE clock, and disables base clocks. Reserved-memory attachment controls whether common buffer handling uses reserved memory or preallocated buffers.

Dependencies and integration: depends on Linux clocks, regmap MMIO, runtime PM, reserved memory, DMA mapping, ALSA SoC DPCM, MediaTek common AFE platform/FE helpers, and `mt8173-afe-common.h` IDs. Machine drivers in the same folder bind to FE names `DL1`, `VUL`, and `HDMI`, and BE names `I2S`/`HDMIO`. Device tree must provide compatible `mediatek,mt8173-afe-pcm`, MMIO resource, IRQ, and clock names from `aud_clks`.

Risks: the driver assumes `afe->memif_size` and `afe->irqs_size` match when initializing both arrays in one loop. `irq_data` contains a duplicate `MT8173_AFE_IRQ_DAI` entry. Runtime-resume error labels for I2S1/I2S2 appear crossed: a failure after enabling I2S1 jumps to a label that disables I2S2, and vice versa. HDMI trigger emits `dev_info` on every command, which can be noisy. Unsupported sample rates return `-EINVAL`, so DT/card constraints must match hardware tables. HDMI memif has no normal enable register and relies on BE trigger sync.

Test signals: build coverage under the MT8173 ASoC config, DT probe with all required clocks/IRQ/resource, `aplay`/`arecord` on DL1/VUL via an MT8173 card, HDMI multichannel playback at 32k-192k with 2/4/6/8 channels, runtime suspend/resume while streams are idle and active, IRQ period-elapsed behavior, and clock error-injection or probe deferral tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-max98090.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-max98090.c

Purpose: provides the MT8173 machine driver for boards using a MAX98090 codec, wiring DPCM front ends to an I2S codec back end with DAPM pins and headset detection.

Important APIs/types/functions: declares jack pins for headphone and headset mic, DAPM widgets/routes for speaker/internal mic/headphone/headset mic, user pin switches, `mt8173_max98090_hw_params` to set codec sysclk to `rate * 256`, `mt8173_max98090_init` to create the jack and call `max98090_mic_detect`, FE links `MAX98090 Playback` and `MAX98090 Capture`, BE link `Codec`, and `mt8173_max98090_dev_probe` for DT binding.

Control flow: probe reads `mediatek,platform` and assigns it to links with empty platforms, reads `mediatek,audio-codec` and assigns it to codec slots with empty names, attaches `card->dev`, then registers the card. At stream hw_params the codec DAI receives a sysclk derived from sample rate. During BE init, the card creates a headset jack and passes it to the MAX98090 codec driver for mic detection.

State and persistence: file-static card/link/jack structures persist for the platform driver lifetime; per-device allocations are devm-managed by ASoC. Runtime state is limited to ALSA jack reporting and DAPM route/pin state. There is no private heap state or custom suspend state.

Dependencies and integration: depends on ALSA SoC core, jack support, MAX98090 codec API, and the MT8173 AFE CPU DAIs named `DL1`, `VUL`, and `I2S`. Device tree must provide `compatible = "mediatek,mt8173-max98090"`, a platform phandle, and one audio-codec phandle.

Risks: only one codec phandle is supported. The BE format is fixed to I2S, normal bit/frame polarity, codec bit/frame clock consumer; boards with different wiring need DT/driver changes. Probe releases local DT node references but stores node pointers into card links, relying on ASoC/device lifetime conventions.

Test signals: card registration from DT, DAPM pin switch visibility, headphone/headset mic jack events through MAX98090, playback and capture through DL1/VUL, and sysclk programming across supported sample rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-max98090.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650-rt5514.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650-rt5514.c

Purpose: machine driver for MT8173 boards with an RT5650/RT5645 primary codec and RT5514 secondary codec, providing speaker/headphone/mic routing and DL1/VUL DPCM links.

Important APIs/types/functions: defines `MCLK_FOR_CODECS` as 12.288 MHz; DAPM widgets/routes include primary speaker/headphone/headset mic and `Sub`-prefixed RT5514 DMIC routes; controls expose pin switches; `mt8173_rt5650_rt5514_hw_params` programs PLL and sysclk for every codec DAI to `rate * 512`; `mt8173_rt5650_rt5514_init` selects RT5645 ASRC sources and registers headset jack/buttons; `codec_conf` adds the `Sub` prefix to the secondary codec; probe wires platform and two codec phandles.

Control flow: probe parses `mediatek,platform`, assigns it to empty platform components, parses `mediatek,audio-codec` index 0 for RT5650 and index 1 for RT5514, stores the second codec node in the codec-conf prefix entry, sets `card->dev`, and registers the card. The FE playback/capture links are dynamic DL1/VUL links; the BE `Codec` link connects CPU `I2S` to both codec DAIs. On first BE init, ASRC and jack detection are configured.

State and persistence: static card/link/jack structures hold long-lived card configuration. Hardware state is codec PLL/sysclk and RT5645 jack/ASRC configuration. No file-local mutable policy beyond the jack object exists.

Dependencies and integration: depends on ALSA SoC DPCM, RT5645 helper APIs, MT8173 AFE CPU DAIs `DL1`, `VUL`, and `I2S`, and DT phandles for platform and two codecs. RT5514 integration is represented as a codec DAI plus prefixed DAPM names, with no direct RT5514 helper calls here.

Risks: both codec DAIs receive identical PLL/sysclk calls; success depends on both codec drivers accepting PLL id 0/sysclk id 1 semantics. Missing either codec phandle aborts probe. Only fixed external MCLK is supported. Stored codec of_node references are not individually released in error paths beyond the platform node.

Test signals: DT probe with two codecs, DAPM route validation for `Sub DMIC1L/R`, headset jack/buttons via RT5645, simultaneous playback/capture through the shared BE, and sample-rate changes checking PLL/sysclk setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650-rt5514.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650-rt5676.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650-rt5676.c

Purpose: machine driver for MT8173 boards using RT5650/RT5645 plus RT5676/RT5677 and optional HDMI, including an intercodec link where RT5676 I2S2 is master.

Important APIs/types/functions: DAPM widgets/routes include speaker, internal mic, headphone, headset mic, `Sub`-prefixed RT5676 paths, and intercodec AIF2 routes; `mt8173_rt5650_rt5676_hw_params` sets codec PLL/sysclk from 12.288 MHz MCLK to `rate * 512`; `mt8173_rt5650_rt5676_init` configures RT5645 and RT5677 ASRC clocks and headset jack detection; DAI links include dynamic playback/capture/HDMI FEs, codec I2S BE, HDMI BE, and no-PCM intercodec BE; codec-conf prefixes the secondary codec.

Control flow: probe assigns the MT8173 AFE platform phandle to all links with empty platform entries, reads three codec phandles from `mediatek,audio-codec` indices 0/1/2 for RT5650, RT5676, and HDMI, associates RT5676 with the codec-conf prefix and intercodec link, then registers the card. BE init configures ASRC paths and jack detection. HDMI FE/BE links are present when the HDMI codec phandle is supplied.

State and persistence: static card, links, codec-conf, and jack objects persist. Mutable hardware state includes codec ASRC source selection, codec PLL/sysclk, jack state, DAPM routing, and the intercodec master/slave clocking relationship.

Dependencies and integration: depends on RT5645 and RT5677 codec helper APIs, MT8173 AFE DAIs `DL1`, `VUL`, `HDMI`, `I2S`, `HDMIO`, and a DT compatible `mediatek,mt8173-rt5650-rt5676`. HDMI is represented by codec DAI `i2s-hifi`.

Risks: all three audio-codec phandles are required, so boards without HDMI need a different card. The intercodec link uses dummy CPU/platform components and assumes codec-to-codec routing is valid. PLL/sysclk ids are hardcoded. Error paths do not put all parsed codec nodes.

Test signals: card probe with three codec phandles, RT5645 jack/buttons, RT5676 `Sub` DAPM route activation, playback/capture, HDMI playback, and intercodec path validation under DAPM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650-rt5676.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650.c

Purpose: machine driver for MT8173 boards using RT5650/RT5645 and HDMI, with optional choice of external 12.288 MHz MCLK or an internal `rate * 256` MCLK source.

Important APIs/types/functions: `enum mt8173_rt5650_mclk` and `mt8173_rt5650_platform_data` store PLL source selection; DAPM widgets/routes and pin switches expose speaker, internal mic, headphone, and headset mic; `mt8173_rt5650_hw_params` sets each codec DAI PLL/sysclk based on selected MCLK and `rate * 512`; `mt8173_rt5650_init` configures ASRC and headset jack/buttons; `mt8173_rt5650_hdmi_init` creates HDMI jack reporting; probe optionally reads `codec-capture` child DAI name and `mediatek,mclk`.

Control flow: probe parses the platform phandle, assigns it to all links, binds RT5650 codec phandle index 0 to both playback and capture codec slots, optionally overrides the capture codec DAI from a `codec-capture` child, optionally reads PLL source policy from `mediatek,mclk`, binds HDMI codec phandle index 1, then registers the card. Runtime hw_params programs codec PLL/sysclk. BE init selects ASRC source based on capture DAI name and registers headset detection; HDMI BE init registers an AVOUT jack.

State and persistence: static `mt8173_rt5650_priv` holds mutable clock-source policy read from DT; static jack objects persist. DAPM, codec clocking, ASRC, and jack state live in ALSA/codec hardware state. No file-private dynamic resources beyond devm card registration are used.

Dependencies and integration: depends on RT5645 helpers, HDMI codec jack support, MT8173 AFE DAIs `DL1`, `VUL`, `HDMI`, `I2S`, and `HDMIO`, and DT properties `mediatek,platform`, `mediatek,audio-codec`, optional `codec-capture`, and optional `mediatek,mclk`.

Risks: the capture codec slot initially aliases the playback codec node; changing only the DAI name assumes the same component exposes both DAIs. The `mediatek,mclk` value is trusted as enum-compatible. Missing HDMI codec phandle aborts probe. Codec node references are stored in global link arrays, making multiple instances unsafe.

Test signals: card probe with and without `codec-capture`, external/internal MCLK policy, RT5645 jack/buttons, HDMI jack reporting, playback/capture over shared codec BE, HDMI playback, and sample-rate changes checking PLL/sysclk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-rt5650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/Makefile

Purpose: defines the MT8183 ASoC build composition for the platform AFE module and board-specific machine drivers.

Important APIs/types/functions: `snd-soc-mt8183-afe-y` groups `mt8183-afe-pcm.o`, `mt8183-afe-clk.o`, and the DAI implementation objects for I2S, TDM, PCM, hostless, and ADDA. Kconfig objects map `CONFIG_SND_SOC_MT8183` to the aggregate AFE module, `CONFIG_SND_SOC_MT8183_MT6358_TS3A227E_MAX98357A` to the MT6358/TS3A227/MAX98357 machine driver, and `CONFIG_SND_SOC_MT8183_DA7219_MAX98357A` to the DA7219/MAX98357/RT1015 variants.

Control flow: during kernel build, kbuild compiles the listed objects into `snd-soc-mt8183-afe.o` when the platform config is enabled, and separately builds machine-driver modules based on board config symbols.

State and persistence: no runtime state; this file controls build-time object aggregation and module availability.

Dependencies and integration: integrates with kernel kbuild and the MT8183 ASoC Kconfig symbols. The aggregate object must include every sub-DAI implementation referenced by `mt8183-afe-pcm.c` registration callbacks.

Risks: missing an object from `snd-soc-mt8183-afe-y` would create unresolved symbols or absent DAI registrations. Machine drivers can build independently only if their referenced common/platform symbols are available through selected configs.

Test signals: `make M=sound/soc/mediatek/mt8183`, all relevant Kconfig combinations, modpost symbol checks, and boot-time probe of both aggregate AFE and board-specific card modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.c

Purpose: centralizes MT8183 audio clock acquisition, top-level AFE clock gating, APLL1/APLL2 routing and tuner control, sample-rate-family APLL selection, and I2S/TDM MCLK divider programming.

Important APIs/types/functions: `aud_clks` maps private clock IDs to DT/CCF names; `mt8183_init_clock` obtains all clocks; `mt8183_afe_enable_clock` enables infrastructure/audio mux/AFE/I2S BCLK switch clocks and sets mux parents; `mt8183_afe_disable_clock` ungates in reverse; `apll1_mux_setting` and `apll2_mux_setting` select 22.5792 MHz or 24.576 MHz APLL-derived paths; `mt8183_apll1_enable/disable` and `mt8183_apll2_enable/disable` control tuner clocks/registers and HD engine bits; `mt8183_get_apll_rate`, `mt8183_get_apll_by_rate`, and `mt8183_get_apll_by_name` route 44.1k-family vs 48k-family clocks; `mt8183_mck_enable/disable` controls per-I2S master-clock selectors and dividers.

Control flow: AFE probe calls `mt8183_init_clock`; runtime resume calls `mt8183_afe_enable_clock` before touching registers, and suspend calls disable. DAPM APLL supplies in I2S/TDM call APLL enable/disable. I2S/TDM MCLK DAPM events call `mt8183_mck_enable`, which selects an APLL family from the requested rate, enables an optional top selector, parents it to the selected APLL mux, enables the divider, and sets divider rate.

State and persistence: all clock pointers are stored in `mt8183_afe_private->clk`. Clock enable counts and parent/rate choices persist in the CCF while active. Tuner and HD engine state persists in regmap registers until disabled or runtime-suspended.

Dependencies and integration: depends on Linux CCF, `mt8183-reg.h` tuner/HD engine bits, `mt8183-afe-common.h` private state and MCLK IDs, and DAPM supply events from I2S/TDM DAI files. DT must expose every clock name in `aud_clks`.

Risks: APLL enable functions call mux-setting helpers but ignore their return values, so a failed mux parent change can be hidden until later clock operations. `mt8183_get_apll_by_name` treats every non-APLL1 name as APLL2. `mt8183_mck_enable` assumes `mck_id` is valid and only special-cases I2S5 MCK. Error paths disable clocks but do not always restore mux parents after later failures.

Test signals: probe with all clocks present, runtime suspend/resume, playback/capture at 44.1k-family and 48k-family rates, DAPM low-jitter/MCLK routes, `clk_summary` parent/rate checks, and fault injection for clock get/enable/set_parent/set_rate failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.h

Purpose: declares the MT8183 AFE clock-control API shared by the AFE core and DAI implementations.

Important APIs/types/functions: defines APLL widget names `APLL1_W_NAME` and `APLL2_W_NAME`, enum IDs `MT8183_APLL1`/`MT8183_APLL2`, forward-declares `struct mtk_base_afe`, and declares init, AFE clock enable/disable, APLL enable/disable, APLL selection helpers, and MCK enable/disable functions.

Control flow: included by `mt8183-afe-clk.c` for definitions and by I2S/TDM/AFE code for calls. DAPM event handlers use these declarations to toggle APLL and MCLK resources; runtime PM uses the AFE clock functions.

State and persistence: no storage in the header; state is carried through `struct mtk_base_afe` and its MT8183 private data.

Dependencies and integration: depends on the MediaTek common AFE object type but avoids including the full definition. The APLL widget names must match DAPM routes in I2S/TDM files.

Risks: no bounds or type safety around integer APLL/MCK IDs; callers must use IDs from `mt8183-afe-common.h`. Changing widget-name strings would break DAPM route predicates.

Test signals: compile all MT8183 objects together, modpost export checks, and runtime DAPM paths that exercise every declared function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-common.h

Purpose: provides shared MT8183 AFE IDs, IRQ IDs, MTKAIF protocol constants, MCLK IDs, private driver state, and cross-file function prototypes for the MT8183 ASoC platform.

Important APIs/types/functions: enumerates memifs `DL1`, `DL2`, `DL3`, `VUL12`, `VUL2`, `AWB`, `AWB2`, `MOD_DAI`, `HDMI`; DAIs `ADDA`, `PCM_1`, `PCM_2`, `I2S_0/1/2/3/5`, `TDM`, hostless loopback/speech; IRQs 0-8/11/12; MTKAIF protocol modes; MCLK IDs; `struct mt8183_afe_private` containing clock array, runtime PM bypass flag, per-DAI private pointers, MTKAIF calibration/DMIC fields, and MCK rates; prototypes for rate transforms, I2S sharing, and each DAI register callback.

Control flow: `mt8183-afe-pcm.c` allocates and owns `mt8183_afe_private`, uses enums to size memif/IRQ arrays, and invokes DAI register callbacks. DAI files store per-DAI state in `dai_priv`, use rate transform helpers, and read/write MTKAIF/DMIC state.

State and persistence: this header defines the long-lived private state layout. `dai_priv` entries are devm-allocated by DAI registration. MTKAIF calibration and DMIC flags persist for the device lifetime and affect ADDA capture configuration.

Dependencies and integration: includes ALSA SoC, Linux list/regmap, and MediaTek common AFE definitions. It is the coupling point between AFE core, clock control, and sub-DAI implementations.

Risks: enum ordering is ABI-like within the driver because arrays are indexed directly by IDs. `dai_priv` is a void pointer array, so type safety is manual. Adding/removing memifs or DAIs requires synchronized changes in memif tables, DAI drivers, register callbacks, and machine links.

Test signals: compile-time coverage across all MT8183 source files, probe-time memif/IRQ array sizing, DAI registration success for each callback, and audio route tests that exercise every DAI ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-pcm.c

Purpose: implements the MT8183 AFE platform core: PCM hardware capabilities, rate transforms, FE memif DAI definitions, DAPM routes for memory interfaces, memif/IRQ metadata, regmap/regcache policy, IRQ handling, runtime PM, reset, sub-DAI aggregation, and platform driver probe/remove.

Important APIs/types/functions: `mt8183_general_rate_transform` and `mt8183_rate_transform` map rates to hardware fields; `mt8183_memif_fs` and `mt8183_irq_fs` bridge common FE ops to rate transforms; `mt8183_memif_dai_driver` exposes DL/UL/HDMI FE DAIs; DAPM mixers route ADDA/I2S/DL sources into UL memifs; `memif_data` describes DMA registers, HD mode/alignment, enable and format fields; `irq_data` describes MCU IRQ registers; `mt8183_is_volatile_reg` defines regcache exclusions; `mt8183_afe_irq_handler` handles period interrupts; runtime PM hooks manage regcache and clocks; `dai_register_cbs` collects ADDA, I2S, PCM, TDM, hostless, and memif sub-DAIs; probe wires everything together.

Control flow: probe sets a 34-bit DMA mask, allocates `afe` and private state, attaches reserved memory or preallocation, initializes clocks, enables runtime PM, gets the parent syscon regmap, attaches/reinitializes a flat regcache after resetting audiosys, marks cache-only/dirty, initializes memifs with dynamic IRQ allocation except HDMI fixed to IRQ8, initializes IRQ data, requests the platform IRQ, registers all sub-DAIs, combines them into one DAI driver set, assigns common callbacks, and registers the platform and DAI components. Runtime resume enables clocks, syncs regcache, enables DCM and AFE; suspend disables AFE, polls off, clears IRQ status twice, marks regcache dirty/cache-only, and disables clocks. IRQ handling masks status by MCU enable bits and reports period elapsed for active memifs with assigned IRQs.

State and persistence: persistent state includes devm-managed `mtk_base_afe`, private MT8183 fields, regcache contents, memif/IRQ arrays, sub-DAI list, runtime PM state, and optional reserved-memory binding. Register writes are cached while the device is suspended, except volatile registers.

Dependencies and integration: depends on the MT8183 clock layer, DAI registration files, `mt8183-reg.h`, common MediaTek AFE FE/platform helpers, syscon parent regmap, reset controller `audiosys`, runtime PM, reserved memory, DMA mapping, and ALSA SoC. Machine drivers bind to FE DAI names `DL1`, `DL2`, `DL3`, `UL1`, `UL2`, `UL3`, `UL4`, `UL_MONO_1`, and `HDMI`.

Risks: default invalid-rate behavior warns and falls back to 48k or 16k fields rather than failing, which can hide bad constraints. `regmap_attach_dev` uses a syscon parent regmap, so parent DT and regmap lifetime are critical. Runtime PM bypass is used during cache initialization and must be balanced. HDMI has a constant IRQ while other memifs allocate dynamically. Volatile register ranges are extensive and easy to get stale against register headers.

Test signals: probe/reset/regcache initialization, runtime suspend/resume with register cache sync, all FE open/hw_params/trigger paths, interrupt period reporting, HDMI playback through fixed IRQ8, invalid-rate warning behavior, reserved-memory and preallocated-buffer boot variants, and DAI aggregation count matching all sub-DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-da7219-max98357.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-da7219-max98357.c

Purpose: board machine driver for MT8183 systems using DA7219 headset codec plus MAX98357A, RT1015, or RT1015P speaker amplifier variants, with optional HDMI/TDM and BT SCO routing.

Important APIs/types/functions: private state stores headset and HDMI jacks; hw_params helpers set MT8183 I2S sysclk, DA7219 MCLK/PLL, and RT1015 PLL/sysclk; hw_free stops DA7219 PLL; fixup callbacks force BE formats to S32_LE or S24_LE; FE startup callbacks constrain normal audio to 48 kHz stereo S16 and BT SCO to 8/16 kHz mono S16; DAI links cover DL1/DL2/DL3, UL1/UL2/UL3/UL_MONO_1, HDMI FE, ADDA, PCM1/2, I2S0/1/2/3/5, and TDM; init hooks set I2S clock sharing and HDMI/headset jacks; three `snd_soc_card` instances select MAX98357A, RT1015, or RT1015P.

Control flow: probe reads platform and optional HDMI codec phandles, selects the card from OF match data, patches the placeholder I2S3 BE link to the codec set and ops for the selected card, enables the TDM link when HDMI codec exists, assigns the platform node to links, requires `mediatek,headset-codec` as an aux DA7219 node, allocates private jack state, selects default pinctrl, and registers the card. During BE hw_params, DA7219 and RT1015 clocks are programmed. I2S2/I2S3 and I2S5/I2S0 sharing is set during BE init callbacks.

State and persistence: static card/link templates are mutated at probe based on card variant, so they are effectively single-instance global state. Per-card private state holds jack objects. Codec PLL/sysclk, DAPM pinctrl, I2S sharing, and HDMI jack state persist while the card is active.

Dependencies and integration: depends on DA7219 and RT1015 codec APIs, MT8183 AFE DAI names, common AFE component lookup `AFE_PCM_NAME`, BT SCO codec component names, optional HDMI codec phandle, headset aux codec phandle, pinctrl default state, and OF compatibles `mediatek,mt8183_da7219_max98357`, `mediatek,mt8183_da7219_rt1015`, and `mediatek,mt8183_da7219_rt1015p`.

Risks: static DAI link arrays are modified in place, making multiple card instances unsafe. DA7219 device name is hardcoded as `da7219.5-001a`, and RT1015 names use fixed I2C bus/address strings. Probe requires a headset codec phandle even if the rest of the card could work. TDM is ignored unless HDMI codec is present. Clock sharing init depends on AFE component lookup succeeding.

Test signals: probe each OF variant, validate I2S3 patching to MAX98357A/RT1015/RT1015P, headset jack and button mapping, DA7219 PLL start/stop, BT SCO 8/16 kHz mono constraints, normal 48 kHz stereo constraints, optional HDMI enablement, and I2S shared-clock routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-da7219-max98357.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-adda.c

Purpose: implements the MT8183 ADDA DAI for analog playback/capture through the audio codec interface, including DL/UL interconnect mixers, MTKAIF protocol/DMIC setup, ADDA DAPM supplies, and ADDA hw_params register programming.

Important APIs/types/functions: DAPM mixer controls connect DL1/DL2/DL3, ADDA UL, and PCM capture sources to ADDA DL channels; `mtk_adda_ul_event` applies DMIC-specific MTKAIF and UL source settings and delays after power-down; `MTKAIF_DMIC` kcontrol stores `afe_priv->mtkaif_dmic`; ADDA widgets include playback/capture supplies and clocks; `set_mtkaif_rx` programs MTKAIF protocol 1/2/2 clock phase settings; `mtk_dai_adda_hw_params` configures playback SRC/up-sampling/gain/SDM or capture MTKAIF/IIR/voice mode; `mt8183_dai_adda_register` contributes DAI driver, controls, widgets, and routes to the AFE sub-DAI list.

Control flow: registration appends one ADDA DAI to `afe->sub_dais`. During DAPM power-up for capture, DMIC mode may rewrite MTKAIF RX and UL source bits. Playback hw_params clears predistortion, maps rate through common ADDA helpers, chooses upsampling, applies gain, enables DL gain, and sets SDM attenuation. Capture hw_params configures MTKAIF protocol, selects internal ADC, maps UL rate, enables IIR, loads fixed high-pass coefficients, writes UL source config, and defaults to AMIC data mode unless the DAPM DMIC event overrides it.

State and persistence: `mtkaif_dmic`, MTKAIF protocol/calibration fields, and phase-cycle data live in `mt8183_afe_private`. ADDA register state is cached by the AFE regmap and controlled by DAPM supplies. The kcontrol changes persistent per-device capture behavior until changed again.

Dependencies and integration: depends on `mtk-dai-adda-common.h` rate transform helpers, MT8183 register definitions, interconnection indices, regmap, AFE private state, and DAPM routes from memif/I2S/PCM/hostless components.

Risks: some `regmap_update_bits` calls in the DMIC event use a zero mask with nonzero values, which is suspicious and may be no-ops depending on macro expansion. MTKAIF protocol defaults must be initialized elsewhere or the default branch does nothing. Playback gain constants are hardcoded. DMIC mode is user-controlled and can conflict with analog mic expectations.

Test signals: ADDA playback at 8k-192k, ADDA capture at 8/16/32/48k, `MTKAIF_DMIC` toggling, AMIC vs DMIC capture, MTKAIF protocol variants including calibrated phase data, DAPM supply sequencing, and register traces for SRC/IIR/SDM settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-hostless.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-hostless.c

Purpose: defines hostless MT8183 DAI routes for internal loopback and speech paths where AFE blocks exchange audio without a normal CPU memory stream driving every edge.

Important APIs/types/functions: `mtk_dai_hostless_routes` connects ADDA UL to ADDA DL for loopback and ADDA/PCM capture to PCM/ADDA playback for speech; `mtk_dai_hostless_startup` applies the AFE hardware constraints to the substream; `mtk_dai_hostless_driver` exposes `Hostless LPBK DAI` and `Hostless Speech DAI`; `mt8183_dai_hostless_register` adds these drivers and routes to `afe->sub_dais`.

Control flow: AFE probe calls the register callback; later ASoC DAPM can activate the hostless routes. On startup, hostless streams inherit `afe->mtk_afe_hardware` constraints. The actual signal routing is entirely through DAPM route activation rather than custom trigger or hw_params programming.

State and persistence: no private state is allocated. Route state lives in DAPM; runtime hardware constraints come from the shared AFE hardware structure.

Dependencies and integration: depends on ADDA and PCM DAPM endpoint names from other MT8183 DAI files and on the common AFE hardware limits initialized by `mt8183-afe-pcm.c`.

Risks: route correctness is string-name dependent. Because there is no custom hw_params/trigger logic, hostless use relies on the source/sink DAIs and DAPM supplies being configured elsewhere. The broad rate set may advertise combinations not useful for all internal paths.

Test signals: DAPM route activation for loopback and speech, startup constraint checks, internal loopback audio validation, and suspend/resume while hostless paths are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-hostless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-i2s.c

Purpose: implements MT8183 I2S DAI support for I2S0/I2S1/I2S2/I2S3/I2S5, including interconnect mixers, low-jitter and MCLK DAPM supplies, APLL selection, shared-clock routing, format selection, sysclk handling, and per-port register programming.

Important APIs/types/functions: `struct mtk_afe_i2s_priv` stores per-I2S rate, low-jitter flag, shared-clock source, MCLK id/rate/APLL, and EIAJ format flag; low-jitter kcontrols expose `I2S*_HD_Mux`; DAPM mixers connect DL/ADDA/PCM sources to playback I2S ports; APLL/MCLK DAPM event handlers call the clock layer; route predicate callbacks decide shared I2S, HD, APLL, and MCLK paths; `mtk_dai_i2s_config` writes rate/format/word-length registers for each I2S id and recursively configures shared ports; `set_sysclk` records desired MCLK; `set_fmt` selects I2S or left-justified/EIAJ; `mt8183_dai_i2s_set_share` exports shared-clock setup to machine drivers; `mt8183_dai_i2s_register` allocates private state and registers DAIs/routes/controls.

Control flow: AFE probe registers I2S DAIs and initializes private state. Machine drivers call `mt8183_dai_i2s_set_share` during BE init for pairs like I2S2/I2S3 and I2S5/I2S0. hw_params records the rate, programs the selected I2S register fields, and configures any shared I2S source. set_sysclk validates output direction and APLL divisibility before saving MCLK state. DAPM routes turn on the matching APLL, MCLK divider, low-jitter supply, and I2S enable bits when audio paths become active.

State and persistence: per-DAI private state persists in `afe_priv->dai_priv`. Low-jitter kcontrol values and MCLK settings persist until changed or powered down; MCLK event clears `mclk_rate` on POST_PMD. Register settings are cached by the AFE regmap across runtime PM.

Dependencies and integration: depends on MT8183 clock helpers, register definitions, interconnection IDs, AFE private state, ALSA DAPM, and machine-driver init hooks. It integrates with memif routes for I2S capture/playback and external codecs via machine DAI links.

Risks: route predicates and private lookup rely on string prefixes like `I2S0`. `set_sysclk` propagates MCLK state only when `share_i2s_id > 0`, so sharing from or to ID 0 may not mirror state as intended. Recursive shared configuration could misbehave if cycles are introduced. Only I2S and left-justified formats are supported.

Test signals: all I2S ports at 8k-192k with S16/S24/S32, low-jitter control toggles, MCLK sysclk validation for 44.1k/48k families, shared I2S pairs used by machine drivers, left-justified variant cards, and DAPM/clock parent checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-pcm.c

Purpose: implements two MT8183 PCM DAIs for modem/Bluetooth-style PCM links, including DAPM routes between DL/ADDA sources and modem pins plus register programming for PCM interface modes.

Important APIs/types/functions: enums describe PCM bit clock, sync, modem, AFIFO, clock-source, word-length, mode, format, inversion, and enable fields; DAPM mixers route DL2/DL1/ADDA UL into PCM playback channels; widgets include `PCM_1_EN`, `PCM_2_EN`, modem input/output pins; routes connect `AFE_TO_MD*` and `MD*_TO_AFE`; `mtk_dai_pcm_hw_params` programs `PCM_INTF_CON1` or `PCM2_INTF_CON`; DAI drivers expose `PCM 1` and `PCM 2` playback/capture with symmetric rate/sample bits.

Control flow: register callback contributes PCM DAIs, widgets, and routes to the AFE. hw_params maps the requested rate to a hardware mode. If either playback or capture widget for the DAI is already active, it returns without reprogramming shared registers. Otherwise it constructs the PCM register value for PCM mode B, AFIFO, dual-mic TX, and per-interface mode fields, then writes the appropriate register.

State and persistence: no private state is allocated. PCM interface state persists in AFE registers and is gated by DAPM supplies. Active widget state prevents reconfiguration while the paired direction is running.

Dependencies and integration: depends on MT8183 rate transform helper, register definitions, interconnection indices, and DAPM endpoint names from memif/ADDA/hostless machine routes.

Risks: active-widget checks avoid midstream reconfiguration but can also leave a second stream with mismatched requested params if constraints fail to enforce symmetry. Only rates 8/16/32/48 kHz are advertised. PCM mode and modem selection are hardcoded for internal modem, slave mode, PCM mode B.

Test signals: PCM1/PCM2 playback and capture at all four rates, simultaneous duplex startup order, DAPM modem pin routing, register trace for `PCM_INTF_CON1`/`PCM2_INTF_CON`, and suspend/resume preserving cached settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-tdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-tdm.c

Purpose: implements the MT8183 TDM playback DAI used primarily for HDMI output, including HDMI channel mux controls, TDM/MCLK/BCK DAPM supplies, format/sysclk handling, channel layout programming, and trigger-time enable.

Important APIs/types/functions: `struct mtk_afe_tdm_priv` stores BCK/MCLK ids/rates, output mode, inversion flags, MCLK multiple, and selected APLL; helper functions derive HDMI word length, TDM word length, BCK cycles, LRCK width, channel grouping, and fixed channel counts; eight HDMI channel DAPM muxes map HDMI output slots to memory channels; TDM clock events call `mt8183_mck_enable/disable`; `mtk_dai_tdm_cal_mclk` validates APLL divisibility; `mtk_dai_tdm_hw_params` computes MCLK/BCK, writes TDM and HDMI output registers; trigger toggles HDMI output and TDM enable; set_sysclk and set_fmt store clock/format policy; register callback allocates private state and registers the DAI/routes/widgets.

Control flow: registration initializes default `mclk_multiple = 128`, BCK id `MT8183_I2S4_BCK`, and MCLK id `MT8183_I2S4_MCK`. Machine BE links set dai_fmt/sysclk as needed. hw_params calculates a default MCLK if not explicitly set, computes BCK from rate/channels/format, writes `AFE_TDM_CON1/2`, HDMI channel count, and bit width. DAPM turns on MCLK and BCK supplies through the clock layer. Trigger start/resume enables HDMI out and TDM; stop/suspend disables both.

State and persistence: per-TDM private state persists in `afe_priv->dai_priv[MT8183_DAI_TDM]`. MCLK rate may persist after explicit sysclk or be reset by DAPM MCK shutdown. TDM/HDMI registers are regcache-managed by the AFE core.

Dependencies and integration: depends on clock helpers, MT8183 register definitions, HDMI memif DAI from `mt8183-afe-pcm.c`, optional HDMI codec machine links, and ALSA DAPM. The Makefile includes it in the aggregate AFE module.

Risks: BCK/MCLK divisibility problems are warnings in hw_params, not hard failures, after default MCLK calculation. Unsupported DAI formats default to I2S instead of returning an error. Channel mapping defaults to zero for invalid channel counts, though the DAI advertises 2-8. Verbose `dev_info` in hot paths can be noisy.

Test signals: HDMI/TDM playback with 2/4/6/8 channels, S16/S24/S32 formats, I2S and DSP_A formats, explicit sysclk and default MCLK paths, APLL family selection, HDMI channel mux controls, and trigger start/stop register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-tdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-interconnection.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-interconnection.h

Purpose: defines numeric interconnection input indices used by MT8183 DAPM mixer controls to connect AFE sources to sinks through `AFE_CONN*` registers.

Important APIs/types/functions: provides `#define` constants for I2S channels, ADDA UL channels, DL1/DL2/DL3 channels, PCM capture channels, and gain outputs. These constants are used as bit positions in `SOC_DAPM_SINGLE_AUTODISABLE` controls across ADDA, I2S, PCM, and memif DAI files.

Control flow: no executable code. At compile time, DAI files include the constants and bake them into DAPM mixer controls; at runtime, DAPM toggles the associated AFE connection register bits.

State and persistence: no state in the header; the effective state is the hardware connection matrix bits controlled by the generated DAPM controls.

Dependencies and integration: tied to MT8183 AFE hardware register layout and `mt8183-reg.h` connection register addresses. Every DAI route using these values depends on the numeric definitions matching the SoC interconnect matrix.

Risks: wrong bit positions silently route audio incorrectly. The sparse numbering makes copy/paste mistakes likely when adding routes. There is no compile-time validation against the register field definitions.

Test signals: route-level audio tests for each source/sink combination, DAPM register tracing for `AFE_CONN*`, and comparing constants against vendor register documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-interconnection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-mt6358-ts3a227-max98357.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-mt6358-ts3a227-max98357.c

Purpose: board machine driver for MT8183 systems using MT6358 primary codec, TS3A227E headset detection, MAX98357A/RT1015/RT1015P speaker variants, optional HDMI/TDM, BT SCO, and optional EC wake-on-voice.

Important APIs/types/functions: private state stores pinctrl states and headset/HDMI jacks; I2S hw_params helpers program CPU MCLK and RT1015 PLL/sysclk; fixups force S32_LE or S24_LE BE formats; startup callbacks constrain normal audio to 48 kHz stereo S16 and BT SCO to 8/16 kHz mono S16; TDM ops switch pinctrl on/off; WOV ops select `wov` and default pin states; init hooks create HDMI jack and set I2S sharing; DAI links cover DL/UL/HDMI/WOV FEs and ADDA/PCM/I2S/TDM BEs; four card variants select MAX98357A, MAX98357B left-justified, RT1015, or RT1015P wiring.

Control flow: probe parses the platform, optional EC codec, and optional HDMI codec phandles; selects card data from OF match; patches the Wake-on-Voice link to the EC codec and enables it when present; patches I2S3 BE link according to selected amp card; applies left-justified format for the `max98357b` card on I2S2/I2S3; enables TDM if HDMI codec is present; assigns platform phandles; optionally adds TS3A227E headset aux device; allocates private pinctrl/jack state; looks up all pin states, selects TDM off and default when available, then registers the card.

State and persistence: static DAI link/card templates are mutated at probe, so they are global card state. Per-card private state stores pinctrl handles and jack objects. Pinctrl state changes persist across TDM/WOV startup/shutdown. I2S sharing and codec clocking persist in AFE/codec state.

Dependencies and integration: depends on MT8183 AFE DAIs, RT1015 and TS3A227E codec helpers, optional EC codec DAI named `Wake on Voice`, optional HDMI codec DAI `i2s-hifi`, BT SCO wideband codec names, pinctrl states `default`, `aud_tdm_out_on`, `aud_tdm_out_off`, `wov`, and OF compatibles for the four card variants.

Risks: static link mutation is not multi-instance safe. Headset aux device is optional; without it no jack detection is installed. Missing pinctrl states are logged but many operations later may fail if required states are absent. WOV startup does not check for an invalid `PIN_WOV` state before selecting. Hardcoded codec component names make board/bus renames fragile.

Test signals: probe all four compatibles, optional EC WOV and HDMI phandle combinations, TS3A227E headset jack events, TDM pinctrl switching, WOV pinctrl switching, RT1015 PLL/sysclk, MAX98357B left-justified format, BT SCO constraints, and normal 48 kHz stereo playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-mt6358-ts3a227-max98357.c -->
