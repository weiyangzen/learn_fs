# Research: subset-b-006440

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lm49453.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lm49453.c

## Purpose
`lm49453.c` is the ALSA SoC codec driver for the TI LM49453 audio codec. It exposes the codec as an I2C-backed `snd_soc_component` with five DAIs for headset, speaker, haptic, earpiece, and line-out playback, plus a capture path on the headset DAI. Most of the file is the static mixer/control/DAPM topology that maps the chip's analog inputs, digital mics, sidetone path, TDM/audio ports, DACs, output drivers, and register-backed mixer switches into ALSA controls.

## Important APIs, Types, And Functions
The private state is minimal: `struct lm49453_priv` stores only the component regmap. `lm49453_reg_defs` supplies the 8-bit register defaults used by `REGCACHE_RBTREE`. The exported kernel integration is the `i2c_driver` named `lm49453`, with `lm49453_i2c_probe()` allocating state, creating the I2C regmap, and registering `soc_component_dev_lm49453` plus the `lm49453_dai[]` array.

The main runtime DAI callbacks are `lm49453_hw_params()`, `lm49453_set_dai_fmt()`, `lm49453_set_dai_sysclk()`, and the five mute callbacks (`lm49453_hp_mute()`, `lm49453_lo_mute()`, `lm49453_ls_mute()`, `lm49453_ep_mute()`, `lm49453_ha_mute()`). `lm49453_set_bias_level()` handles power state transitions by syncing the regcache on OFF-to-STANDBY and changing the chip-enable bits in `LM49453_P0_PMC_SETUP_REG`.

## Control Flow
Probe is simple and device-managed: allocate `lm49453_priv`, initialize the I2C regmap from `lm49453_regmap_config`, then call `devm_snd_soc_register_component()`. Once a machine driver binds a DAI, ALSA calls the DAI ops. `hw_params` maps supported sample rates to ADC and DAC clock dividers: 8/16/24/32/48 kHz use 256, 11.025/22.05/44.1 kHz use 216, and 96 kHz uses 127; other rates return `-EINVAL` despite the DAI advertising a broader 8-192 kHz range. `set_fmt` programs port 1 clock-provider bits and supports I2S, DSP_A, and DSP_B. DSP modes enable mode/phase bits and choose the RX MSB shift. `set_sysclk` accepts 12.288 MHz, 19.2 MHz, 26 MHz, 48 kHz, and 32.576 kHz, but currently only updates the PLL/FLL select bit to zero for MCLK-like inputs and no-ops low-frequency inputs.

DAPM control flow is mostly declarative. The route map connects `PORT1_SDI`/`PORT2_SDI` playback sources into RX channel PGAs, then into headphone, speaker, haptic, line-out, and earpiece mixers and DACs. Capture routes analog/digital mic and ADC sources through per-port TX mixers to `PORT1_SDO`/`PORT2_SDO`. Sidetone routes ADC/DMIC sources through a sidetone mixer back into playback mixers.

## State And Persistence
The persistent hardware-facing state is in the LM49453 registers and the regmap cache. ALSA mixer settings update registers directly through SOC control macros. Bias transitions power the chip on/off through `LM49453_PMC_SETUP_CHIP_EN`; when returning from OFF, `regcache_sync()` restores cached control values. No firmware, NVM, platform data, runtime PM, or explicit suspend/resume callbacks are present.

## Dependencies And Integration Points
The driver depends on the Linux I2C, regmap, and ASoC component/DAPM/control frameworks. `lm49453.h` supplies all register addresses and bit definitions. A board or machine driver must instantiate an I2C device with ID `lm49453`, connect one or more of the named DAIs, and define external audio routes for the endpoints (`HPOUTL`, `HPOUTR`, `EPOUT`, `LSOUT*`, `LOOUT*`, `HAOUT*`, mics, AUX, and digital mic data pins).

