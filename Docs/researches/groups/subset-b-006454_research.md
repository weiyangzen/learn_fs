# Research: subset-b-006454

This grouped report covers Realtek ASoC amplifier codec drivers under `sources/distributed-fs/ceph-client/sound/soc/codecs`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1011.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1011.c

## Purpose
`rt1011.c` is the Linux ASoC component and I2C driver for the Realtek RT1011 smart amplifier. It exposes one playback DAI, a register cache for a 16-bit register/16-bit value device, DAPM-controlled power sequencing, PLL/sysclk programming, TDM slot routing, user controls for mono source and advanced coefficients, and speaker R0 calibration support.

## Important APIs, Types, And Functions
The driver is centered on `struct rt1011_priv` from `rt1011.h`, which stores the `snd_soc_component`, `regmap`, calibration work item, BQ/DRC coefficient arrays, clock state, PLL state, calibrated R0 data, receiver/speaker mode, and I2S reference selection. `rt1011_i2c_probe()` allocates private state, parses `realtek,temperature_calib` and `realtek,r0_calib`, creates the regmap, validates `RT1011_DEVICE_ID`, initializes `cali_work`, and registers `soc_component_dev_rt1011` plus `rt1011_dai`. `rt1011_probe()` schedules calibration work and allocates five `RT1011_BQ_DRC_NUM` coefficient buffers. `rt1011_remove()` and shutdown reset the part.

The ASoC DAI ops are `rt1011_hw_params()`, `rt1011_set_dai_fmt()`, and `rt1011_set_tdm_slot()`. Component-level clock callbacks are `rt1011_set_component_sysclk()` and `rt1011_set_component_pll()`, using `rl6231_pll_calc()`. Mixer controls include `DIN Source`, TDM source/location selectors, `RECV SPK Mode`, five `AdvanceMode ...` BQ/DRC controls, `R0 Calibration`, `R0 Load Mode`, `R0 Temperature`, and `I2S Reference`.

## Control Flow
Probe reads the device ID and registers the component. Component probe schedules `rt1011_calibration_work()`, which performs startup calibration or property-driven R0 loading, writes the init register list, applies optional temperature/R0 properties, and leaves ADC settings initialized. Playback setup validates sample width, frame size, and sysclk/lrck ratio; if the current sysclk is unsupported, it force-programs a BCLK-sourced PLL at 256fs. DAI format accepts codec bit/frame slave mode, normal or inverted BCLK, and I2S/left-justified/DSP A/DSP B formats. TDM setup requires exactly one RX slot for the DAC source and one or two TX slots for ADC data, then programs slot count, slot width, mono left/right routing, ADCDAT locations, and ADCDAT pin direction.

DAPM routes `AIF1RX` through `DAC` to `SPO`, with many supplies for LDO, PLL, bias, sense, mixer, boost, and temperature paths. `rt1011_dac_event()` enables speaker temperature protection on post-power-up and clears it on pre-power-down. Bias OFF writes a three-register reset sequence.

## State And Persistence
Register state is cached with `REGCACHE_MAPLE`; suspend enables cache-only mode and marks the cache dirty, while resume syncs it back. Calibration deliberately bypasses the cache while directly programming hardware, then marks and syncs the cache. Runtime state in `rt1011_priv` persists across ASoC callbacks but is not stored outside memory. Device properties can seed calibration values at boot. BQ/DRC arrays hold user-supplied coefficient lists and mirror writes to validated hardware registers.

## Dependencies And Integration Points
The file depends on ASoC core, DAPM, regmap I2C, ACPI/OF matching, and Realtek helper `rl6231_pll_calc()`. It binds to I2C ID `rt1011`, OF compatible `realtek,rt1011`, and ACPI HID `10EC1011`. Machine drivers interact through standard ASoC DAI and component callbacks. Userspace can interact through ALSA mixer controls, including unusually broad coefficient-setting controls.

## Risks
Calibration is long and timing-sensitive, uses many magic register writes, and runs as asynchronous work after component probe. Controls such as `RECV SPK Mode`, `R0 Calibration`, and `R0 Load Mode` only take effect when DAPM bias is OFF, so userspace writes during active playback may appear accepted but not change hardware. `rt1011_bq_drc_coeff_put()` casts integer control storage to a coefficient struct array, so ABI size and 32-bit versus 64-bit layout are important; the header adds a reserved field under `CONFIG_64BIT`. TDM validation rejects many layouts and assumes paired stereo source slots. The forced PLL fallback in `hw_params()` can hide bad machine-driver clock setup.

## Test Signals
Useful tests include I2C probe with valid and invalid ID values, suspend/resume register cache sync, DAI format rejection paths, sample widths 8/16/20/24/32, PLL fallback when sysclk is not an exact 256fs multiple, TDM masks with zero, multiple, odd, and adjacent slots, mixer control round trips for BQ/DRC arrays, and R0 calibration/property-load behavior. Runtime logs from calibration report EFUSE offsets and computed R0 resistance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1011.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1011.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1011.h

