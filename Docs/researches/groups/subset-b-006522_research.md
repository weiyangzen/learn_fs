# Research Group: subset-b-006522

This grouped report covers the requested MediaTek ASoC source files. Each section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-mt6359.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-mt6359.c

## Purpose

`mt8188-mt6359.c` is the ALSA SoC machine driver for MT8188 boards using the MT6359 PMIC codec and several optional external codecs or amplifiers. It binds through `mtk_soundcard_common_probe`, provides the static DPCM front-end/back-end topology for the MT8188 audio card, and customizes that topology at probe time based on the codec endpoints described in device tree and the `mtk_soundcard_pdata` selected by compatible string.

The file covers both the baseline EVB design and variants with NAU8825, RT5682S, ES8326, MAX98390, HDMI, DisplayPort, and dumb amplifier endpoints. It also exposes SOF bridging links for `SOF_DMA_DL2`, `SOF_DMA_DL3`, `SOF_DMA_UL4`, and `SOF_DMA_UL5`.

## Important APIs, Types, and Data

The core static data is a large `struct snd_soc_dai_link mt8188_mt6359_dai_links[]` array. It defines playback FEs (`DL2`, `DL3`, `DL6`, `DL7`, `DL8`, `DL10`, `DL11`), capture FEs (`UL1`, `UL2`, `UL3`, `UL4`, `UL5`, `UL6`, `UL8`, `UL9`, `UL10`), regular BEs (`DL_SRC`, `UL_SRC`, `DMIC`, `DPTX`, `ETDM*`, `PCM1`), and SOF BEs (`AFE_SOF_DL2`, `AFE_SOF_DL3`, `AFE_SOF_UL4`, `AFE_SOF_UL5`). The `SND_SOC_DAILINK_DEFS` macros associate CPU DAIs, dummy codecs, MT6359 codec DAIs, or empty platform components.

The driver defines `enum mt8188_jacks` for shared jack storage: headset, DP, HDMI, and max count. DAPM widgets and controls include baseline MT6359 headphone/mic, AP DMIC, HDMI/DP sinks, SOF DMA mixers, and pinctrl widgets for ETDM speaker/headphone and MTKAIF pin states. Optional widgets and controls are added for dumb speakers, dual/rear speakers, and NAU8825-style headphone jacks.

Important functions are:

- `mt8188_mt6359_mtkaif_calibration()`: runs MTKAIF MISO phase calibration against MT6359 using topckgen test registers.
- `mt8188_mt6359_accdet_init()` and `mt8188_mt6359_init()`: set MT6359 protocol, calibrate MTKAIF, and enable PMIC accessory detection.
- `mt8188_dptx_hw_params()` and `mt8188_dptx_hw_params_fixup()`: force DPTX BE clocking and 32-bit format.
- `mt8188_hdmi_codec_init()` and `mt8188_dptx_codec_init()`: create AV output jacks and register them with codec components.
- `mt8188_max98390_hw_params()` and `mt8188_max98390_codec_init()`: configure four-slot TDM speaker routing and add speaker controls.
- `mt8188_headset_codec_init()` / `mt8188_headset_codec_exit()`: add headset DAPM controls, map jack buttons, and attach/detach external headset codec jack callbacks.
- Codec-specific hw_params hooks for NAU8825, RT5682S, and ES8326 set PLL/sysclk/TDM slot requirements.
- `mt8188_sof_be_hw_params()` validates the AFE component is runtime-active before SOF BE use.
- `mt8188_mt6359_soc_card_probe()` is the central topology customizer.

## Control Flow

Module load registers a platform driver named `mt8188_mt6359` with an OF match table for four compatible strings. The common MediaTek soundcard probe receives the selected `mtk_soundcard_pdata`, whose `card_data` points to the shared `mt8188_mt6359_soc_card` and whose `soc_probe` callback is `mt8188_mt6359_soc_card_probe()`.