## Risks And Notes
The advertised DAI rates include 192 kHz, but `lm49453_hw_params()` rejects anything above 96 kHz except listed rates. Register defaults contain a duplicate entry for register 85, which may be harmless but is suspicious. The route table has likely copy/paste defects: `HPR Mixer` maps `"DMIC2L Switch"` to `"DMIC2 Right"`, and `HAR Mixer` uses `"Sideton Switch"` instead of `"Sidetone Switch"`, so that route may never match its control. All DAI format programming targets audio port 1 registers, so port 2 behavior depends on static defaults or external assumptions. `lm49453_set_dai_sysclk()` accepts `clk_id` and `dir` but ignores them.

## Test Signals
Useful checks include building the codec driver with ASoC enabled, probing an I2C LM49453, verifying all ALSA controls enumerate, and using `amixer`/DAPM debugfs to confirm expected routes power up. Runtime tests should cover accepted and rejected sample rates, I2S/DSP_A/DSP_B formats, mute behavior per output DAI, OFF-to-STANDBY regcache restore, and route activation for sidetone, DMIC, ADC, port 1, and port 2 paths. The suspicious route/control spellings should be validated with DAPM route warnings or audio path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lm49453.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lm49453.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lm49453.h

## Purpose
`lm49453.h` is the register and bit-definition companion for the LM49453 codec driver. It names the page 0 and page 1 register map, important register masks, fixed programming constants for PLL/FLL/VCO setup, chip-enable states, audio-port format bits, reset/page selectors, jack-detect modes, and the single clock source constant used by the driver family.

## Important APIs, Types, And Constants
The file has no functions or structs. Its API is preprocessor definitions consumed by `lm49453.c`. Important constants include `LM49453_MAX_REGISTER`, `LM49453_PAGE_REG`, page selectors (`LM49453_PAGE0_SELECT`, `LM49453_PAGE1_SELECT`), power bits for `LM49453_P0_PMC_SETUP_REG`, mute masks for ADC/DAC DSP registers, audio-port master/slave and format bits, and jack-detect configuration values. The register names are grouped by hardware block: clocks/PLL, analog input/output stages, ADC/DAC DSP, GPIO/haptics, digital mixer, audio ports, sample-rate registers, effects/ALC, digital mics, sidetone, clipping monitors, headset detect, pull-downs, reset, and page 1 sidetone/charge-pump/DAC registers.

## Control Flow
This header does not implement control flow. It controls driver behavior indirectly by providing symbolic addresses and masks for regmap and ASoC control operations. `lm49453.c` uses these definitions to build register defaults, controls, widgets, routes, DAI callbacks, mute operations, and bias transitions.

## State And Persistence
The header models persistent hardware state as register addresses and bit masks. It does not store state itself. Page-aware definitions matter because LM49453 has at least two register pages sharing 8-bit addresses; the current driver regmap uses an 8-bit address space and page register but does not implement a regmap range/page selector, so page 1 definitions are present for future or indirect use but are not heavily exercised in the C file.

## Dependencies And Integration Points
The only include is `<linux/bitops.h>` for `BIT()`. The definitions are tightly coupled to TI LM49453 datasheet naming and to the ASoC codec implementation in `lm49453.c`. Any machine-driver or board-level logic should include this header only if it needs register-level constants; normal users interact through ALSA controls.

## Risks And Notes
Because the constants are raw register ABI, mistakes propagate directly to hardware programming. The broad `LM49453_MAX_REGISTER` value covers the whole 8-bit range but does not itself distinguish pages or read-only/write-clear registers. Fixed values such as `LM49453_FLL_REF_FREQ_VAL` and `LM49453_VCO_TARGET_VAL` are defined but not visibly used by the paired driver, suggesting incomplete PLL/FLL support or stale definitions.

## Test Signals
Compile coverage is the primary test signal for this header. Functional validation comes from the C driver successfully addressing the intended hardware registers. Additional review should compare the register map and bit masks against the LM49453 datasheet, especially page 1 definitions, audio port format masks, chip enable values, and jack-detect configuration constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lm49453.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lochnagar-sc.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lochnagar-sc.c