## Purpose
`rt1011.h` defines the RT1011 register map, bit fields, clock source enumerations, coefficient-control ABI structures, and private driver state consumed by `rt1011.c`.

## Important APIs, Types, And Definitions
The header declares `RT1011_DEVICE_ID_NUM`, register addresses from reset/clock/PLL blocks through audio interface, power, protection, BQ/DRC, class-D, calibration, EFUSE, and max-register definitions. It defines bit masks and shifts for sysclk source selection, PLL input selection, PLL M/N/K fields, MCLK detection, DAC/ADC clock enables, TDM master/slave mode, TDM/I2S format and word length, BCLK inversion, channel counts, ADCDAT direction/location, mixer mutes, power supplies, speaker protection, receiver/speaker mode, class-D impedance gain, and sine generator enable.

The public-ish internal enums describe system clock sources (`MCLK`, `BCLK`, `PLL1`, `RCCLK`), PLL sources, DAI IDs, I2S reference modes, and advanced coefficient banks. `struct rt1011_bq_drc_params` is the ALSA control payload element containing a register and value, with a 64-bit-only reserved field to preserve layout expectations. `struct rt1011_priv` is the driver state object used by the C file.

## Control Flow
The header has no executable control flow, but its constants directly drive all driver branches: `rt1011_set_component_sysclk()` selects `RT1011_FS_SYS_PRE_*`, PLL setup writes `RT1011_PLL1_*` and `RT1011_PLL2_*`, TDM setup uses the slot/channel masks, DAPM supply widgets use the power bit positions, and calibration writes the STP, EFUSE, reciprocal, and class-D registers.

## State And Persistence
The persistent state contract is `struct rt1011_priv`: component/regmap pointers, calibration work, allocated coefficient banks, current sysclk/lrck/bclk and PLL settings, selected coefficient set, current R0 register value, calibration completion flag, device-property calibration values, receiver/speaker mode, and I2S reference mode. The register definitions also establish what can be cached by the regmap and restored after suspend.

## Dependencies And Integration Points
This header is private to the RT1011 codec driver and includes no Linux headers itself. It is tightly coupled to `rt1011.c` and indirectly to ASoC, regmap, and `rl6231` PLL helper usage. The `struct rt1011_bq_drc_params` layout is visible through ALSA control payload handling, so userspace tooling that writes advanced coefficient controls depends on it.

## Risks
The file contains a very large hardware register contract with many magic values referenced from the C file; incorrect masks or shifts can silently corrupt unrelated hardware fields. The BQ/DRC payload count is fixed at 128 entries and the conditional 64-bit padding is ABI-sensitive. Some comments and naming are sparse, so adding new controls or calibration writes requires checking the datasheet or existing driver patterns.

## Test Signals
Compile coverage catches missing masks, enum names, and struct members. Runtime validation should focus on each C-file user: PLL register encoding, TDM slot masks, DAPM power-bit toggles, coefficient payload transfer on 32-bit and 64-bit builds, and max-register/readable/volatile ranges matching real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1011.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015.c

## Purpose
`rt1015.c` is the ASoC I2C codec driver for the Realtek RT1015 smart amplifier. It provides one playback DAI, regmap-backed register defaults, power and boost controls, DAPM sequencing for DAC and class-D startup, PLL/sysclk programming, TDM slot mapping, and optional platform/device-property power-up delay.

## Important APIs, Types, And Functions
`struct rt1015_priv` from `rt1015.h` stores component/regmap pointers, platform data, clock and PLL state, boost mode, bypass-boost state, DAC-in-use state, and calibration completion. `rt1015_i2c_probe()` selects default or provided platform data, reads `realtek,power-up-delay-ms`, initializes regmap, validates either accepted device ID, and registers `soc_component_dev_rt1015`. The component exports controls for DAC volume/mute, `Boost Mode`, `Mono LR Select`, `Bypass Boost`, and DAC output-volume update behavior.

DAI operations are `rt1015_hw_params()`, `rt1015_set_dai_fmt()`, and `rt1015_set_tdm_slot()`. Component callbacks `rt1015_set_component_sysclk()` and `rt1015_set_component_pll()` program clock-tree and PLL registers using `rl6231_pll_calc()`. `rt1015_calibrate()` performs a bypass-boost calibration/power-state sequence under DAPM lock and regcache bypass.

## Control Flow
Probe validates hardware and registers the component. Component probe only records the component pointer. On playback, `hw_params()` requires a supported sysclk/lrck ratio from `rl6231_get_clk_info()`, rejects unsupported frame sizes and widths, then programs I2S word length and clock divider. DAI format supports codec master or slave clocking, normal or inverted BCLK, and I2S/left-justified/DSP A/DSP B formats. TDM slot setup accepts 2/4/6/8 slots, 16/20/24/32-bit slot widths, exactly one RX source slot, and no TX slots.

DAPM routes `AIFRX` to `DAC`, optional PLL, `Amp Drv`, and `SPO`. `r1015_dac_event()` marks the DAC busy, writes different power/reset sequences depending on bypass-boost mode, and clears busy state on power-down. `rt1015_amp_drv_event()` enables BCLK and class-D DC detection before power-up and sleeps for the configured power-up delay after power-up.

