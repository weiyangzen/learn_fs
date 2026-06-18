# Research: subset-b-006527

Grouped research report for the MT8192 MediaTek ASoC platform files under `sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192`. Each section preserves the exact source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/Makefile

## Purpose
This Makefile wires the MT8192 ALSA SoC audio platform objects into the kernel build. It defines the multi-object platform driver `snd-soc-mt8192-afe-y`, which combines the AFE platform, clock, GPIO, ADDA, common control, I2S, PCM, and TDM DAI implementation objects into `snd-soc-mt8192-afe.o`. It also conditionally builds the machine driver `mt8192-mt6359-rt1015-rt5682.o`.

## Important build targets
`snd-soc-mt8192-afe-y` includes `mt8192-afe-pcm.o`, `mt8192-afe-clk.o`, `mt8192-afe-gpio.o`, `mt8192-dai-adda.o`, `mt8192-afe-control.o`, `mt8192-dai-i2s.o`, `mt8192-dai-pcm.o`, and `mt8192-dai-tdm.o`. `obj-$(CONFIG_SND_SOC_MT8192)` selects the platform driver. `obj-$(CONFIG_SND_SOC_MT8192_MT6359_RT1015_RT5682)` selects a board-level machine driver that consumes these CPU DAIs.

## Control flow and integration
The file has no runtime control flow, but it defines the link-time composition of the platform. The order makes the platform PCM object the central module, while all DAI and helper objects provide symbols used by `mt8192-afe-pcm.c`. The machine-driver object is separate because it binds this AFE to board codecs and routes.