Probe-time customization walks every prelink. For `DPTX_BE` and `ETDM3_OUT_BE`, non-dummy codecs receive DP or HDMI jack init functions. For `DL_SRC_BE` or `UL_SRC_BE`, the first link receives MT6359 init. For ETDM in/out links, the codec DAI name controls behavior: MAX98390 links receive speaker init and, unless flagged as two-amp I2S mode, MAX98390 TDM hw_params; NAU8825, RT5682S, and ES8326 links receive their respective ops plus headset init/exit; otherwise a non-dummy codec gets dumb speaker init once.

At PCM startup/hw_params time, DPCM FEs and BEs use the configured ops. DPTX sets MCLK to `rate * 256`. RT5682S programs PLL1 from BCLK and sets CPU MCLK to `rate * 128`. ES8326 and NAU8825 set codec/CPU clocks to common audio multiples. MAX98390 maps four amplifiers by I2C component name to TDM TX slots.

MT6359 init first selects `MT6359_MTKAIF_PROTOCOL_2_CLK_P2`, then performs calibration. Calibration locates the AFE component, obtains `mt8188_afe_private`, optionally turns on the `MTKAIF_PIN` DAPM pinctrl state, runtime-resumes the AFE device, enables codec calibration, sweeps phases 0 through 42, and watches topckgen monitor bits for MISO completion and cycle changes. It stores chosen phases and cycle counts in `afe_priv->mtkaif_params`, then disables calibration, runtime-puts the AFE device, and restores pinctrl.

## State and Persistence

Persistent runtime state is held by ALSA card structures and the MediaTek AFE private data, not by files. Jack state lives in `mtk_platform_card_data->jacks`. MTKAIF calibration results persist in `afe_priv->mtkaif_params` for later AFE/codec use. Probe customization mutates DAI link function pointers and ops in the shared card instance for the live device. DAPM widget/control additions are registered into the sound card and persist until card teardown.

The driver uses Linux runtime PM around MTKAIF calibration and checks runtime PM state for SOF BE hw_params. It does not store userspace-visible configuration outside ALSA controls and jack state.

## Dependencies and Integration Points

This file depends on ALSA SoC core APIs, MediaTek common soundcard helpers, MTK SOF helpers, MT8188 AFE private definitions, MT6359 codec and accessory-detection helpers, NAU8825 and RT5682 codec headers, Linux input key codes, OF matching, regmap, and runtime PM. Device-tree endpoint naming and codec DAI names are critical because probe logic selects ops by string comparison (`max98390-aif1`, `nau8825-hifi`, `rt5682s-aif1`, `ES8326 HiFi`) and link names (`DPTX_BE`, `ETDM*_BE`, etc.).

Integration with topckgen is through `afe_priv->topckgen` and local offsets `CKSYS_AUD_TOP_CFG` / `CKSYS_AUD_TOP_MON`. SOF integration is declared by `g_sof_conn_streams` and passed via `mt8188_sof_priv`.

## Risks

The calibration loop is hardware-sensitive. If topckgen is absent it logs and skips calibration; if monitor done bits never assert it exits after 10000 polls and records failure. The loop uses cycle transition detection to pick `phase - 1`, so off-by-one or monitor instability can produce bad audio capture timing. `pm_runtime_get_sync()` is not checked, so a runtime PM failure could be hidden before register access.

Several probe decisions rely on exact DAI link and codec DAI strings. A device-tree or codec-driver rename can silently skip jack setup or clock ops. MAX98390 slot assignment relies on exact I2C component names, so address changes require matching updates. `mt8188_mck_disable` style bounds concerns are not in this file, but similar DAI ops here should still validate component counts before dereferencing codec DAIs. The shared static card/link structures mean multi-instance use would need scrutiny, although these SoC machine drivers generally bind one card per platform.

## Test Signals

Useful validation includes kernel build coverage for `CONFIG_SND_SOC_MT8188`, boot probe logs for each compatible, ALSA card enumeration, DPCM route creation, `amixer` visibility for expected DAPM switches, jack insert/removal for MT6359/NAU8825/RT5682S/ES8326, HDMI/DP AVOUT jack events, playback/capture smoke tests on all FEs, SOF playback/capture through the four SOF DMA paths, and suspend/resume with active or recently active audio. Hardware tests should include MTKAIF calibration logs, headset button mapping per codec variant, MAX98390 two-amp and four-amp speaker layouts, and DPTX/HDMI sample-rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-mt6359.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-reg.h

