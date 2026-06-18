# Research Report: subset-b-006538

This grouped report covers Rockchip SAI/SPDIF controller support and Samsung ASoC controller and board-machine support under `sources/distributed-fs/ceph-client/sound/soc`. Each file section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.c

## Purpose
Implements the Rockchip SAI ASoC CPU DAI driver for `rockchip,rk3576-sai`. It exposes playback and/or capture DAIs depending on DT `dma-names`, configures I2S/left/right-justified/DSP/TDM framing, drives DMA through `snd_dmaengine`, handles runtime PM and regmap caching, and reports FIFO/frame-sync failures through IRQs.

## Important APIs, Types, And Functions
- `struct rk_sai_dev` is the full device state: clocks, reset controls, regmap, DMA descriptors, active PCM substreams, lane routing arrays, version, TDM/frame-pulse mode, master/slave state, and `xfer_lock`.
- DAI operations are collected in `rockchip_sai_dai_ops`: `.startup`, `.shutdown`, `.hw_params`, `.set_fmt`, `.set_sysclk`, `.prepare`, `.trigger`, and `.set_tdm_slot`.
- `rockchip_sai_set_fmt()` translates `SND_SOC_DAIFMT_*` master/slave, inversion, and data format flags into `SAI_CKR`, `SAI_TXCR`, `SAI_RXCR`, shift, and frame-sync programming.
- `rockchip_sai_hw_params()` chooses lanes, word width, slot width, frame width, DMA burst, and master-mode BCLK divider from PCM parameters.
- `rockchip_sai_start()`, `rockchip_sai_stop()`, `rockchip_sai_xfer_start()`, `rockchip_sai_xfer_stop()`, and `rockchip_sai_clear()` drive transfer lifecycle and FIFO clear/reset recovery.
- `rockchip_sai_parse_paths()` reads optional `rockchip,sai-tx-route` and `rockchip,sai-rx-route` DT properties and maps logical paths to SDO/SDI lanes.
- `rockchip_sai_isr()` handles TX underrun, RX overrun, frame-sync error, and frame-sync lost interrupts, stopping affected PCM substreams on xruns.
- `rockchip_sai_probe()` owns allocation, reset lookup, MMIO/regmap setup, IRQ, clocks, version read, DAI construction, route parsing, runtime PM setup, DMA PCM registration, and component registration.

## Control Flow
Probe builds a per-device DAI based on available `tx`/`rx` DMA names, initializes default FIFO thresholds, parses optional lane routes, enables runtime PM, registers a dmaengine PCM, and registers the ASoC component. At stream startup, only one substream per direction is accepted and optional mixer-configured PCM wait time is copied into the substream. `set_fmt` stops or clears the hardware before changing clock provider/polarity/format fields. `hw_params` programs stream-specific lane count, sample width, slot count, frame width, DMA burst, and, in master mode, validates that `mclk_rate` can exactly derive the requested BCLK. `prepare` enables master clocks and frame-sync detection. Trigger start enables DMA and stream bits; trigger stop disables DMA, waits for stream idle, and clears FIFO logic. Runtime suspend disables frame-sync detection, stops/gates transfer clocks, switches regmap to cache-only, delays for BCLK leakage avoidance, then disables `mclk` and `hclk`; resume re-enables clocks and syncs cached registers.

## State And Persistence
Runtime state is in `rk_sai_dev` and hardware registers cached by regmap. `mclk_rate` is set by `.set_sysclk`; `wait_time[]` is user-visible ALSA control state and is applied to future substreams. `substreams[]` tracks active ALSA streams so the IRQ path can call `snd_pcm_stop_xrun()`. `initialized`, `is_master_mode`, `is_tdm`, `fpw`, and route/lane arrays persist for the device lifetime. There is no disk persistence.

## Dependencies And Integration Points
Depends on Linux ASoC, dmaengine PCM, regmap, runtime PM, reset controls, clocks, device tree, IRQ handling, and `rockchip_sai.h`. Integrates with machine drivers through standard CPU DAI callbacks, `SND_SOC_DAIFMT_*`, TDM slot APIs, `set_sysclk`, DMA channel names `tx`/`rx`, and optional DT lane route properties. Register accessibility, volatility, and precious RX data semantics are declared through `rockchip_sai_regmap_config`.

## Risks And Edge Cases
- Master-mode BCLK generation is strict: `mclk_rate` must match an integer divider within `CLK_SHIFT_RATE_HZ_MAX`, so machine drivers must call `.set_sysclk` correctly.
- `set_fmt` and TDM changes intentionally stop clocks and streams; misuse while active can cause audible glitches despite locking.
- `rockchip_sai_clear()` falls back to full reset and regcache sync on timeout, which can recover hardware but may hide timing bugs.
- Frame-sync lost detection in slave mode assumes CRU SCLK equals external SCLK; the comment flags this as a hardware/clocking caveat.
- Lane routing validates only array length and lane index, so invalid board-level topology may still pass software checks.
- IRQ is optional; without it xrun/frame-sync diagnostics and automatic substream stop are absent.

## Test Signals
Useful validation includes probe with DT variants containing tx-only, rx-only, and full duplex DMA names; ALSA playback/capture across supported formats and rates; TDM slot enable/disable; lane route DT property tests; suspend/resume and runtime autosuspend; induced TX underrun/RX overrun IRQ handling; and checking regmap cache sync after reset and PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.h -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.h

## Purpose
Defines the Rockchip SAI register map, bit fields, helper macros, version constants, path-selection encodings, FIFO/status fields, and frame-sync timeout controls used by `rockchip_sai.c`.

## Important APIs, Types, And Functions
This header exposes macros rather than functions. Important groups include `SAI_XCR_*` for TX/RX control fields, `SAI_FSCR_*` for frame sync width and pulse width, `SAI_XFER_*` for clock/frame/stream start and idle bits, `SAI_CKR_*` for master/slave and clock polarity, `SAI_DMACR_*` for DMA enable/thresholds, `SAI_INTCR_*`/`SAI_INTSR_*` for interrupt control/status, `SAI_RX_PATH()` and `SAI_TX_PATH()` for lane routing, version constants `SAI_VER_2307` through `SAI_VER_2403`, and register offsets through `SAI_LOOPBACK_LR`.

## Control Flow
There is no runtime control flow. The macros encode register programming contracts consumed by the driver when translating ASoC formats, PCM parameters, runtime PM, path routing, IRQ handling, and mixer controls into hardware writes.

## State And Persistence
No state is stored in the header. The macros describe hardware state persisted in MMIO registers and cached by the driver's regmap.

## Dependencies And Integration Points
Requires kernel bit helpers such as `BIT()` and `GENMASK()` from including source context. It is tightly coupled to `rockchip_sai.c` and the RK3576 SAI register layout. Version comments document feature gates such as FSXN, FSE, FSLOST, forced clear, chained SAI, TX auto gate, and loopback LR selection.

## Risks And Edge Cases
- Several macros subtract one from user values; callers must avoid zero for fields like slot width or frame width unless explicitly allowed.
- `SAI_CLR_FCR` has a `TODO` comment, so forced-clear semantics are not fully documented in the code.
- Register bit meanings change around `SAI_VER_2307` and `SAI_VER_2311`; driver code must keep version checks aligned with this header.
- Path macros assume lane indexes in range and do not validate values.