## State, dependencies, and risks
There is no persistent state. Dependencies are Kconfig symbols and object names matching the actual source files. A stale object list would produce unresolved symbols or omit a DAI family from the combined component. Test signals are kernel build coverage for `CONFIG_SND_SOC_MT8192=y/m` and the machine config, plus module load probing of `mediatek,mt8192-audio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-clk.c

## Purpose
This file owns MT8192 AFE clock discovery, parent selection, top-level AFE clock enable/disable, APLL tuner control, and per-I2S/TDM master-clock divider programming. It is the main bridge between the ASoC driver and Linux CCF/syscon clock resources.

## Important APIs and data
`aud_clks[CLK_NUM]` maps the enum values from `mt8192-afe-clk.h` to device-tree clock names. Public functions include `mt8192_init_clock()`, `mt8192_afe_enable_clock()`, `mt8192_afe_disable_clock()`, `mt8192_apll1_enable()`, `mt8192_apll1_disable()`, `mt8192_apll2_enable()`, `mt8192_apll2_disable()`, `mt8192_get_apll_rate()`, `mt8192_get_apll_by_rate()`, `mt8192_get_apll_by_name()`, `mt8192_mck_enable()`, `mt8192_mck_disable()`, and `mt8192_set_audio_int_bus_parent()`. `struct mt8192_mck_div` and `mck_div[]` describe the clock mux and divider clock for each MCLK/BCLK id.

## Control flow
Probe calls `mt8192_init_clock()`, which devm-allocates `afe_priv->clk`, obtains every named clock with `devm_clk_get()`, and obtains `apmixedsys`, `topckgen`, and `infracfg` regmaps from phandles. Runtime resume calls `mt8192_afe_enable_clock()`: it enables infra audio clocks, enables and parents `top_mux_audio` and `top_mux_audio_int` to 26 MHz, parents `top_mux_audio_h` to APLL2, then enables `aud_afe_clk`. Runtime suspend calls `mt8192_afe_disable_clock()` in reverse.

APLL enable functions first select the APLL mux tree (`apll1_mux_setting()` or `apll2_mux_setting()`), enable the 22M/24M and tuner gates, write tuner configuration registers, and enable the high-definition engine bit in `AFE_HD_ENGEN_ENABLE`. Disable clears the engine and tuner bits, disables the tuner and APLL gate, and returns mux parents to `top_clk26m`.

MCLK enable chooses APLL1 for non-8-kHz-family rates and APLL2 for 8-kHz-family rates, enables the per-I2S mux when present, parents it to the APLL mux, enables the divider clock, and sets its rate. Disable turns off divider and mux clocks.

## State and persistence
State lives in `struct mt8192_afe_private`: `clk`, `topckgen`, `apmixedsys`, `infracfg`, and caller-owned MCLK rate fields. Hardware state is the set of CCF enable counts, mux parent relationships, AFE tuner registers, and top clock divider rates. Regmap cache does not cover CCF state, so runtime PM must restore clocks before regcache sync.

## Dependencies and integration
This file depends on CCF (`linux/clk.h`), syscon/regmap, AFE register definitions, and the private structure in `mt8192-afe-common.h`. It is called by `mt8192-afe-pcm.c` runtime PM and by DAI files when DAPM supplies need APLL, MCLK, or BCLK. Device tree must provide all named clocks and the `mediatek,apmixedsys`, `mediatek,topckgen`, and `mediatek,infracfg` phandles.

## Risks and test signals
Most enable paths do not unwind previously enabled clocks after a later failure, so probe/runtime-PM error testing should watch for leaked enable counts. `mt8192_init_clock()` records missing clocks as NULL after warnings, but later code dereferences `afe_priv->clk[id]`; incomplete DT clock tables can become runtime crashes. Functional tests should cover runtime suspend/resume, APLL1 and APLL2 sample-rate families, `set_sysclk()` divisibility failures, and DAPM paths that enable TDM/I2S MCLKs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-clk.h

## Purpose
This header defines MT8192 clock register offsets, bit fields, clock ids, APLL ids, MCLK ids, and public clock-control prototypes used by the AFE platform and DAI implementations.

## Important definitions
Register constants cover APLL/tuner registers, `CLK_CFG_*`, `CLK_AUDDIV_*`, top audio monitor/config registers, and infra status registers. Bit macros describe divider power-down bits, divider value fields, and per-I2S APLL select bits. `APLL1_W_NAME` and `APLL2_W_NAME` provide DAPM supply names shared by I2S/TDM route predicates. The clock enum starts at `CLK_AFE` and ends at `CLK_NUM`, matching `aud_clks[]` in `mt8192-afe-clk.c`.

## APIs and integration
The header exposes the top-level runtime PM clock operations, APLL enable/disable helpers, APLL selection helpers, MCLK enable/disable helpers, and `mt8192_set_audio_int_bus_parent()`. DAI code uses these APIs from DAPM event handlers and `set_sysclk()` flows.

## State and dependencies
The header forward-declares `struct mtk_base_afe` and avoids including the full base AFE header. State is implicit in the enum ordering: the C file, private `clk` array, and DAI MCLK ids all depend on these values staying stable.

## Risks and test signals
Bitfield definitions must match the SoC clock controller binding and register manual. The `CLK_AUDDIV_4` mask-shift macros for div8/div9 use shift zero in this source, which is suspicious and should be checked against hardware documentation if legacy direct regmap divider programming is restored. Build tests catch enum/prototype mismatches; hardware tests catch wrong parent, divider, or APLL selection through bad sample clock output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-common.h

## Purpose
This is the shared MT8192 AFE contract. It declares all memory interfaces, backend DAI ids, IRQ ids, MTKAIF protocol modes, MCLK ids, the platform-private state structure, and cross-file registration/helper prototypes.

## Important types and fields
The first enum defines FE memifs (`DL1` through `HDMI`) followed by backend DAIs (`ADDA`, I2S ports, HW gain, SRC, PCM, TDM) and `MT8192_DAI_NUM`. The IRQ enum defines IRQ slots 0-26 plus IRQ31 for TDM/HDMI. `struct mt8192_afe_private` holds clock pointers, syscon regmaps, sidetone gain, a runtime-PM bypass flag, `dai_on[]`, per-DAI private pointers, MTKAIF calibration/protocol state, DMIC/ADDA6 options, and cached MCK rates.

## APIs and integration
Registration prototypes let `mt8192-afe-pcm.c` assemble all sub-DAIs into one ASoC component. Rate conversion helpers are used by FE, IRQ, PCM, I2S, and ADDA paths. `mt8192_dai_set_priv()` centralizes devm allocation for per-DAI private structures. `mt8192_dai_i2s_set_share()` is exported for machine drivers that need two I2S DAIs to share a clock.

## Control flow and state
The private structure is allocated during platform probe and then populated by clock init and DAI registration. Runtime state persists across active streams and runtime-PM cycles but is devm-owned and freed on device removal. The `pm_runtime_bypass_reg_ctl` flag is used during probe regcache initialization to enable clocks without programming AFE registers through the normal suspend/resume sequence.

## Dependencies and risks
This header depends on Linux list/regmap headers, ASoC types, the MediaTek base AFE helpers, and `mt8192-reg.h`. The enum values are ABI-like within the driver: memif arrays, IRQ maps, DAPM routes, and DAI ids index on them directly. Reordering without updating all tables would silently misroute audio, wrong-clock DAIs, or period interrupts. Test signals include successful probe, complete DAI registration count, correct ALSA PCM list, and route activation for each major DAI family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-control.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-control.c

## Purpose
This file provides shared software-to-hardware rate encoding helpers and a generic per-DAI private-data allocator.

## Important functions
`mt8192_general_rate_transform()` maps rates from 8 kHz through 384 kHz to the general AFE register encoding. `dai_memif_rate_transform()` maps DAI/Modem DAI memif rates to their four-value encoding. `pcm_rate_transform()` maps PCM interface rates. `mt8192_rate_transform()` chooses the specialized mapping for DAI/Modem DAI and PCM1/PCM2, otherwise falls back to the general mapping. `mt8192_dai_set_priv()` devm-allocates a private blob, optionally copies default data into it, and stores it in `afe_priv->dai_priv[id]`.

## Control flow
Callers in FE and DAI hw_params paths pass the requested sample rate and target aud block id. Invalid rates do not fail; the helpers warn and return a default encoding: 48 kHz for general, 16 kHz for DAI memif, and 32 kHz for PCM. DAI registration calls `mt8192_dai_set_priv()` to install per-port state such as I2S or TDM private structures.

## State and dependencies
The rate helpers are stateless except for warning through `dev_warn()`. `mt8192_dai_set_priv()` mutates `struct mt8192_afe_private` and relies on devm memory lifetime tied to `afe->dev`. It uses enum ids from `mt8192-afe-common.h`.

## Risks and test signals
Defaulting invalid rates can keep streams running with wrong hardware configuration, so tests should verify that ALSA constraints prevent unsupported rates before hw_params where possible. `mt8192_dai_set_priv()` has no bounds check on `id`; callers must pass valid `MT8192_DAI_NUM` indexes. Unit-style review should check every caller id and hardware tests should validate register encodings for 44.1-kHz and 48-kHz families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.c

## Purpose
This file manages audio pinctrl state selection for ADDA, I2S, TDM, VOW, and clock pins. DAI DAPM events call it to switch pins on when a hardware path powers up and off when it powers down.

## Important data and APIs
`enum mt8192_afe_gpio` enumerates on/off pin states for ADDA data, CH34 data, I2S0/1/2/3/5/6/7/8/9, VOW data/clock, MOSI clock, and TDM. `aud_gpios[]` maps each enum to a pinctrl state name and cached `pinctrl_state`. `mt8192_afe_gpio_init()` obtains the global pinctrl, resolves all states, enables `aud_clk_mosi_on`, and initializes ADDA pins off. `mt8192_afe_gpio_request()` is the exported selector used by DAI code.

## Control flow
Initialization calls `devm_pinctrl_get()` and attempts `pinctrl_lookup_state()` for every known state. Missing states are logged at debug level and left unprepared. `mt8192_afe_gpio_select()` validates the enum, checks that the state was prepared, and calls `pinctrl_select_state()`. Runtime callers enter `mt8192_afe_gpio_request()`, take `gpio_request_mutex`, switch on the DAI id, select the appropriate on/off state, and release the mutex. ADDA and ADDA_CH34 split playback/uplink through helper functions; VOW toggles both clock and data states.

## State and persistence
The file uses a global `aud_pinctrl`, static `aud_gpios[]` state cache, and a static mutex. State persists for the module lifetime rather than per-device, which is acceptable for a single SoC audio device but risky if multiple instances were ever probed.

## Dependencies and integration
It depends on Linux pinctrl consumer APIs and DAI ids from `mt8192-afe-common.h`. ADDA, I2S, and TDM DAPM event handlers call `mt8192_afe_gpio_request()` during `PRE_PMU`/`POST_PMD`.

## Risks and test signals
`mt8192_afe_gpio_request()` returns success even if an inner selection fails for most cases, because it ignores helper return values. Missing pinctrl states can therefore result in silent audio pin misconfiguration. Test signals include DT pinctrl state coverage, debug logs for lookup failures, oscilloscope/loopback verification of I2S/TDM/ADDA pins, and DAPM route activation/deactivation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.h

## Purpose
This header exposes the MT8192 AFE GPIO/pinctrl interface to DAI implementation files.

## APIs
`mt8192_afe_gpio_init(struct device *dev)` initializes pinctrl and caches available audio pin states. `mt8192_afe_gpio_request(struct device *dev, bool enable, int dai, int uplink)` toggles the pinctrl state for a backend DAI, with `uplink` selecting capture versus playback for ADDA-style DAIs.

## Integration and dependencies
The header forward-declares `struct device`; users include it alongside `mt8192-afe-common.h` for DAI ids. It is consumed by ADDA, I2S, TDM, and platform probe code.

## State, risks, and tests
The state is implemented in `mt8192-afe-gpio.c` as module-static pinctrl caches. The API relies on integer DAI ids rather than a typed enum in the prototype, so invalid ids are only caught at runtime. Tests should cover probe-time pinctrl initialization and every DAI id path that calls `mt8192_afe_gpio_request()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-pcm.c

