# subset-b-006502 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8997.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8997.c

Purpose: implements the ASoC codec component for the Wolfson/Cirrus WM8997, an Arizona-family audio codec exposed by a parent MFD device. The file binds the codec-facing ALSA controls, DAPM widgets/routes, DAIs, FLLs, jack support, speaker IRQ setup, and runtime PM registration around the shared Arizona helper layer.

Important APIs, types, and functions: `struct wm8997_priv` embeds `struct arizona_priv` and two `struct arizona_fll` instances. `wm8997_sysclk_ev()` wraps the common Arizona SYSCLK/DVFS clock event path and applies a revision-0 async regmap patch after SYSCLK power-up. `wm8997_set_fll()` dispatches the public component `.set_pll` ids from `wm8997.h` to `arizona_set_fll()` or `arizona_set_fll_refclk()`. `wm8997_component_probe()` initializes the component regmap, speaker support, DAPM pointer, and disables the unused HAPTICS pin. `wm8997_probe()` is the platform-driver entry point that allocates state, loads OF audio platform data, probes the jack codec device, initializes FLLs and DAIs, latches volume-update bits, enables runtime PM, initializes common Arizona services, speaker IRQs, volume limits, and registers the component/DAIs.

Control flow: the platform driver named `wm8997-codec` is created by `module_platform_driver()`. Probe obtains the parent `struct arizona`, allocates `wm8997_priv`, reads audio pdata if needed, initializes DVFS and jack support early to allow `-EPROBE_DEFER`, sets both FLL VCO multipliers, initializes both FLLs against MFD IRQs, fixes sample rate 2 and 3 to 8 kHz and 16 kHz, initializes each DAI with `arizona_init_dai()`, enables digital volume update bits, enables runtime PM, then registers the ASoC component. Runtime audio paths are then controlled by DAPM routes and controls. SYSCLK DAPM events pass through `wm8997_sysclk_ev()`, which delegates pre-power and post-power-down to `arizona_clk_ev()` and delegates DVFS handling to `arizona_dvfs_sysclk_ev()`.

State and persistence behavior: persistent runtime state is `wm8997_priv`, especially the embedded Arizona core pointer and two FLL descriptors. Most mixer/EQ/DRC/LHPF/noise gate/output settings are hardware registers cached through the parent Arizona regmap. The driver explicitly latches volume update bits in DAC volume registers. It stores `arizona->dapm` on component probe and clears it on component remove. Runtime PM is enabled at platform probe and disabled at remove or error unwind. No filesystem persistence exists.

Dependencies and integration points: depends on the MFD Arizona core (`linux/mfd/arizona/core.h`, `registers.h`) and local shared codec helpers in `arizona.h`. ALSA SoC integration uses `snd_soc_component_driver`, DAPM widgets/routes, TLV controls, `arizona_dai_ops`, and `arizona_simple_dai_ops`. It exposes five DAIs: two AIF interfaces and three SLIMbus-style simple DAIs. Machine drivers configure sysclk, FLL, jack, DAI params, and DAPM routes through ALSA SoC. Parent platform data or device tree config supplies input modes, jack, speaker, and volume-limit details through Arizona helpers.

Risks and edge cases: the revision-0 SYSCLK patch writes a fixed register sequence asynchronously and is guarded only by `arizona->rev`; any mismatch with silicon revision can break clock startup. Probe has several resource phases and must unwind jack, runtime PM, and speaker IRQs in the right order. DAPM routes contain large macro-expanded mixer graphs, so route-name drift against controls/widgets can silently break paths. FLL ids outside the four defined ids return `-EINVAL`. The driver assumes the parent MFD regmap and IRQ layout are already valid.

Test signals: compile coverage under the relevant `SND_SOC`/Arizona configs is the first signal. Runtime signals include successful `wm8997-codec` platform probe, registered AIF/SLIM DAIs in ASoC debugfs, working jack reporting via `set_jack`, no DAPM route resolution warnings, SYSCLK/FLL lock IRQ activity, speaker IRQ initialization, and playback/capture on AIF1/AIF2 plus SLIM paths at supported formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8997.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8997.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8997.h

Purpose: provides the small public/local interface header for the WM8997 codec driver. It identifies the file as an Arizona-family ASoC codec and defines the FLL ids accepted by the WM8997 component `.set_pll` callback.