## Purpose

`mt8188-reg.h` is the MT8188 audio front-end hardware register map. It provides symbolic offsets and bitfield masks for the MT8188 AFE, ASYS, ADDA, DMIC, ETDM, PCM, SPDIF, DPTX, GASRC, connection matrix, secure mask, memory interface, interrupt, clock-gate, gain, monitor, and tuner blocks. It is a declarative hardware contract consumed by MT8188 platform and DAI drivers rather than executable code.

## Important APIs, Types, and Data

The file exports preprocessor macros only. Major offset families include:

- Top/control and IRQ registers: `AUDIO_TOP_CON0..6`, `ASYS_IRQ*`, `AFE_IRQ*`, `ADSP_IRQ_*`, status/monitor registers, and sine generator controls.
- Digital audio interface blocks: `PCM_INTF_CON1/2`, `ETDM_IN*`, `ETDM_OUT*`, `ETDM_COWORK_*`, `AFE_DPTX_CON/MON`, SPDIF in/out configuration and channel status registers.
- Analog codec interface blocks: `AFE_ADDA_*`, `AFE_ADDA6_*`, MTKAIF config/monitor registers, ADDA UL/DL source controls, SDM and DC compensation controls.
- Memory interface blocks: DL and UL base/current/end/control registers for `DL1`, `DL2`, `DL3`, `DL6`, `DL7`, `DL8`, `DL10`, `DL11`, `UL1`, `UL2`, `UL3`, `UL4`, `UL5`, `UL6`, `UL8`, `UL9`, and `UL10`, plus checksum, bus monitor, agent counter, and buffer monitor registers.
- Routing fabric: very large `AFE_CONN*`, `AFE_CONN*_1.._6`, `AFE_CONN_RS`, `AFE_CONN_16BIT`, `AFE_CONN_24BIT`, `AFE_CONN_DI`, and matching `AFE_SECURE_MASK_CONN*` definitions.
- DMIC and gain blocks: `AFE_DMIC0..3_*`, `DMIC_GAIN*`, `DMIC_BYPASS_HW_GAIN`, and generic gain-control masks.
- Sample-rate conversion blocks: `AFE_ASRC11/12_*` and `AFE_GASRC0..11_NEW_CON*` with timing and calibration masks.

`AFE_MAX_REGISTER` is defined as `AFE_CONN183_6`, marking the highest register offset known to this map and typically feeding regmap bounds.

Important bitfield macros cover clock gates (`AUDIO_TOP_CON*_PDN_*`), ASYS timing bits, PCM polarity/master/format bits, MTKAIF protocol/delay bits, DMIC mode/gain bits, ETDM channel/word/clock/format bits, DPTX channel and sample-width bits, ADDA voice/mute/gain/source controls, and GASRC calibration/timing fields.

## Control Flow

There is no runtime control flow in this header. Control flow is indirect: other MT8188 driver files include these macros and use them in regmap reads/writes, clock gating, DAI setup, memif setup, interrupt setup, and ALSA control handling. The register definitions are grouped by hardware block and by register field comments, which indicates expected call-site ownership. For example, ETDM DAI code should combine `ETDM_CON0_*`, `ETDM_IN_CON*`, and `ETDM_OUT_CON*` masks when programming serial ports; memif code should use the `AFE_DL*` and `AFE_UL*` base/end/control offsets; clock code should update `AUDIO_TOP_CON*` PDN bits.

## State and Persistence

The header itself holds no state. It describes volatile hardware state in MMIO registers. State persistence is therefore the hardware register contents across clock/reset domains and the regmap cache policy used by the including driver. Register writes affect live audio routing, DMA memory windows, interrupt enablement, clock gating, gain ramps, ASRC calibration, and secure routing masks. Because many macros define control bits for clocks or resets, incorrect use can persist until hardware reset or explicit reprogramming.