## Test Signals
Compile coverage is the main signal. Runtime tests should confirm that macro-derived register values match hardware documentation for I2S, DSP, TDM, lane route, and interrupt scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.c

## Purpose
Implements the Rockchip S/PDIF playback-only ASoC DAI driver for multiple Rockchip SoCs. It configures IEC958 channel status, S/PDIF data width/alignment, DMA playback, clocks, runtime PM, and RK3288 GRF routing.

## Important APIs, Types, And Functions
- `enum rk_spdif_type` distinguishes compatible-specific behavior.
- `struct rk_spdif_dev` stores device, `mclk`, `hclk`, playback DMA data, and regmap.
- `rk_spdif_hw_params()` builds consumer IEC958 status bytes with `snd_pcm_create_iec958_consumer_hw_params()`, writes channel-status registers, chooses BMC divider and word format, and clears MCLK-domain logic before applying format changes.
- `rk_spdif_trigger()` enables/disables DMA and starts/stops `SPDIF_XFER`.
- `rk_spdif_set_sysclk()` sets `mclk` rate when machine drivers provide one.
- `rk_spdif_probe()` handles RK3288 GRF selection, clocks, MMIO regmap, DMA data, PM setup, dmaengine PCM registration, and component/DAI registration.

## Control Flow
On probe, compatible data is read; RK3288 writes GRF `RK3288_GRF_SOC_CON2` to select the working 8-channel S/PDIF solution. The driver maps registers, creates a flat regmap, sets the playback DMA FIFO address, enables runtime PM, and registers a two-channel playback DAI. During `hw_params`, it writes channel-status frames, enables channel-status embedding, computes 128fs BMC divider from current `mclk`, programs sample format and justification, and pulses `SPDIF_CFGR_CLR`. Trigger start enables transmit DMA and transfer start; trigger stop disables both. Runtime suspend/resume gates clocks and toggles regmap cache-only mode.

## State And Persistence
The driver holds only device-local pointers and DMA configuration. Register state is cached by regmap across runtime suspend. There is no persistent software configuration aside from clock rate set through `.set_sysclk`.

## Dependencies And Integration Points
Uses ASoC DAI callbacks, `snd_dmaengine_pcm`, IEC958 PCM helpers, regmap, runtime PM, clocks, syscon GRF, and `rockchip_spdif.h`. Integrates with DT compatible strings from RK3066 through RK3568 and with DMA through the S/PDIF sample data register.

## Risks And Edge Cases
- `rk_spdif_hw_params()` assumes current `mclk` can derive 128fs and does not validate divider accuracy beyond `DIV_ROUND_CLOSEST`.
- Only playback is supported; capture requests are impossible at DAI capability level.
- RK3288 depends on the `rockchip,grf` phandle.
- The header macro typo `SDPIF_CFGR_VDW_MASK` is consistently used but easy to misread.
- Runtime suspend can drop register writes if callers fail to hold PM references.

## Test Signals
Playback tests for 16/20/24/32-bit formats and 8-192 kHz rates, IEC958 channel-status inspection, RK3288 DT probe with GRF, runtime suspend/resume, and trigger start/stop register traces are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.h -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.h

## Purpose
Defines the Rockchip S/PDIF register offsets and bitfield helpers for transfer configuration, DMA control, transfer start/stop, channel-status/user/validity registers, and version register.

## Important APIs, Types, And Functions
The file consists of macros: `SPDIF_CFGR_CLK_DIV()`, clear/channel-status/adjust/halfword/data-width fields, `SPDIF_DMACR_TDE_*`, `SPDIF_DMACR_TDL()`, `SPDIF_XFER_TXS_*`, fixed offsets such as `SPDIF_CFGR`, `SPDIF_DMACR`, `SPDIF_SMPDR`, and indexed offsets `SPDIF_VLDFRn()`, `SPDIF_USRDRn()`, and `SPDIF_CHNSRn()`.

## Control Flow
No executable flow. The driver uses these macros to build regmap masks and values in `hw_params`, trigger handling, and regmap access validation.

## State And Persistence
No software state. The macros describe S/PDIF hardware registers whose state is cached by `rockchip_spdif.c`.

## Dependencies And Integration Points
Requires kernel `BIT()`, `GENMASK()`, and `FIELD_PREP()` definitions from including context. The macros are consumed only by the Rockchip S/PDIF driver.

## Risks And Edge Cases
- `SPDIF_CFGR_CLK_DIV(x)` encodes `x - 1`, so divider zero or underflow would be invalid if caller passed a bad value.
- The data-width mask macro is spelled `SDPIF_CFGR_VDW_MASK`; this is harmless in current code but is a maintainability trap.
- Field macros do not validate hardware-supported ranges.

## Test Signals
Compile tests and register-value trace tests for each supported PCM format and DMA threshold configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/Kconfig

## Purpose
Declares Samsung ASoC controller and machine-driver configuration options. It gates core Samsung ASoC support, individual PCM/SPDIF/I2S interfaces, and board drivers for SMDK, Wolfson reference boards, Snow, Odroid, Arndale, TM2, Aries, and Midas.

## Important APIs, Types, And Functions
The `menuconfig SND_SOC_SAMSUNG` option depends on Samsung/Exynos platforms or `COMPILE_TEST`, requires `COMMON_CLK`, and selects `SND_SOC_GENERIC_DMAENGINE_PCM`. Sub-options select controller drivers (`SND_SAMSUNG_PCM`, `SND_SAMSUNG_SPDIF`, `SND_SAMSUNG_I2S`) and machine drivers with codec/MFD/I2C/SPI/EXTCON/IIO dependencies.

## Control Flow
There is no runtime flow. Kconfig selection controls which objects the Makefile builds and ensures dependent codec/controller drivers are enabled.

## State And Persistence
Kernel build configuration is the persisted state. No runtime state.

## Dependencies And Integration Points
Integrates with the kernel Kconfig system, codec Kconfig symbols such as `SND_SOC_WM8994`, `SND_SOC_MAX98090`, `MFD_ARIZONA`, and controller symbols used by machine drivers.

## Risks And Edge Cases
- Broad `COMPILE_TEST` support may compile drivers without real hardware coverage.
- Some machine drivers select controller drivers but depend on old platform families or specific codec MFDs, so unmet dependencies can silently hide board support.
- Board drivers that require IIO/EXTCON/GPIOLIB encode those dependencies here; missing selections become build-time rather than runtime failures.

## Test Signals
Configuration matrix builds for Samsung/Exynos and `COMPILE_TEST`, plus dependency checks that selecting each machine driver pulls the intended controller and codec modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/Makefile

## Purpose
Maps Samsung ASoC Kconfig symbols to object files for controller wrappers and machine drivers.

## Important APIs, Types, And Functions
Defines composite objects such as `snd-soc-s3c-dma-y := dmaengine.o`, `snd-soc-samsung-spdif-y := spdif.o`, `snd-soc-pcm-y := pcm.o`, `snd-soc-i2s-y := i2s.o`, and `snd-soc-idma-y := idma.o`. It then wires `obj-$(CONFIG_...)` entries for each board driver.

