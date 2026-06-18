# Research Group: subset-b-006519

This grouped report covers the MT8183 register definition header and the MT8186 ASoC AFE clock, GPIO, control, PCM, audsys-clock, ADDA, and hostless files in source order. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-reg.h

## Purpose

`mt8183-reg.h` is the MT8183 audio front end register map and bitfield catalog. It has no executable control flow; its purpose is to give the MT8183 ASoC drivers stable symbolic names for MMIO offsets, register maximums, IRQ status masks, mux input/output bit indexes, and register-field shift/mask pairs.

## Important APIs, Types, and Data

The public surface is entirely preprocessor definitions. The first block defines register offsets for audio top gates, AFE core control, I2S, PCM, TDM, ADDA, MTKAIF, ASRC, gain, sidetone, sine generator, connection matrix, memif base/current/end pointers, MSB address extensions, IRQ counters/status/clear registers, and debug/monitor registers. `AFE_MAX_REGISTER` is set to `AFE_GENERAL2_ASRC_2CH_CON13`, and `AFE_IRQ_STATUS_BITS` covers the 13 MCU IRQ status bits used by the MT8183 driver.

The second block defines field triplets such as `*_SFT`, `*_MASK`, and `*_MASK_SFT`. These are consumed by `regmap_update_bits()` and table-driven structures in MT8183 code. High-use groups include `AFE_DAC_CON0/1/2` memif enable, mono, and mode fields; `AFE_MEMIF_HD_MODE`, `AFE_MEMIF_HDALIGN`, `AFE_MEMIF_MSB`, `AFE_MEMIF_MINLEN/MAXLEN/PBUF_SIZE`; `AFE_IRQ_MCU_CON0/1/2` and `AFE_IRQ_MCU_CLR`; ADDA and MTKAIF fields; and PCM/TDM/I2S format and enable fields.

## Control Flow and State

There are no functions, allocation, locks, or persistent variables. Runtime state lives in hardware registers addressed by these macros and in driver structures that include this header. The correctness contract is static: offset constants must match the SoC register layout, and field masks must match hardware bit positions.

## Dependencies and Integration Points

This header is included by MT8183 AFE, clock, ADDA, I2S, PCM, and TDM implementation files. It also indirectly defines the register vocabulary for regmap volatile checks, memif metadata tables, DAPM route controls, IRQ handling, runtime suspend/resume register programming, and ALSA hw_params paths.

## Risks

The file has no type safety. A wrong shift, mask, or offset compiles cleanly and can misprogram hardware, corrupt DMA pointers, break interrupt acknowledgement, or route audio through the wrong connection matrix endpoint. Some macro names are reused across I2S register groups, so including code must be careful to use the intended register-specific field. Because `AFE_MAX_REGISTER` bounds regmap access/cache coverage, extending the register map without updating it would hide later registers from regmap.

## Test Signals

Build coverage should catch missing macro names but not semantic offset mistakes. Runtime test signals are ASoC card probe, regmap initialization, successful playback/capture on DL/VUL/AWB paths, IRQ period callbacks, suspend/resume with regcache sync, I2S/PCM/TDM loopback, ADDA/MTKAIF capture/playback, and debugfs/regmap traces confirming writes hit expected offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/Makefile

## Purpose

This Kbuild file assembles the MT8186 ASoC platform driver object and the MT8186 machine-driver object. It determines which MT8186 audio implementation files are linked when the relevant kernel configuration symbols are enabled.

## Important APIs, Types, and Data

`snd-soc-mt8186-afe-y` lists the component objects for the platform AFE driver: PCM/probe, audsys clock provider, AFE clock orchestration, GPIO, ADDA, common controls, I2S, hardware gain, PCM DAI, SRC, hostless, TDM, miscellaneous controls, and MT6366 helpers. `obj-$(CONFIG_SND_SOC_MT8186)` links those objects into `snd-soc-mt8186-afe.o`. `obj-$(CONFIG_SND_SOC_MT8186_MT6366)` links the separate `mt8186-mt6366.o` machine driver.

## Control Flow and State

There is no runtime flow. The build-time order affects link composition but not constructor order; platform registration still comes from the C files' module/platform-driver declarations.

## Dependencies and Integration Points