## Dependencies and Integration Points

This file assumes Linux `BIT()` and `GENMASK()` macros are available from the including context. It integrates with MT8188 AFE common/platform drivers, DAI implementations for ADDA/DMIC/ETDM/PCM/DPTX/SPDIF/GASRC, and regmap configuration. The exact offsets are a hardware ABI between the kernel and MT8188 silicon. Device-tree resources must map the AFE register base that these offsets are relative to.

The header also ties into cross-file private data: machine and platform drivers use MTKAIF-related masks and offsets when calibrating or setting codec interface protocols; clock drivers use audio top PDN bits; PCM/memif code uses base/current/end definitions to program DMA windows.

## Risks

The main risk is silent hardware misprogramming. Offsets and masks are not type-checked, many names are mechanically similar, and several large connection and secure-mask ranges differ only by suffix. A single copied `_5` versus non-suffixed connection register can route the wrong audio path or bypass a security mask. Some definitions have spelling quirks such as `VOCIE` and `MULIT`; downstream code must use the exact macro names. Because `AFE_MAX_REGISTER` gates the declared map size, omissions above that address can block valid regmap access if hardware grows.

Another risk is semantic inversion in PDN/gate bits. Some `AUDIO_TOP_CON*` bits are power-down bits where setting disables a block, while other enable fields elsewhere use positive logic. Call sites must centralize on helpers where possible. Secure-mask registers need particular care because testing only normal audio may not expose mistakes in protected or HDMI/DP routes.

## Test Signals

Build testing catches missing macros and syntax but not offset correctness. Useful runtime signals include regmap read/write traces, successful probe without regmap range failures, playback/capture through every memif listed by the platform driver, ETDM/PCM/DPTX/SPDIF loopback where available, DMIC capture at all supported rates, gain ramp behavior, interrupt delivery and clearing for ASYS/AFE IRQs, ASRC/GASRC calibration status, suspend/resume register restoration, and negative testing of secure or disabled routes. Hardware bring-up should compare this header against the MT8188 datasheet or vendor register dump and audit all `AFE_CONN*` and `AFE_SECURE_MASK_CONN*` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/Makefile

## Purpose

The MT8189 ASoC Makefile wires the platform and machine drivers into the kernel build. It adds the shared MediaTek ASoC include directory, aggregates the MT8189 AFE platform object from its component source files, and conditionally builds the MT8189 platform and NAU8825 machine driver based on Kconfig symbols.

## Important APIs, Types, and Data

The file is Kbuild data rather than C code. `subdir-ccflags-y += -I$(srctree)/sound/soc/mediatek/common` makes common MediaTek headers visible to all compilation units in this folder. `snd-soc-mt8189-afe-objs` declares the object list linked into `snd-soc-mt8189-afe.o`: PCM core, clock control, ADDA DAI, I2S DAI, PCM DAI, and TDM DAI. `obj-$(CONFIG_SND_SOC_MT8189)` enables the platform object, while `obj-$(CONFIG_SND_SOC_MT8189_NAU8825)` enables `mt8189-nau8825.o`.

## Control Flow

There is no runtime control flow. During kernel build, Kbuild expands the conditional object variables according to `.config`. If `CONFIG_SND_SOC_MT8189=y` or `m`, all listed platform objects are compiled and linked as the MT8189 AFE driver. If the NAU8825 machine-driver config is selected, that machine driver is also built.

## State and Persistence

No runtime state is held. The Makefile affects build artifacts and module composition. A stale or missing object entry persists only as a build configuration issue until the Makefile or Kconfig selection changes.

## Dependencies and Integration Points

The platform object list must stay aligned with implemented MT8189 source files and exported functions declared in `mt8189-afe-common.h` and `mt8189-afe-clk.h`. The include path integrates with `../common/mtk-base-afe.h` and other shared MediaTek audio helpers. Kconfig symbols `CONFIG_SND_SOC_MT8189` and `CONFIG_SND_SOC_MT8189_NAU8825` must be defined elsewhere in the sound subsystem.

## Risks