## Purpose
This is the MT8192 AFE platform driver. It registers the ALSA component, FE memory-interface DAIs, DAPM routes for memif capture/playback, memif hardware metadata, IRQ metadata, regmap caching policy, runtime PM, and platform probe/remove.

## Important data and APIs
`mt8192_afe_hardware` defines PCM hardware constraints. `mt8192_memif_dai_driver[]` declares FE DAIs: DL1/DL12/DL2-DL9 playback, UL1-UL8 capture, mono DAI captures, and HDMI playback. `memif_data[]` maps each memif id to base/current/end address registers, sample-rate bit fields, mono/quad/HD/alignment bits, enable bits, and pbuf/minlen fields. `irq_data[]` maps AFE IRQ ids to counter, fs, enable, and clear registers. `memif_irq_usage[]` assigns fixed IRQs to memifs.

## Control flow
Probe sets a 34-bit DMA mask, allocates `struct mtk_base_afe` and `struct mt8192_afe_private`, initializes reserved memory or enables preallocated buffers, initializes clocks, resets audiosys, enables runtime PM, attaches the parent syscon regmap, warms and reinitializes the regcache with clocks temporarily enabled, allocates memif and IRQ arrays, requests the platform IRQ, registers all sub-DAI families via `dai_register_cbs[]`, combines sub-DAIs with `mtk_afe_combine_sub_dai()`, fills base AFE callbacks, and registers the ASoC component with `mtk_afe_pcm_platform`.