This file integrates with the kernel sound SoC Kbuild hierarchy and with Kconfig symbols. It must stay synchronized with registration callbacks in `mt8186-afe-pcm.c` and exported helpers declared in MT8186 headers.

## Risks

Omitting an object can create undefined symbols or silently remove DAI/control registration. Adding a new DAI implementation without updating this list leaves the code unbuilt even if headers compile elsewhere. The MT6366 common helper being included in the AFE object means codec-board helper dependencies must remain compatible with platform-driver builds.

## Test Signals

Primary validation is `CONFIG_SND_SOC_MT8186=y/m` and `CONFIG_SND_SOC_MT8186_MT6366=y/m` kernel builds. Link errors, missing module aliases, or a probed AFE component lacking expected DAIs are direct signals that this Makefile is out of sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.c

## Purpose

`mt8186-afe-clk.c` is the MT8186 AFE clock consumer/orchestration layer. It obtains common clock framework handles, registers local audsys gate clocks, enables and disables audio infrastructure clocks, selects APLL parents, controls APLL tuner registers, and provides MCLK helpers for I2S and TDM users.

## Important APIs, Types, and Functions

The `aud_clks[CLK_NUM]` table maps clock IDs from `mt8186-afe-clk.h` to device-tree/clkdev names. `mt8186_init_clock()` registers audsys gate clocks, allocates `afe_priv->clk`, performs `devm_clk_get()` for every ID, and looks up `apmixedsys`, `topckgen`, and `infracfg` syscon regmaps. `mt8186_afe_enable_clock()` and `mt8186_afe_disable_clock()` manage the core clock sequence: infra audio, 26 MHz MTKAIF clock, top audio mux, audio internal bus mux, audio high-speed mux, and AFE gate. `mt8186_afe_enable_cgs()`/`disable_cgs()` enable the BCLK/ASRC/TDM clock gates from `CLK_I2S1_BCLK` through `CLK_ETDM_OUT1_BCLK`.

`mt8186_apll1_enable()` and `mt8186_apll2_enable()` set mux parents, enable 22.5792 MHz or 24.576 MHz paths, program `AFE_APLL*_TUNER_CFG`, and set `AFE_HD_ENGEN_ENABLE`. The matching disable functions clear those hardware bits and return muxes to `CLK_CLK26M`. `mt8186_get_apll_by_rate()` chooses APLL2 for rates divisible by 8000 and APLL1 otherwise. `mt8186_mck_enable()` selects the right APLL parent for an I2S/TDM master-clock mux, enables the divider, and sets the requested rate.

## Control Flow and State

Probe calls `mt8186_init_clock()` before regmap initialization. Runtime resume calls `mt8186_afe_enable_clock()` followed by `mt8186_afe_enable_cgs()`, and runtime suspend reverses that through `mt8186_afe_disable_cgs()` and `mt8186_afe_disable_clock()`. Clock handles and syscon regmaps persist in `struct mt8186_afe_private`. APLL and MCLK helpers are invoked by DAPM clock supplies and DAI hw_params code elsewhere.

## Dependencies and Integration Points

The file depends on Linux CCF, regmap/syscon, `mt8186-audsys-clk.c`, register macros from `mt8186-reg.h`, and the private state in `mt8186-afe-common.h`. Its clock-name strings must match both audsys registered gates and device-tree clock providers. ASoC DAPM clock supplies such as `aud_dac_clk` rely on these clocks being registered and discoverable.

## Risks

Several error paths return after enabling an earlier clock without fully unwinding muxes or prepared parents, especially inside APLL mux setup and MCLK setup. `mt8186_init_clock()` logs missing clocks and stores `NULL`; later helpers dereference clock slots without null checks, so missing DT/clkdev entries can become crashes rather than probe failures. `mt8186_get_apll_by_name()` defaults to APLL2 for every non-APLL1 name, so bad names are not rejected. MCLK IDs are not bounds checked before indexing `mck_div`.

## Test Signals

Useful signals include AFE probe with all `devm_clk_get()` entries present, runtime PM cycles without clock leak warnings, DAPM playback/capture paths enabling the expected audsys gates, 44.1 kHz paths selecting APLL1 and 48 kHz-family paths selecting APLL2, and I2S/TDM MCLK output rate measurements. Failure signatures are `clk_prepare_enable`/`clk_set_parent` errors, missing clock-provider names, or suspend/resume hangs around AFE enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.h

