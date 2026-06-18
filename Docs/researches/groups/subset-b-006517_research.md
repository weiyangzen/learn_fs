# subset-b-006517 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.h

## Purpose

This header is the shared MediaTek ASoC sound-card contract used by newer machine drivers. It describes platform card data, optional SOF private data, PCM startup constraints, and the common probe/parsing helpers that bind a `snd_soc_card` to platform/codec DAI-link information.

## Important APIs, Types, and Functions

- `enum mtk_pcm_constraint_type` indexes playback, capture, and HDMI/DP constraint slots.
- `struct mtk_pcm_constraints_data` carries optional channel and rate constraint lists for startup.
- `struct mtk_platform_card_data` holds the `snd_soc_card`, jack array, PCM constraints, counts, and flags.
- `struct mtk_soundcard_pdata` exposes board-specific card name/data, SOF integration data, and an optional `soc_probe()` hook.
- `mtk_soundcard_common_playback_ops` and `mtk_soundcard_common_capture_ops` are reusable FE startup ops.
- `mtk_soundcard_startup()`, `parse_dai_link_info()`, `clean_card_reference()`, and `mtk_soundcard_common_probe()` are exported helper entry points.

## Control Flow

The header has no executable flow. Consumers supply a `platform_device` and platform data to `mtk_soundcard_common_probe()`, which is expected to parse DAI-link information, apply card references, run optional SoC-specific probing, and register the ASoC card. Runtime stream startup calls flow through common playback/capture ops into `mtk_soundcard_startup()` to enforce the selected constraint set.

## State and Persistence Behavior

The file defines in-memory card metadata only. State lives in the card data, jack data, constraints, and any SOF/private data that consumers attach. Persistence is handled by ASoC core and platform drivers, not this header.

## Dependencies and Integration Points

It depends on ALSA SoC types, platform devices, and MediaTek-specific SOF/card data declared elsewhere. It is an integration seam between machine drivers, device-tree DAI-link parsing, optional SOF support, and common stream-constraint handling.

## Risks and Edge Cases

Constraint indexes must match `MTK_CONSTRAINT_MAX`; mismatched counts can make startup access the wrong constraint slot. `card_data->card` and jack arrays are borrowed references, so lifetime must outlive probe/registration. Shared parsing helpers need strict cleanup on partial probe failures to avoid stale OF/component references.

## Test Signals

Build all MediaTek machine drivers using this header. Runtime signals are successful card registration, correct DAI-link population from DT, jack creation, and startup failures for intentionally unsupported rates/channels.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soundcard-driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/Makefile

## Purpose

This Makefile wires the MT2701 audio platform and machine drivers into Kbuild.

## Important APIs, Types, and Functions

It defines `snd-soc-mt2701-afe-y := mt2701-afe-pcm.o mt2701-afe-clock-ctrl.o`, builds that composite object under `CONFIG_SND_SOC_MT2701`, and adds machine drivers for `CONFIG_SND_SOC_MT2701_CS42448` and `CONFIG_SND_SOC_MT2701_WM8960`.

## Control Flow

There is no runtime flow. At build time, Kbuild links the PCM platform code and clock-control code into one MT2701 AFE module/object, while codec-specific machine drivers are independently selected by Kconfig.

## State and Persistence Behavior

No state is stored. The file controls which compiled objects are present in the kernel or modules.

## Dependencies and Integration Points

The platform object depends on `mt2701-afe-pcm.c` and `mt2701-afe-clock-ctrl.c`. Machine entries depend on codec drivers for CS42448/BT SCO or WM8960 being available through ASoC.

## Risks and Edge Cases

Missing one of the platform objects would break link-time references between PCM and clock helpers. Enabling a machine driver without the platform driver or matching DT nodes would build but not produce a usable sound card.

## Test Signals

Kbuild coverage with each listed Kconfig symbol verifies object names and symbol resolution. Runtime card enumeration validates the selected machine object binds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.c

## Purpose

This file implements MT2701/MT7622 AFE clock acquisition and sequencing. It obtains the base audio gates, per-I2S source/divider/MCLK/hopping/ASRC clocks, optional Bluetooth merge-interface clock, and exposes helpers used by the PCM driver's runtime PM and DAI callbacks.

## Important APIs, Types, and Functions

- `mt2701_init_clock()` gets named clocks from DT and fills `mt2701_afe_private`.
- `mt2701_afe_enable_clock()` and `mt2701_afe_disable_clock()` control global audsys gates and AFE/ASYS register enables.
- `mt2701_afe_enable_i2s()` / `mt2701_afe_disable_i2s()` enable ASRC output and per-direction I2S hopping clocks.
- `mt2701_afe_enable_mclk()` / `mt2701_afe_disable_mclk()` wrap per-I2S MCLK gates.
- `mt2701_enable_btmrg_clk()` / `mt2701_disable_btmrg_clk()` control the optional BT merge gate.
- `mt2701_mclk_configuration()` chooses an MCLK parent from the 98.304 MHz or 90.3168 MHz PLL domains and programs the divider.

## Control Flow

Probe calls `mt2701_init_clock()`. Runtime resume calls `mt2701_afe_enable_clock()`, which enables base gates in dependency order, sets `ASYS_TOP_CON_ASYS_TIMING_ON`, enables `AFE_DAC_CON0_AFE_ON`, and writes ASRC initialization values. Runtime suspend clears those register bits and disables gates in reverse-ish order. I2S startup enables MCLK, prepare configures parent/divider, and path enable activates ASRC/hopping clocks. Shutdown disables path clocks and MCLK.

## State and Persistence Behavior

Clock handles and per-I2S MCLK rates live in `mt2701_afe_private` and `mt2701_i2s_path`. Hardware state is register-backed and is reset/reprogrammed across runtime PM. The PCM driver's backup list preserves selected AFE registers around suspend.

## Dependencies and Integration Points

The file depends on Common Clock Framework, regmap, MT2701 register macros, and `struct mt2701_afe_private`. It is linked into the platform object and called by `mt2701-afe-pcm.c`.

## Risks and Edge Cases

Clock-name mismatches in DT cause probe failure, except `audio_mrgif_pd` is optional unless probe defers. `mt2701_mclk_configuration()` requires `mclk_rate` to divide one supported PLL domain; a zero or unsupported rate fails. BT merge helpers assume `mrgif_ck` is valid before use. Correct unwind order matters because partial clock enable failures otherwise leave gates active.

## Test Signals