## State And Persistence
The regmap uses `REGCACHE_RBTREE`; suspend switches to cache-only and marks dirty, and resume syncs the cache. If bypass calibration had been completed, resume reruns `rt1015_calibrate()`. `boost_mode`, `bypass_boost`, `dac_is_used`, and `cali_done` live in memory. Device-tree or ACPI properties only set initial platform data, not persistent hardware state.

## Dependencies And Integration Points
The driver depends on ASoC, regmap I2C, ACPI/OF, `sound/rt1015.h` platform data, and `rl6231` helpers. It binds to I2C `rt1015`, OF `realtek,rt1015`, and ACPI `10EC1015`. Machine drivers configure clocks and TDM through normal ASoC DAI/component callbacks; userspace controls boost and mono selection via ALSA mixer controls.

## Risks
`Bypass Boost` returns `-EBUSY` if the DAC is active, so control timing matters. Calibration and DAPM event sequences use hardware-specific magic values and sleeps. `hw_params()` fails rather than falling back if sysclk is not a supported ratio, unlike RT1011/RT1305. TDM input assumes stereo content starts at slot 0/2/4/6 and rejects any TX mask. The driver accepts two device IDs, so board identification must be checked carefully.

## Test Signals
Test ID validation for both supported IDs, device-property power-up delay, boost-mode register writes, bypass-boost calibration once-per-boot and after resume, DAPM busy behavior, unsupported sysclk ratios, all supported sample widths, DAI format combinations, and TDM RX masks for valid even/odd slot selections and invalid multi-slot cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015.h

## Purpose
`rt1015.h` is the private register and state header for the RT1015 amplifier driver. It maps the RT1015 register space, defines bit masks used by clock, TDM, DAC, boost, and power logic, and declares the driver's private state structure.

## Important APIs, Types, And Definitions
The header includes `<sound/rt1015.h>` for platform data, then defines two accepted device IDs, register addresses for clock/PLL, dummy registers, ID/status, DAC/ADC, TDM, mixer, protection, boost, power, class-D, and smart-boost timing. Bit definitions cover sysclk source, PLL source and M/N/K fields, BCLK detection, version ID values, mono channel selection, DAC volume/mute fields, TDM master/slave, I2S/TDM format and word length, TDM slot counts, smart-boost auto/fixed/bypass flags, power supplies, DC detection, and class-D power.

Enums define system clock sources, PLL sources, DAI IDs, chip revisions, boost modes (`BYPASS`, `ADAPTIVE`, `FIXED_ADAPTIVE`), bypass-boost states, and hardware versions. `struct rt1015_priv` carries all driver runtime state: component, platform data, regmap, sysclk, PLL settings, boost mode, bypass-boost flag, DAC usage flag, and calibration flag.

## Control Flow
The header does not execute code. It defines the constants used by `rt1015.c` control flow: `rt1015_set_component_sysclk()` uses `RT1015_CLK_SYS_PRE_SEL_*`, PLL programming uses `RT1015_PLL_*`, DAI format and TDM slot setup use the I2S/TDM masks, boost controls update `RT1015_SMART_BST_CTRL1`, and DAPM events toggle reset, power, boost, and detection registers.

## State And Persistence
`struct rt1015_priv` establishes the state persisted across callbacks. Register defaults in the C file use these addresses and masks for regcache restoration. Platform data persists in memory and includes the power-up delay used by DAPM.

## Dependencies And Integration Points
The header is coupled to `rt1015.c`, the ASoC component model, regmap, and the external `sound/rt1015.h` platform-data ABI. Machine drivers and firmware nodes influence behavior indirectly through platform data and ASoC DAI callbacks.

## Risks
The device ID value `0x1011` overlaps with another Realtek part naming convention, and the C file accepts both `0x1011` and `0x1015`. Many fields are packed masks with minimal comments; wrong shifts affect power sequencing and TDM routing. The boost-mode enums are exposed through ALSA controls by numeric values, so reordering them would change control semantics.

## Test Signals
Build coverage validates symbol use. Runtime tests should exercise bit fields indirectly: sysclk/PLL setup, boost-mode register updates, DAC mute/volume controls, mono channel selection, TDM slot mapping, DC detection enable, and platform-data power-up delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015p.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015p.c

## Purpose
`rt1015p.c` is a minimal ASoC platform driver for RT1015P/RT1019P-style speaker amplifiers controlled through a shutdown (`sdb`) GPIO rather than an I2C register map. It exposes a fixed-rate playback DAI and DAPM events that assert/deassert the GPIO around playback.