## Control Flow
No runtime flow. Kbuild uses the symbol-to-object mappings to compile and link modules or built-ins.

## State And Persistence
No runtime state. Build artifacts are determined by active kernel configuration.

## Dependencies And Integration Points
Integrates with Kbuild and the Kconfig symbols in the adjacent `Kconfig`. The I2S symbol builds both `i2s.o` and `idma.o`, reflecting the shared internal-DMA support.

## Risks And Edge Cases
- Object names must stay synchronized with Kconfig symbols; stale mappings would create missing modules.
- `snd-soc-idma.o` is built whenever Samsung I2S is enabled, even if a SoC variant does not use IDMA.

## Test Signals
Build tests with each controller and machine-driver symbol enabled as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/aries_wm8994.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/aries_wm8994.c

## Purpose
Machine driver for Samsung Aries and Fascinate 4G WM8994-based audio. It defines HiFi, baseband voice, and Bluetooth links, DAPM widgets/routes, dock/headset detection, mic-bias regulators, codec FLL programming, and optional FM routing.

## Important APIs, Types, And Functions
- `struct aries_wm8994_variant` selects modem DAI format and FM availability.
- `struct aries_wm8994_data` stores extcon, regulators, GPIOs, ADC, and variant.
- `headset_det_irq_thread()` debounces headset detect GPIO, enables micbias, reads IIO ADC, classifies jack type, and toggles earpath selection.
- `aries_hw_params()` and `aries_hw_free()` start/stop WM8994 FLL1 for AIF1 audio.
- `aries_baseband_init()` configures WM8994 FLL2 for 8 kHz voice.
- `aries_late_probe()` registers dock and headset jacks, extcon notifier, GPIO IRQ, jack zones, and media-button GPIO.
- `aries_audio_probe()` parses DT, regulators, GPIOs, extcon, IIO channel, routing, CPU/codec phandles, registers an auxiliary component with a "Voice call" DAI, and registers the card.

## Control Flow
Probe validates DT-only operation, selects variant data, obtains supplies and GPIO/ADC/extcon resources, parses routing and child `cpu`/`codec` nodes, binds codec phandles for all links, binds CPU/platform for the main I2S link and Bluetooth SCO CPU, registers the modem component, then registers the card. Late probe creates jack objects and installs notifiers/IRQs. At stream parameter setup, the codec FLL rate is selected from sample width/rate; on free, the codec returns to MCLK1.

## State And Persistence
Device state is in `aries_wm8994_data`, while `aries_dock` and `aries_headset` are static jack objects. GPIO/extcon/ADC events update ALSA jack state. FLL and sysclk selections live in codec hardware state until changed. No disk persistence.

## Dependencies And Integration Points
Depends on WM8994 codec/MFD, Samsung I2S DAI names, BT SCO PCM, extcon, IIO voltage ADC, GPIO descriptors, regulators, and DT audio routing. Integrates with DAPM for speakers, microphones, modem, Bluetooth, line out, and optional FM.

## Risks And Edge Cases
- Static card and jack structures can make multiple simultaneous devices unsafe.
- ADC threshold zones are hard-coded, unlike Midas where thresholds come from DT.
- Headset IRQ assumes detect GPIO remains asserted for 300 ms before ADC classification.
- Error paths release only top-level CPU/codec child nodes; phandles assigned into DAI links are devm/card lifetime assumptions.
- Variant selection depends on matching DT compatible; missing match data would be fatal.

## Test Signals
DT probe for both compatible variants, jack insertion/removal and media button tests, dock extcon notifications, FLL rate tests for 8/11.025/24-bit cases, modem/Bluetooth link activation, and DAPM path checks for FM-present and FM-absent variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/aries_wm8994.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/arndale.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/arndale.c

## Purpose
Machine driver for Arndale boards with either RT5631/ALC5631 or WM1811 codecs. It creates a simple single-link I2S card and applies codec-specific clock setup.

## Important APIs, Types, And Functions
- `arndale_rt5631_hw_params()` sets Samsung I2S CDCLK output, RCLK source, and RT5631 sysclk at `rate * 256`.
- `arndale_wm1811_hw_params()` chooses WM1811 MCLK1 rate based on width/rate and applies the `+1` clock rounding workaround.
- `arndale_put_of_nodes()` releases CPU and codec phandles in DAI links.
- `arndale_audio_probe()` selects a card from OF match data, parses `samsung,audio-cpu` and `samsung,audio-codec`, and registers it.

## Control Flow
OF compatible selects the RT5631 or WM1811 static card. Probe fills CPU/platform/codec OF nodes and registers the card. During `hw_params`, the selected ops configure CPU/codec clocks for the active sample rate and format.

## State And Persistence
The card and DAI links are static structures mutated with OF nodes at probe time. No runtime state beyond clock settings in CPU/codec drivers.

## Dependencies And Integration Points
Integrates with Samsung I2S (`SAMSUNG_I2S_*`) and either RT5631 or WM8994/WM1811 codec DAIs. Depends on DT properties `samsung,audio-cpu` and `samsung,audio-codec`.

## Risks And Edge Cases
- Static card mutation is not multi-instance safe.
- Clock setup is narrow and does not validate all possible rates/formats beyond codec/CPU return values.
- Node cleanup relies on remove/error paths; successful devm card registration keeps phandles until remove.

## Test Signals
Probe tests for all three compatibles, DT missing-phandle failures, playback with 16/24-bit rates, and remove/unbind phandle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/arndale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/bells.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/bells.c

## Purpose
Machine driver for Wolfson Bells boards with WM2200, WM5102, or WM5110 codec topologies. It wires AP-to-DSP, DSP-to-codec, optional baseband, and optional sub-speaker links, and manages Arizona/WM0010/WM9081 clocks.

## Important APIs, Types, And Functions
- `struct bells_drvdata` holds per-card SYSCLK and ASYNCCLK rates.
- `bells_set_bias_level()` starts FLL1 and optional FLL2 when entering prepare from standby.
- `bells_set_bias_level_post()` stops FLLs when returning to standby.
- `bells_late_probe()` configures codec SYSCLK/ASYNCCLK/OPCLK, WM0010 clock, AIF clocks, and WM9081 MCLK depending on available runtime links.
- Static DAI link arrays model WM2200, WM5102, and WM5110 variants.

## Control Flow
Platform ID selects one of three static cards. Registration is simple; late probe then locates relevant runtimes by link index and programs clock trees. Bias-level transitions dynamically start and stop codec FLLs around DAPM power changes.

## State And Persistence
Per-card clock rates are static `drvdata`. Runtime FLL/sysclk state persists in the attached codec components until bias transitions change it. No private allocation or disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S, WM0010 DSP component, WM2200/WM5102/WM5110 codecs, WM1250 EV1, WM9081, DAPM, and platform device IDs. Codec-conf prefixes distinguish the sub WM9081.

## Risks And Edge Cases
- Uses static cards indexed by `pdev->id`; invalid IDs would index out of bounds because probe does not validate.
- Late probe uses numeric DAI indexes and `card->num_rtd` comparisons, so topology changes are fragile.
- FLL startup errors are logged in bias prepare but some paths continue returning success.