Probe logs for all required clock names, runtime PM suspend/resume loops, I2S playback/capture at 44.1/48 kHz families, high-rate MCLK requests, and BT SCO startup/shutdown are the main signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.h

## Purpose

This header declares the MT2701 clock-control API exported from `mt2701-afe-clock-ctrl.c` to the AFE PCM/platform driver.

## Important APIs, Types, and Functions

It forward-declares `struct mtk_base_afe` and `struct mt2701_i2s_path`, then declares initialization, global enable/disable, per-I2S path clock enable/disable, MCLK enable/disable, BT merge clock control, and MCLK parent/divider configuration helpers.

## Control Flow

The header has no flow. Its declarations support the PCM probe/runtime path (`init`, runtime resume/suspend) and DAI path (`startup`, `prepare`, `shutdown`, BT merge startup/shutdown).

## State and Persistence Behavior

No state is stored here. Callers mutate `mt2701_afe_private`, `mt2701_i2s_path`, CCF clock state, and AFE registers through the declared helpers.

## Dependencies and Integration Points

It is included by `mt2701-afe-pcm.c` and implemented by `mt2701-afe-clock-ctrl.c`. The forward declarations keep include coupling low, but callers still need the common MT2701 structures from `mt2701-afe-common.h`.

## Risks and Edge Cases

The API does not encode valid I2S IDs or clock state, so callers must pass IDs validated against the SoC variant. Calling disable helpers without matching successful enables relies on CCF tolerance.

## Test Signals

Build coverage catches signature drift. Runtime I2S and BT paths validate the declared helpers are called in the right lifecycle order.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-common.h

## Purpose

This header defines the MT2701 AFE private contract: memory-interface IDs, back-end DAI IDs, IRQ IDs, base-clock IDs, PLL-domain constants, I2S path metadata, SoC variant flags, and private driver state.

## Important APIs, Types, and Functions

- `MT2701_PLL_DOMAIN_0_RATE` and `MT2701_PLL_DOMAIN_1_RATE` identify MCLK parent-rate families.
- Memif enum covers DL1-DL5, multichannel DLM, UL1-UL5, DLBT, ULBT, and IO DAI IDs for I2S and MRG BT.
- IRQ enum defines three ASYS IRQ lines.
- `enum audio_base_clock` indexes named clocks acquired in the clock driver.
- `struct mt2701_i2s_data` maps one I2S control register to ASRC FS shift/mask fields.
- `struct mt2701_i2s_path` stores path refcounts, occupation flags, clock handles, MCLK rate, and per-direction register metadata.
- `struct mt2701_soc_variants` distinguishes MT2701 from MT7622 one-heart-mode behavior.
- `struct mt2701_afe_private` is platform-private state used across PCM and clock code.

## Control Flow

There is no executable flow. The enums drive array indexes in the PCM file, and the structs are initialized at probe before DAI callbacks and runtime PM use them.

## State and Persistence Behavior

`mt2701_i2s_path.on[]`, `occupied[]`, and `mclk_rate` are in-memory state that persists while the platform device is bound. Clock handles are devm-owned. Register state is not stored here but is addressed through included `mt2701-reg.h`.

## Dependencies and Integration Points

The header includes ALSA SoC, CCF, regmap, local register definitions, and the common `mtk-base-afe` infrastructure. It is shared by clock-control, PCM platform, and machine drivers.

## Risks and Edge Cases

Enum ordering is an ABI inside the driver because memif arrays, DAI IDs, and route IDs depend on it. `MT2701_IO_*` values follow `MT2701_MEMIF_NUM`, so adding memifs can shift all IO IDs. The one-heart-mode flag changes MCLK path selection and must match the compatible data.

## Test Signals

Build all MT2701 objects and boot both `"mediatek,mt2701-audio"` and `"mediatek,mt7622-audio"` compatibles. Confirm DAI IDs, I2S counts, and MCLK selection through logs/regmap traces.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-pcm.c

## Purpose

This is the MT2701/MT7622 AFE platform driver. It registers PCM FE DAIs, I2S and BT merge BE DAIs, DAPM interconnect routes, memory-interface metadata, IRQ metadata, runtime PM hooks, and the platform driver binding for `"mediatek,mt2701-audio"` and `"mediatek,mt7622-audio"`.

## Important APIs, Types, and Functions

- `mt2701_afe_hardware` defines PCM buffer/period/format capabilities.
- `mt2701_afe_i2s_rates`, `mt2701_afe_i2s_fs()`, `mt2701_memif_fs()`, and `mt2701_irq_fs()` translate sample rates to hardware fields.
- I2S DAI ops: `mt2701_afe_i2s_startup()`, `mt2701_afe_i2s_prepare()`, `mt2701_afe_i2s_shutdown()`, and `mt2701_afe_i2s_set_sysclk()`.
- BT merge ops: `mt2701_btmrg_startup()`, `mt2701_btmrg_hw_params()`, and `mt2701_btmrg_shutdown()`.
- FE ops specialize the common MediaTek FE helpers for single DL and DLM multichannel constraints.
- `mt2701_asys_isr()` clears ASYS IRQ status and calls `snd_pcm_period_elapsed()`.
- `mt2701_afe_pcm_dev_probe()` allocates `mtk_base_afe`, memifs, IRQs, I2S paths, clocks, and registers ASoC components.

## Control Flow

Probe allocates private state, selects SoC variant data, maps the parent syscon regmap, requests the named `asys` IRQ, initializes memif/IRQ/I2S arrays, configures clock handles, enables runtime PM, then registers the common DMA platform component and the MT2701 DAI component. FE startup delegates to common code after enforcing DL/DLM exclusivity. I2S startup enables MCLK; prepare checks occupancy, programs MCLK, configures ASRC/I2S registers, resets the I2S block, and enables the path. Capture also enables the paired output path. Shutdown decrements path refcounts, disables paths when the count reaches zero, and disables MCLK. Runtime PM delegates global clock enable/disable to the clock-control file.

## State and Persistence Behavior

State is held in `mt2701_afe_private`, `mt2701_i2s_path`, `afe->memif`, and `afe->irqs`. `occupied[]` prevents simultaneous same-direction users on one I2S path; `on[]` reference-counts actual hardware enable. `mrg_enable[]` keeps BT merge clocking alive while either stream direction is active. `mt2701_afe_backup_list` identifies registers saved/restored by common suspend/resume helpers.

## Dependencies and Integration Points