Important APIs, types, and functions: includes `arizona.h` so users of this header share the common Arizona codec declarations. Defines `WM8997_FLL1`, `WM8997_FLL2`, `WM8997_FLL1_REFCLK`, and `WM8997_FLL2_REFCLK`. These ids are consumed by `wm8997_set_fll()` in `wm8997.c`.

Control flow: the header has no executable control flow. Its include guard `_WM8997_H` prevents duplicate definitions. At runtime, machine drivers or other codec setup code pass these constants to `snd_soc_component_set_pll()` or equivalent component operations; `wm8997.c` maps them to the correct `struct arizona_fll`.

State and persistence behavior: no state is stored here. The constants are compile-time ids only.

Dependencies and integration points: tightly coupled to `wm8997.c` and the shared Arizona helper layer. It also documents that WM8997 clocking follows the Arizona FLL abstraction rather than a private clock API.

Risks and edge cases: if these ids diverge from the switch in `wm8997_set_fll()`, FLL setup from machine drivers will fail with `-EINVAL`. The values are part of an in-tree driver contract and should remain stable.

Test signals: compile users of `wm8997.h`; runtime FLL configuration should select FLL1/FLL2 and their reference clocks without `-EINVAL` from the component `.set_pll` callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8997.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8998.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8998.c

Purpose: implements the ASoC codec component for the WM8998 Arizona-family codec. It registers the WM8998 mixer/control surface, DAPM graph, AIF and SLIMbus DAIs, FLL clock controls, jack support, GPIO/audio helper setup, speaker IRQ handling, and platform-driver lifecycle.

Important APIs, types, and functions: `struct wm8998_priv` holds `struct arizona_priv` plus two FLL descriptors. `wm8998_asrc_ev()` validates ASRC source rate selectors on DAPM `PRE_PMU` and rejects unsupported or illegal ASRC rate combinations before enabling ASRC widgets. `wm8998_inmux_put()` implements A/B input mux switching for IN1L, IN1R, and IN2, deriving analog/digital mode bits from `arizona->pdata.inmode[]`, updating source registers, and synchronizing DAPM mux power. `wm8998_set_fll()` maps ids from `wm8998.h` to shared FLL helpers. `wm8998_component_probe()` initializes regmap, speaker, GPIO, and DAPM state. `wm8998_probe()` handles platform allocation, OF audio pdata, jack device probing, FLL/DAI initialization, digital volume-update latching, runtime PM, common init, speaker IRQs, and component registration.

Control flow: the `wm8998-codec` platform driver probes below an Arizona MFD parent. Probe allocates codec-private state, parses audio pdata if platform data is absent, sets `core.num_inputs` to three logical inputs, probes jack support early, initializes FLL1 and FLL2, initializes all five DAIs, latches digital volume update bits, enables runtime PM, initializes common Arizona state, requests speaker IRQs, and registers the component. The component driver exposes controls and DAPM arrays. During audio routing, input mux writes both mode and source bits and DAPM updates mux power. ASRC widgets call `wm8998_asrc_ev()` before power-up, ensuring selected sample-rate registers are legal.

State and persistence behavior: persistent state lives in `wm8998_priv`, the parent Arizona core, the two FLLs, and hardware registers cached by the parent regmap. Input mode state is not owned by this file; it reads platform/device-tree mode data from `arizona->pdata.inmode`. `arizona->dapm` is set while the component is live and cleared on remove. Runtime PM is enabled during platform probe and disabled on remove/error. No on-disk persistence exists.

Dependencies and integration points: depends on the Arizona MFD core, local `arizona.h`, and ALSA SoC component/DAPM/control APIs. It exposes AIF1, AIF2, AIF3, SLIM1, and SLIM2 DAIs using `arizona_dai_ops` and `arizona_simple_dai_ops`. It integrates with jack reporting through `arizona_jack_set_jack`, GPIO initialization through `arizona_init_gpio()`, speaker power/IRQ helpers, and shared EQ/DRC/LHPF/ISRC/ASRC route macros.

Risks and edge cases: ASRC validation rejects route power-up if rate selectors do not match expected system or async sample-rate registers; this is correct but can surface as DAPM path enable failure. `wm8998_inmux_put()` relies on platform input-mode array indexing, so incorrect pdata can program the wrong DMIC/single-ended mode. The DAPM graph is large and macro-heavy, making name mismatches or missing widgets easy to introduce. Error unwinding must free speaker IRQs, disable PM, and remove jack support in order. FLL id misuse returns `-EINVAL`.