During runtime resume, `mt8192_afe_enable_clock()` runs first. If register control is not bypassed, regcache is restored, infra/audio DCM is enabled, CPU HD alignment is configured, output connections are forced to 24-bit, and AFE is enabled in `AFE_DAC_CON0`. Runtime suspend disables AFE, polls for `AFE_ON_RETM` to drop, clears IRQ status twice, resets sinegen, marks regcache cache-only/dirty, then disables clocks.

The IRQ handler reads `AFE_IRQ_MCU_EN` and `AFE_IRQ_MCU_STATUS`, masks to MCU-enabled status bits, calls `snd_pcm_period_elapsed()` for active memifs whose assigned IRQ bit is set, and clears handled status in `AFE_IRQ_MCU_CLR`.

## DAPM and routing
The file contains large mixer and route tables for UL memifs and tiny-connection muxes. These tables route ADDA, I2S, PCM, CONNSYS I2S, SRC, and DL paths into capture memifs. `ul_tinyconn_event()` toggles `AFE_MEMIF_CONN` tiny-connection usage bits around UL tinyconn mux power.

## State and persistence
Persistent driver state includes devm-owned `afe`, `afe_priv`, memif array, IRQ array, and combined DAI tables. Hardware register state is cached with flat regcache while suspended; volatile registers are excluded by `mt8192_is_volatile_reg()`. `pm_runtime_bypass_reg_ctl` protects probe-time regcache initialization from normal AFE register programming.