The file depends on syscon parent regmap, the `asys` IRQ, the clock-control helper file, common MediaTek FE/platform helpers, ASoC DAPM/DPCM, and machine drivers that reference CPU DAI names like `PCMO0`, `PCM_multi`, `PCM0`, `I2S0`, and `MRG BT`.

## Risks and Edge Cases

I2S path counters are not explicitly locked in this file, so correctness depends on ASoC serialization. Unsupported sample rates return `-EINVAL`, but callers must propagate all `mt2701_i2s_path_enable()` failures. Capture's automatic output-path enable makes shutdown symmetry critical. BT merge only supports 8/16 kHz. DLM disables/enables agents for all single DL memifs due to hardware coupling and rejects concurrent single-DL playback.

## Test Signals

Test normal playback/capture, simultaneous capture/playback on the same I2S, DLM multichannel playback, rejection of concurrent DLM/single-DL streams, BT SCO 8/16 kHz, runtime suspend/resume, and IRQ period-elapsed delivery.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-cs42448.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-cs42448.c

## Purpose

This machine driver describes an MT2701 board using a CS42448 codec plus a BT SCO codec path. It creates DPCM FE links for multichannel playback, PCM captures, and BT streams, BE links for four I2S ports and MRG BT, card controls/widgets, a GPIO-controlled I2SIN1 mux, and DT binding logic.

## Important APIs, Types, and Functions

- `struct mt2701_cs42448_private` stores mux state and two optional GPIO selectors.
- `mt2701_cs42448_i2sin1_mux_get()` / `_set()` expose an ALSA enum control for four input selections.
- `mt2701_cs42448_fe_ops_startup()` constrains selected FEs to 48 kHz.
- `mt2701_cs42448_be_ops_hw_params()` computes MCLK as `rate * 64 * (2 or 4)` and sets CPU/codec sysclk.
- `mt2701_cs42448_dai_links[]` defines FE and BE DPCM links.
- `mt2701_cs42448_machine_probe()` resolves DT phandles, GPIOs, routing, and registers the card.

## Control Flow

Probe allocates private state, parses `mediatek,platform`, assigns that node to all platform components without names, parses `mediatek,audio-codec` for CS42448 links, parses `mediatek,audio-codec-bt-mrg` for the BT BE, parses `audio-routing`, gets optional mux GPIOs low by default, stores drvdata, and registers the card. Stream startup on 48 kHz FEs installs a rate constraint. BE `hw_params` programs matching CPU and codec MCLKs.

## State and Persistence Behavior

The mux value is stored in `priv->i2s1_in_mux` and persisted only while the card is bound. GPIO output state persists in hardware until changed or reset. DAI-link OF-node assignments are stored in static link structures during probe.

## Dependencies and Integration Points

Depends on MT2701 CPU DAI names, CS42448 codec DAI name `cs42448`, BT SCO DAI `bt-sco-pcm-wb`, DT phandles, `audio-routing`, and optional GPIO descriptors.

## Risks and Edge Cases

The mux setter updates `i2s1_in_mux` even after an invalid value warning, so invalid ALSA control values could desynchronize software intent and GPIO state. Static card/link data means repeated bind/unbind paths rely on devm cleanup and not reusing stale OF nodes incorrectly. Missing BT codec phandle fails the whole card.

## Test Signals

Check card registration, DAPM pins, mux ALSA control GPIO transitions, 48 kHz constraint enforcement, MCLK values on all I2S BEs, and BT playback/capture over MRG.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-cs42448.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-reg.h

## Purpose

This header defines MT2701 AFE register offsets and bit masks used by the platform, clock, I2S, DLM, IRQ, and BT merge paths.

## Important APIs, Types, and Functions

It maps top control registers, I2S input/output controls, connection matrix registers, ASYS IRQ registers, DAC/memif controls, DL/UL buffer base/current registers, BT DAI registers, ASRC init values, DLM packet buffer fields, and I2S control fields such as FS, reset, enable, one-heart mode, I2S mode, word length, and input phase fix.

## Control Flow

There is no executable control flow. Constants are consumed by `regmap_update_bits()` and `regmap_write()` in the PCM and clock-control files.

## State and Persistence Behavior

The header describes hardware state layout. Runtime PM and common suspend/resume code use these offsets to save/restore selected registers and reinitialize clocks/ASRC.

## Dependencies and Integration Points

It is included by `mt2701-afe-common.h` and therefore reaches the PCM and clock layers. The values must match the SoC register map and the parent syscon range.

## Risks and Edge Cases

Bitfield mistakes directly corrupt audio routing, clocking, IRQ clear, or memif enable behavior. Some connection registers are sparse (`AFE_CONN41`), so code must not assume contiguous matrix offsets. DLM channel macros do not range-check channel values.

## Test Signals

Regmap traces during playback/capture/BT/runtime PM should show writes to expected offsets. DAPM route toggles validate connection matrix bits, while IRQ tests validate `ASYS_IRQ_*` offsets and clear bits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-wm8960.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-wm8960.c

## Purpose

This machine driver registers a simple MT2701 card using WM8960 on I2S0 with one playback FE, one capture FE, and one no-PCM BE.

## Important APIs, Types, and Functions

- DAPM widgets/controls expose `Headphone` and `AMIC`.
- FE links use CPU DAIs `PCMO0` and `PCM0`.
- BE link uses CPU DAI `I2S0` and codec DAI `wm8960-hifi`.
- `mt2701_wm8960_be_ops_hw_params()` computes and sets CPU/codec MCLK.
- `mt2701_wm8960_machine_probe()` parses platform/codec phandles, audio routing, and registers the card.

## Control Flow

Probe parses `mediatek,platform`, assigns it to unnamed platform components, parses `mediatek,audio-codec`, assigns it to unnamed codec components, parses `audio-routing`, then registers the card. During BE `hw_params`, MCLK is derived from sample rate using 64 BCLK/LRCLK and a 2x or 4x MCLK/BCLK divisor.

## State and Persistence Behavior

There is no private state. Static card/link structures hold OF-node references while bound; local probe code releases parsed nodes after registration.

## Dependencies and Integration Points

Depends on MT2701 platform DAIs, WM8960 codec DAI, DT phandles, and ASoC DPCM routing. It reuses MT2701 CPU DAI sysclk support.

## Risks and Edge Cases

MCLK setup return values from `snd_soc_dai_set_sysclk()` are ignored, so clock programming failures may surface later as silent or misclocked streams. Static link structures can retain assigned nodes across unusual reprobe paths.

## Test Signals

Card registration, `audio-routing` resolution, headphone/mic DAPM switching, playback/capture at 44.1/48 kHz families, and MCLK reg/clock traces validate behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-wm8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/Makefile