Test signals: successful probe should register `wm8998-codec` and five DAIs. ALSA controls should include IN muxes, ASRC rate, EQ/DRC/LHPF, output, noise-gate, AEC, SPDIF, and mixer controls. Runtime tests should exercise AIF1/AIF2/AIF3 playback/capture, SLIM routes, ASRC routes with valid/invalid rate selectors, input A/B mux changes for analog and DMIC modes, jack detection, speaker IRQs, and suspend/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8998.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8998.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8998.h

Purpose: provides the local/public header for the WM8998 ASoC codec driver and defines the FLL selector ids used by its component clock API.

Important APIs, types, and functions: includes `arizona.h` and defines `WM8998_FLL1`, `WM8998_FLL2`, `WM8998_FLL1_REFCLK`, and `WM8998_FLL2_REFCLK`. These constants are the accepted ids in `wm8998_set_fll()`.

Control flow: no executable logic. Machine drivers pass these constants through the ALSA SoC component PLL path; `wm8998.c` switches on them to configure the selected Arizona FLL or its reference clock.

State and persistence behavior: no runtime state. The file contributes compile-time constants only.

Dependencies and integration points: couples the WM8998 codec driver to the shared Arizona codec support header and to machine-driver clock configuration.

Risks and edge cases: changing these numeric ids would break existing machine-driver code or cause `.set_pll` to reject requests. The header has no validation by itself; validation occurs in `wm8998.c`.

Test signals: compile inclusion and runtime FLL setup through `snd_soc_component_set_pll()` should reach FLL1/FLL2 or reference-clock setup successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8998.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9081.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9081.c

Purpose: implements an I2C/regmap ALSA SoC codec driver for the WM9081 mono output codec. The driver exposes analog input mix, DAC playback, DRC, EQ/ReTune Mobile, lineout, speaker, FLL/sysclk, DAI format, TDM slot, mute, bias, DAPM, and I2C registration behavior.

Important APIs, types, and functions: `struct wm9081_priv` stores the regmap, clock source/rates, sample-rate and BCLK state, master/slave state, FLL parameters, TDM width, and `struct wm9081_pdata`. `wm9081_volatile_register()` and `wm9081_readable_register()` define regmap policy. `wm9081_reset()` writes the software reset id. `speaker_mode_get()`/`speaker_mode_put()` expose Class D/Class AB speaker mode while blocking mode changes when the speaker is enabled. `fll_factors()` calculates FLL dividers, FRATIO, OUTDIV, N, and K. `wm9081_set_fll()` safely disables CLK_SYS/FLL, applies factors, then re-enables. `configure_clock()` chooses MCLK or FLL-derived SYSCLK. `clk_sys_event()` configures/disables clocks around DAPM power. `wm9081_set_bias_level()` handles VMID/bias ramp and regcache-only off state. `wm9081_set_dai_fmt()`, `wm9081_hw_params()`, `wm9081_mute()`, `wm9081_set_sysclk()`, and `wm9081_set_tdm_slot()` implement the DAI contract. `wm9081_i2c_probe()` performs chip-id validation, reset, pdata copy, IRQ polarity setup, cache-only setup, and component registration.

Control flow: I2C probe allocates state, initializes an 8-bit-register/16-bit-value regmap, reads `WM9081_SOFTWARE_RESET` expecting `0x9081`, resets the chip, copies platform data, configures IRQ polarity/output style, switches regmap to cache-only, and registers one playback DAI. Component probe enables zero-cross defaults and adds direct EQ controls only when no ReTune Mobile configs are supplied. DAI setup first records sysclk source through `.set_sysclk`; `.set_fmt` programs master/slave, data format, and clock inversions; `.hw_params` computes BCLK and SYSCLK, selects register-encoded sample-rate and clock ratios, optionally writes the closest ReTune Mobile EQ profile, then programs clock and AIF registers. DAPM powers `CLK_SYS` through `clk_sys_event()`, which calls `configure_clock()` before enabling and disables the FLL after power-down.