The main risk is build drift. Adding a new DAI implementation without adding it to `snd-soc-mt8189-afe-objs` can leave registration functions unresolved or features absent. Removing or renaming a source file without updating this list breaks builds. If the common include path changes, all local sources using shared MediaTek headers can fail. Machine drivers are conditional separately from the platform driver, so configuration dependencies must prevent selecting a machine driver without the required platform support.

## Test Signals

Useful checks are `make M=sound/soc/mediatek/mt8189`, full kernel builds for built-in and module configurations, `modpost` symbol checks, and boot/probe validation with `CONFIG_SND_SOC_MT8189` and `CONFIG_SND_SOC_MT8189_NAU8825` enabled. Build logs should show every object in `snd-soc-mt8189-afe-objs` compiled exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.c

## Purpose

`mt8189-afe-clk.c` implements MT8189 AFE clock acquisition, gating, parent selection, APLL setup, MCLK setup, and always-on peripheral clock enablement. It is the clock-control layer used by MT8189 platform and DAI drivers to make register access, main AFE operation, audio PLLs, and serial-port master clocks available.

## Important APIs, Types, and Data

`struct mt8189_mck_div` maps each logical MCLK ID to an optional mux clock and a divider clock. `mck_div[]` covers I2S input/output MCLKs, FMI2S, TDM output MCLK, and TDM output BCK. `aud_clks[]` maps the `MT8189_CLK_*` enum values from `mt8189-afe-clk.h` to device-tree clock names such as `top_aud_intbus`, `apll1`, `apll12_div_i2sin0`, `top_i2sout0`, and `aud_mst_ck_peri`.

Exported or externally declared functions include:

- `mt8189_init_clock()`: allocates the clock pointer array, obtains all clocks with `devm_clk_get`, resets APLL muxes to 26 MHz, and enables AO peripheral clocks.
- `mt8189_afe_enable_clk()` / `mt8189_afe_disable_clk()`: wrappers over `clk_prepare_enable` and `clk_disable_unprepare`.
- `mt8189_afe_enable_reg_rw_clk()` / `mt8189_afe_disable_reg_rw_clk()`: prepare clocks needed for AFE register/internal SRAM access.
- `mt8189_afe_enable_main_clock()` / `mt8189_afe_disable_main_clock()`: toggle the main audio 26 MHz top clock gate.
- `mt8189_apll1_enable()` / `mt8189_apll1_disable()` and `mt8189_apll2_enable()` / `mt8189_apll2_disable()`: configure muxes, top gates, tuner registers, and positive APLL enable bits.
- `mt8189_get_apll_rate()`, `mt8189_get_apll_by_rate()`, and `mt8189_get_apll_by_name()`: identify APLL sources.
- `mt8189_mck_enable()` / `mt8189_mck_disable()`: select an APLL parent, enable divider clocks, set output rates, and shut them down.

Static helpers convert clock-gate IDs to registers, masks, and on/off values. This matters because some top fields are positive enables in `AUDIO_ENGEN_CON0`, while others are power-down bits in `AUDIO_TOP_CON4`.

## Control Flow

Clock initialization starts with `mt8189_init_clock()`. It allocates `afe_priv->clk`, fetches every clock named in `aud_clks[]`, calls `mt8189_afe_disable_apll()` to put APLL-related muxes back under `clk26m`, and then enables always-on peripheral clocks for intbus, slave, and master audio peripheral domains. Failure in clock fetching aborts initialization; failure in AO enable unwinds only the clocks enabled by that helper.

APLL enable first calls either `apll1_mux_setting(true)` or `apll2_mux_setting(true)`. These helpers enable the top APLL mux, set it to the APLL clock, enable the corresponding engineering mux, set it to APLL divided by four, enable the audio high mux, and set it to the full APLL. Errors unwind previously enabled muxes and parents. The public APLL enable function then clears top power-down gates, programs `AFE_APLL1_TUNER_CFG` or `AFE_APLL2_TUNER_CFG`, enables the frequency tuner, and asserts the positive APLL enable bit. Disable reverses the positive enable, disables tuner, applies PDN gates, and returns muxes to 26 MHz.