## Test Signals
Platform-device probe for ids 0-2, link creation count, DAPM bias transitions with FLL start/stop traces, late-probe clock programming, and baseband/sub link audio smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/bells.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/dma.h -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/dma.h

## Purpose
Declares Samsung's ASoC dmaengine registration helper for controller drivers that need a compatible DMA PCM platform with optional custom channel names and DMA device.

## Important APIs, Types, And Functions
Exports the prototype `samsung_asoc_dma_platform_register(struct device *dev, dma_filter_fn filter, const char *tx, const char *rx, struct device *dma_dev)`.

## Control Flow
No executable flow. Callers use the helper during probe after filling their `snd_dmaengine_dai_dma_data`.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `<sound/dmaengine_pcm.h>` and is used by Samsung I2S, PCM, and S/PDIF drivers. The comments document that `tx`/`rx` may be NULL when DMA channel names are the defaults.

## Risks And Edge Cases
The header does not encode ownership or lifetime; callers rely on the implementation's devm allocation.

## Test Signals
Build coverage and successful probe of all callers with default and explicit channel names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/dmaengine.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/dmaengine.c

## Purpose
Implements a small wrapper around `devm_snd_dmaengine_pcm_register()` for Samsung ASoC controller drivers.

## Important APIs, Types, And Functions
`samsung_asoc_dma_platform_register()` allocates `struct snd_dmaengine_pcm_config`, sets `prepare_slave_config`, compatibility filter, optional DMA device, playback/capture channel names, and registers the PCM with `SND_DMAENGINE_PCM_FLAG_COMPAT`. It is exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
Controller probe calls the helper; allocation failure returns `-ENOMEM`; otherwise registration result is returned directly.

## State And Persistence
The PCM config is devm-managed and lives for the device lifetime. No persistent state beyond the registered component/PCM platform.

## Dependencies And Integration Points
Depends on ASoC, PCM, and dmaengine PCM APIs. It centralizes the compatibility-mode DMA registration used by Samsung I2S, PCM, and S/PDIF controller drivers.

## Risks And Edge Cases
The helper does no validation of channel names or DMA device compatibility; failures surface from dmaengine registration or later channel requests.

## Test Signals
Probe tests for callers with explicit channel names (`tx`, `rx`, `tx-sec`) and NULL names, plus module symbol/export build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/dmaengine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/i2s-regs.h -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/i2s-regs.h

## Purpose
Defines Samsung I2S register offsets and bit fields used by the Samsung I2S and internal DMA drivers.

## Important APIs, Types, And Functions
Macro groups cover `I2SCON`, `I2SMOD`, FIFO control/status, prescaler, AHB internal DMA, transfer size/count, stream addresses, TDM/status registers, active/pause bits, format/clock selection fields, variant-specific Exynos bit positions, FIFO count extractors, and IDMA level interrupt controls.

## Control Flow
No executable flow. The macros are used by `i2s.c` for DAI control and by `idma.c` for internal DMA setup and interrupts.

## State And Persistence
No software state. The defined fields describe MMIO state saved/restored by `i2s.c` runtime PM and manipulated by IDMA.

## Dependencies And Integration Points
Consumed by Samsung I2S controller and IDMA component. It must match hardware layout variants referenced through per-variant offsets in `i2s.c`.

## Risks And Edge Cases
- Shared macros cover multiple hardware generations; callers must use variant offsets/masks correctly.
- FIFO count macros encode fixed bit widths and differ for secondary FIFO.
- IDMA macros are tightly coupled to the internal-DMA ring logic in `idma.c`.

## Test Signals
Compile coverage plus hardware register trace tests for I2S format, BCLK/RCLK, FIFO flush, active/pause, and IDMA interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/i2s-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/i2s.c

## Purpose
Implements the Samsung/Exynos I2S ASoC CPU DAI driver. It supports primary and optional secondary playback DAIs over one hardware block, DMA and optional IDMA, variant-specific register layouts, clock-provider registration, runtime PM, clock/format negotiation, and DAPM mixing routes.

## Important APIs, Types, And Functions
- `struct samsung_i2s_variant_regs` abstracts register offsets and masks across I2S versions.
- `struct samsung_i2s_dai_data` stores quirks, PCM rates, variant regs, and optional fixups.
- `struct i2s_dai` models one DAI instance, including DMA data, sibling pointers, RFS/BFS constraints, and manager/open state.
- `struct samsung_i2s_priv` stores shared controller state, locks, clocks, register base, quirks, suspend register cache, and optional clock provider data.
- `i2s_set_sysclk()`, `i2s_set_fmt()`, `i2s_set_clkdiv()`, `i2s_hw_params()`, and `i2s_trigger()` are the core DAI callbacks.
- `i2s_txctrl()`, `i2s_rxctrl()`, and `i2s_fifo()` manipulate active/pause and FIFO flush state.
- `config_setup()` resolves BCLK/RCLK constraints and prescaler programming.
- `i2s_register_clock_provider()` exposes `cdclk`, `rclk_src`, and `prescaler` clocks to DT consumers when `#clock-cells` is present.
- `samsung_i2s_probe()` handles DT/platform-data probe, DAI allocation, DMA setup, optional secondary device creation, component registration, runtime PM, and clock provider setup.

## Control Flow
Probe selects variant data from OF or platform ID, allocates one or two DAI descriptors, maps registers, enables the `iis` clock, fills DMA addresses, registers dmaengine PCM for primary and optional secondary device, registers the component, enables runtime PM, and optionally registers clocks. DAI probe initializes DMA pointers, resets hardware if required, configures IDMA register base for supported variants, stops/flushes streams, and gates CDCLK. Startup marks a DAI opened and assigns manager ownership if the sibling is not manager. `set_fmt` and clock APIs reject changes that conflict with active sibling state. `hw_params` programs channel count and sample width and updates frame clock. Trigger start takes a PM reference, applies fixups, calls `config_setup()`, starts RX or TX; trigger stop pauses the stream, flushes FIFO, and releases PM. Runtime suspend caches selected registers and disables clocks; resume restores them.

## State And Persistence
Shared state includes `slave_mode`, `rclk_srcrate`, suspend register snapshots, sibling DAI open/manager flags, and per-DAI requested RFS/BFS. Hardware register state is not regmap-backed; it is explicitly saved/restored on runtime PM. Clock-provider registrations live until remove.

## Dependencies And Integration Points
Depends on ASoC, PM runtime, common clock framework, OF/platform data, `dma.h`, `idma.h`, `i2s.h`, and `i2s-regs.h`. Exposes CPU DAI names `samsung-i2s` and `samsung-i2s-sec`. Integrates with machine drivers via Samsung-specific clock IDs, BCLK divider ID, DT clocks, and optional `samsung,idma-addr`.