## Purpose

This Makefile defines the MT6797 AFE composite platform driver and MT6351 machine driver build entries.

## Important APIs, Types, and Functions

`snd-soc-mt6797-afe-y` links `mt6797-afe-pcm.o`, `mt6797-afe-clk.o`, `mt6797-dai-pcm.o`, `mt6797-dai-hostless.o`, and `mt6797-dai-adda.o`. `CONFIG_SND_SOC_MT6797` builds the platform object, and `CONFIG_SND_SOC_MT6797_MT6351` builds the machine card.

## Control Flow

Kbuild combines sub-DAI implementation objects with the platform probe object so the registration callbacks resolve at link time.

## State and Persistence Behavior

No runtime state; it controls compiled object composition.

## Dependencies and Integration Points

The platform object depends on all sub-DAI files because `mt6797-afe-pcm.c` calls each `mt6797_dai_*_register()` callback. The machine driver depends on the platform and MT6351 codec names being present.

## Risks and Edge Cases

Dropping a sub-DAI object breaks links or removes routes expected by the MT6351 card. Enabling only the machine driver without a matching platform/codec DT stack leaves no card.

## Test Signals

Kbuild with `CONFIG_SND_SOC_MT6797=y/m` and `CONFIG_SND_SOC_MT6797_MT6351=y/m` should link cleanly; runtime should enumerate all FE/BE DAIs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.c

## Purpose

This file handles MT6797 AFE clock lookup and global clock enable/disable sequencing.

## Important APIs, Types, and Functions

- Internal clock IDs cover infra audio, infra 26 MHz, top audio mux, audio bus mux, two PLL parents, and 26 MHz parent.
- `mt6797_init_clock()` allocates `afe_priv->clk` and obtains all named clocks.
- `mt6797_afe_enable_clock()` enables infra clocks and top muxes, sets `top_mux_audio` parent to 26 MHz, and enables the audio bus mux.
- `mt6797_afe_disable_clock()` disables bus, mux, 26 MHz, and infra clocks.

## Control Flow

Probe initializes handles. Runtime resume enables clocks in dependency order; runtime suspend disables them. Error labels unwind earlier enables when later steps fail.

## State and Persistence Behavior

Clock pointers persist in `mt6797_afe_private`. Hardware clock state changes only during runtime PM or explicit callers.

## Dependencies and Integration Points

Uses Common Clock Framework and is called from `mt6797-afe-pcm.c` runtime PM and probe.

## Risks and Edge Cases

The enable error path logs failures but returns `0` after unwinding instead of the failing `ret`, which can make runtime resume/probe appear successful with clocks disabled. Parent selection is fixed to 26 MHz, so boards requiring a different parent are unsupported here.

## Test Signals

Clock failure injection should verify returned errors. Runtime PM traces should show balanced enable/disable counts. Boot logs should confirm all DT clock names are found.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.h

## Purpose

This header declares the MT6797 AFE clock-control interface.

## Important APIs, Types, and Functions

It forward-declares `struct mtk_base_afe` and exports `mt6797_init_clock()`, `mt6797_afe_enable_clock()`, and `mt6797_afe_disable_clock()`.

## Control Flow

No executable flow. The declarations support platform probe and runtime PM hooks.

## State and Persistence Behavior

No state is stored here; state resides in the platform-private clock array and CCF.

## Dependencies and Integration Points

Included by `mt6797-afe-pcm.c`, implemented by `mt6797-afe-clk.c`, and linked via the MT6797 composite object.

## Risks and Edge Cases

The API is minimal and cannot express partial clock state or validate runtime PM ordering; callers must handle return values carefully.

## Test Signals

Compile coverage and runtime PM clock traces validate the interface.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-common.h

## Purpose

This common header defines MT6797 memif IDs, DAI IDs, IRQ IDs, platform-private clock state, sample-rate transform declarations, and sub-DAI registration entry points.

## Important APIs, Types, and Functions

Memif enum covers DL1/DL2/DL3, VUL/AWB/VUL12, DAI, MOD_DAI, then DAI IDs for ADDA, PCM1, PCM2, hostless loopback, and hostless speech. IRQ enum exposes IRQ1/2/3/4/7. `struct mt6797_afe_private` stores a dynamically allocated clock pointer array. The header declares `mt6797_general_rate_transform()`, `mt6797_rate_transform()`, and three DAI registration callbacks.

## Control Flow

The platform probe uses the registration callbacks to build `afe->sub_dais`, then combines them into one DAI component. Rate-transform helpers are used by FE/IRQ setup and by DAI-specific `hw_params`.

## State and Persistence Behavior

Only the clock pointer array is defined as private state here. Memif/IRQ/DAI state is stored in common `mtk_base_afe` arrays initialized by the platform file.

## Dependencies and Integration Points

Includes ALSA SoC, Linux list/regmap, and common MediaTek base AFE infrastructure. It is shared by all MT6797 platform and sub-DAI files.

## Risks and Edge Cases

Enum ordering is critical because array indexes and DAI IDs depend on it. `MT6797_DAI_ADDA = MT6797_MEMIF_NUM` means adding memifs shifts all DAI IDs unless all users are updated.

## Test Signals

Compile all MT6797 objects and inspect registered DAI names/IDs. Stream tests on every memif and DAI validate ID alignment.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-pcm.c

## Purpose

This is the MT6797 AFE platform driver. It defines rate mappings, PCM hardware constraints, FE memif DAIs, DAPM routes for capture memory interfaces, memif/IRQ register metadata, IRQ handling, runtime PM register programming, sub-DAI combination, and platform driver binding.

## Important APIs, Types, and Functions

- `mt6797_general_rate_transform()` and `mt6797_rate_transform()` convert ALSA rates to hardware values.
- `mt6797_memif_dai_driver[]` exposes DL1-DL3, UL1-UL3, and two mono capture DAIs.
- `memif_data[]` maps base/current/end, fs, mono, enable, and HD fields for each memif.
- `irq_data[]` maps IRQ counters, fs fields, enable fields, and clear bits.
- `mt6797_afe_irq_handler()` handles enabled MCU IRQ status and calls `snd_pcm_period_elapsed()`.
- Runtime PM functions enable/disable clocks, AFE, IRQ routing, HD alignment, and 24-bit connections.
- `mt6797_afe_pcm_dev_probe()` allocates state, MMIO regmap, memifs/IRQs, requests IRQ, registers ADDA/PCM/hostless/memif sub-DAIs, combines them, and registers ASoC components.