## Purpose
`lochnagar-sc.c` is a small ASoC component driver that models the Cirrus Logic Lochnagar board sound-card endpoints. It provides three DAIs: one line interface and two USB audio interfaces. The driver mainly supplies DAPM endpoints/routes, runtime hardware constraints, DAI format validation, and MCLK enable/disable for the line interface.

## Important APIs, Types, And Functions
`struct lochnagar_sc_priv` stores the required `mclk`. The component driver `lochnagar_sc_driver` exposes two line widgets (`Line Jack`, `USB Audio`) and routes between those widgets and the DAI streams. The DAI array `lochnagar_sc_dai[]` declares `lochnagar-line`, `lochnagar-usb1`, and `lochnagar-usb2`. `lochnagar_sc_probe()` allocates private state, obtains the `"mclk"` clock, stores drvdata, and registers the component and DAIs.

The DAI callbacks are `lochnagar_sc_startup()`, `lochnagar_sc_line_startup()`, `lochnagar_sc_line_shutdown()`, `lochnagar_sc_set_line_fmt()`, and `lochnagar_sc_set_usb_fmt()`. `lochnagar_sc_hw_rule_rate()` adds a dynamic upper bound tying sample rate to frame size so bit clock stays within `24576000 / frame_bits`.

## Control Flow
On probe, device-managed allocation and `devm_clk_get()` must succeed before registering the ASoC component. On stream startup, all DAIs get a fixed supported-rate list of 8 kHz through 192 kHz families plus a hardware rule that refines rate based on `SNDRV_PCM_HW_PARAM_FRAME_BITS`. The line DAI additionally enables `mclk` before constraints are installed and limits channels to 4 or 8. On line shutdown, `mclk` is disabled. DAI format calls require I2S with normal bit/frame polarity; the line DAI must be codec bit/frame consumer (`SND_SOC_DAIFMT_CBC_CFC`), and the USB DAIs must be provider (`SND_SOC_DAIFMT_CBP_CFP`).

## State And Persistence
Runtime state is limited to the prepared/enabled state of `mclk`; it is not reference-counted in the driver beyond ALSA startup/shutdown ordering. The component has no regmap, persistent controls, or suspend/resume hooks. ALSA's runtime constraints and DAPM graph are rebuilt from static data at registration.

## Dependencies And Integration Points
The driver depends on the platform bus, common clock framework, ASoC, and Lochnagar MFD device tree binding. It matches `cirrus,lochnagar2-soundcard` and exposes the platform alias `lochnagar-soundcard`. Machine drivers can connect the DAI names and rely on this component to enforce the Lochnagar board's channel/rate/format limitations.

## Risks And Notes
If `lochnagar_sc_line_startup()` enables `mclk` and then a later constraint call fails, it returns without disabling `mclk`, leaving a possible clock leak on rare error paths. The format validation masks out only clock-provider bits and requires exact format/polarity matches, so any machine-driver format flags outside the expected set will be rejected. The rate rule depends on `FRAME_BITS` max being meaningful when the rule runs.