## Risks And Edge Cases
- Primary and secondary DAIs share registers; lock and manager logic is critical. Incorrect concurrent use can return `-EAGAIN` or corrupt format/clock state.
- `i2s_create_secondary_device()` error path calls `platform_device_unregister(priv->pdev_sec)` before assignment in one failure branch, which is suspicious.
- Clock-provider setup assumes parent clock lookup succeeds enough to build names; missing parents can leave NULL parent names.
- Runtime PM save/restore covers only selected registers; less-used registers may rely on reset/default state.
- `config_setup()` computes PSR by integer division without explicit zero/rounding checks beyond existing clock-rate setup.
- Static compatible quirk data must match hardware exactly for register offsets and supported BCLK/RCLK values.

## Test Signals
Primary playback/capture and secondary playback tests, simultaneous FE/BE routing through playback mixer, BCLK/RCLK constraint tests with sibling active, suspend/resume register restoration, DT clock-provider consumers, IDMA-capable variant playback, all OF compatibles, and fault injection for missing clocks/DMA/idma address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/i2s.h

## Purpose
Provides Samsung I2S public DAI names and machine-driver clock/divider IDs.

## Important APIs, Types, And Functions
Defines `SAMSUNG_I2S_DAI`, `SAMSUNG_I2S_DAI_SEC`, `SAMSUNG_I2S_DIV_BCLK`, `SAMSUNG_I2S_RCLKSRC_0`, `SAMSUNG_I2S_RCLKSRC_1`, `SAMSUNG_I2S_CDCLK`, `SAMSUNG_I2S_OPCLK`, and OPCLK source constants such as `SAMSUNG_I2S_OPCLK_PCLK`.

## Control Flow
No executable flow. Machine drivers pass these constants to `snd_soc_dai_set_sysclk()` or `snd_soc_dai_set_clkdiv()`.

## State And Persistence
No state.

## Dependencies And Integration Points
Shared by Samsung machine drivers and `i2s.c`. It is the lightweight external contract for configuring Samsung I2S clocks without exposing register internals.

## Risks And Edge Cases
Constants must remain synchronized with `i2s_set_sysclk()` and `i2s_set_clkdiv()` switch cases. Incorrect clock ID use returns `-EINVAL` or can conflict with active DAI state.

## Test Signals
Compile coverage for machine drivers and runtime clock setup calls on Arndale, Midas, Odroid, Snow, SMDK, Aries, and other Samsung boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/idma.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/idma.c

## Purpose
Implements the Samsung I2S0 internal DMA PCM component for low-power audio memory playback, used with I2S variants that support IDMA.

## Important APIs, Types, And Functions
- `struct idma_ctrl` stores per-substream state, ring addresses, period size/count, callback, and token.
- Static `idma` holds global register base and LP audio memory transmit address.
- `idma_reg_addr_init()` initializes the global MMIO base and low-power TX address; exported for `i2s.c`.
- `idma_hw_params()`, `idma_prepare()`, `idma_trigger()`, `idma_pointer()`, `idma_mmap()`, `idma_open()`, and `idma_close()` implement PCM component callbacks.
- `iis_irq()` handles I2S AHB level interrupts, advances the level interrupt address around the ring, and calls the period callback.

## Control Flow
The platform driver obtains an IRQ and registers an ASoC component. On PCM open it allocates `idma_ctrl` and requests the shared I2S IRQ. `hw_params` enables IDMA mode in `I2SMOD`, configures AHB reload/mask, sets runtime DMA buffer metadata, and stores ring boundaries. `prepare` stops DMA and enqueues initial start/level/size registers. Trigger start/stop toggles `ST_RUNNING` and AHB DMA enable. IRQ clears level interrupt, advances the next interrupt address modulo the buffer, and calls `snd_pcm_period_elapsed()` through `idma_done()`. `pcm_new` maps the fixed low-power memory region as a continuous DMA buffer.

## State And Persistence
Global static state stores the IDMA register base, low-power TX physical address, and IRQ number. Per-open state is allocated in `runtime->private_data`. DMA ring position is hardware-derived from `I2STRNCNT`. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S register definitions, ASoC PCM component callbacks, IRQ APIs, DMA mask APIs, and `idma.h`. `i2s.c` calls `idma_reg_addr_init()` when the hardware supports IDMA and passes the secondary DAI's `idma_playback.addr`.

## Risks And Edge Cases
- Static global IDMA state prevents clean multi-controller support.
- `idma_close()` calls `free_irq(idma_irq, prtd)` before checking `prtd`, so a corrupt NULL private_data would be unsafe.
- The buffer is mapped with `ioremap()` from a fixed physical address; platform memory reservation must be correct.
- Only playback is handled.
- Period callback receives `prtd->period` rather than byte count naming, but callback ignores bytes except for signature.

## Test Signals
IDMA playback on supported I2S0 hardware, mmap playback, period interrupt cadence, pointer progression and wraparound, trigger pause/resume, and open/close IRQ lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/idma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/idma.h -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/idma.h

## Purpose
Declares constants and the initialization hook for Samsung I2S internal DMA.

## Important APIs, Types, And Functions
Defines `LPAM_DMA_STOP`, `LPAM_DMA_START`, `MAX_IDMA_PERIOD`, `MAX_IDMA_BUFFER`, and prototype `idma_reg_addr_init(void __iomem *regs, dma_addr_t addr)`.

## Control Flow
No executable flow. `i2s.c` uses the prototype to hand MMIO base and low-power memory address to `idma.c`.

## State And Persistence
No state in the header.

## Dependencies And Integration Points
Depends on `dma_addr_t` and `void __iomem` types from including kernel headers. Couples the I2S controller driver to the IDMA PCM component.

## Risks And Edge Cases
The fixed buffer limits are compile-time constants and must match hardware/firmware low-power memory allocation expectations.

## Test Signals
Compile coverage and IDMA playback buffer/period limit validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/idma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/littlemill.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/littlemill.c

## Purpose
Machine driver for Wolfson Littlemill boards with Samsung I2S, WM8994, and WM1250 baseband. It manages WM8994 FLLs, DAPM pins/routes, baseband clock supply, and headset jack detection.

## Important APIs, Types, And Functions
- `littlemill_set_bias_level()` and `_post()` start/stop WM8994 FLL1 around codec bias transitions.
- `littlemill_hw_params()` updates global `sample_rate` and programs FLL1/SYSCLK.
- `bbclk_ev()` starts/stops WM8994 FLL2 for the baseband AIF2 clock.
- `littlemill_late_probe()` initializes AIF1/AIF2 sysclks and registers headset jack detection through WM8958/WM8994 helpers.

## Control Flow
Probe registers a static card with CPU and baseband DAI links. During normal audio `hw_params`, FLL1 is set from 32.768 kHz MCLK2 to `sample_rate * 512`. DAPM bias prepare can start FLL1 if no stream did. Bias standby switches back to MCLK2 and stops FLL1. The baseband clock DAPM supply starts/stops FLL2. Late probe configures initial MCLK2 clocks and jack detection.

## State And Persistence
`sample_rate` is a file-static global used for bias-level FLL setup. Codec FLL/sysclk and jack status persist in hardware/ASoC runtime state. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S platform names, WM8994 codec APIs, WM1250 EV1, DAPM, and codec mic-detect helpers.