MCLK enable validates `mck_id`, derives APLL1 for rates not divisible by 8000 and APLL2 for 8 kHz-family rates, optionally enables and reparents the MCLK mux, enables the divider clock, and sets the divider to the requested rate. MCLK disable disables the divider and optional mux.

Register-read/write clock enable sets audio intbus and audio high mux parents to `clk26m` after enabling them. Main clock enable/disable writes the `MT8189_AUDIO_26M_EN_ON` top gate through regmap.

## State and Persistence

Runtime state is stored in `struct mt8189_afe_private`: `clk` is the devm-managed array of clock handles, and `mck_rate[]` is declared in the private struct although this file does not update it. Hardware state persists in the common clock framework's prepare/enable counts, mux parent selections, divider rates, and AFE regmap bits. APLL tuner register settings persist until disabled, reset, or overwritten.

No file-backed persistence exists. All state is per-device and tied to probe lifetime. Because this layer uses prepare/enable counts, callers must keep enable/disable calls balanced.

## Dependencies and Integration Points

The implementation depends on Linux CCF (`struct clk`, `devm_clk_get`, `clk_set_parent`, `clk_set_rate`, `clk_get_rate`, `clk_prepare_enable`), regmap, and MT8189 register macros from `mt8189-reg.h`. It assumes `afe->platform_priv` is a valid `struct mt8189_afe_private` and `afe->regmap` is initialized before gate/tuner operations.

Device tree must provide every clock name listed in `aud_clks[]`; one missing clock fails `mt8189_init_clock()`. Other MT8189 DAI files should call `mt8189_apll*` and `mt8189_mck_*` around stream setup, and platform code should call `mt8189_afe_enable_reg_rw_clk()` before register access when the domain may be off.

## Risks

`mt8189_mck_disable()` checks only `mck_id < 0`; it does not reject `mck_id >= MT8189_MCK_NUM` before indexing `mck_div[mck_id]`. Callers must pass valid IDs or this can read past the table. `mt8189_mck_enable()` can leak an enabled mux or divider on later parent/rate failures because not every error path disables earlier clocks. Similarly, APLL enable has multi-step regmap/clock side effects and does not fully unwind all top gates if a later gate write fails.

`mt8189_afe_enable_reg_rw_clk()` ignores return values from enable and parent-setting helpers, so callers receive success even if clocks failed. `mt8189_afe_enable_top_cg()` returns success when `afe->regmap` is null after logging an error, which can hide probe ordering mistakes. `mt8189_get_apll_by_name()` returns APLL2 for all non-`APLL1` names, so invalid names are not distinguishable from a valid APLL2 request.

Concurrent callers need external serialization or balanced reference patterns; this file does not maintain explicit users or locks. Parent selection of shared muxes can affect multiple active MCLK users if the clock tree is not designed for concurrent independent rates.

## Test Signals

Build coverage should include all MT8189 AFE objects. Runtime validation should inspect probe logs for successful `devm_clk_get` of every name, clock summary/debugfs parent and rate changes during 44.1 kHz and 48 kHz-family playback, balanced prepare counts after stream stop, and regmap traces for `AUDIO_ENGEN_CON0`, `AUDIO_TOP_CON4`, `AFE_APLL1_TUNER_CFG`, and `AFE_APLL2_TUNER_CFG`. Audio tests should cover I2S in/out, TDM MCLK/BCK, repeated stream start/stop, rate switching between APLL1 and APLL2 families, suspend/resume, and forced failure injection for missing clocks or failed `clk_set_parent`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.h

## Purpose

`mt8189-afe-clk.h` is the public MT8189 AFE clock-control interface for local platform and DAI code. It defines logical APLL IDs, the full clock-index enum used by `mt8189-afe-clk.c`, APLL widget names, and function prototypes for enabling, disabling, selecting, and initializing audio clocks.

## Important APIs, Types, and Data