## Important APIs, Types, And Functions
`struct rt1015p_priv` stores the optional `sdb` GPIO descriptor and a `calib_done` flag. `rt1015p_platform_probe()` allocates state, gets optional `sdb` as `GPIOD_OUT_LOW`, stores driver data, and registers `rt1015p_component_driver` with `rt1015p_dai_driver`. `rt1015p_sdb_event()` is the main behavior: on `SND_SOC_DAPM_PRE_PMU` it drives the GPIO high and waits 300 ms only the first time after boot or suspend; on `SND_SOC_DAPM_POST_PMD` it drives the GPIO low. `rt1015p_suspend()` clears `calib_done`.

## Control Flow
The platform device binds through OF or ACPI. ASoC routes `HiFi Playback` into an `SDB` output driver widget and then to `Speaker`. When playback powers the route, DAPM calls `rt1015p_sdb_event()` before power-up to bring the amp out of shutdown. When playback powers down, the GPIO is lowered after power-down. If no GPIO is described, the event is a no-op while the DAI still exists.

## State And Persistence
There is no register cache and no hardware state persisted by the driver beyond the GPIO level. `calib_done` avoids repeating the initial 300 ms delay until suspend resets it. The GPIO is requested low at probe and driven low after playback.

## Dependencies And Integration Points
The driver depends on platform devices, GPIO descriptors, ASoC component/DAI/DAPM APIs, OF compatibles `realtek,rt1015p` and `realtek,rt1019p`, and ACPI IDs `RTL1015` and `RTL1019`. Machine drivers see a DAI named `HiFi` with `HiFi Playback`, one or two channels, 48 kHz only, and S24/S32 formats.

## Risks
The driver assumes the amplifier only needs GPIO shutdown control and a first-power-up delay. Boards without an `sdb` GPIO silently skip control, which can be valid or can hide firmware description errors. Supported PCM parameters are narrow: 48 kHz and S24/S32 only. There is no remove/shutdown callback to force the GPIO low except through devm cleanup and DAPM powerdown.

## Test Signals
Test binding through both OF compatibles/ACPI IDs, optional and present GPIO paths, first playback delay, repeated playback without delay, suspend clearing `calib_done`, and machine-driver compatibility with the fixed DAI name and stream parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1015p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1016.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1016.c

## Purpose
`rt1016.c` is the ASoC I2C driver for the Realtek RT1016 stereo amplifier. It provides a playback DAI, register defaults plus a small probe-time patch, DAC volume/mute controls, DAPM-managed power supplies, data-swap muxing, sysclk/PLL programming, and I2S format setup.

## Important APIs, Types, And Functions
`struct rt1016_priv` stores component/regmap pointers, clock and PLL state, lrck/bclk, and master-mode status. `rt1016_i2c_probe()` allocates state, initializes an 8-bit-register/16-bit-value regmap, validates `RT1016_DEVICE_ID`, resets the chip, registers `rt1016_patch`, and registers the ASoC component. Component callbacks include `rt1016_probe()`, `rt1016_remove()`, suspend, and resume. DAI ops are `rt1016_hw_params()` and `rt1016_set_dai_fmt()`. Component clock callbacks are `rt1016_set_component_sysclk()` and `rt1016_set_component_pll()`.

Controls are `DAC Playback Volume` and `DAC Playback Switch`. DAPM also includes a `Data Swap Mux` with L/R, R/L, L/L, and R/R modes, mapped to `RT1016_I2S_DATA_SWAP_SFT`.

## Control Flow
Probe validates hardware, resets it, applies the patch, and registers the codec. `hw_params()` validates sysclk/lrck using `rl6231_get_clk_info()`, validates frame size and 16/20/24/32-bit widths, tracks bclk, programs 64fs BCLK in master mode when needed, sets I2S word length, and programs FS/OSR dividers. `set_dai_fmt()` handles codec master or slave mode, BCLK polarity, and I2S/left-justified/DSP A/DSP B formats. PLL setup chooses MCLK or BCLK as source and calls `rl6231_pll_calc(freq_in, freq_out * 4, ...)`.

DAPM routes `AIFRX` through the data-swap mux and many supplies to `DAC` and `SPO`. Conditional PLL supply routing depends on `sysclk_src == RT1016_SCLK_S_PLL`.

## State And Persistence
The regmap uses `REGCACHE_RBTREE`. Suspend switches to cache-only and marks dirty, while resume syncs. The patch writes are registered with regmap after reset. Runtime clock and format state remain in `rt1016_priv` only.

## Dependencies And Integration Points
The driver depends on ASoC, DAPM, I2C regmap, OF `realtek,rt1016`, ACPI `10EC1016`, I2C ID `rt1016`, and Realtek `rl6231` clock helpers. Machine drivers configure the DAI named `rt1016-aif`; supported playback rates are 8 kHz through 48 kHz and formats are S8, S16_LE, S20_3LE, and S24_LE.

## Risks
The driver has no TDM slot callback, so machine drivers needing explicit slot maps must rely on basic I2S format controls. PLL calculation multiplies output by four, which is hardware-specific and easy to break if refactored. Master-mode BCLK width handling only adjusts a single bit for frame sizes over 32. Register patch failure is only a warning, so audio may proceed with suboptimal hardware configuration.