## Test Signals
Build and DT binding tests should confirm the platform device probes with an `mclk`. ALSA PCM tests should verify line streams only accept 4 or 8 channels, USB streams accept 1-8 channels, unsupported rates are rejected, and high frame-bit configurations refine max rate correctly. DAI format tests should cover accepted I2S NB_NF provider/consumer combinations and rejected polarity/format variants. Clock tests should verify line startup/shutdown balances `mclk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lochnagar-sc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.c

## Purpose
`lpass-macro-common.c` provides shared helpers for Qualcomm LPASS macro codec drivers. It centralizes attachment and activation of optional power domains and stores a process-wide LPASS codec-version value used by macro drivers such as RX/TX/WSA/VA to select register layouts and feature behavior.

## Important APIs, Types, And Functions
The exported APIs are `lpass_macro_pds_init()`, `lpass_macro_pds_exit()`, `lpass_macro_set_codec_version()`, and `lpass_macro_get_codec_version()`. `lpass_macro_pds_init()` returns a `struct lpass_macro` containing attached `"macro"` and `"dcodec"` power-domain devices, or `NULL` if the device has no `power-domains` property. Version state is a static `enum lpass_codec_version` protected by `lpass_codec_mutex`.

## Control Flow
Power-domain initialization first checks device tree for `power-domains`; absence means the caller should continue without domain handles. If present, it allocates `struct lpass_macro`, attaches the `"macro"` domain, runtime-resumes it, attaches the `"dcodec"` domain, and runtime-resumes it. Each failure path unwinds only the resources already acquired. Exit performs the reverse `pm_runtime_put()` and `dev_pm_domain_detach()` operations when the handle is non-NULL. Codec-version setters/getters lock around the static global value.

## State And Persistence
The helper persists two kinds of state: per-device power-domain handles in `struct lpass_macro`, owned by the caller, and one global codec-version enum shared by all users in the kernel image. Power-domain runtime state persists until `lpass_macro_pds_exit()`. The codec version defaults to zero (`LPASS_CODEC_VERSION_UNKNOWN`) until some other code calls `lpass_macro_set_codec_version()`.

## Dependencies And Integration Points
The file depends on Linux device tree helpers, generic PM domains, runtime PM, platform device headers, and the declarations in `lpass-macro-common.h`. It exports symbols with GPL visibility for other LPASS macro modules. `lpass-rx-macro.c` uses `lpass_macro_pds_init()` during probe, registers `lpass_macro_pds_exit_action()` as a managed cleanup action, and reads `lpass_macro_get_codec_version()` to choose register defaults and strides.

## Risks And Notes
`lpass_macro_pds_exit()` assumes both `macro_pd` and `dcodec_pd` are valid when `pds` is non-NULL; callers should only pass objects returned successfully by init. The codec version is global rather than per-device, which is simple for single-codec systems but risky if multiple LPASS codec generations coexist. If no provider sets the version before a macro probes, consumers may reject probe as unsupported.

## Test Signals
Tests should cover devices with and without `power-domains`, failure injection for each attach/resume step, balanced runtime-PM puts on removal, and version set/get behavior under concurrent callers. Integration tests should verify macro drivers probe successfully only after the expected codec version has been established.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.h

## Purpose
`lpass-macro-common.h` declares shared LPASS macro flags, version enums, power-domain state, helper prototypes, and small inline helpers used by Qualcomm LPASS macro codec drivers.

## Important APIs, Types, And Constants
`LPASS_MACRO_FLAG_HAS_NPL_CLOCK` marks SoCs whose macro driver should request an NPL clock. `LPASS_MACRO_FLAG_RESET_SWR` records a SoundWire reset capability/requirement. `enum lpass_version` identifies broader LPASS platform versions, while `enum lpass_codec_version` identifies codec register-layout generations from unknown through v2.9. `struct lpass_macro` stores the `"macro"` and `"dcodec"` power-domain device pointers. The header declares the power-domain init/exit helpers and global codec-version get/set helpers implemented in `lpass-macro-common.c`.

Two inline helpers are important to users: `lpass_macro_pds_exit_action()` adapts the exit function to `devm_add_action_or_reset()`, and `lpass_macro_get_codec_version_string()` converts most known codec versions to readable strings.

## Control Flow
This header has no standalone runtime flow. Its inline cleanup action simply forwards a `void *` to `lpass_macro_pds_exit()`. The string conversion switch returns explicit strings for versions 1.0, 1.1, 1.2, 2.0, 2.1, 2.5, 2.6, 2.7, and 2.8, and falls back to `"NA"` for unknown or not-yet-listed values.

## State And Persistence
The header defines the shape of per-device power-domain state but does not allocate it. It also defines the enum values used by the global codec-version state in the C file. Since these enum values are ABI-like inside the driver family, changing order would affect every switch that persists or compares the numeric version.

## Dependencies And Integration Points
The header expects users to include kernel bit macros before or through surrounding includes; it uses `BIT()` in flag definitions. It is consumed by LPASS macro drivers such as `lpass-rx-macro.c` for flags, power-domain cleanup, and codec-version dispatch. Device match tables store the flag bits in `.data`, and probe code uses the version enum to select register maps.

## Risks And Notes
The string helper omits `LPASS_CODEC_VERSION_2_9`, returning `"NA"` even though the enum defines it. The header does not include `<linux/bitops.h>` itself, so standalone inclusion depends on prior includes for `BIT()`. The global codec-version model declared here is not per-device.

## Test Signals
Compile tests should include this header from each LPASS macro user. Functional tests should verify flag interpretation from OF match data, managed cleanup via `lpass_macro_pds_exit_action()`, and version-string output for every enum value, especially newer versions that may currently fall through to `"NA"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-rx-macro.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-rx-macro.c