## Control Flow

Probe initializes clocks first, maps MMIO, creates regmap, allocates memif and IRQ arrays, requests the platform IRQ, builds `afe->sub_dais` through the registration callback array, combines sub-DAIs, assigns common callbacks, enables runtime PM, and registers platform plus DAI components. Runtime resume enables clocks, routes IRQs to the MCU, sets normal/8_24 data modes, marks output connections as 24-bit, and turns on AFE. Runtime suspend clears AFE on, waits for retention to drop, clears pending IRQs, and disables clocks. ISR reads MCU enable/status, filters active bits, services memifs with substreams, and clears status.

## State and Persistence Behavior

State resides in `afe->memif`, `afe->irqs`, `afe->sub_dais`, and `mt6797_afe_private.clk`. No register backup list is configured; runtime resume reprograms key global format/IRQ/AFE state. Memif substream and IRQ usage state is managed by common FE helpers.

## Dependencies and Integration Points

Depends on MMIO resources, platform IRQ, `mt6797-reg.h`, clock helpers, ADDA/PCM/hostless sub-DAI registration, common MediaTek FE/platform helpers, and machine drivers that consume the registered DAI names.

## Risks and Edge Cases

Unsupported rates fall back to 48 kHz or 16 kHz with warnings rather than hard failure in transform helpers. Probe's PM-runtime-disabled path jumps to `err_pm_disable` with `ret` still zero after `pm_runtime_enable()` succeeds but runtime PM is unavailable. Clock enable currently risks swallowing failures through the clock file. ISR assumes `irq_usage` is valid whenever `substream` is set.

## Test Signals

Boot/probe with IRQ and MMIO resources, run playback on DL1-DL3, capture on UL and mono DAIs, test ADDA/PCM/hostless machine routes, verify period interrupts, and exercise runtime PM with regmap traces.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-adda.c

## Purpose

This file implements the MT6797 analog/digital audio ADDA DAI, including DAPM mixers, ADDA power supplies, clock supplies, sample-rate-specific playback/capture register programming, and registration into the platform sub-DAI list.

## Important APIs, Types, and Functions

- DAPM mixer controls select DL and capture sources into `ADDA_DL_CH1/CH2`.
- Supplies control `ADDA Enable`, playback/capture source enable bits, DAC/ADC clocks, and `mtkaif_26m_clk`.
- `mtk_adda_ul_event()` delays after capture power-down to satisfy a 1/fs settling requirement.
- `mtk_dai_adda_hw_params()` programs playback predistortion, DL SRC mode/gain, voice mode, and capture UL source/new-interface settings.
- `mt6797_dai_adda_register()` adds the ADDA DAI, widgets, and routes to `afe->sub_dais`.

## Control Flow

During platform probe, registration appends one sub-DAI. At stream `hw_params`, playback clears predistortion, maps rate through common ADDA helpers, selects upsampling mode, enables gain, and writes DL source registers. Capture selects internal ADC, maps rate to UL voice mode, configures new-interface registers, handles hires versus normal mode, and writes UL source config. DAPM turns supply bits on/off around active routes and delays after capture power down.

## State and Persistence Behavior

No private state is allocated. Hardware register state persists until DAPM or runtime PM changes it. Routes and widgets are static and combined into the platform component.

## Dependencies and Integration Points

Depends on `mtk-dai-adda-common.h` for rate transforms, MT6797 register/interconnection macros, regmap, and ASoC DAPM. It connects memif DL/UL streams, PCM modem DAIs, and hostless routes through ADDA endpoints.

## Risks and Edge Cases

Capture code writes `AFE_ADDA_NEWIF_CFG2` with rate-specific hires mode, then unconditionally overwrites the same field with `8 << 28`, which may defeat hires configuration. Playback gain constants are hardware-tuned magic values. DAPM route bit errors can silently connect wrong channels.

## Test Signals

Playback/capture at 8/16/32/48/96/192 kHz, DAPM power sequencing, regmap checks for DL/UL source registers, and analog loopback/hostless paths validate behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-hostless.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-hostless.c

## Purpose

This file registers MT6797 hostless DAIs for ADDA loopback and speech routing, allowing internal audio paths to run without a normal CPU memory-interface endpoint.

## Important APIs, Types, and Functions

- `mtk_dai_hostless_routes[]` connects hostless loopback and speech DL/UL streams to ADDA and PCM capture/playback widgets.
- `mtk_dai_hostless_startup()` assigns the platform PCM hardware constraints.
- `mtk_dai_hostless_driver[]` defines `Hostless LPBK DAI` and `Hostless Speech DAI`.
- `mt6797_dai_hostless_register()` appends drivers and routes to the sub-DAI list.

## Control Flow

Platform probe calls the registration helper. At stream startup, hostless DAIs simply apply `afe->mtk_afe_hardware`. DAPM route activation determines which internal ADDA/PCM paths are powered and connected.

## State and Persistence Behavior

No private state. Active route and stream state is managed by ASoC DAPM/DPCM and common PCM runtime structures.

## Dependencies and Integration Points

Depends on ADDA widgets/routes from `mt6797-dai-adda.c`, PCM widgets/routes from `mt6797-dai-pcm.c`, and machine links in `mt6797-mt6351.c`.

## Risks and Edge Cases

Because this is route-only hardware control, route-name drift between files breaks paths at runtime. Hostless DAIs advertise broad high-rate formats, but actual linked ADDA/PCM routes may be narrower.

## Test Signals

Start hostless loopback and speech streams, inspect DAPM route activation, and confirm no external CPU memif DMA is required beyond expected ALSA runtime setup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-hostless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-pcm.c

## Purpose

This file implements MT6797 modem PCM interface DAIs (`PCM 1` and `PCM 2`) with DAPM mixers/routes and hardware parameter programming for PCM interface registers.

## Important APIs, Types, and Functions

- Local enums encode PCM format, mode, sync, clock, AFIFO, BT mode, word length, and enable values.
- DAPM mixers route ADDA_UL and DL memif channels to PCM playback widgets.
- `mtk_dai_pcm_hw_params()` maps stream rate to a PCM mode and programs `PCM_INTF_CON1` or `PCM2_INTF_CON`.
- `mtk_dai_pcm_driver[]` defines symmetric playback/capture DAIs for 8/16/32/48 kHz.
- `mt6797_dai_pcm_register()` appends widgets/routes/drivers to `afe->sub_dais`.

## Control Flow