## Test Signals
Test reset and patch registration at probe, invalid ID rejection, sysclk ratio rejection, master and slave DAI formats, BCLK inversion, all supported sample widths, suspend/resume cache sync, and data-swap mux register changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1016.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1016.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1016.h

## Purpose
`rt1016.h` defines the RT1016 register addresses, bit masks, clock/PLL enums, DAI IDs, and private state used by the RT1016 ASoC I2C driver.

## Important APIs, Types, And Definitions
The header defines `RT1016_DEVICE_ID_VAL`, an 8-bit register address map from reset/pad/I2C/volume/analog/version registers through clock, I2S, DAC, short-circuit, silence-detect, class-D, PLL, and power controls. Masks cover stereo volume fields, DAC mute bits, system clock and PLL source selection, FS/OSR dividers, clock/power enables, I2S BCLK ratio and polarity, data swap, word length, master/slave, data format, silence detection, DAC clock generation, PLL M/N/K fields, and final power-control bits.

Enums define system clock source (`MCLK` or `PLL`), PLL source (`MCLK` or `BCLK`), and DAI IDs. `struct rt1016_priv` carries component, regmap, sysclk/lrck/bclk, master flag, and PLL source/input/output.

## Control Flow
No code runs in this header. The C file uses these definitions to validate and program DAI format, clock dividers, PLL coefficients, DAPM supply widgets, volume controls, data swap, and reset/patch behavior.

## State And Persistence
`struct rt1016_priv` defines all non-regmap runtime state. Register defaults and the regmap cache in `rt1016.c` depend on the address map and max register. No persistent firmware property structure is declared.

## Dependencies And Integration Points
The header is private to `rt1016.c` and assumes Linux ASoC/regmap types are available before use in the C file. Its enum values are used by machine-driver sysclk and PLL calls routed through ASoC component callbacks.

## Risks
Several control fields share registers, so mask correctness is critical. The power-control bits are heavily used by DAPM; an incorrect bit value can leave supplies on or mute audio. The DAI ID enum has a spare `RT1016_AIFS` but the driver registers one DAI, so future multi-DAI changes need care.

## Test Signals
Compile-time usage catches missing definitions. Runtime tests should validate volume/mute fields, I2S format and data-swap fields, sysclk/PLL source bits, FS/OSR divider programming, and DAPM power bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1016.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.c

## Purpose
`rt1017-sdca-sdw.c` is the SoundWire SDCA ASoC driver for the Realtek RT1017 smart amplifier. Unlike the I2C codecs in this subset, it uses a 32-bit SoundWire SDCA regmap, SoundWire slave lifecycle callbacks, runtime PM, SoundWire stream/port configuration, and SDCA controls for power, mute, rate, and channel cluster selection.

## Important APIs, Types, And Functions
`struct rt1017_sdca_priv` stores the ASoC component, regmap, SoundWire slave, bus params, and hardware-init flags. `rt1017_sdca_sdw_probe()` creates the SoundWire regmap and calls `rt1017_sdca_init()`, which allocates state and registers the component and DAI. `rt1017_sdca_read_prop()` declares SoundWire properties: source port 2 for IV capture, sink port 1 for playback, full data ports, simple channel prepare, timeouts, paging support, and interrupt quirks. `rt1017_sdca_update_status()` triggers hardware init when the slave attaches.

ASoC DAI ops are `rt1017_sdca_pcm_hw_params()`, `rt1017_sdca_pcm_hw_free()`, `rt1017_sdca_set_sdw_stream()`, and `rt1017_sdca_shutdown()`. DAPM event callbacks control PDE23 power state, class-D PWM trim/class-D register, and feedback path register changes.

## Control Flow
SoundWire probe only initializes software state. Real hardware programming occurs in `rt1017_sdca_io_init()` after the slave reports attached. First init enables runtime PM and autosuspend; later init reopens the cache and bypasses it. The function writes a software reset, applies `rt1017_blind_write`, updates init flags, and drops the PM reference.

For PCM setup, the machine driver first supplies an SDW stream pointer through `.set_stream`. `hw_params()` selects SoundWire direction and port based on playback versus capture, builds stream and port configs from rate, width, and channels, calls `sdw_stream_add_slave()`, maps supported rates to SDCA FS indices, and writes the SDCA CS21 FS control. `hw_free()` removes the slave from the stream. DAPM routes DP1 playback through DAC and CLASS D to speaker output, and IV feedback generators through DP2 capture.

## State And Persistence
The regmap uses `REGCACHE_MAPLE` with 32-bit register addresses and 8-bit values. Runtime PM suspend sets cache-only when hardware was initialized; resume waits for SoundWire reinitialization when needed, then syncs the cache. `hw_init` is cleared on unattached status, while `first_hw_init` controls one-time runtime PM setup and later cache-bypass behavior.

## Dependencies And Integration Points
The driver depends on SoundWire core, SDCA register macros, runtime PM, ASoC, regmap SoundWire, and DAPM. It binds with `SDW_SLAVE_ENTRY_EXT(0x025d, 0x1017, 0x3, 0x1, 0)`. It integrates with machine drivers through the DAI named `rt1017-aif`, playback stream `DP1 Playback`, capture stream `DP2 Capture`, and SoundWire stream handoff.