State and persistence behavior: driver state persists in `wm9081_priv` for clock configuration, FLL input/output rates, current sample rate, computed BCLK, master mode, TDM width, and platform ReTune/IRQ data. Hardware register state is cached by regmap using `REGCACHE_MAPLE`. Bias-off sets `regcache_cache_only(true)`, while cold standby clears cache-only and syncs. FLL state is cached in `fll_fref`/`fll_fout` to skip no-op reconfiguration. There is no filesystem persistence.

Dependencies and integration points: depends on I2C, regmap, ALSA SoC controls/DAPM/DAI APIs, local register definitions in `wm9081.h`, and platform definitions in `include/sound/wm9081.h`. Machine drivers must provide MCLK/sysclk setup and can provide ReTune Mobile tables and IRQ polarity data. The codec reports a stereo-capable playback DAI even though the physical output is mono.

Risks and edge cases: FLL math has explicit bounds: Fref must be scaled to 13.5 MHz or less, Fvco target must reach at least 90 MHz, and FRATIO must match a fixed table. Unsupported clock, DAI format, inversion, sample width, TDM slot count, or TDM mask returns `-EINVAL`. `speaker_mode_put()` refuses mode changes while `SPK_ENA` is set; userspace can see this as a mixer-control failure. `configure_clock()` falls back to raw MCLK if FLL setup fails in FLL mode, so machine-driver clock assumptions should be tested. Regcache-only off-state requires bias transitions to sync before live access.

Test signals: successful I2C probe with chip id `0x9081`, reset, and ASoC registration. Runtime tests should cover MCLK-only and FLL-MCLK sysclk modes, 8 kHz through 96 kHz playback, 16/20/24/32-bit formats, I2S/left/right/DSP modes, master/slave clock directions, TDM slot masks, mute toggling, ReTune profile selection by sample rate, speaker mode protection while enabled, and suspend/bias transitions that force cache-only and cache sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9081.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9081.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9081.h

Purpose: defines the WM9081 codec register map, bit masks, shifts, and widths used by `wm9081.c`. It is a local hardware contract for the driver, not an algorithmic implementation.

Important APIs, types, and functions: includes `sound/soc.h`, defines sysclk source ids `WM9081_SYSCLK_MCLK` and `WM9081_SYSCLK_FLL_MCLK`, enumerates register addresses from `WM9081_SOFTWARE_RESET` through `WM9081_EQ_20`, and defines `WM9081_REGISTER_COUNT` and `WM9081_MAX_REGISTER`. Field definitions cover lineout/speaker volume and mute bits, VMID and bias controls, analog mixer inputs, anti-pop controls, power-management bits, clock controls, FLL controls, audio-interface controls, interrupt status/masks/polarity, DAC digital volume/mute/deemphasis, DRC parameters, write-sequencer bits, SPI/MW slave bits, and EQ coefficient/gain registers.

Control flow: none. The C driver uses these constants in regmap defaults, readable/volatile register filters, DAPM widgets, mixer controls, bias transitions, FLL programming, DAI format setup, TDM setup, mute, and EQ/ReTune writes.

State and persistence behavior: no runtime state is held in the header. The defined addresses and masks describe the hardware state that regmap caches and that `wm9081.c` writes during probe, bias changes, DAPM events, and DAI configuration.

Dependencies and integration points: used directly by `wm9081.c` and indirectly by any local code that needs WM9081 register names. It complements `include/sound/wm9081.h`, which supplies platform data structures such as ReTune Mobile settings and IRQ configuration.

Risks and edge cases: generated bitfield definitions must match the silicon datasheet. Incorrect masks or shifts can corrupt adjacent hardware fields, especially shared clock/FLL, audio-interface, DRC, and EQ registers. The sysclk ids must remain in sync with `wm9081_set_sysclk()` and `configure_clock()`.

Test signals: compile-time use across all register references; runtime success is demonstrated by readable-register filtering, correct regcache defaults, FLL/DAI programming, mixer controls, DAPM power paths, and EQ/DRC controls working without invalid register or bitfield behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9081.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9090.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9090.c

Purpose: implements an I2C/regmap ALSA SoC component driver for WM9090/WM9093 analog output hardware. It has no DAI of its own; instead it exposes analog line-input controls, mixers, headphone/speaker outputs, AGC platform configuration, DAPM routing, bias sequencing, and DC-servo headphone startup/shutdown handling.