`APLL1_W_NAME` and `APLL2_W_NAME` provide stable string names for APLL selection, likely shared with DAPM or controls. The first enum defines logical `MT8189_APLL1` and `MT8189_APLL2`. The second enum defines every clock handle index in `afe_priv->clk`: top muxes, APLL roots, APLL divided clocks, APLL12 dividers for I2S/FMI2S/TDM, per-interface muxes, `clk26m`, and peripheral audio clocks. `MT8189_CLK_NUM` sizes the array.

The API exposes MCLK management (`mt8189_mck_enable`, `mt8189_mck_disable`), APLL lookup (`mt8189_get_apll_rate`, `mt8189_get_apll_by_rate`, `mt8189_get_apll_by_name`), initialization (`mt8189_init_clock`), raw clock wrapper helpers, per-APLL enable/disable, main-clock enable/disable, and register-read/write clock enable/disable.

## Control Flow

The header has no executable control flow. It shapes call flow by requiring consumers to call `mt8189_init_clock()` at platform probe before any other clock operation, then use the narrower helpers around stream and register-access lifetimes. DAI code should enable an APLL and MCLK before programming serial output clocks and disable them when the route is no longer active. Platform PM code should use main and reg-rw helpers when entering or leaving powered states.

## State and Persistence

No state is stored in the header. The enum values are persistent ABI within this driver directory because they index `afe_priv->clk` and the `aud_clks[]` table. Reordering or inserting values without matching `mt8189-afe-clk.c` and device-tree clock names can break every clock operation. Runtime state lives in `struct mt8189_afe_private` from `mt8189-afe-common.h` and the Linux clock framework.

## Dependencies and Integration Points

The header forward-declares `struct mtk_base_afe` and uses `struct clk` in prototypes, so including files can call clock helpers without pulling in implementation details. It integrates with `mt8189-afe-common.h` through `MT8189_MCK_NUM` and `struct mt8189_afe_private`, with `mt8189-afe-clk.c` for implementation, with MT8189 DAI files for stream clocking, and with Kbuild through the platform object list.

## Risks

The clock enum order is fragile. It must match `aud_clks[]` exactly and must remain consistent with any device-tree clock-names binding. Adding a clock requires updating this enum, the string table, and likely binding documentation. The exposed raw enable/disable wrappers make it possible for callers to bypass higher-level sequencing, so usage audits should prefer APLL/MCLK/main/reg-rw helpers where possible. `mt8189_get_apll_by_name()` has no invalid-name status in its signature, which limits caller-side validation.

## Test Signals

Compile tests catch signature mismatches between declarations and definitions. Runtime tests should validate every public helper has at least one exercised caller path: probe for `mt8189_init_clock`, register access paths for reg-rw helpers, playback/capture setup for MCLK helpers, and 44.1/48 kHz-family streams for APLL selection. Static analysis should check that enum additions are reflected in the implementation string table and in `MT8189_CLK_NUM`-sized allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-common.h

## Purpose

`mt8189-afe-common.h` is the shared MT8189 AFE platform contract. It defines sample-rate encodings, MTKAIF protocol IDs, memory-interface and DAI IDs, interrupt IDs, audio clock-gate IDs, MCLK IDs, channel-merge IDs, the private per-device state structure, and DAI registration prototypes. MT8189 PCM, clock, and DAI implementation files include this header to share IDs and state layout.

## Important APIs, Types, and Data

The rate enums map ALSA rates to hardware encodings. `MTK_AFE_RATE_*` covers the common internal rate table including high-rate and 260 kHz variants. `MTK_AFE_IPM2P0_RATE_*` maps the newer IPM 2.0 hardware encodings with explicit hex values. Smaller `MTK_AFE_DAI_MEMIF_RATE_*` and `MTK_AFE_PCM_RATE_*` enums cover reduced-rate domains.

The MTKAIF protocol enum defines protocol 1, protocol 2, and protocol 2 clock phase 2. The large memif/DAI enum assigns IDs for download memifs, uplink memifs, ETDM input, HDMI, and non-memif DAIs such as ADDA, ADDA channel groups, AP DMIC, I2S in/out, PCM, TDM, and DPTX. `MT8189_DAI_NUM` sizes DAI-private arrays.