## Risks
Hardware init is status-driven, so register access before attach can fail or be cached unexpectedly. `hw_params()` requires an SDW stream and `sdw_slave`; missing machine-driver setup returns `-EINVAL`. Only 44.1, 48, 96, and 192 kHz are mapped to SDCA FS codes. Blind writes are large and hardware-specific. Resume waits up to 5 seconds for SoundWire initialization and can return `-ETIMEDOUT`.

## Test Signals
Test SoundWire attach/unattach cycles, first and repeated hardware init, runtime suspend/resume with unattach request, playback and capture stream setup/removal, missing `.set_stream` failure, supported and unsupported rates, DAPM PDE/class-D/feedback event writes, and readable/volatile register coverage for SDCA controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.h

## Purpose
`rt1017-sdca-sdw.h` defines the private SDCA entity/control identifiers, selected vendor register fields, supported SDCA rate codes, driver state, and default register table for the RT1017 SoundWire smart amplifier.

## Important APIs, Types, And Definitions
The header includes regmap, SoundWire, SDW type/register, and ASoC headers. It defines SDCA function number `FUNC_NUM_SMART_AMP`, entity IDs for power domains, converter, SAPU, extension unit, feature unit, and UDMPU, and control IDs for sample-rate index, requested power state, protection status, bypass, mute, volume, and cluster selection. It also defines `RT1017_CLASSD_INT_1`, `RT1017_PWM_TRIM_1`, and PWM frequency source masks.

The rate enum maps 44.1, 48, 96, and 192 kHz to SDCA FS index values. `struct rt1017_sdca_priv` carries component, regmap, SoundWire slave, bus params, and `hw_init`/`first_hw_init` flags. `rt1017_sdca_reg_defaults[]` seeds the regmap cache for vendor and SDCA controls, including default mute, bypass, FS index, and PDE power-state values.

## Control Flow
The header contains no functions. Its SDCA macros and defaults drive `rt1017-sdca-sdw.c` register access in hardware init, DAPM events, ALSA controls, PCM rate setup, PM cache sync, and readable/volatile register declarations.

## State And Persistence
`struct rt1017_sdca_priv` defines the state persisted across SoundWire status, PM, and ASoC callbacks. The default table establishes reset/cache state and is used by regmap for restore after suspend or reattach.

## Dependencies And Integration Points
This header is tightly coupled to the Linux SoundWire SDCA macro API, especially `SDW_SDCA_CTL()`. It is private to the RT1017 SDCA SoundWire driver but its constants encode the SDCA function topology used by ASoC controls and DAPM.

## Risks
The 32-bit SDCA address construction is easy to misuse; wrong function/entity/control IDs can target unrelated controls. The default table mixes vendor registers and SDCA controls, so additions must be checked against readable/volatile lists in the C file. `struct rt1017_sdca_priv` has a `params` field that is not actively used in the current C file, which can confuse future changes.

## Test Signals
Build coverage validates SDCA macro usage. Runtime tests should verify default mute/bypass/power states, FS index writes for each supported rate, PDE power-state DAPM transitions, cache restore after SoundWire resume, and readable/volatile coverage for all defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1019.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1019.c

## Purpose
`rt1019.c` is the ASoC I2C driver for the Realtek RT1019 amplifier. It exposes a compact 8-bit-value regmap, one playback DAI, DAC volume and mono source controls, DAPM shutdown control, DAI clock/PLL programming, and TDM slot selection.

## Important APIs, Types, And Functions
`struct rt1019_priv` from `rt1019.h` stores component/regmap pointers, sysclk/lrck/bclk, PLL state, and a bclk-ratio field. `rt1019_i2c_probe()` allocates state, initializes a 16-bit-register/8-bit-value regmap, reads two device ID bytes, accepts either RT1019 ID value, and registers `soc_component_dev_rt1019`. `rt1019_probe()` stores the component pointer and initializes `RT1019_SDB_CTRL` to shutdown value `0xa`.

DAI ops are `rt1019_hw_params()`, `rt1019_set_dai_fmt()`, `rt1019_set_dai_sysclk()`, `rt1019_set_dai_pll()`, and `rt1019_set_tdm_slot()`. Controls are `DAC Playback Volume` and `Mono LR Select`. DAPM uses `r1019_dac_event()` to write `RT1019_SDB_CTRL` high on DAC power-up and low on power-down.

## Control Flow
Probe validates the device and registers the component. `hw_params()` checks sysclk/lrck with `rl6231_get_clk_info()`, computes bclk from frame size, maps pre-dividers 1/2/4 to DAC filter, DAC OSR, ASRC, FIFO, and calibration clock fields, maps sample width to TDM data length, and writes clock-tree and TDM registers. DAI format supports BCLK inversion and I2S/left-justified/DSP A/DSP B, but does not handle codec master/slave flags. PLL setup selects BCLK or internal RC25M source, forces manual bit/clock selection, computes PLL values, and writes split M/Q/K fields. TDM slot setup supports 2/4/6/8 slots, 8/16/20/24/32-bit slot widths, and exactly one RX mask bit used to map stereo slot pairs.