## Purpose

This header defines the MT8186 AFE clock IDs, APLL names, and clock-control APIs used by MT8186 DAI and platform-driver code.

## Important APIs, Types, and Data

`PERI_BUS_DCM_CTRL` gives the infracfg offset used during runtime resume. `APLL1_W_NAME` and `APLL2_W_NAME` are string labels used in DAPM routes. The APLL enum identifies `MT8186_APLL1` and `MT8186_APLL2`. The large clock enum indexes `afe_priv->clk` and includes audsys gates, infra clocks, top muxes, APLL roots, I2S/TDM master-clock selectors, APLL divider clocks, and `CLK_CLK26M`.

The exported prototypes include core clock init, CG enable/disable, runtime clock enable/disable, APLL enable/disable helpers, APLL selection helpers, audio internal bus parent selection, and MCLK enable/disable.

## Control Flow and State

The header holds no state. Its enum ordering is state-critical because implementation tables in `mt8186-afe-clk.c` use these values as array indexes. `CLK_NUM` sizes the private clock-handle array.

## Dependencies and Integration Points

It forward-declares `struct mtk_base_afe` and is included by AFE PCM, ADDA, and other DAI files that need to control clocks. The enum must stay aligned with `aud_clks[CLK_NUM]` and with clock IDs expected by the local audsys gate provider.

## Risks

Changing enum order breaks all array-indexed clock lookup. Adding a clock without extending `aud_clks[]` or the DT clock graph can cause null clock pointers or missing gate registration. The comment that MCK helpers will be replaced by CCF indicates a transitional API with higher maintenance risk.

## Test Signals

Build failures catch missing declarations, but runtime probe and DAPM clock-supply activation are the meaningful tests. Inspect logs for every clock name being acquired and test MCLK users after any enum/table change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-common.h

## Purpose

`mt8186-afe-common.h` is the central MT8186 AFE contract shared by the platform driver, clock code, control helpers, and DAI implementations. It defines memif IDs, DAI IDs, IRQ IDs, APLL/MTKAIF enums, common stream aliases, private runtime state, and registration/control prototypes.

## Important APIs, Types, and Data

The first enum assigns `MT8186_MEMIF_*` IDs for playback and capture DMA engines and then continues into DAI IDs such as ADDA, AP DMIC, I2S, HW gain, SRC, PCM, TDM, and hostless paths. Aliases such as `MT8186_RECORD_MEMIF`, `MT8186_PRIMARY_MEMIF`, and `MT8186_BARGEIN_MEMIF` identify policy-level stream roles. `MT8186_IRQ_0` through `MT8186_IRQ_26` index IRQ metadata. MTKAIF protocol constants and ADDA gain constants are shared with ADDA setup code. MCLK IDs identify I2S/TDM master-clock outputs.

`struct mt8186_afe_private` stores clock handles, clkdev lookups, syscon regmaps, per-memif IRQ counter overrides, debug/control values, xrun assertions, DAI on/private data arrays, MTKAIF calibration/protocol fields, DMIC and loopback state, and MCLK rates.

Function prototypes expose DAI registration callbacks, misc-control registration, rate transforms, I2S sharing, and DAI-private allocation.

## Control Flow and State

The header defines no flow, but its IDs drive almost every runtime table in this directory. `mt8186_afe_pcm_dev_probe()` allocates `struct mt8186_afe_private`; DAI register functions attach per-DAI private blocks into `dai_priv`; ALSA controls mutate fields such as `irq_cnt`, `xrun_assert`, and `mtkaif_dmic`; runtime clock code populates `clk`, `lookup`, and syscon pointers.

## Dependencies and Integration Points

It includes ALSA SoC, Linux list/regmap, `mt8186-reg.h`, and the MediaTek base AFE API. Every MT8186 DAI implementation relies on these IDs being stable and matching the DAI-driver arrays, memif metadata, DAPM routes, GPIO selection switch, and IRQ usage table.

## Risks