## Risks And Edge Cases
- Global `sample_rate` is not multi-card safe and defaults to 44.1 kHz.
- Bias-level FLL setup may race conceptually with stream-specific rates if multiple rates are used.
- DAPM widget `"Headset Mic"` is declared as `SND_SOC_DAPM_HP`, which looks semantically odd.

## Test Signals
Playback at multiple rates, DAPM bias transitions without active stream, baseband DAPM clock supply activation, headset detection, and register traces for FLL1/FLL2 start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/littlemill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/lowland.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/lowland.c

## Purpose
Machine driver for Wolfson Lowland boards using Samsung I2S, WM5100, WM1250 baseband, and WM9081 sub speaker codec.

## Important APIs, Types, And Functions
- `lowland_wm5100_init()` sets WM5100 SYSCLK from MCLK1, configures OPCLK output, creates headset jack pins, and starts WM5100 detection.
- `lowland_wm9081_init()` disables `LINEOUT` DAPM pin and sets WM9081 MCLK.
- Static DAI links define CPU, baseband, and sub speaker paths; `sub_params` fixes sub speaker to 44.1 kHz S32 stereo.

## Control Flow
Probe registers the static card. Link init for the main codec sets clocks and jack detection. Link init for the sub speaker configures its clock and disables a DAPM pin. ASoC then manages the three DAI links and DAPM routes.

## State And Persistence
Static card/link/jack objects hold runtime state. Codec clocks and jack state persist in ASoC/hardware state. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S named platform, WM5100 codec, WM9081 codec, WM1250 EV1, DAPM, jack APIs, and codec-conf prefixing for the sub codec.

## Risks And Edge Cases
- Static structures are not multi-instance safe.
- Clock rates are hard-coded to 44.1 kHz-derived values.
- Minimal error handling beyond link init return codes.

## Test Signals
Probe/register card, WM5100 jack detection, main/baseband/sub link activation, and DAPM route validation for main speaker/sub codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/lowland.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/midas_wm1811.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/midas_wm1811.c

## Purpose
Machine driver for Samsung Midas WM1811/WM8994-family audio. It supports HiFi, voice, Bluetooth links, DAPM routing and pins, codec FLL1 management, GPIO/ADC headset detection and button classification, optional FM/lineout GPIO selection, and DT-driven thresholds.

## Important APIs, Types, And Functions
- `struct midas_priv` stores optional routing GPIOs, headset detect/key GPIOs, ADC channel, current FLL1 rate, and headset jack.
- `headset_jack_check()` enables headset mic bias via DAPM, reads ADC, and classifies jack type.
- `headset_key_check()` reads ADC and maps thresholds to media/volume buttons.
- `midas_start_fll1()` and `midas_stop_fll1()` manage WM8994 FLL1 and SYSCLK.
- `midas_aif1_hw_params()` chooses FLL1 rate for HiFi stream parameters.
- DAPM event handlers `midas_ext_spkmode()`, `midas_fm_set()`, and `midas_line_set()` adjust codec mixer/GPIO routes.
- `midas_late_probe()` sets initial MCLK2 sysclk and registers either codec-native or GPIO/ADC jack detection.
- `midas_probe()` parses DT GPIOs, ADC, threshold arrays, card name/routing, CPU/codec phandles, registers external voice/Bluetooth DAIs, and registers the card.

## Control Flow
Probe allocates private state, acquires optional FM/lineout/headset resources, validates IIO voltage channel and threshold arrays when GPIO headset detection is used, parses card metadata/routing, binds all DAI links to the CPU and codec nodes, registers extra voice/Bluetooth DAIs, and registers the card. Late probe initializes codec sysclk and jack detection path. During HiFi `hw_params`, FLL1 rate is selected from PCM parameters. DAPM bias transitions start FLL1 in prepare and stop it in standby.

## State And Persistence
Private state tracks the active FLL1 rate and jack object. Static threshold arrays are filled from DT at probe. GPIO outputs reflect DAPM route state. Codec FLL/sysclk persists in hardware state. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S IDs, WM8994/WM1811 codec APIs, GPIO descriptors, IIO voltage ADC, DAPM, DT card/routing/phandle parsing, and external DAIs for voice/Bluetooth registered by this file.

## Risks And Edge Cases
- Static card and threshold arrays are mutated from DT and not multi-instance safe.
- There are non-ASCII spaces in two error strings, which is harmless but inconsistent with kernel ASCII style.
- FLL switching must avoid active-clock glitches; `midas_start_fll1()` temporarily switches to MCLK2 only when reconfiguring an existing FLL.
- ADC thresholds are treated as microvolt values but stored in fields named `min_mv`/`max_mv`.

## Test Signals
DT threshold validation, GPIO/ADC headset and button detection, codec-native jack detection fallback, HiFi playback across rates, DAPM bias FLL transitions, FM/lineout GPIO toggling, and voice/Bluetooth link registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/midas_wm1811.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/odroid.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/odroid.c

## Purpose
Machine driver for Odroid XU3/XU4 audio. It builds a DPCM-style card with primary and optional secondary front ends feeding an I2S mixer/backend linked to one or more codecs, and manages Exynos I2S clock rates.

## Important APIs, Types, And Functions
- `struct odroid_priv` embeds the card, I2S bus/op clocks, a lock, active backend sample rate, and backend-active flag.
- `odroid_card_fe_startup()` constrains FE channels to stereo.
- `odroid_card_fe_hw_params()` rejects FE rates that differ from an active backend.
- `odroid_card_be_hw_params()` selects PLL/rfs values for supported rates, sets bus and SCLK rates, and programs the second codec sysclk when present.
- `odroid_card_be_trigger()` tracks backend active state.
- `odroid_audio_probe()` parses DT widgets/routes, CPU/codec child nodes, DAI names, codec links, clocks, and registers the card.

## Control Flow
Probe creates a private card, parses name/widgets/routes, chooses whether the secondary FE exists based on number of CPU `sound-dai` phandles, resolves DAI names and codec components, obtains I2S clocks, and registers the card. FE startup/hw_params enforce stereo and active-backend rate consistency. Backend hw_params configures clock tree from the requested sample rate; backend trigger marks active/inactive under lock.

## State And Persistence
`be_sample_rate` and `be_active` persist during runtime to coordinate front ends. Clock pointers are held until remove. DAI codec allocations are released in remove. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S clock provider names (`i2s_opclk1`, `iis`), DT child `cpu`/`codec` nodes, ASoC DPCM flags (`dynamic`, `no_pcm`), MAX98090-style codec capability detection, and backwards-compatible Samsung routing properties.

## Risks And Edge Cases
- `odroid_audio_remove()` uses `platform_get_drvdata()`, but probe stores drvdata only through `snd_soc_card_set_drvdata(card, priv)`, so platform drvdata availability depends on ASoC registration side effects.
- Rate table is explicit; unsupported rates fail.
- CPU child node is used before null-check in `of_count_phandle_with_args(cpu, ...)`.
- Clock rates use `+1`/`+2` workarounds for PLL rounding, so exact-rate assumptions should be avoided.

## Test Signals
DT probes with one and two CPU DAIs, playback and capture-capable codec variants, FE/backend rate mismatch rejection, supported rate table coverage, secondary FE playback, and remove/unbind resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/odroid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.c