## State And Persistence
Regmap uses `REGCACHE_MAPLE`; this file has no explicit suspend/resume callbacks, so cache handling relies on the component/regmap lifecycle. Clock and PLL selections persist in `rt1019_priv` during driver lifetime. Shutdown state is controlled by DAPM and initialized in component probe.

## Dependencies And Integration Points
Dependencies include ASoC, DAPM, I2C regmap, ACPI/OF, and `rl6231` helpers. It binds to I2C `rt1019`, OF `realtek,rt1019`, and ACPI `10EC1019`. Machine drivers configure the DAI named `rt1019-aif`; playback supports 8 kHz through 192 kHz and S8/S16/S20_3LE/S24 formats.

## Risks
The register default table contains duplicate address `0x0100` with different values, which may be intentional override or a maintenance hazard. There is no explicit PM cache sync path. `set_dai_fmt()` ignores master/slave configuration, which may surprise machine drivers expecting full format validation. Only pre_div values 0, 1, and 3 are accepted after helper mapping. TDM slot logic assumes stereo source pairs and does not validate TX mask.

## Test Signals
Test two-byte ID validation, shutdown register transitions on DAPM power, sysclk and PLL source paths, unsupported clock ratios, supported widths including 32-bit TDM slot width, DAI format inversion and DSP modes, TDM RX masks for even and odd slot positions, and behavior across system suspend if the platform uses this codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1019.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1019.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1019.h

## Purpose
`rt1019.h` defines the RT1019 private register map, bit masks, clock and PLL enums, and driver state for the RT1019 ASoC I2C amplifier driver.

## Important APIs, Types, And Definitions
The header defines accepted IDs `RT1019_DEVICE_ID_VAL` and `RT1019_DEVICE_ID_VAL2`, registers for reset, input data selection, analog selection, power strap, beep, version/vendor/device IDs, shutdown, clock tree, PLL, TDM, mono mixer, and beep controls. Bit fields cover automatic versus manual power-strap selection, sysclk source, PLL source, FIFO divider, DAC filter divider, DAC OSR, ASRC input divider, calibration clock divider, PLL M/Q/K fields, TDM BCLK polarity, slot width, channel count, I2S format, data length, and DAC slot selection.

Enums define system clock source (`BCLK` or `PLL`), PLL source (`BCLK` or `RC25M`), and DAI IDs. `struct rt1019_priv` holds component, regmap, sysclk/lrck/bclk, PLL settings, and a bclk-ratio value.

## Control Flow
The header contains no executable flow. `rt1019.c` uses the definitions to program clock dividers in `hw_params()`, PLL coefficients in `set_pll()`, format and TDM slot fields, mono channel controls, and SDB power transitions.

## State And Persistence
`struct rt1019_priv` is the driver's runtime state contract. The register constants and max register bound drive regmap cache behavior in the C file. No platform data or firmware-property state is declared.

## Dependencies And Integration Points
The header is private to `rt1019.c` and is indirectly tied to ASoC DAI callbacks and the `rl6231` PLL helper. Machine-driver clock IDs must match the enum values used by `set_sysclk()` and `set_pll()`.

## Risks
The register map uses 16-bit addresses with 8-bit values; mixing it with other Realtek codecs that use 16-bit values would be a bug. Several names refer to I2S TX fields even though the amplifier primarily consumes playback slots, which can make slot direction reasoning error-prone. The spare `bclk_ratio` state field is present but unused in current code.

## Test Signals
Compile coverage catches definitions. Runtime tests should verify ID byte assembly, PLL source bits, manual strap bits, clock-tree divider fields, TDM data length and slot selection masks, mono select control, and SDB control writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1019.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1305.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1305.c

## Purpose
`rt1305.c` is the ASoC I2C component driver for Realtek RT1305/RT1306 stereo amplifiers. It provides a playback DAI, regmap support for normal and private-register windowed ranges, initialization and calibration sequences, DAPM power routing for DAC/class-D/sense paths, sysclk/PLL programming, and PCM format setup.

## Important APIs, Types, And Functions
`struct rt1305_priv` is defined locally and stores component/regmap pointers, sysclk/lrck/bclk, master flag, and PLL state. `rt1305_i2c_probe()` allocates state, initializes regmap with private range support, validates `RT1305_DEVICE_ID`, resets the chip, runs `rt1305_calibrate()`, and registers `soc_component_dev_rt1305`. Component callbacks include `rt1305_probe()` for init-list writes, `rt1305_remove()`, suspend, resume, `rt1305_set_component_sysclk()`, and `rt1305_set_component_pll()`.

DAI ops are `rt1305_hw_params()` and `rt1305_set_dai_fmt()`. Controls include stereo DAC playback volume and `RX Channel Select`. `rt1305_classd_event()` toggles `PDB_JD` around class-D power, with a 150-200 ms delay before power-down.