## Dependencies and integration
This file depends on MediaTek common FE/AFE helpers, Linux reset/PM/DMA/reserved memory APIs, the clock/GPIO/control/DAI registration files, and `mt8192-reg.h`. It is the integration point for all other files in this subset.

## Risks and test signals
Key risks are regcache correctness, volatile-register coverage, fixed memif-to-IRQ mapping mistakes, runtime-PM ordering, and DT resource completeness. Remove calls `pm_runtime_disable()` and may also manually suspend/disable clocks, so clock balance should be tested. Test signals include successful probe, ALSA card and PCM enumeration, period interrupts for each memif, suspend/resume with active and inactive streams, HDMI/TDM IRQ31, and route-specific capture/playback loopback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-adda.c

## Purpose
This file implements the ADDA, ADDA_CH34, AP_DMIC, and AP_DMIC_CH34 backend DAIs, including DAPM mixers/routes, MTKAIF setup, analog/digital mic switching, playback/capture register programming, sidetone filter controls, and ADDA-related ALSA controls.

## Important APIs and data
`mt8192_dai_adda_register()` adds ADDA DAI drivers, controls, widgets, and routes to the base AFE. The DAI ops use `mtk_dai_adda_hw_params()`. DAPM event handlers include `mtk_adda_ul_event()`, `mtk_adda_ch34_ul_event()`, `mtk_adda_dl_event()`, `mtk_adda_ch34_dl_event()`, `mtk_adda_pad_top_event()`, `mtk_adda_mtkaif_cfg_event()`, and `mtk_stf_event()`. Controls include sidetone gain, ADDA downlink gain, MTKAIF DMIC switch, and ADDA6-only switch.

## Control flow
Playback hw_params builds downlink SRC settings from the sample rate, configures upsampling, unmute, optional voice mode, gain, predistortion reset, sigma-delta modulator gain/order, and SDM auto reset. ADDA and CH34 select different register banks. Capture hw_params maps the uplink rate, enables IIR, writes fixed 35-Hz high-pass coefficients, selects internal ADC/AMIC mode by default, and calls `mtk_adda_ul_src_dmic()` for AP_DMIC variants.