The single combined enum means inserting a memif or DAI in the middle changes numeric IDs and breaks table indexes unless all arrays are updated. `dai_priv` is a `void *` array, so mismatched IDs or shared private blocks can cause type confusion. State fields are generally not protected by dedicated locks beyond the external ALSA/control paths, so changes should respect existing call contexts.

## Test Signals

Validation should include probing all DAI registration callbacks, checking `afe->num_dai_drivers`, opening each named FE/BE stream, exercising controls that mutate private state, and verifying DAPM routes resolve with the intended DAI IDs. Compiler warnings for missing enum cases in switch statements are useful after adding IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-control.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-control.c

## Purpose

This file provides MT8186 helper logic for converting ALSA sample rates into hardware field encodings and for allocating per-DAI private data blocks.

## Important APIs, Types, and Functions

Local enums define hardware encodings for general AFE sample rates, PCM rates, TDM rates, and TDM relatch rates. `mt8186_general_rate_transform()` maps standard rates from 8 kHz through 384 kHz, including 11.025/22.05/44.1-family and 352.8 kHz, to general AFE codes. `tdm_rate_transform()` and `pcm_rate_transform()` provide DAI-specific encoding sets. `mt8186_tdm_relatch_rate_transform()` encodes relatch rates. `mt8186_rate_transform()` dispatches to PCM, TDM, or general mapping based on `aud_blk`. `mt8186_dai_set_priv()` devm-allocates a private block, optionally copies initial data into it, and stores it in `afe_priv->dai_priv[id]`.

## Control Flow and State

Rate transforms are pure switch functions except for logging invalid inputs. Invalid rates fall back to a 48 kHz code rather than returning an error. `mt8186_dai_set_priv()` mutates persistent per-device private state and relies on devm lifetime.

## Dependencies and Integration Points

The helpers are declared in `mt8186-afe-common.h` and used by memif prepare/trigger, ADDA/PCM/TDM/SRC style hw_params paths, and DAI registration code. They depend on `dev_err()` for diagnostics and on valid MT8186 DAI IDs.

## Risks

Fallback-to-48 kHz can mask unsupported-rate bugs and program a stream with the wrong hardware code. `mt8186_dai_set_priv()` does not bounds-check `id`, so callers must pass IDs within `MT8186_DAI_NUM`. It also overwrites `dai_priv[id]` without freeing or detecting an existing allocation, although current registration paths call it once per DAI.

## Test Signals

Unit-like coverage can compare all advertised DAI rates against transform outputs. Runtime signals are successful hw_params for PCM, TDM, ADDA, memif, and SRC paths at all supported rates, plus logs for invalid-rate fallbacks during negative testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.c

## Purpose

`mt8186-afe-gpio.c` manages MT8186 audio pinctrl states for ADDA, I2S, TDM, and PCM pins. DAPM events and DAI code call it to switch external audio pins between active and inactive states.

## Important APIs, Types, and Functions

The private `enum mt8186_afe_gpio` enumerates every on/off pinctrl state: ADDA MOSI/MISO clocks and data, I2S0-3, TDM, and PCM. `struct audio_gpio_attr` stores a state name, preparation flag, and `pinctrl_state *`. `aud_gpios[]` maps enum entries to device-tree pinctrl state names. `mt8186_afe_gpio_init()` gets the device pinctrl, looks up each state, marks available states prepared, and initializes supported DAI pins to disabled states. `mt8186_afe_gpio_request()` is the exported switch entry point. It serializes with `gpio_request_mutex`, maps DAI ID plus uplink flag to a pinctrl state, and calls `mt8186_afe_gpio_select()`.

## Control Flow and State

Initialization stores a global `aud_pinctrl` pointer and persistent state descriptors in `aud_gpios[]`. Request flow is `mt8186_afe_gpio_request()` -> ADDA-specific helper or generic state select -> `pinctrl_select_state()`. ADDA toggles clock and data pins in an ordered sequence, with different MOSI/MISO paths for downlink and uplink.

## Dependencies and Integration Points

This file depends on Linux pinctrl and DAI IDs from `mt8186-afe-common.h`. ADDA DAPM events call it before/after playback and capture. I2S, TDM, and PCM DAI implementations use the same request API. Device tree must provide pinctrl state names that match `aud_gpios[]`.

## Risks