Registration occurs during platform probe. On `hw_params`, the function skips reprogramming if either playback or capture widget is already active, preserving symmetric active configuration. Otherwise it builds the PCM control word for the selected DAI and writes all fields except enable bit, which is controlled by DAPM supplies.

## State and Persistence Behavior

No private state. Hardware PCM interface configuration remains in registers while the DAI is active. Active DAPM widget flags are used as the guard against reconfiguration.

## Dependencies and Integration Points

Uses MT6797 interconnection/register macros, `mt6797_rate_transform()`, ASoC DAPM, and machine BE links named `PCM 1` and `PCM 2`.

## Risks and Edge Cases

The active-widget guard can preserve stale format if a second stream asks for a conflicting rate; symmetric flags should prevent this, but route-level behavior depends on ASoC ordering. PCM1 is configured as slave/internal modem and PCM2 has a different bit layout, so shared changes are risky.

## Test Signals

Run PCM1/PCM2 playback and capture at all four advertised rates, test simultaneous symmetric streams, and trace writes to `PCM_INTF_CON1`/`PCM2_INTF_CON`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-interconnection.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-interconnection.h

## Purpose

This header defines MT6797 AFE interconnection input indices used by DAPM mixer controls to program `AFE_CONN*` matrix bits.

## Important APIs, Types, and Functions

It assigns symbolic IDs for I2S, ADDA UL, DL1-DL3, PCM capture, gain outputs, and I2S2 channels. There are no functions or structs.

## Control Flow

No executable flow. The constants are embedded in `SOC_DAPM_SINGLE_AUTODISABLE()` controls across ADDA, PCM, and memif routes.

## State and Persistence Behavior

The header defines the bit positions for persistent connection-matrix register state. DAPM manages the actual register bits as widgets/routes activate.

## Dependencies and Integration Points

Included by MT6797 platform and DAI files. It must match the hardware connection matrix and `mt6797-reg.h` connection register offsets.

## Risks and Edge Cases

A wrong index routes audio to the wrong source or channel. The numbering is sparse and not self-validating, so generated-style updates need hardware-map verification.

## Test Signals

DAPM route tests and regmap traces should confirm intended bits are toggled for ADDA, PCM, hostless, and memif capture routes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-interconnection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-mt6351.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-mt6351.c

## Purpose

This machine driver registers an MT6797 sound card paired with the MT6351 codec. It defines DPCM FE links for playback, capture, mono capture, and hostless streams, plus BE links for the primary codec and two PCM modem interfaces.

## Important APIs, Types, and Functions

`mt6797_mt6351_dai_links[]` references CPU DAIs `DL1`, `DL2`, `DL3`, `UL1`, `UL2`, `UL3`, `UL_MONO_1`, hostless DAIs, `ADDA`, `PCM 1`, and `PCM 2`. `mt6797_mt6351_dev_probe()` parses `mediatek,platform` and `mediatek,audio-codec`, assigns OF nodes, and registers the card.

## Control Flow

Probe sets `card->dev`, parses the platform phandle and assigns it to all unnamed platform components, parses codec phandle and assigns it to all unnamed codec components, then registers the card. FEs use pre-trigger ordering; hostless and BEs ignore suspend.

## State and Persistence Behavior

No private runtime state. Static DAI-link structures hold component node assignments while the card is registered.

## Dependencies and Integration Points

Depends on the MT6797 platform DAIs, MT6351 codec DAI `mt6351-snd-codec-aif1`, DT phandles, and DPCM routing from sub-DAI files.

## Risks and Edge Cases

The codec phandle is assigned to all unnamed codec components, including dummy-codec FEs if their generated component arrays are considered unnamed; correctness depends on ASoC link macro semantics. Static link data and OF-node reuse can be fragile across reprobe. No `audio-routing` parse is present, so board-specific routing is fixed to DAI links/sub-DAI DAPM.

## Test Signals

Card registration, DAI link enumeration, playback/capture on all FEs, hostless loopback/speech, suspend behavior for ignore-suspend links, and codec BE activation validate the driver.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-mt6351.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-reg.h

## Purpose

This large register header maps the MT6797 AFE register space and bitfields for top clocks, memifs, ADDA, IRQs, connection matrices, ASRC, PCM modem interfaces, gains, and debug/monitor registers.

## Important APIs, Types, and Functions

It defines register offsets from `AUDIO_TOP_CON0` through `AFE_CBIP_SLV_DECODER_MON0`, `AFE_MAX_REGISTER`, `AFE_IRQ_STATUS_BITS`, and detailed `_SFT`, `_MASK`, and `_MASK_SFT` macros for fields consumed by platform, ADDA, PCM, and runtime PM code.

## Control Flow

No executable flow. The macros are used in regmap configuration, runtime resume/suspend, IRQ clear/status handling, memif setup, ADDA source programming, DAPM supplies, and PCM interface setup.

## State and Persistence Behavior

The file describes persistent hardware state. Some state is reprogrammed on runtime resume, while stream-specific fields remain active during a stream. Monitor/status registers are read by runtime or debug paths and should not be cached as normal state.

## Dependencies and Integration Points

Included by MT6797 platform and DAI files. It must remain consistent with `memif_data[]`, `irq_data[]`, DAPM controls, and the MMIO resource size.

## Risks and Edge Cases

Mask/shift errors are high impact because many fields are programmed through generic helpers. The header includes IRQ5 fields even the driver uses IRQ1/2/3/4/7. Sparse connection and ASRC registers make contiguous assumptions unsafe. Runtime PM relies on retention and AFE-on bits matching hardware.

## Test Signals

Compile coverage, regmap traces for memif/IRQ/ADDA/PCM writes, IRQ period tests, and comparison to the vendor register map are the strongest checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/Makefile

## Purpose

This Makefile builds the MT7986 AFE platform composite and optional WM8960 machine driver.

## Important APIs, Types, and Functions

`snd-soc-mt7986-afe-y` links `mt7986-afe-pcm.o` and `mt7986-dai-etdm.o`. `CONFIG_SND_SOC_MT7986` builds the platform object, and `CONFIG_SND_SOC_MT7986_WM8960` builds `mt7986-wm8960.o`.

## Control Flow

Kbuild links ETDM DAI support into the platform object so `mt7986_afe_pcm.c` can call `mt7986_dai_etdm_register()`.

## State and Persistence Behavior

No runtime state; only build composition.

## Dependencies and Integration Points

The platform object depends on the ETDM sub-DAI file. The machine object depends on the platform DAI names and WM8960 codec driver.