DAPM power events select ADDA GPIOs on `PRE_PMU` and switch them off after a 125-us delay on `POST_PMD`. Capture events also program MTKAIF RX data mode for DMIC. `mtk_adda_mtkaif_cfg_event()` configures MTKAIF protocol 1 or 2, handles protocol-2 phase calibration data, applies RX clock inversion, and programs inter-channel delay cycles for ADDA and ADDA6. ADDA6-only mode sets a sync-word disable bit while CH34 capture is active.

The sidetone DAPM event reads the current UL voice mode, selects a 16/32/48-kHz coefficient table, clears gains, un-bypasses the filter, writes half-tap count, iterates coefficient writes while polling the write-ready bit, and bypasses/zeros gains again on power-down.

## State and persistence
Mutable state is stored in `afe_priv`: `mtkaif_protocol`, phase calibration arrays, DMIC switches, ADDA6-only flag, and sidetone positive gain. Controls update this state and DAPM events consume it. Register programming is restored through regcache unless marked volatile by the platform file.

## Dependencies and integration
The file depends on `mt8192-afe-clk.h`, `mt8192-afe-gpio.h`, `mt8192-interconnection.h`, common ADDA transform helpers from `../common/mtk-dai-adda-common.h`, and ASoC DAPM/control APIs. Routes connect DL memifs, gains, PCM captures, SRC outputs, AP DMIC inputs, and sidetone output to ADDA endpoints.

## Risks and test signals
Phase calibration data is trusted when protocol 2 clock phase mode is selected; missing calibration only warns and leaves configuration partially skipped. Control-set values are minimally validated. GPIO request return values are ignored by event handlers. A route entry for ADDA DL CH4 maps `DL6_CH2` text to `I_DL6_CH1`, which should be checked. Test signals include AMIC and DMIC capture for both channel pairs, ADDA6-only capture, protocol-1/protocol-2 MTKAIF boards, sidetone enable at 16/32/48 kHz, and playback gain/SDM behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-i2s.c

## Purpose
This file implements MT8192 CONNSYS I2S plus I2S0/1/2/3/5/6/7/8/9 backend DAIs. It owns I2S DAI definitions, low-jitter controls, DAPM widgets/routes, per-I2S private state, sysclk handling, shared-clock relationships, normal I2S register programming, and CONNSYS ASRC-trigger flow.

## Important types and APIs
`struct mtk_afe_i2s_priv` stores DAI id, last rate, low-jitter enable, shared I2S id, MCLK id, MCLK rate, and selected APLL. `mt8192_dai_i2s_register()` registers all I2S DAIs, controls, widgets, routes, and private data. `mt8192_dai_i2s_set_share()` is exported so machine drivers can configure a secondary I2S to share the main port clock. DAI ops include `mtk_dai_i2s_hw_params()`, `mtk_dai_i2s_set_sysclk()`, and CONNSYS-specific hw_params/trigger.

## Control flow
Low-jitter ALSA enum controls update `i2s_priv->low_jitter_en`. DAPM route predicates inspect private state to connect the active I2S endpoint to the matching APLL supply, MCLK supply, HD supply, and shared I2S enable supply. Normal I2S hw_params calls `mtk_dai_i2s_config()`, which translates rate/format, writes the appropriate `AFE_I2S_CON*` register for the DAI id, stores the rate, and recursively configures a shared I2S parent if configured.

`mtk_dai_i2s_set_sysclk()` only accepts `SND_SOC_CLOCK_OUT`, verifies the requested MCLK can be generated exactly by the selected APLL, stores the MCLK rate/APLL, and propagates those values to a shared I2S target. CONNSYS I2S hw_params programs proxy I2S mode, ASRC mode, and calibration constants. CONNSYS trigger start/resume enables I2S, calibrator, and ASRC and marks `dai_on`; stop/suspend disables ASRC/calibrator/I2S, bypasses ASRC, and clears `dai_on`.

## DAPM and routing
The route tables expose playback I2S outputs, capture I2S inputs, dummy widgets for codec-less activation, loopback muxes, tinyconn muxes, and dense interconnect mixers from DL/ADDA/PCM/SRC sources. DAPM supplies also call GPIO and MCLK helpers through event handlers in the omitted route/widget tables.