`aud_pinctrl` and `aud_gpios[]` are global, so multiple MT8186 AFE instances would share state. Missing pinctrl states are logged at debug level and only fail later if requested. `mt8186_afe_gpio_init()` calls `mt8186_afe_gpio_request()` during initialization even for states that may not exist, intentionally tolerating optional pins but making failures easy to overlook. Header comments mention mt6833, which is cosmetic but can confuse maintenance.

## Test Signals

Probe should show successful pinctrl lookup for expected board states. Runtime testing should verify pin transitions with ADDA playback/capture, each I2S bus, TDM, and PCM paths. Missing or misspelled device-tree state names surface as `gpio type ... not prepared` debug logs and silent audio pin inactivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.h

## Purpose

This header exposes the MT8186 audio GPIO/pinctrl initialization and request API to DAI implementation files.

## Important APIs, Types, and Data

It forward-declares `struct mtk_base_afe` and declares `mt8186_afe_gpio_init(struct device *dev)` plus `mt8186_afe_gpio_request(struct device *dev, bool enable, int dai, int uplink)`. The `dai` argument uses `MT8186_DAI_*` IDs, and `uplink` distinguishes ADDA capture from playback pin groups.

## Control Flow and State

The header has no state. Its functions are implemented in `mt8186-afe-gpio.c`, where global pinctrl state and a mutex are maintained.

## Dependencies and Integration Points

Consumers need Linux `struct device` and boolean definitions through their includes. ADDA, I2S, PCM, and TDM code call the request function in DAPM events or DAI lifecycle hooks.

## Risks

The API accepts raw integer DAI IDs, so invalid IDs are only detected at runtime. The misleading file comment names mt6833 while the include guard and symbols are MT8186-specific.

## Test Signals

Compile coverage verifies function declarations. Runtime validation is board-specific pinctrl activation through the implementation file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-pcm.c

## Purpose

`mt8186-afe-pcm.c` is the main MT8186 AFE platform driver. It defines FE memif DAIs, ALSA PCM operations, controls, DAPM widgets/routes for memory interfaces and channel merge, memif and IRQ metadata tables, regmap caching policy, IRQ handling, runtime PM, and the platform probe path.

## Important APIs, Types, and Functions

`mt8186_afe_hardware` sets PCM constraints and formats. FE DAI ops include `mt8186_fe_startup()`, `shutdown()`, `hw_params()`, `hw_free()`, `prepare()`, and `trigger()`. Startup binds the substream to the memif, sets hardware constraints, and acquires a dynamic IRQ only if a memif has no constant IRQ. Trigger enables/disables memif hardware, configures IRQ counter/fs fields, optionally delays small-latency capture before IRQ enable, and clears pending IRQs on stop.

Control callbacks expose `Audio IRQ1 CNT`, `Audio IRQ2 CNT`, and `record_xrun_assert`, storing values in `afe_priv->irq_cnt` and `xrun_assert`. DAPM widgets and routes describe UL1-UL8 capture mixers, UL5 channel-merge (`CM1_EN`) and mux paths, hostless UL virtual inputs, and routing from ADDA, I2S, PCM, connsys I2S, SRC, and gain blocks.

`memif_data[MT8186_MEMIF_NUM]` maps every memif to base/current/end registers, MSB registers, fs/mono/quad/enable/HD/align/pbuf/minlen fields. `irq_data[MT8186_IRQ_NUM]` maps all 27 IRQs to counter, fs, enable, and clear registers. `memif_irq_usage[]` gives the current fixed memif-to-IRQ assignment. `mt8186_is_volatile_reg()` marks clock-controlled, current-pointer, monitor/debug, IRQ, tuner, and other hardware-changing registers volatile for regmap. `mt8186_afe_irq_handler()` reads enabled MCU IRQ status, calls `snd_pcm_period_elapsed()` for memifs whose IRQ bit fired, then clears status.

`mt8186_afe_runtime_suspend()` disables AFE, waits for `AFE_DAC_MON`, clears IRQs twice, resets sinegen, makes regmap cache-only/dirty, disables CGs, and disables clocks. Resume enables clocks/CGs, syncs regcache, enables DCM, programs CPU HD alignment and 24-bit connection registers, and turns AFE on. Probe allocates `mtk_base_afe` and `mt8186_afe_private`, handles reserved-memory fallback, maps MMIO, initializes clocks, allocates memif/IRQ arrays, requests IRQ, registers all sub-DAIs through `dai_register_cbs[]`, resets audiosys, bootstraps runtime PM for regmap defaults, and registers the ASoC component.