## Control Flow
Probe validates hardware, resets, performs calibration, then registers ASoC. Component probe writes an init list including private registers, speaker protection, DAC, ADC, and power status settings. `hw_params()` computes a 256fs sysclk divider; if unsupported, it force-programs a BCLK-sourced PLL and sysclk at 256fs. It supports 8/16/20/24-bit samples and writes I2S data length plus clock divider. DAI format supports codec master/slave, normal or inverted BCLK, and I2S/left-justified/DSP A/DSP B formats.

DAPM routes `AIF1RX` through a DAC, many analog/digital supplies, left/right DAC switches, `CLASS D`, and outputs `SPOL`/`SPOR`. Conditional routes enable PLL0 when the sysclk is PLL-derived from RC clock and PLL1 when sysclk source is PLL.

Calibration bypasses the cache, resets hardware, programs EFUSE/readout and sine-generator/private-register sequences, reads DAC offsets, measures left and right R0 values after long sleeps, computes reciprocal values with `do_div()`, conditionally writes calibrated R0 to private registers, restores key power/clock registers, and exits cache bypass.

## State And Persistence
The regmap uses `REGCACHE_MAPLE`, 8-bit register addresses, 16-bit values, and one private range addressed through `RT1305_PRIV_INDEX`/`RT1305_PRIV_DATA`. Suspend/resume switch cache-only and sync. Calibration writes are direct hardware operations with cache bypass. Runtime clock and PLL selections live in memory.

## Dependencies And Integration Points
The driver depends on ASoC, DAPM, I2C regmap range windows, ACPI/OF matching, and `rl6231_pll_calc()`. It binds to OF `realtek,rt1305`/`realtek,rt1306`, ACPI `10EC1305`/`10EC1306`, and I2C IDs `rt1305`/`rt1306`, but still validates the RT1305 device ID value. Machine drivers use DAI `rt1305-aif`.

## Risks
Calibration is invasive and runs synchronously in I2C probe, including two 2-second sleeps, which can slow boot and fail probe if hardware is marginal. The R0 range check uses reciprocal values and constants whose names (`R0_UPPER`, `R0_LOWER`) are easy to misread. Hardware sequences contain many magic private-register writes. Forced PLL fallback can mask bad clock setup. Although compatible strings include RT1306, the ID check requires `RT1305_DEVICE_ID_NUM`.

## Test Signals
Test regmap private-range access, probe timing and ID failure, calibration logs and R0 failure path, init-list writes after component probe, sysclk fallback PLL path, DAI master/slave and format options, sample width rejection for 32-bit, DAPM class-D power timing, suspend/resume cache sync, and RT1306-compatible board behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1305.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1305.h

## Purpose
`rt1305.h` defines the RT1305 amplifier register map, bit masks, clock/PLL enums, DAI IDs, and R0 calibration bounds used by `rt1305.c`.

## Important APIs, Types, And Definitions
The header defines `RT1305_DEVICE_ID_NUM`, 8-bit register addresses for reset, clocks, DFLL, EFUSE clocking, PLLs, mixer, DAC/ADC, SPDIF, I2S, power, protection, private index/data, ID, EFUSE, DC calibration, DAC offsets, trim, internal oscillator, and biquad coefficient ranges. Bit fields cover PLL source selection, sysclk source and divider, PLL M/N/K fields, DAC mute bits, I2S output master/slave, I2S format/word length/BCLK polarity, many power-control supplies, clock-detect source, and class-D/ADC/DAC power bits.

Enums define sysclk source (`MCLK`, `PLL1`, `RCCLK`), PLL source (`BCLK`, `MCLK`, `RCCLK`), and DAI IDs. `R0_UPPER` and `R0_LOWER` define reciprocal-domain thresholds used by calibration.

## Control Flow
The header has no executable logic. Its constants drive `rt1305.c` regmap defaults, private-range setup, init-list writes, readable/volatile filters, DAPM supply widgets, clock and PLL programming, DAI format setup, and calibration register programming.

## State And Persistence
No private state struct is declared here; `rt1305_priv` lives in the C file. The register map and masks define what can be cached, restored, and accessed through the private register window.

## Dependencies And Integration Points
The header is private to the RT1305 driver and indirectly tied to ASoC, regmap, and `rl6231` helper usage. Constants for `RT1305_PRIV_INDEX` and `RT1305_PRIV_DATA` are especially important for regmap range-window integration.

## Risks
The header packs a broad hardware contract into macros with limited comments. Power-control masks are numerous and used in DAPM routes, so bit mistakes can affect power sequencing. `R0_UPPER` and `R0_LOWER` are named from an ohm perspective but compared against reciprocal values in the C file, which invites incorrect edits.

## Test Signals
Compile coverage validates macro use. Runtime tests should verify private-register window access, PLL/sysclk bit programming, I2S format/length fields, DAPM power-bit behavior, clock-detect source selection, DAC mute and volume fields, and calibration threshold handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1305.h -->