## Purpose
Implements the Samsung S3C PCM controller ASoC DAI driver for two possible PCM instances. It configures DSP_A/DSP_B framing, serial clock source/dividers, DMA FIFO control, and platform-data GPIO/DMA integration.

## Important APIs, Types, And Functions
- `struct s3c_pcm_info` stores lock, device, MMIO base, SCLK-per-FS, idle clock mode, pclk/cclk, and DMA descriptors.
- `s3c_pcm_snd_txctrl()` and `s3c_pcm_snd_rxctrl()` enable/disable TX/RX DMA, FIFO, controller, dipstick thresholds, and serial clock.
- `s3c_pcm_trigger()` dispatches trigger commands to TX/RX control under lock.
- `s3c_pcm_hw_params()` supports only 16-bit samples and computes SCLK/SYNC dividers.
- `s3c_pcm_set_fmt()`, `s3c_pcm_set_clkdiv()`, and `s3c_pcm_set_sysclk()` implement format and clock APIs.
- `s3c_pcm_dev_probe()` validates platform ID, maps registers, enables clocks, fills DMA addresses, registers dmaengine PCM, enables runtime PM, and registers the DAI.

## Control Flow
Probe uses `pdev->id` to select static per-instance state and DMA arrays, optionally calls platform GPIO config, maps MMIO, enables audio-bus and PCM clocks, stores DMA FIFO addresses, registers DMA PCM, then registers one DAI. `hw_params` calculates dividers from chosen source clock and `sclk_per_fs`. `set_fmt` accepts only master DSP_A/DSP_B with inverted bit clock and normal frame, and records continuous/gated idle clock behavior. Trigger toggles DMA/FIFO enable bits for playback or capture.

## State And Persistence
Two static `s3c_pcm_info` entries and static DMA descriptor arrays persist for module lifetime. Per-instance state includes `sclk_per_fs` and `idleclk`. Hardware register state is not explicitly saved by PM despite runtime PM being enabled.

## Dependencies And Integration Points
Depends on platform data `s3c_audio_pdata`, Samsung DMA helper, clocks named `audio-bus` and `pcm`, ASoC DAI APIs, and `pcm.h` constants used by machine drivers.

## Risks And Edge Cases
- Only platform-data style probe is supported; no OF match table appears here.
- Runtime PM is enabled but no PM ops are defined, so clock gating is manual only at remove.
- `s3c_pcm_snd_txctrl()` and RX stop paths set `SERCLK_EN` when `!idleclk`, which looks counterintuitive and should be checked against hardware docs.
- Only 16-bit stereo rates are supported.
- Static instance arrays limit supported IDs to 0 and 1.

## Test Signals
Probe for ids 0/1, invalid id failure, DSP_A/DSP_B format setup, 8-96 kHz 16-bit playback/capture, clock source switching, DMA channel acquisition, and trigger start/stop register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.h

## Purpose
Defines Samsung PCM machine-driver constants for source clock selection and SCLK-per-frame divider selection.

## Important APIs, Types, And Functions
Defines `S3C_PCM_CLKSRC_PCLK`, `S3C_PCM_CLKSRC_MUX`, and `S3C_PCM_SCLK_PER_FS`.

## Control Flow
No executable flow. Machine drivers pass these constants to `snd_soc_dai_set_sysclk()` and `snd_soc_dai_set_clkdiv()`.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by `pcm.c` and SMDK PCM machine driver. It is the public configuration contract for the Samsung PCM DAI.

## Risks And Edge Cases
Constants must remain aligned with `s3c_pcm_set_sysclk()` and `s3c_pcm_set_clkdiv()`.