## Risks and Edge Cases

Leaving out `mt7986-dai-etdm.o` breaks the machine BE path and the platform link. Building the machine driver without platform/codec support yields no usable card.

## Test Signals

Kbuild both Kconfig symbols and boot with a matching DT card to validate object integration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-common.h

## Purpose

This header defines MT7986 AFE IDs, private platform state, rate-transform declaration, and ETDM registration entry point.

## Important APIs, Types, and Functions

Memif enum covers `DL1` and `VUL12`; `MT7986_DAI_ETDM` follows the memifs. IRQ enum exposes three IRQs. `struct mt7986_afe_private` stores bulk clocks, clock count, runtime-PM register-control bypass flag, and per-DAI private pointers. `mt7986_afe_rate_transform()` and `mt7986_dai_etdm_register()` are declared.

## Control Flow

The platform probe allocates this private structure, fills bulk clock data, uses the bypass flag during regmap initialization, and lets ETDM `set_fmt()` allocate per-DAI format state in `dai_priv`.

## State and Persistence Behavior

Bulk clocks and ETDM format state persist while the platform device is bound. `pm_runtime_bypass_reg_ctl` is a transient probe-time/runtime-PM guard that prevents register writes before regmap defaults are captured.

## Dependencies and Integration Points

Includes ALSA SoC, CCF, list/regmap, and common MediaTek base AFE. Shared by MT7986 platform, ETDM DAI, and machine driver.

## Risks and Edge Cases

`dai_priv` is indexed by DAI ID, so enum stability matters. ETDM code assumes `set_fmt()` has initialized `dai_priv[dai->id]` before `hw_params`; machine drivers must supply a valid DAI format.

## Test Signals

Compile coverage, platform probe, ETDM format negotiation, and runtime PM around regmap initialization validate this contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-pcm.c

## Purpose

This is the MT7986 AFE platform driver. It registers DL1/VUL12 memif DAIs, combines them with ETDM, sets up bulk clocks, MMIO regmap with volatile registers, IRQ metadata, runtime PM, and platform binding for `"mediatek,mt7986-afe"`.

## Important APIs, Types, and Functions

- `mt7986_afe_rate_transform()` maps ALSA rates to MT7986 hardware values.
- `mt7986_memif_dai_driver[]`, `memif_data[]`, and `irq_data[]` describe FE DAIs, memory-interface registers, and IRQ registers.
- `mt7986_is_volatile_reg()` marks current pointers, monitor registers, and IRQ status volatile.
- `mt7986_init_clock()` uses `devm_clk_bulk_get()`.
- `mt7986_afe_irq_handler()` services enabled MCU IRQs.
- Runtime PM enables/disables bulk clocks and audio top/engine registers.
- `mt7986_afe_pcm_dev_probe()` maps resources, initializes regmap under temporary clock enable, registers ETDM/memif sub-DAIs, and registers ASoC components.

## Control Flow

Probe allocates `mtk_base_afe`, sets driver data early, maps MMIO, obtains bulk clocks, enables runtime PM, temporarily bypasses register control while clocks are on to initialize regmap defaults, then allocates memif/IRQ arrays and requests IRQ. It registers ETDM first, memif second, combines sub-DAIs, assigns common callbacks, and registers platform/DAI components. Runtime resume enables clocks and audio top/engine clocks; suspend disables register clocks, clears IRQ status, and disables bulk clocks. ISR filters status by MCU enable bits and memif IRQ usage before period notifications.

## State and Persistence Behavior

Persistent state includes bulk clocks, `pm_runtime_bypass_reg_ctl`, memif/IRQ arrays, sub-DAIs, and regmap cache. Volatile current/monitor/status registers bypass cache. Resume re-enables top clocks but stream-specific memif state is handled by common FE logic.

## Dependencies and Integration Points

Depends on DT MMIO/IRQ/clocks, `mt7986-reg.h`, ETDM registration, common MediaTek FE/platform helpers, and machine links using `DL1`, `UL1`, and `ETDM`.

## Risks and Edge Cases

`pm_runtime_get_sync()` return is not checked during regmap default capture. Runtime remove disables PM and may call suspend manually. Rate transform falls back to 48 kHz with warning for unsupported rates, but advertised rates limit most invalid input. IRQ handler clears only `status_mcu`, so invalid IRQs with no matching status clear zero.

## Test Signals

Probe with regmap default capture, playback/capture through DL1/UL1, ETDM BE activation, IRQ period delivery, runtime PM cycles, and regcache/volatile behavior through debugfs are key signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-dai-etdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-dai-etdm.c

## Purpose

This file implements the MT7986 ETDM DAI used as the external audio interface, with DAPM routing between memif endpoints and ETDM pins, format negotiation, stream parameter programming, trigger control, and sub-DAI registration.

## Important APIs, Types, and Functions

- `struct mtk_dai_etdm_priv` stores BCLK/LRCLK inversion, slave mode, and wire format.
- `mt7986_etdm_rate_transform()` maps rates to ETDM-specific FS values.
- `get_etdm_wlen()` and `get_etdm_ch_fixup()` convert ALSA width/channels to hardware fields.
- `mtk_dai_etdm_startup()` / `shutdown()` gate bulk clocks and ETDM in/out top clocks.
- `mtk_dai_etdm_config()` writes ETDM IN/OUT control, relatch, clock-source, FS, and divider fields.
- `mtk_dai_etdm_set_fmt()` parses I2S/DSP_A/DSP_B, inversion, and master/slave flags.
- `mt7986_dai_etdm_register()` adds the DAI, widgets, and routes.

## Control Flow

Platform probe registers the ETDM sub-DAI. Machine-driver `dai_fmt` calls `set_fmt()`, which allocates DAI-private format state. Startup enables clocks and clears ETDM top powerdown bits. `hw_params()` accepts 8/12/16/24/32/48/96/192 kHz and configures both playback and capture sides with matching format fields. Trigger start/resume enables both ETDM IN5 and OUT5; stop/suspend disables both. Shutdown powers down ETDM top gates and disables clocks.

## State and Persistence Behavior

Format state persists in `afe_priv->dai_priv[MT7986_DAI_ETDM]` after `set_fmt()`. Hardware format/rate state persists in ETDM registers until reconfigured or suspended. No explicit locking protects repeated `set_fmt()` allocations, but devm ownership handles lifetime.

## Dependencies and Integration Points

Depends on MT7986 register fields, bitfield helpers, common AFE state, ASoC DAI format negotiation, and machine drivers that set `.dai_fmt` on the ETDM BE.