Important APIs, types, and functions: `struct wm9090_priv` stores platform data and the regmap. `wm9090_volatile()` and `wm9090_readable()` define register access policy. `wait_for_dc_servo()` polls DC-servo readback until both channels report calibration complete or a 1000 ms timeout. `hp_ev()` sequences headphone power: enables charge pump, enables HPOUT channels, delays, starts DC servo startup calibration, waits, removes shorts, and reverses the sequence on power-down. `wm9090_add_controls()` registers DAPM widgets/routes and controls, selecting single-ended or differential input routes based on platform data and loading AGC registers when enabled. `wm9090_set_bias_level()` controls VMID and bias transitions and syncs regcache on OFF-to-STANDBY. `wm9090_probe()` sets default volume-update and zero-cross bits, enables TOCLK, and installs controls. `wm9090_i2c_probe()` validates device id `0x9093`, resets the part, copies platform data, and registers a component with no DAIs.

Control flow: I2C probe initializes regmap, verifies the reset register, resets the chip, copies optional platform data, stores private data, and registers the ASoC component. Component probe configures cached defaults and calls `wm9090_add_controls()`. That function always adds the base analog routes and controls, then conditionally adds IN1/IN2 single-ended controls or differential routes. During DAPM operation, the HP PGA widget calls `hp_ev()` on power-up and power-down, and bias transitions control VMID/bias independently of the headphone event sequence.

State and persistence behavior: persistent driver state is the platform data and the regmap cache. `REGCACHE_MAPLE` stores hardware register values between bias states. OFF-to-STANDBY performs `regcache_sync()`. The DC servo state is hardware runtime state only; this driver does not preserve servo calibration across path changes because analog routes may alter offsets. AGC values are loaded from platform data during control setup and remain in registers/cache.

Dependencies and integration points: depends on I2C, regmap, ALSA SoC component/control/DAPM APIs, platform definitions in `include/sound/wm9090.h`, and local register definitions in `wm9090.h`. It integrates into a larger sound card as an auxiliary analog component rather than a PCM endpoint. Machine/platform data decides whether IN1/IN2 are differential and whether AGC is enabled/configured.

Risks and edge cases: `wait_for_dc_servo()` can block roughly one second and only logs on timeout, so audio path startup may proceed with imperfect calibration. The driver expects chip id `0x9093` even for ids table entries `wm9090` and `wm9093`. Input topology depends on platform data; wrong `lin1_diff`/`lin2_diff` values expose incorrect controls/routes. Because no DAIs are registered, card integration must route audio through another component and use DAPM/control links correctly. Bias and HP event sequencing are pop/click sensitive.

Test signals: successful I2C probe, reset, and component registration. Runtime signals include visible base controls and conditional IN1B/IN2B controls for single-ended configurations, correct DAPM routes for differential/single-ended inputs, headphone path power-up with DC-servo completion logs, speaker route operation through SPKMIX/SPKOUT, AGC register programming when platform data enables it, and regcache sync after bias OFF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9090.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9090.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9090.h

Purpose: defines the local WM9090/WM9093 hardware register map and bitfield constants consumed by `wm9090.c`.

Important APIs, types, and functions: enumerates register addresses for software reset, power management, clocking, line controls, line input volume registers, headphone and speaker volumes, output and speaker mixers, anti-pop, write sequencer, charge pump, DC servo, analog headphone controls, and AGC controls. Defines `WM9090_REGISTER_COUNT` and `WM9090_MAX_REGISTER`. Field definitions include power enables, thermal shutdown, input enables, TOCLK, line input differential/clamp bits, volume/mute/ZC/VU bits, mixer switches and attenuations, VMID/anti-pop, write sequencer fields, charge pump enable, DC servo trigger/readback bits, headphone short/output delay controls, and AGC thresholds/attack/decay/min-gain fields.

Control flow: no executable logic. `wm9090.c` uses these definitions for regmap defaults, readable/volatile register filters, ALSA controls, DAPM widgets/routes, headphone power sequencing, DC-servo polling, platform AGC loading, and bias control.

State and persistence behavior: no state is stored in the header. It names hardware state that is cached in the component regmap and updated by DAPM, bias, probe, and controls.

Dependencies and integration points: private to the codec driver directory and paired with `wm9090.c`; platform data lives in `include/sound/wm9090.h`. The register constants define the hardware contract for analog output and auxiliary component integration.