IRQ enums define normal MCU IRQ IDs `MT8189_IRQ_0` through selected IRQ 31 and a custom TDM IRQ namespace. Clock-gate enums define IDs consumed by clock helpers for `AUDIO_ENGEN_CON0` and `AUDIO_TOP_CON4` bits. MCLK IDs enumerate I2S, FMI2S, TDM MCLK, and TDM BCK clocks. `CM0`, `CM1`, and `CM_NUM` describe channel-merge state slots.

`struct mt8189_afe_private` is the central state object. It contains the clock-handle array, PMIC regmap, per-DAI private pointers, MTKAIF protocol/calibration/DMIC fields, ADDA vote/status booleans, MCLK rate cache, and channel-merge rate/channel fields.

The file declares DAI registration entry points: `mt8189_dai_adda_register`, `mt8189_dai_i2s_register`, `mt8189_dai_pcm_register`, and `mt8189_dai_tdm_register`.

## Control Flow

The header itself has no executable control flow, but it defines the call graph glue. Platform probe allocates and attaches `struct mt8189_afe_private`, initializes clocks and regmaps, then invokes the DAI registration functions declared here. DAI and PCM code use the shared enum IDs to index memif data, IRQ data, DAI private storage, clock gates, and MCLK rates. Clock code uses the clock-gate and MCLK enums to map abstract driver requests to register masks and clock framework handles.

## State and Persistence

Runtime state persists for the life of the probed AFE device in `struct mt8189_afe_private`. `clk` is devm-owned and remains valid until device teardown. `pmic_regmap` points at PMIC register access. `dai_priv[]` stores per-DAI submodule state. MTKAIF calibration fields store chosen phases and cycles, while booleans track ADDA downlink/uplink/vote/max-volume status. `mck_rate[]` can cache requested MCLK rates across DAI operations. Channel-merge fields keep active rates and merged channel count.

No file-backed persistence exists. Any hardware state represented by these fields must be reinitialized after probe, reset, or resume according to platform PM behavior.

## Dependencies and Integration Points

The header includes Linux regmap, ALSA SoC, `mt8189-reg.h`, and the common MediaTek `mtk-base-afe.h`. It integrates every MT8189 source file in the directory: the Makefile compiles implementations that agree on these IDs; `mt8189-afe-clk.c` uses clock and private-state definitions; DAI files use memif/DAI/IRQ/rate IDs; machine drivers indirectly depend on the platform exposing the correct DAI names and capabilities.

The enum values also form internal ABI with static arrays in implementation files. For example, memif arrays are expected to be indexed by `MT8189_MEMIF_*`, DAI-private arrays by IDs below `MT8189_DAI_NUM`, and clock arrays by values from `mt8189-afe-clk.h`.

## Risks

The largest risk is enum drift. Adding, removing, or reordering IDs can corrupt indexing into arrays throughout the driver. Because many arrays are sized by terminal enum values, out-of-tree users or partially updated files can compile but misaddress state. `dai_priv` uses `void *`, so type safety is deferred to callers. Calibration arrays have fixed size 4 rather than an explicit MTKAIF channel enum, so related code must agree on channel count.

Shared booleans such as `is_adda_dl_on`, `is_adda_ul_on`, and `is_mt6363_vote` may need locking if manipulated from concurrent DAI paths. The header does not define synchronization rules. Rate enums must be mapped carefully; the standard, IPM2.0, memif, and PCM rate namespaces are not interchangeable even when names look similar.

## Test Signals

Compile tests should cover all MT8189 objects after any enum or struct change. Runtime signals include successful registration of every DAI ID, correct ALSA PCM exposure for all memifs, IRQ delivery for all configured IRQ IDs, successful clock/MCLK setup using private `clk` state, MTKAIF calibration persistence, ADDA vote transitions, and channel-merge operation. Static checks should verify array sizes and switch statements cover `MT8189_DAI_NUM`, `MT8189_MEMIF_NUM`, `MT8189_IRQ_NUM`, `MT8189_AUDIO_CG_NUM`, and `MT8189_MCK_NUM` where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-common.h -->