## Risks and Edge Cases

`bck_inv`, `lrck_inv`, and `slave_mode` are parsed but not currently written to ETDM inversion/master fields, so non-default formats may be accepted without effect. `hw_params()` configures both directions even for one-way streams. `set_fmt()` must run before `hw_params()` or `etdm_data` is NULL.

## Test Signals

Validate I2S playback/capture through WM8960, rejected unsupported rates such as 44.1 kHz despite advertised macro including 44.1-family rates, ETDM trigger enable bits, and behavior for inversion/master flags.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-dai-etdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-reg.h

## Purpose

This header defines MT7986 AFE register offsets and bitfields for top clocks, engine clocks, IRQs, ETDM IN/OUT, connection matrix, and DL/VUL memory interfaces.

## Important APIs, Types, and Functions

It declares offsets for IRQ control/status/clear/config registers, ETDM IN5/OUT5 controls, connection matrix registers, memif monitor/current/base/end registers with MSB support, `AFE_MAX_REGISTER`, IRQ masks, DL0/VUL0 control fields, and ETDM field macros built with `BIT()`/`GENMASK()`.

## Control Flow

No executable flow. Platform and ETDM files use these macros in regmap config, runtime PM, IRQ handling, memif data tables, DAPM controls, and ETDM parameter programming.

## State and Persistence Behavior

The header maps persistent hardware state. `mt7986-afe-pcm.c` marks current/monitor/status registers volatile to avoid caching live hardware values.

## Dependencies and Integration Points

Included by MT7986 PCM and ETDM files. Values must align with the MMIO resource and hardware programming guide.

## Risks and Edge Cases

ETDM fields use mask macros with `FIELD_PREP`; mismatched masks cause invalid packed values. `AFE_MAX_REGISTER` stops at `AFE_VUL0_CON0`, so any later register addition needs regmap range updates. 64-bit DMA address fields depend on base/end/current MSB offsets being correct.

## Test Signals

Regmap traces for runtime PM, IRQ config/clear, memif DMA setup, and ETDM format/rate setup validate the map.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-wm8960.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-wm8960.c

## Purpose

This machine driver registers an MT7986 card using WM8960 over ETDM. It defines playback/capture FE links, an ETDM-to-WM8960 BE link, DAPM endpoint controls, and DT parsing for child `platform` and `codec` nodes.

## Important APIs, Types, and Functions

- FE links use CPU DAIs `DL1` and `UL1`.
- BE link uses CPU DAI `ETDM`, codec DAI `wm8960-hifi`, and I2S normal-bitclock/normal-frame codec-bitclock/frame-clock provider format.
- `mt7986_wm8960_machine_probe()` parses `platform/sound-dai` and `codec/sound-dai`, assigns OF nodes, parses `audio-routing`, registers the card, and releases node references.

## Control Flow

Probe obtains the `platform` child, parses its first `sound-dai`, assigns it to all unnamed platform components, then obtains the `codec` child and assigns its `sound-dai` to unnamed codec components. It parses routing and registers the card. The static BE format drives ETDM `set_fmt()`.

## State and Persistence Behavior

No private state. Static link/card structures carry OF-node assignments during card lifetime. Node references are dropped after registration.

## Dependencies and Integration Points

Depends on MT7986 platform DAIs, WM8960 codec DAI, a DT graph with `platform` and `codec` child nodes, and `audio-routing`.

## Risks and Edge Cases

The driver does not set codec/CPU sysclk in `hw_params`; clocking must be covered by platform/codec defaults or DT. Assigning the same codec node to all unnamed codec components depends on DAI-link macro semantics. ETDM supports only a subset of its advertised rates in `hw_params`.

## Test Signals

Card registration from child-node DT, DAPM headphone/mic pins, ETDM `set_fmt()` execution, playback/capture, and routing parse failures are key tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-wm8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/Makefile

## Purpose

This Makefile builds the MT8173 AFE platform driver and several codec-specific machine drivers.

## Important APIs, Types, and Functions

`CONFIG_SND_SOC_MT8173` builds `mt8173-afe-pcm.o`. Machine entries build MAX98090, RT5650, RT5650+RT5514, and RT5650+RT5676 card drivers under their respective Kconfig symbols.

## Control Flow

Kbuild selects independent platform and machine objects. Machine drivers bind to the platform through DAI names and DT references at runtime.

## State and Persistence Behavior

No runtime state. It controls which object files are available.

## Dependencies and Integration Points

Depends on the MT8173 platform file and codec drivers. Machine drivers require matching DT compatible strings and routing.

## Risks and Edge Cases

Unlike newer platform composites, this platform has a single object; missing machine Kconfig symbols only removes board-card support, not the AFE itself. Machine/platform Kconfig mismatch can build a card that cannot bind.

## Test Signals

Kbuild all listed Kconfig combinations and boot DTs for each supported codec board.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-afe-common.h

## Purpose

This header defines shared MT8173 AFE IDs for memory interfaces, IO DAIs, IRQs, and clocks.

## Important APIs, Types, and Functions

Memif enum includes DL1, DL2, VUL, DAI, AWB, MOD_DAI, and HDMI, followed by IO IDs for modem PCM, PMIC, I2S, second I2S, hardware gains, merge out/in, DAIBT, and HDMI. IRQ enum gives one IRQ per memif-like stream. Clock enum lists infra/top audio gates, I2S master clocks, I2S3 bit clock, and BCK0/BCK1. There are no function declarations.

## Control Flow

No executable flow. `mt8173-afe-pcm.c` uses these enum values as DAI IDs, memif array indexes, IRQ array indexes, and clock-array indexes.

## State and Persistence Behavior

The header defines IDs only. Actual clock handles and AFE private state are in `mt8173-afe-pcm.c`.

## Dependencies and Integration Points

Includes CCF and regmap headers because the platform file's common structures need those types. Machine drivers depend indirectly on the DAI ID/name mapping created from these IDs.

## Risks and Edge Cases

Enum ordering is critical: changing memif order changes array indexes and IO DAI numeric IDs. `MT8173_AFE_IRQ_MOD_DAI` exists, but the platform file's IRQ data table line for MOD_DAI uses `MT8173_AFE_IRQ_DAI`, so maintainers should verify whether that is intentional hardware sharing or a bug.

## Test Signals

Build MT8173 platform and run stream tests for each memif/IRQ path, especially DAI vs MOD_DAI and HDMI, to validate ID alignment.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/mt8173-afe-common.h -->