## Purpose
`lpass-rx-macro.c` is the Qualcomm LPASS RX macro ASoC component driver. It controls the playback-side macro for headphone left/right and auxiliary outputs, plus echo-reference capture. The driver exposes four playback DAIs, one echo capture DAI, a large DAPM graph for RX ports/interpolators/IIR/sidetone/echo paths, version-specific register maps, software controls for companders and processing modes, and runtime power/clock management.

## Important APIs, Types, And Functions
`struct rx_macro` is the central state object. It holds component/regmap pointers, clocks (`mclk`, optional `npl`, `macro`, `dcodec`, `fsgen`), power-domain handles, codec version, version-specific RX register strides, mux selections (`rx_port_value`), active channel masks/counts per DAI, bit widths, user counts for MCLK/main path/Class-H/softclip clocks, and booleans for ear mode, headphone power mode, HD2, softclip, and AUX HPF.

The public integration is the platform driver `rx_macro_driver`, matching several `qcom,*-lpass-rx-macro` compatibles. `rx_macro_probe()` obtains clocks and optional power domains, maps MMIO, chooses version-specific defaults and register strides, creates the regmap, enables initial clocks, resets/enables the SoundWire clock block, registers the ASoC component/DAIs, enables runtime PM, and registers an output clock named `lpass-rx-mclk`. `rx_macro_remove()` disables clocks. Runtime PM callbacks switch the regmap to cache-only on suspend and restore clocks/regcache on resume.

The major DAI functions are `rx_macro_hw_params()`, `rx_macro_get_channel_map()`, and `rx_macro_digital_mute()`. The major DAPM/event functions are `rx_macro_mclk_event()`, `rx_macro_enable_main_path()`, `rx_macro_enable_mix_path()`, `rx_macro_enable_rx_path_clk()`, and `rx_macro_enable_echo()`. Processing helpers include compander coefficient loading/configuration, softclip, AUX HPF, Class-H, HD2, headphone delay LUT bypass, and IIR coefficient byte controls.

## Control Flow
Probe starts from OF match flags and the global codec version from `lpass_macro_get_codec_version()`. For versions before 2.5, RX1/RX2 registers use older offsets and strides; for 2.5 through 2.8, the driver uses newer offsets and a larger stride. It dynamically builds a combined `reg_default` array, installs it in a copied regmap config, and initializes an MMIO regmap with 16-bit registers, 32-bit values, 4-byte stride, and custom readable/writeable/volatile filters.

Component probe initializes the component regmap, applies DSM delay and DC coefficient defaults through version-aware register macros, then adds either pre-2.5 or 2.5+ volume controls and the matching `RX INT1 DEM MUX` widget. Static controls and widgets cover RX0-5 muxes, IIRs, interpolators, mix paths, echo muxes, outputs, and `RX_MCLK` supply.