## State and persistence
Each I2S private block is devm-allocated by `mt8192_dai_set_priv()` from `mt8192_i2s_priv[]` defaults. Runtime state includes rate, low-jitter flag, shared id, MCLK rate, and APLL selection. Hardware state includes I2S format/rate registers, ASRC registers, MCLK dividers, GPIO state, and DAPM-powered clocks.

## Dependencies and integration
The file depends on AFE clock helpers for APLL/MCLK, GPIO helpers for pinctrl, `mt8192_rate_transform()`, interconnection port defines, and ASoC DAPM route predicates. Machine drivers can call the exported sharing API after DAI private state exists.

## Risks and test signals
`set_sysclk()` uses `share_i2s_id > 0`, so sharing to I2S0 id zero will not propagate MCLK state even though `>= 0` is used elsewhere. Recursive shared configuration could loop if configured cyclically by a caller. CONNSYS ASRC constants are hard-coded. Tests should cover every I2S port, low-jitter on/off, MCLK exact divisibility for 44.1/48-kHz families, shared I2S pairs including I2S0, CONNSYS start/stop, dummy routes, loopback, and suspend/resume while `dai_on` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-pcm.c

## Purpose
This file implements the two modem PCM backend DAIs (`PCM 1` and `PCM 2`) and their DAPM routing to/from DL, ADDA, I2S, and modem endpoints.

## Important data and APIs
The file defines PCM-specific enum values for left-channel repeat, VBT 16-kHz mode, modem source, sync type, Bluetooth mic mode, AFIFO/ASRC selection, clock master/slave, word length, PCM mode, format, BCLK inversion, and enable state. `mtk_dai_pcm_driver[]` exposes two full-duplex DAIs with 8/16/32/48-kHz rates and 16/24/32-bit formats. `mt8192_dai_pcm_register()` registers the DAI drivers, widgets, and routes.

## Control flow
DAPM widgets include mixers for PCM playback channels and supplies backed by `PCM_INTF_CON1` and `PCM2_INTF_CON`. `mtk_pcm_en_event()` currently logs power events only. `mtk_dai_pcm_hw_params()` translates the requested rate using `mt8192_rate_transform()`, skips reprogramming if either playback or capture widget is already active, then writes PCM interface configuration. PCM1 is configured as slave, PCM mode B, one-BCLK sync, AFIFO, dual-mic TX, no BCLK inversion. PCM2 uses PCM mode B, 32-BCLK word length, AFIFO, and rate encoding in `PCM2_INTF_CON`.

## State and persistence
The file stores no private per-DAI state. State lives in AFE hardware registers and ASoC DAPM widget active counts. The active-count early return preserves current register settings for symmetric full-duplex use.

## Dependencies and integration
It depends on `mt8192-afe-common.h`, `mt8192-interconnection.h`, regmap, and ASoC DAI/DAPM helpers. Routes connect PCM playback to modem outputs (`AFE_TO_MD1`, `AFE_TO_MD2`) and PCM capture from modem inputs, with additional interconnect mixers from DL, ADDA, and I2S sources.

## Risks and test signals
The active-widget shortcut can retain stale parameters if a second stream attempts incompatible settings despite symmetric constraints. The event handler does not manage GPIO or clocks directly, so correctness relies on DAPM register supplies and parent AFE clocks. Tests should cover PCM1/PCM2 playback and capture, full-duplex same-rate operation, unsupported rates being rejected before hw_params, modem loopback paths, and suspend/resume with PCM routes active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-tdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-tdm.c

## Purpose
This file implements the MT8192 TDM/HDMI playback backend DAI, including HDMI channel mux controls, TDM format/rate/channel programming, MCLK/BCLK DAPM supplies, GPIO selection, and private TDM clock state.