## Control Flow and State

The persistent driver state is `struct mtk_base_afe` plus `struct mt8186_afe_private`. Memif state tracks substreams and IRQ usage. Controls persist IRQ counter overrides and xrun debug behavior until stream shutdown resets them. Runtime PM keeps register state in a flat regcache while power is off, except volatile registers. Probe is the only platform registration path and publishes the driver for `compatible = "mediatek,mt8186-sound"`.

## Dependencies and Integration Points

The file integrates Linux platform devices, DMA masks, reserved memory, reset control, IRQ, runtime PM, regmap, ALSA SoC components, MediaTek common AFE helpers, and all MT8186 DAI registration modules. It uses clock helpers from `mt8186-afe-clk.c`, GPIO APIs, interconnection bit indexes, and register macros.

## Risks

The fixed `memif_irq_usage[]` has a TODO to verify each mapping; wrong mapping breaks period interrupts. `mt8186_afe_irq_handler()` returns `ret` directly on regmap read failure even though the function type is `irqreturn_t`. `enable_irq_wake()` has no matching disable in this file. Missing clock handles from `mt8186_init_clock()` may become later null dereferences. The volatile register list is large and must remain accurate, or regcache can replay stale monitor/current-pointer state or fail to restore required controls. The probe error path after `pm_runtime_resume_and_get()` is delicate and should be retested after changes.

## Test Signals

Strong signals include successful platform probe, complete DAI/component registration, `aplay`/`arecord` on all DL/UL memifs, period IRQ delivery, suspend/resume with playback/capture recovery, UL5 12-channel channel-merge paths, IRQ counter controls updating live hardware, and regmap cache sync without warnings. Build tests should include modular and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.c

## Purpose

`mt8186-audsys-clk.c` registers the MT8186 audsys clock gates that live inside the AFE register space. These gates become CCF/clkdev clocks consumed by DAPM clock supplies and by `mt8186-afe-clk.c`.

## Important APIs, Types, and Functions

`struct afe_gate` describes a gate clock ID, name, parent, register offset, bit, flags, clock ops, and gate polarity. The `GATE_AUD0/1/2` macros build entries for `AUDIO_TOP_CON0`, `AUDIO_TOP_CON1`, and `AUDIO_TOP_CON2`. `aud_clks[CLK_AUD_NR_CLK]` defines AFE, APLL 22/24 MHz, tuner, TDM, ADC/DAC, I2S BCLK, ASRC, hi-res, ADDA6, third DAC, and ETDM gate clocks.

`mt8186_audsys_clk_register()` allocates `afe_priv->lookup`, loops over the gate table, registers each gate with `clk_register_gate()` using `afe->base_addr + gate->reg`, creates a `clk_lookup` with `con_id = gate->name` and `dev_id = dev_name(afe->dev)`, stores it for cleanup, and registers `mt8186_audsys_clk_unregister()` as a devm action. The unregister action drops clkdev lookups and unregisters gates.

## Control Flow and State

The file is called from `mt8186_init_clock()` before consumer `devm_clk_get()` calls. Registered gates persist for the device lifetime and are torn down by the devm action. `afe_priv->lookup` is the cleanup ledger.

## Dependencies and Integration Points

It depends on Linux CCF, clkdev, AFE base MMIO, register offsets, and clock IDs from `mt8186-audsys-clkid.h`. The gate names must match the consumer strings in `mt8186-afe-clk.c` and DAPM `SND_SOC_DAPM_CLOCK_SUPPLY()` names.

## Risks

Registration failures are logged and skipped, but the function continues; later consumers may receive missing clocks. If `kzalloc_obj(*cl)` fails after some gates are registered, cleanup relies on the devm action only if it is reached, so this path deserves scrutiny. Gate bit polarity uses `CLK_GATE_SET_TO_DISABLE`; a wrong flag would invert clock enable behavior. Direct gate registration against AFE MMIO assumes the base address is valid and clock-register layout matches the table.