At PCM setup, `rx_macro_hw_params()` maps playback sample rates through `sr_val_tbl` and writes matching PCM-rate fields on any interpolator whose mux currently consumes an active RX port for the DAI. `rx_macro_mux_put()` is the key ALSA control path for selecting which AIF drives each RX0-5 port; it updates `rx_port_value`, `active_ch_mask`, and `active_ch_cnt`, then triggers DAPM mux power updates. `rx_macro_get_channel_map()` reports RX DMA slots from the active masks or echo TX slots from echo mux registers.

DAPM power-up of an interpolator calls `rx_macro_enable_interp_clk()`, which mutes the PGA, enables DSM clock, sets HPF cutoff, optionally loads compander coefficients, enables HD2, configures LUT bypass, compander, softclip/AUX HPF, and Class-H, then increments a main-path user count. Power-down decrements the count and, when it reaches zero, disables clocks, resets the path, restores 48 kHz rate defaults, clears HPF bits, and disables the same optional processing blocks. `rx_macro_digital_mute()` uses active channel masks and current mux registers to set PGA mute and keep needed path clocks enabled.

## State And Persistence
Hardware state lives in MMIO registers mediated by regmap and DAPM. Regcache persists register values across runtime suspend; suspend marks the cache dirty/cache-only and disables `fsgen`, `npl`, and `mclk`, while resume reenables them and syncs the cache. In-memory ALSA control state includes compander enables, softclip/AUX HPF booleans, headphone modes, active AIF-to-port maps, per-DAI bit width, and clock user counts. These are not persisted outside the driver instance and must remain synchronized with DAPM events.

## Dependencies And Integration Points
The driver depends on ASoC, DAPM, regmap MMIO, platform resources, OF matching, runtime PM, common clocks, OF clock providers, and `lpass-macro-common` for power domains, flags, and codec version. It exports an `lpass-rx-mclk` clock derived from `npl` or `mclk`; SoundWire or sibling blocks can consume that clock. Machine drivers integrate through the DAI names `rx_macro_rx1` through `rx_macro_rx4` and `rx_macro_echo`, DAPM route names such as `HPHL_OUT`, `HPHR_OUT`, and `AUX_OUT`, and the RX mux controls that bind AIF playback streams to RX ports.

## Risks And Notes
Version detection is global, so an unset or wrong codec version makes probe fail or programs the wrong register offsets. Optional clock handling is uneven: `npl` is optional by match flag but some paths call `clk_set_rate()` and enable/disable it without NULL checks, relying on the clock framework tolerating NULL or on SoC flags being accurate. `rx_macro_int_dem_inp_mux_put()` can leave `look_ahead_dly_reg` uninitialized if called with an unexpected enum register. User-counted state (`main_clk_users`, `rx_mclk_users`, `softclip_clk_users`, `clsh_users`, `active_ch_cnt`) can underflow or drift if DAPM/control transitions are unbalanced; some functions clamp after detecting underflow, others do not. The sample-rate mapping defaults to zero if no table entry matches, though DAI rate masks should prevent unsupported rates. The control labels for IIR band switches appear offset (`IIR1` labels use IIR0 registers and `IIR2` labels use IIR1 registers), which may be intentional user naming but should be checked.

## Test Signals
Build tests should cover all supported compatibles and codec-version switch cases. Probe tests should validate required clocks, optional NPL behavior, power-domain attach paths, MMIO resource mapping, SoundWire reset, ASoC registration, runtime PM activation, and `lpass-rx-mclk` provider registration. ALSA tests should route each AIF to RX0-5, verify active channel maps and DMA slot reporting, run supported integer and fractional rates, exercise mute/unmute with main and mix paths, and capture echo references from all three echo muxes. DAPM/regmap tests should verify clock user counts balance, regcache sync restores state after runtime suspend, version-specific RX1/RX2 registers are used correctly, and compander/softclip/AUX HPF/Class-H/HD2/IIR controls program expected registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-rx-macro.c -->