## Important types and APIs
`struct mtk_afe_tdm_priv` stores DAI id, BCK id/rate, output mode, BCK/LRCK inversion, MCLK id/multiple/rate, and selected APLL. Helper functions map PCM format to TDM word length, channel BCK width, LRCK width, channel count encoding, and channels per serial data line. `mt8192_dai_tdm_register()` installs the single `TDM` playback DAI plus widgets/routes and private state.

## Control flow
DAPM supplies run in sequence: APLL, TDM MCK, TDM BCK, and TDM enable. `mtk_tdm_mck_en_event()` enables/disables the MCLK divider using `mt8192_mck_enable()` and clears `mclk_rate` on power-down. `mtk_tdm_bck_en_event()` enables/disables the BCK divider. `mtk_tdm_en_event()` toggles TDM GPIO state. Route predicates connect `TDM_MCK` only to the APLL matching `tdm_priv->mclk_apll`.

`mtk_dai_tdm_set_sysclk()` validates output-clock direction and calls `mtk_dai_tdm_cal_mclk()`, which selects an APLL by rate family and requires exact divisibility. `mtk_dai_tdm_set_fmt()` stores I2S/DSP_A/DSP_B mode and BCLK/LRCK inversion. `mtk_dai_tdm_hw_params()` derives MCLK if not explicit (`rate * 512`), computes BCK, warns if BCK cannot be generated from MCLK, writes `AFE_TDM_CON1` for mode/width/channel settings, writes `AFE_TDM_CON2` to map channel pairs to serial outputs, and writes HDMI channel count.

## State and persistence
The TDM private state is devm-owned and stored in `afe_priv->dai_priv[MT8192_DAI_TDM]`. Hardware state is split between AFE TDM registers, HDMI connection registers, top clock dividers, and pinctrl state. `mclk_rate` is reset to zero when MCLK powers down, causing the next hw_params to recompute default MCLK unless userspace/machine driver calls `set_sysclk()` again.

## Dependencies and integration
The file depends on clock helpers, GPIO helpers, AFE register definitions, and DAPM supplies named `APLL1`/`APLL2`. It also routes HDMI mux widgets into the FE HDMI memif declared in `mt8192-afe-pcm.c`.

## Risks and test signals
The code only warns when BCK is not divisible from MCLK; it does not fail hw_params, so invalid clocks may continue. `get_tdm_id_by_name()` always returns the single TDM id, which is fine now but would not scale to multiple TDM instances. Tests should cover I2S/DSP_A/DSP_B formats, inversion modes, 2/4/6/8-channel HDMI playback, explicit and default MCLK, APLL1/APLL2 families, and DAPM power-down/up sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-tdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-interconnection.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-interconnection.h

## Purpose
This header defines numeric AFE interconnection input-port ids used by DAPM mixer controls throughout the MT8192 audio driver.

## Important definitions
The first group defines direct input port ids below 32 for I2S0, ADDA uplink, DL1/DL2/DL12/DL3, PCM capture, gain outputs, ADDA CH34, and I2S2 channels. The second group defines ids from hardware values >= 32 by subtracting `I_32_OFFSET`, including CONNSYS I2S, SRC outputs, DL4-DL9, I2S6, and I2S8.

## Integration
ADDA, I2S, PCM, and memif DAPM mixer controls use these macros as shift positions in `SOC_DAPM_SINGLE_AUTODISABLE()` against `AFE_CONN*` or `AFE_CONN*_1` registers. The split at 32 matches the hardware register-bank split in connection registers.

## State, dependencies, and risks
This header has no runtime state. It depends on callers selecting the correct `AFE_CONN` register bank for each macro. A mismatch between label, port macro, and register bank silently creates wrong audio routes. Test signals are route-level loopback or board audio tests that activate every DAPM mixer source, especially the >=32 ports that require `_1` registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-interconnection.h -->