## Test Signals

Test with `CONFIG_COMMON_CLK` and MT8186 AFE probe. Check that every `aud_*` clock can be acquired by `devm_clk_get()`, DAPM clock supplies enable routes, and clock summary/debugfs shows expected prepare counts during playback/capture. Missing gate names show as `devm_clk_get ... fail` later in clock init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.h

## Purpose

This header declares the MT8186 audsys gate-clock registration entry point.

## Important APIs, Types, and Data

It exposes `int mt8186_audsys_clk_register(struct mtk_base_afe *afe);`. The implementation registers local gate clocks and clkdev lookups for AFE-internal audio gates.

## Control Flow and State

The header owns no state. The function is called during AFE clock initialization before consumer clock lookup.

## Dependencies and Integration Points

Consumers must have `struct mtk_base_afe` visible or forward-declared by included headers. `mt8186-afe-clk.c` includes this header and treats registration as part of probe setup.

## Risks

The header does not forward-declare `struct mtk_base_afe` itself, so include ordering matters. Any signature change must be synchronized with the implementation and the AFE clock init path.

## Test Signals

Build coverage catches declaration mismatch. Runtime clock acquisition in `mt8186_init_clock()` confirms registration did its job.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clkid.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clkid.h

## Purpose

This header defines numeric IDs for the MT8186 audsys gate-clock table.

## Important APIs, Types, and Data

The enum starts at `CLK_AUD_AFE` and lists gate IDs for AFE, 22/24 MHz APLL outputs, APLL tuners, TDM, ADC/DAC, DAC pre-distortion, TML, NLE, I2S1-4 BCLKs, connsys/general ASRC gates, hi-res ADC/DAC gates, ADDA6 gates, third DAC gates, ETDM input/output BCLKs, and terminates with `CLK_AUD_NR_CLK`.

## Control Flow and State

No runtime flow or data exists. The enum values index `aud_clks[]` and `afe_priv->lookup[]` in `mt8186-audsys-clk.c`.

## Dependencies and Integration Points

The IDs are consumed by audsys gate registration and must remain aligned with `CLK_AUD_NR_CLK` sizing. Names produced from these IDs are later consumed by `mt8186-afe-clk.c` through CCF lookup.

## Risks

Changing enum order or inserting IDs without updating the gate table can mismatch names, bits, and cleanup entries. The enum declaration style lacks a space after `enum`, which is harmless but nonstandard.

## Test Signals

Build catches missing IDs; runtime clock debug and full AFE probe catch table-size and gate-name mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clkid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-adda.c

## Purpose

`mt8186-dai-adda.c` implements the MT8186 ADDA and AP-DMIC DAI block. It defines DAPM controls/routes for analog/digital playback and capture, handles MTKAIF and DMIC setup, programs ADDA sample-rate/filter/SDM registers in hw_params, and registers the ADDA/AP_DMIC DAI drivers.

## Important APIs, Types, and Functions

`struct mtk_afe_adda_priv` stores current playback and capture rates, used by hi-res DAPM route predicates. `mtk_adda_dl_ch1_mix[]` and `mtk_adda_dl_ch2_mix[]` route DL memifs, ADDA UL loopback, gain, PCM capture, and SRC outputs into ADDA playback channels. `mtk_adda_ul_src_dmic()` configures DMIC mode and channel enable bits. DAPM event handlers manage GPIOs, MTKAIF protocol selection, pad top settings, calibration-based delay programming, and ADDA playback/capture pin enable/disable.

Controls include `ADDA_DL_GAIN` and `MTKAIF_DMIC Switch`; the latter persists in `afe_priv->mtkaif_dmic`. DAPM widgets include ADDA playback/capture supplies, AUD_PAD_TOP, ADDA_MTKAIF_CFG, AP_DMIC_EN, ADDA_FIFO, ADDA_UL_Mux, AP_DMIC input, and ADC/DAC clock supplies. Hi-res route predicates enable `aud_dac_hires_clk` or `aud_adc_hires_clk` only above 48 kHz.