Risks and edge cases: masks and shifts touch power, charge-pump, DC-servo, and anti-pop bits where incorrect values can cause audible artifacts or failed output enable. Duplicate generic names such as `WM9090_IN1_VU` and `WM9090_HPOUT1_VU` appear for multiple registers, so users must pair them with the correct register address.

Test signals: compile all `wm9090.c` references; runtime verification comes from correct regmap access filtering, default register cache values, DAPM-controlled output sequencing, DC-servo status polling, and mixer/control behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9090.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9705.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9705.c

Purpose: implements ALSA SoC support for the WM9705 AC97 codec. It registers AC97 mixer controls, DAPM widgets/routes, two AC97 DAIs, AC97 rate programming, suspend/resume reset handling, and platform-driver component registration. It supports both an MFD-provided WM97xx AC97/regmap instance and the legacy ASoC AC97 bus path.

Important APIs, types, and functions: `struct wm9705_priv` stores the `struct snd_ac97 *` and optional `struct wm97xx_platform_data *`. `wm9705_regmap_config` defines a 16-bit AC97 regmap with stride 2, AC97 volatile policy, defaults, and maple cache. `wm9705_snd_ac97_controls` exposes standard AC97 playback/capture controls. DAPM widgets/routes model mic, capture selectors, DACs, ADCs, headphone/mono/line outputs, and legacy analog inputs. `ac97_prepare()` enables variable rate audio in `AC97_EXTENDED_STATUS` and writes either playback DAC or capture ADC sample rate from the PCM runtime. `wm9705_soc_suspend()` writes `AC97_POWERDOWN` with cache bypass. `wm9705_soc_resume()` performs an AC97 reset/warm reset with vendor-id validation and syncs the component cache. `wm9705_soc_probe()` obtains or creates the AC97 device/regmap and initializes the component regmap. `wm9705_probe()` allocates state, records optional MFD platform data, and registers the component and DAIs.

Control flow: the platform driver `wm9705-codec` registers one component with two DAIs: `wm9705-hifi` playback/capture and `wm9705-aux` mono playback. Component probe chooses the backing AC97 path. If MFD platform data exists, it reuses the supplied AC97 object and regmap. Otherwise, when `CONFIG_SND_SOC_AC97_BUS` is enabled, it creates an AC97 component and initializes an AC97 regmap; if neither path is possible it returns `-ENXIO`. On stream prepare, the DAI operation writes the requested runtime rate to the appropriate AC97 rate register. On PM resume, the codec is reset and the cache is restored.

State and persistence behavior: state is limited to the AC97 device pointer and optional MFD platform data pointer. Hardware register values are cached by regmap/component cache. Suspend bypasses the cache to force `AC97_POWERDOWN` directly; resume resets AC97 and syncs cached settings. There is no filesystem persistence.

Dependencies and integration points: depends on Linux AC97 support (`sound/ac97_codec.h`, `sound/ac97/codec.h`, `sound/ac97/compat.h`), WM97xx MFD platform data, regmap AC97 helpers, and ALSA SoC component/DAI/DAPM APIs. Machine drivers route audio through the AC97 DAI names and controls. The vendor id is `0x574d4c05` with a full mask.

Risks and edge cases: if neither MFD platform data nor `CONFIG_SND_SOC_AC97_BUS` is available, component probe fails with `-ENXIO`. `wm9705_soc_probe()` calls `snd_soc_component_set_drvdata(component, wm9705->ac97)`, replacing the component drvdata from the private struct with the AC97 pointer; later remove calls `snd_soc_component_get_drvdata()` as `struct wm9705_priv *`, which is a risky pattern unless surrounding ASoC behavior preserves the original pointer elsewhere. DAPM routes simulate missing hardware input-output switches using input mute controls, so mixer mutes affect power routing semantics. Resume requires AC97 reset success and vendor-id match before cache sync.

Test signals: successful platform probe and component probe through MFD and legacy AC97-bus paths, valid vendor-id reset, ALSA controls for AC97 playback/capture, DAPM route resolution, stream prepare writing playback and capture rates across supported 8 kHz to 48 kHz values, suspend writes to `AC97_POWERDOWN`, and resume reset plus cache sync restores mixer settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9705.c -->