## Test Signals
Compile coverage and SMDK PCM `hw_params` successfully configuring `S3C_PCM_CLKSRC_MUX` and `S3C_PCM_SCLK_PER_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_spdif.c

## Purpose
Legacy SMDK S/PDIF machine driver. It creates an S/PDIF DIT codec device and soc-audio card, manually programs the Samsung audio clock hierarchy, and configures S/PDIF clock rates for supported sample rates.

## Important APIs, Types, And Functions
- `set_audio_clock_heirachy()` obtains global clocks (`fout_epll`, `mout_epll`, `sclk_audio`, `sclk_spdif`) and sets their parents.
- `set_audio_clock_rate()` sets EPLL and S/PDIF source rates.
- `smdk_hw_params()` maps sample rates to PLL frequencies, uses 512fs, and calls `snd_soc_dai_set_sysclk()` with `SND_SOC_SPDIF_INT_MCLK`.
- `smdk_init()` allocates/registers platform devices for `spdif-dit` and `soc-audio`.

## Control Flow
Module init creates the DIT and soc-audio platform devices, associates the static card, and then sets the clock hierarchy. On stream setup, `hw_params` chooses 45.1584 MHz for 44.1 kHz or 49.152 MHz for 32/48/96 kHz families, sets source clocks, and tells the CPU DAI to use internal MCLK.

## State And Persistence
Static platform-device pointers persist until module exit. Clock parent/rate changes persist in the clock framework while the module is active.

## Dependencies And Integration Points
Depends on Samsung S/PDIF DAI, generic `spdif-dit` codec, legacy `soc-audio` platform-device registration, and global clock names.

## Risks And Edge Cases
- Legacy non-DT style with global `clk_get(NULL, ...)` names is fragile on modern systems.
- Function name has typo `heirachy`, harmless but visible.
- Only 32/44.1/48/96 kHz sample rates are accepted.
- Clock parent/rate calls ignore some return values.

## Test Signals
Module load/unload, platform-device creation cleanup on failures, playback at supported rates, unsupported-rate rejection, and clock parent/rate inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994.c

## Purpose
SMDK I2S machine driver for WM8994. It defines primary I2S and secondary FIFO playback links, programs WM8994 FLL1 based on stream parameters, disables unused codec pins, and supports optional DT CPU phandle parsing.

## Important APIs, Types, And Functions
- `smdk_hw_params()` calculates WM8994 FLL output based on width/rate and sets FLL1/SYSCLK.
- `smdk_wm8994_init_paiftx()` disables unused DAPM pins.
- Static DAI links bind `samsung-i2s.0` and `samsung-i2s-sec` to `wm8994-aif1`.
- `smdk_audio_probe()` optionally replaces CPU/platform names with `samsung,i2s-controller` OF node and registers the card.

## Control Flow
Probe sets card device, updates the primary link for DT if present, then registers the static card. Link init disables not-connected codec pins. `hw_params` starts FLL1 for both primary and secondary links.

## State And Persistence
Static card/link structures are mutated for DT. Codec FLL/SYSCLK settings persist until changed by codec/card lifecycle. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S primary and secondary DAI names, WM8994 codec, DAPM, and optional DT property `samsung,i2s-controller`.

## Risks And Edge Cases
- DT parsing updates only the first DAI link, leaving secondary link name-based.
- Static card mutation is not multi-instance safe.
- FLL is not explicitly stopped in this machine driver.

## Test Signals
Probe with platform-name and DT modes, primary and secondary playback, DAPM disabled-pin verification, and FLL rate setup for 8/11.025/24-bit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994pcm.c

## Purpose
SMDK PCM machine driver for WM8994 over the Samsung PCM controller. It supports an 8 kHz DSP_B PCM link and configures codec FLL/sysclk plus CPU PCM source clock/divider.

## Important APIs, Types, And Functions
- `smdk_wm8994_pcm_hw_params()` accepts only 8 kHz, sets WM8994 FLL1/SYSCLK to 512fs, sets CPU `S3C_PCM_CLKSRC_MUX`, and sets `S3C_PCM_SCLK_PER_FS`.
- Static DAI link connects `samsung-pcm.0` to `wm8994-aif1` with DSP_B, inverted bit clock, codec/provider clock flags.
- `snd_smdk_probe()` registers the static card.

## Control Flow
Probe assigns device and registers card. During hw_params, unsupported rates fail; 8 kHz configures codec and PCM controller clocks before stream start.

## State And Persistence
Static card/link data only. Codec and PCM clock settings persist in hardware until changed.

## Dependencies And Integration Points
Depends on Samsung PCM DAI constants from `pcm.h`, WM8994 codec APIs, and platform DAI names.

## Risks And Edge Cases
- Only 8 kHz is accepted.
- No DT parsing or dynamic routing.
- FLL is not explicitly stopped.

## Test Signals
8 kHz playback/capture setup, unsupported-rate rejection, CPU DAI clock/divider call success, and card registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/snow.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/snow.c

## Purpose
Machine driver for Google Snow Exynos boards with MAX98090/MAX98091/MAX98095 and optional HDMI codec support. It parses old and new DT bindings, computes I2S bus clock rates, sets codec MCLK, and registers a single I2S card.

## Important APIs, Types, And Functions
- `struct snow_priv` stores one dynamically filled DAI link and I2S bus clock.
- `snow_card_hw_params()` validates 16/24-bit audio, computes BFS/RFS from rate and width, selects an available PLL rate/prescaler combination, and sets the I2S bus clock.
- `snow_late_probe()` sets codec sysclk to 24 MHz `FIN_PLL_RATE`.
- `snow_probe()` builds the DAI link, supports new child-node DT with `snd_soc_of_get_dai_link_codecs()`, supports legacy `samsung,i2s-controller`/`samsung,audio-codec`, and registers the card.

## Control Flow
Probe allocates private link state, initializes I2S format, tries new DT binding first, obtains codec list and `i2s_opclk0` for new bindings, otherwise falls back to legacy phandles, assigns platform OF node, optionally parses card name, stores drvdata, and registers the card. `hw_params` runs only on new binding links with ops installed. Remove releases OF nodes, codec allocations, and clock.

## State And Persistence
Private DAI link and clock pointer persist for device lifetime. Clock rate is adjusted per stream. Static `snow_snd` card is shared template state.

## Dependencies And Integration Points
Depends on Samsung I2S, DT child-node bindings, MAX9809x/HDMI codec links, common clock framework, and ASoC card parsing helpers.

## Risks And Edge Cases
- Static card template plus dynamic link pointer is not multi-instance safe.
- PLL selection loop tests unsigned difference `(pll_rate[i] - rclk * psr) <= 2`, which can underflow when PLL is lower than target.
- Remove unconditionally calls `snd_soc_of_put_dai_link_codecs()` and `clk_put()` even for legacy path where codec allocation/clock may differ.
- Only selected rates and 16/24-bit widths are supported.

## Test Signals
Probe with legacy and new DT bindings, multi-codec HDMI case, supported/unsupported rate and width tests, I2S clock-rate verification, late-probe codec sysclk setup, and remove-path resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/snow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/spdif.c

## Purpose
Implements the Samsung S/PDIF controller ASoC DAI driver. It supports playback-only S16_LE S/PDIF output, clock source selection, FIFO/config/status programming, DMA setup, shutdown reset, and component suspend/resume register save/restore.

## Important APIs, Types, And Functions
- `struct samsung_spdif_info` stores lock, device, MMIO, clock rate, pclk/sclk, saved registers, and playback DMA descriptor.
- `spdif_set_sysclk()` selects internal/external MCLK and records clock rate.
- `spdif_hw_params()` validates playback/S16_LE, sets DMA data, FIFO threshold, user-data bit behavior, PCM data mode, MCLK divider ratio, sample frequency status, category, and copyright bit.
- `spdif_trigger()` toggles power via `spdif_snd_txctrl()`.
- `spdif_shutdown()` resets and powers down.
- `spdif_suspend()`/`spdif_resume()` save and restore `CLKCON`, `CON`, and `CSTAS`.
- `spdif_probe()` configures platform data GPIO, clocks, MMIO, DMA, DMA PCM registration, drvdata, and component/DAI registration.

## Control Flow
Probe initializes one static controller instance, enables `spdif` and `sclk_spdif` clocks, maps registers, fills DMA address for `DATA_OUTBUF`, registers DMA PCM, and registers a playback DAI. Machine driver calls `.set_sysclk` before `.hw_params`; `hw_params` uses the stored rate divided by sample rate to choose 256/384/512fs divider. Trigger starts/stops by setting the power bit. Shutdown asserts software reset and powers off. Component suspend saves registers and resets hardware; resume restores them.

## State And Persistence
One static `spdif_info` and static DMA descriptor persist for module lifetime. `clk_rate` is software state set by machine driver. Saved registers persist across system suspend. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung DMA helper, platform data GPIO/DMA fields, clocks named `spdif` and `sclk_spdif`, `spdif.h` clock-source constants, and ASoC S/PDIF machine links.

## Risks And Edge Cases
- Static singleton prevents multiple controller instances.
- Capture is rejected in `hw_params` and not advertised.
- Only S16_LE and four sample rates are supported.
- `spdif_suspend()` initializes local `con` from old `saved_con` before updating `saved_con`, then writes `con | CON_SW_RESET`; this may reset using stale saved state.
- `spdif_set_sysclk()` records `freq` without validating clock hardware rate.

## Test Signals
Playback at 32/44.1/48/96 kHz, ratio validation for 256/384/512fs, trigger power-bit traces, suspend/resume register restore, shutdown reset, and probe failure cleanup for missing clocks/MMIO/DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/spdif.h -->
# sources/distributed-fs/ceph-client/sound/soc/samsung/spdif.h

## Purpose
Defines public Samsung S/PDIF machine-driver clock source IDs for internal and external MCLK.

## Important APIs, Types, And Functions
Defines `SND_SOC_SPDIF_INT_MCLK` and `SND_SOC_SPDIF_EXT_MCLK`.

## Control Flow
No executable flow. Machine drivers pass these IDs to `snd_soc_dai_set_sysclk()`, and `spdif.c` maps them to the `CLKCTL_MCLK_EXT` bit.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by Samsung SMDK S/PDIF machine driver and Samsung S/PDIF controller driver.

## Risks And Edge Cases
The include guard is defined as `__FILE__`, an unusual but functioning pattern. Constants must stay synchronized with `spdif_set_sysclk()`.

## Test Signals
Compile coverage and SMDK S/PDIF sysclk calls for internal MCLK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/samsung/spdif.h -->