`mtk_dai_adda_hw_params()` programs downlink input mode, upsampling, mute/gain, voice mode, predistortion reset, SDM gain/dither/auto-reset, uplink voice mode, IIR coefficients, internal ADC selection, MTKAIF RX data mode, and AP-DMIC source config. `mt8186_dai_adda_register()` adds the DAI group, controls, widgets, and routes, allocates ADDA private data, and shares that private data with AP_DMIC.

## Control Flow and State

Registration runs during AFE probe via `dai_register_cbs[]`. At stream setup, ALSA calls `hw_params()` and updates ADDA registers according to stream direction and DAI ID. DAPM powers routes and invokes event handlers around playback/capture supplies. Persistent state includes ADDA rates, MTKAIF DMIC/protocol/calibration fields in `mt8186_afe_private`, and shared ADDA/AP_DMIC private data.

## Dependencies and Integration Points

The file depends on regmap, delays, clock helpers, GPIO helpers, MT8186 interconnection IDs, common AFE definitions, and MediaTek ADDA common rate-transform helpers. It integrates with DAPM routes from memif, I2S, PCM, SRC, gain, and hostless DAIs.

## Risks

MTKAIF protocol-2 clock-phase handling relies on calibration fields being populated; missing phases log errors and skip delay programming. ADDA and AP_DMIC share one private block, so rate state can reflect the most recent stream on either DAI. GPIO requests are not fatal in DAPM event handlers; pinctrl failures can leave routes powered without pins active. Register programming uses many literal values and SoC-specific bitfields, so hardware revisions need careful audit.

## Test Signals

Exercise ADDA playback and capture at 8/16/48/96/192 kHz, AP_DMIC capture, MTKAIF DMIC switch transitions, hi-res route activation above 48 kHz, suspend/resume around active ADDA paths, and hostless loopback routes feeding ADDA. Regmap traces should show expected ADDA/MTKAIF/SDM/IIR writes during hw_params and DAPM power-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-hostless.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-hostless.c

## Purpose

`mt8186-dai-hostless.c` registers virtual/hostless DAIs and DAPM routes for internal audio paths that do not represent direct CPU memory-interface playback/capture. These paths connect ADDA loopback, FM, SRC, barge-in, hardware gain, and AAudio-style internal routes.

## Important APIs, Types, and Functions

`mt8186_hostless_hardware` defines PCM constraints for hostless streams. `mtk_dai_hostless_routes[]` connects hostless stream endpoints to existing DAPM widgets: ADDA UL to ADDA/I2S playback for loopback, connsys I2S through HW gain to ADDA/I2S for FM, SRC outputs to ADDA/I2S, I2S0 into SRC for barge-in, and HW gain 2 into SRC 2 for AAudio. `mtk_dai_hostless_startup()` applies hostless hardware constraints and requires integer periods. `mtk_dai_hostless_driver[]` defines FE hostless DAIs for LPBK, FM, SRC_1, SRC_Bargein, AAudio HW gain/SRC, and BE capture-only DAIs for UL1/UL2/UL3/UL5/UL6.

`mt8186_dai_hostless_register()` allocates an AFE sub-DAI group, adds it to `afe->sub_dais`, and attaches the hostless DAI-driver and route arrays.

## Control Flow and State

There is no direct hardware register programming in this file. Probe-time registration publishes DAI and route definitions. Runtime startup only applies ALSA constraints; actual audio routing and hardware enablement happens through the DAPM widgets and DAIs supplied by ADDA, I2S, SRC, gain, and memif files.

## Dependencies and Integration Points

The file depends on `mt8186-afe-common.h` for DAI IDs and MediaTek base AFE list structures. It integrates tightly with route names from ADDA, I2S, SRC, gain, connsys I2S, and memif DAPM definitions; route-name mismatches prevent DAPM graph construction.

## Risks

Because routes are string-based, renaming a widget or stream in another DAI file can silently break hostless paths at runtime. Hostless startup does not program rates into hardware itself, so the backing BE DAIs must receive compatible hw_params through normal ASoC routing. The comment typo "Hostelss" is harmless but should not propagate into user-visible stream names.

## Test Signals

Test DAPM graph creation with no unresolved routes, then exercise hostless loopback, FM, SRC, barge-in, and AAudio paths. `aplay`/`arecord` or machine-driver path tests should confirm constraints, route power-up, and audio movement through the corresponding hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-hostless.c -->
