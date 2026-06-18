# subset-b-006489 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8510.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8510.c

Purpose: ALSA SoC codec driver for the WM8510 mono/stereo audio codec, exposing playback, capture, mixer, boost, limiter, ALC, companding, EQ-adjacent, PLL, divider, and DAPM controls through a single `wm8510-hifi` DAI. It supports I2C and SPI control paths using a 7-bit register/9-bit value regmap with MAPLE cache because two-wire control cannot read the hardware registers.

Important APIs/types/functions: `struct wm8510_priv` stores only the regmap; `wm8510_reg_defaults`, `wm8510_volatile()`, `wm8510_snd_controls`, DAPM widgets/routes, and `soc_component_dev_wm8510` define component behavior. DAI ops are `wm8510_pcm_hw_params()`, `wm8510_mute()`, `wm8510_set_dai_fmt()`, `wm8510_set_dai_clkdiv()`, and `wm8510_set_dai_pll()`. `pll_factors()` computes predivide/N/K for the PLL and stores it in the file-scope `pll_div`.

Control flow: bus probe allocates private data, creates the regmap, stores driver data, and registers the component. Component probe issues reset. Machine drivers configure PLL/dividers and DAI format; `hw_params()` programs word length and filter coefficient bits from PCM width/rate. Bias transitions sync the cache when leaving OFF, apply a 100 ms VMID charge in standby, then shut down POWER1-3 in OFF.

State and persistence: register state persists in regcache; reset is volatile. PLL calculation uses file-global scratch state, not per-device state. Bias state is held in hardware registers and DAPM. Dependencies include ALSA SoC, regmap, I2C/SPI, delay helpers, and machine-driver DAI calls.

Risks: the global `pll_div` is shared across devices and would be unsafe for concurrent multi-instance programming. `pll_factors()` only warns on unsupported N ranges. `wm8510_modinit()` can mask a successful I2C registration with a later SPI registration error. Test signals include I2C/SPI probe, reset/cache sync after OFF, supported/unsupported formats and inversions, PLL disable/reprogram, divider IDs, mute bit behavior, and DAPM route power-up of input/output paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8510.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8510.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8510.h

Purpose: public register and clock-divider definitions for the WM8510 codec driver. It names the codec register addresses from reset through mono mix, the cache register count, and symbolic divider IDs/bit encodings used by machine drivers through `set_clkdiv()`.

Important APIs/types/functions: the key exported constants are `WM8510_RESET`, `WM8510_POWER1` through `WM8510_MONOMIX`, `WM8510_OPCLKDIV`, `WM8510_MCLKDIV`, `WM8510_ADCCLK`, `WM8510_DACCLK`, and `WM8510_BCLKDIV`. Divider values include DAC/ADC half/fourth-rate flags, PLL output divisors, BCLK divisors, and MCLK divisors. `struct wm8510_setup_data` contains legacy board-data fields for SPI/I2C selection, bus, and address.

Control flow: no executable logic exists here; the C file consumes these definitions when programming regmap and when decoding DAI clock-divider requests. State and persistence are indirect: constants must match hardware bit positions and the driver's regmap max/cache assumptions.

Dependencies and integration points: included by `wm8510.c` and potentially board or machine code that configures the codec. It has no external include dependencies.

Risks: incorrect bit constants would silently program the wrong hardware fields. `WM8510_CACHEREGNUM` is legacy metadata rather than the actual regmap default count. Test signals are compile coverage of users of the constants, DAI divider programming for each ID/value, and comparison against datasheet register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8510.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8523.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8523.c

Purpose: ALSA SoC driver for the WM8523 stereo DAC. It provides playback-only DAI support, I2C probing with device-ID/revision validation, regulator-managed power sequencing for `AVDD` and `LINEVDD`, cached register access, DAC volume/mute/deemphasis/zero-detect controls, and simple line-output DAPM topology.

Important APIs/types/functions: `struct wm8523_priv` keeps the regmap, bulk supplies, configured `sysclk`, and runtime rate constraints. `wm8523_set_dai_sysclk()` derives valid sample rates from MCLK/LRCLK ratios. `wm8523_startup()` requires MCLK and installs those constraints. `wm8523_hw_params()` programs sample-rate ratio, provider-mode BCLK divider, and word length. `wm8523_set_dai_fmt()` programs provider/consumer mode, I2S/left/right/DSP formats, and clock polarity. `wm8523_set_bias_level()` controls regulator enable, cache sync, and SYS_ENA power states.

Control flow: I2C probe allocates private state, initializes regmap, acquires/enables regulators, reads ID/revision, resets by writing the ID register, disables supplies, and registers the component. Component probe initializes the constraint list pointer/count and latches volume update/zero-cross defaults.

State and persistence: `sysclk` and the constraint array persist per device. Device registers are cached; device ID and revision are volatile. Bias OFF disables supplies, while standby re-enables supplies and syncs the cache.

Dependencies/integration: Linux I2C, regmap, regulator bulk APIs, ALSA SoC controls/DAPM, and machine-driver `set_sysclk()` ordering. Risks include startup failing if `set_sysclk()` was not called, unsupported MCLK/fs ratios, provider-mode BCLK divider limits, and an error message that prints `ret` instead of the unexpected ID value. Test signals include ID mismatch paths, regulator failures, rate-constraint generation, all supported sample widths/formats, and bias OFF-to-STANDBY sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8523.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8523.h

Purpose: generated-style register map and field definitions for the WM8523 stereo DAC. It is the authoritative local source for register addresses, register count/max, and bit masks/shifts/widths used by `wm8523.c`.

Important APIs/types/functions: registers include `WM8523_DEVICE_ID`, `WM8523_REVISION`, `WM8523_PSCTRL1`, `WM8523_AIF_CTRL1`, `WM8523_AIF_CTRL2`, `WM8523_DAC_CTRL3`, `WM8523_DAC_GAINL`, `WM8523_DAC_GAINR`, and `WM8523_ZERO_DETECT`. Field constants cover chip ID/revision, system enable state, TDM mode/slot, deemphasis, AIF master, LRCLK/BCLK inversion, word length, interface format, BCLK divider, sample-rate selector, DAC mute bits, volume ramps, VU bits, and zero-detect count.

Control flow: no executable logic exists; the implementation uses these constants in regmap updates, DAI format/hw_params, bias power sequencing, and mixer controls. State/persistence impact is through masks that preserve unrelated register bits during `snd_soc_component_update_bits()`.

Dependencies and integration points: included by `wm8523.c`; no external dependencies beyond the C preprocessor. Risks are typical for hardware headers: stale masks or shifts would break runtime programming despite compiling cleanly. Test signals include register-field coverage in DAI format, hw_params, bias, and control tests, plus datasheet comparison for `WM8523_REGISTER_COUNT` and `WM8523_MAX_REGISTER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8523.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8524.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8524.c

Purpose: minimal platform-driver ALSA SoC support for the WM8524 hardware-controlled stereo DAC. The chip has no register control bus in this driver; it validates clock/rate combinations, enforces a fixed I2S slave format, exposes playback DAPM endpoints, and controls an external mute GPIO.

Important APIs/types/functions: `struct wm8524_priv` stores optional state required by runtime playback: mute GPIO, `sysclk`, and the computed rate-constraint list. `wm8524_set_dai_sysclk()` computes standard sample rates from known LRCLK ratios, accepting `freq == 0` as unconstrained. `wm8524_startup()` applies constraints when MCLK is known and unmutes via GPIO. `wm8524_shutdown()` mutes. `wm8524_set_fmt()` accepts only I2S, normal clocks, codec bit/frame consumer. `wm8524_hw_params()` checks the requested LRCLK against computed constraints.

Control flow: platform probe allocates private data, requires `wlf,mute` GPIO as output-low, stores drvdata, and registers one playback DAI. Component probe initializes the constraint-list pointer/count. DAI startup/shutdown toggles the mute line around stream lifetime; `mute_stream()` also drives it if present.

State and persistence: only in-memory sysclk/rate constraints and GPIO state persist; there is no regmap/cache. Dependencies include platform bus, GPIO descriptors, ALSA SoC, and machine-driver clock/format negotiation.

Risks: mute GPIO is mandatory despite code checking for null later; a missing `set_sysclk()` allows any rate through by design; startup sets GPIO to 1 while shutdown sets 0, so board polarity must match `GPIOD_OUT_LOW` and binding expectations. Test signals include GPIO acquisition/probe deferral, fixed-format rejection, constrained/unconstrained rate paths, mute_stream behavior, and DAPM endpoint registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8524.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8580.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8580.c

Purpose: ALSA SoC I2C driver for WM8580/WM8581 multichannel codecs. It supports the primary audio interface only, providing 6 DAC channels for WM8580 or 8 for WM8581, 2 ADC channels, PLLA/PLLB programming, sysclk selection, multichannel DAPM/routes, regulator-managed supplies, and playback/capture DAI callbacks.

Important APIs/types/functions: `struct wm8580_priv` holds regmap, three regulators, PLL state for A/B, chip variant data, and per-DAI sysclk values. `pll_factors()` scales PLL output into the 90-100 MHz range using `post_table`; `wm8580_set_dai_pll()` disables, programs, and re-enables selected PLL. `wm8580_paif_hw_params()` validates sysclk/fs ratio and programs word length, BCLK ratio, and DAC oversampling. `wm8580_set_paif_dai_fmt()` handles provider/consumer mode, I2S/left/right/DSP formats, and legal clock inversions. `wm8580_set_sysclk()` selects MCLK/PLLA/PLLB/ADCMCLK source per DAI.

Control flow: I2C probe initializes regmap, supplies, variant match data, and registers two DAIs. Component probe conditionally adds WM8581 DAC4 controls/widgets/routes, enables supplies, resets the codec, and leaves supplies enabled until remove. Runtime DAI calls configure clocks and formats before stream parameters.

State and persistence: PLL in/out frequencies and per-DAI sysclk are private state; register defaults are cached with reset volatile. Volume update controls temporarily set cache-only to clear VU bits before writing values and then trigger latch bits.

Dependencies/integration: I2C, regmap, regulators, ALSA SoC, TLV controls, DAPM, and OF/I2C match data. Risks include no validation that selected PLL source frequency matches programmed PLL state, restricted S/PDIF/secondary AIF support, exact sysclk/fs requirements, and variant-dependent channel constraints. Test signals include WM8580 vs WM8581 probe, regulator failure cleanup, PLL invalid ranges, clock-source selection per DAI, channel min/max constraints, mute-all bit, and cache/VU volume writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8580.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8580.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8580.h

Purpose: public constants for configuring WM8580/WM8581 clocks and DAIs from machine drivers. It names PLL IDs, clock-divider selector IDs, clock-source values, and primary DAI IDs used by `wm8580.c`.

Important APIs/types/functions: `WM8580_PLLA` and `WM8580_PLLB` identify PLLs for `set_pll()`. `WM8580_MCLK` and `WM8580_CLKOUTSRC` identify `set_clkdiv()` selector fields. `WM8580_CLKSRC_MCLK`, `WM8580_CLKSRC_PLLA`, `WM8580_CLKSRC_PLLB`, `WM8580_CLKSRC_OSC`, `WM8580_CLKSRC_NONE`, and `WM8580_CLKSRC_ADCMCLK` express source choices. `WM8580_DAI_PAIFRX` and `WM8580_DAI_PAIFTX` distinguish playback and capture primary audio interfaces.

Control flow: no executable code; the implementation switches on these IDs in DAI clock callbacks. State/persistence is indirect through values saved in `wm8580_priv.sysclk[]` and PLL state.

Dependencies and integration points: included by the codec driver and by board/machine code configuring clocks. Risks include ABI-like coupling: changing numeric values would break existing machine drivers. Test signals are compile-time users of each constant and runtime `set_pll`, `set_clkdiv`, and `set_sysclk` coverage for valid and invalid IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8580.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8711.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8711.c

Purpose: ALSA SoC playback-only driver for the WM8711 DAC/headphone codec, based on WM8731-style clocking and register layout. It supports I2C and SPI control with cached 7-bit/9-bit regmap, output volume controls, output-mixer DAPM, stream active/deactivate sequencing, sample-rate coefficient programming, and bias power control.

Important APIs/types/functions: `struct wm8711_priv` stores regmap and selected `sysclk`. DAI ops include `wm8711_hw_params()`, `wm8711_pcm_prepare()`, `wm8711_shutdown()`, `wm8711_mute()`, `wm8711_set_dai_sysclk()`, and `wm8711_set_dai_fmt()`. The `coeff_div` table maps supported MCLK/rate pairs to SRATE fields. `wm8711_probe()` resets the codec and latches output volume update bits.

Control flow: I2C/SPI probe allocates private data, creates regmap, stores drvdata, and registers the component. `set_sysclk()` accepts only common audio MCLKs. `hw_params()` selects coefficient index and word length, writes SRATE and IFACE. `prepare()` sets ACTIVE; `shutdown()` clears ACTIVE after a short delay when no component stream remains active.

State and persistence: sysclk is per-device state; registers persist through regcache with reset volatile. Bias OFF writes full powerdown and ACTIVE=0; STANDBY syncs cache when returning from OFF. Dependencies include ALSA SoC, regmap, I2C/SPI, DAPM, and machine clock setup.

Risks: `get_coeff()` returns 0 when no match is found, so missing/invalid sysclk can silently program the 12.288 MHz/48 kHz entry. The DAPM route references `Line Input` although no input widget is declared in this driver. `wm8711_modinit()` returns 0 even if bus registration fails. Test signals include invalid sysclk, unsupported rates, active bit prepare/shutdown, mute bit, cache sync after OFF, and both bus probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8711.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8711.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8711.h

Purpose: register and legacy setup definitions for the WM8711 codec driver. It provides symbolic addresses for the small WM8711 register map plus IDs used by machine-driver configuration.

Important APIs/types/functions: register constants cover left/right output volume, analog/digital audio paths, power, interface, sample rate, active, and reset registers. `WM8711_CACHEREGNUM`, `WM8711_SYSCLK`, and `WM8711_DAI` provide legacy metadata/IDs. `struct wm8711_setup_data` holds an I2C address for older board-data flows.

Control flow: no runtime logic exists in the header. `wm8711.c` uses these constants for regmap max/defaults, component controls, DAI callbacks, and reset/power sequencing.

State and persistence: constants determine which fields are cached and which hardware register is volatile. Dependencies are minimal; this header does not include other headers.

Risks: the declared cache register count does not include reset and is legacy. Any mismatch between these addresses and the hardware map affects all controls and DAI programming. Test signals include compile users, reset volatility, DAI sysclk ID compatibility, and register-address comparison with known WM8711 maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8711.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8727.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8727.c

Purpose: very small ALSA SoC platform driver for the WM8727 stereo DAC, a device with no software control interface. The driver only declares playback capabilities and DAPM output routes.

Important APIs/types/functions: `wm8727_dai` defines one `wm8727-hifi` playback stream with 2 channels, rates 32 kHz, 44.1 kHz, 48 kHz, 96 kHz, and 192 kHz, and S16/S24 formats. `wm8727_dapm_widgets` exposes `VOUTL` and `VOUTR`; routes connect both outputs directly to the playback stream. `wm8727_probe()` registers the component and DAI with devm.

Control flow: platform-device probe registers a static component; there are no DAI ops, no regmap, no clock callbacks, no bias callback, and no remove handler beyond devm cleanup. Runtime sample rate is determined externally by clock ratios, as noted in the source comment.

State and persistence: no private state exists. Hardware state is controlled by board wiring and external clocks. Dependencies are ALSA SoC and platform bus/module infrastructure.

Risks: absence of format/clock validation means machine drivers must ensure the physical clocks match the requested PCM configuration. There is no OF match table, so integration depends on platform-device naming. Test signals include platform probe, DAPM route visibility, supported-rate negotiation, and machine-level playback with valid/invalid external clock combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8727.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8728.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8728.c

Purpose: ALSA SoC driver for the WM8728 stereo DAC with I2C/SPI control. It exposes playback volume, deemphasis, mute, word-length programming, fixed slave I2S format handling, and DAPM outputs while relying on a cached write-only register map.

Important APIs/types/functions: `struct wm8728_priv` stores the regmap. `wm8728_reg_defaults` intentionally differ from physical defaults to latch volume update bits, mute output, and enable infinite zero detect. DAI ops are `wm8728_hw_params()`, `wm8728_mute()`, and `wm8728_set_dai_fmt()`. `wm8728_set_bias_level()` powers the DAC down/up through the DACCTL power bit and syncs regcache when returning from OFF.

Control flow: I2C/SPI probe allocates private state, initializes the regmap, stores drvdata, and registers one playback DAI. `set_fmt()` accepts only I2S format and full codec slave mode, but supports four clock inversion combinations. `hw_params()` supports 16/20/24-bit samples and rejects other widths.

State and persistence: all registers are cached via MAPLE; there is no readable volatile register callback. Bias OFF sets the DAC powerdown bit, while standby/on clears it and syncs cached settings. Dependencies include ALSA SoC, regmap, I2C/SPI, and TLV controls.

Risks: hardware supports more than the driver exposes, so machine drivers needing non-I2S or master mode cannot use this implementation as-is. The regmap default policy is behavioral, not physical, so reset assumptions need care. `wm8728_modinit()` can return the last bus registration result only. Test signals include bus probes, mute/deemphasis controls, 16/20/24-bit hw_params, format rejection, bias OFF-to-standby cache sync, and DAPM output paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8728.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8728.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8728.h

Purpose: compact register-address header for the WM8728 DAC driver. It names the four writable registers used by `wm8728.c`.

Important APIs/types/functions: `WM8728_DACLVOL`, `WM8728_DACRVOL`, `WM8728_DACCTL`, and `WM8728_IFCTL` identify left/right volume, DAC control, and interface-control registers. There are no field masks, structs, or function declarations.

Control flow: no executable logic. The C driver uses these constants for regmap defaults, mixer controls, mute/power bits, word-length selection, and DAI format programming.

State and persistence: constants shape the cached register surface; the driver sets `max_register` to `WM8728_IFCTL`. Dependencies are none beyond inclusion by C code.

Risks: this minimal header leaves bit meanings as literals in the C file, increasing maintenance risk when changing field handling. Test signals are compile coverage and runtime writes to all four registers via controls, bias, mute, hw_params, and set_fmt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8728.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731-i2c.c

Purpose: I2C bus wrapper for the shared WM8731 codec core. It performs bus-specific allocation/regmap setup and then delegates all codec behavior to `wm8731_init()`.

Important APIs/types/functions: `wm8731_i2c_probe()` allocates `struct wm8731_priv`, stores it with `i2c_set_clientdata()`, initializes `wm8731_regmap` through `devm_regmap_init_i2c()`, reports regmap allocation failures, and calls `wm8731_init(&i2c->dev, wm8731)`. The file also declares OF compatible `wlf,wm8731`, I2C ID `wm8731`, and the `module_i2c_driver()` registration.

Control flow: probe is invoked by I2C core, sets up private data/regmap, then shared init obtains clocks/regulators, resets/configures the codec, and registers the component/DAI. There is no remove logic beyond devm cleanup and the core driver's power-management callbacks.

State and persistence: private state is owned by the shared core; this wrapper only persists the regmap pointer and clientdata association. Dependencies include Linux I2C, module infrastructure, regmap declarations from `wm8731.h`, and shared core symbol availability.

Risks: no device ID read is performed, so successful probe depends on the I2C device binding being correct and basic register writes succeeding later. Test signals include I2C probe, regmap error path, OF/modalias matching, shared init failure propagation, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731-spi.c

Purpose: SPI bus wrapper for the shared WM8731 codec core. It mirrors the I2C wrapper but initializes regmap over SPI and registers through `module_spi_driver()`.

Important APIs/types/functions: `wm8731_spi_probe()` allocates `struct wm8731_priv`, stores it with `spi_set_drvdata()`, creates a regmap using `devm_regmap_init_spi(spi, &wm8731_regmap)`, logs allocation errors, and delegates to `wm8731_init()`. The OF match table uses compatible `wlf,wm8731`; the SPI driver name is `wm8731`.

Control flow: SPI probe handles only transport setup. All codec reset, regulator, clock, control, DAPM, and DAI registration is in the core file. Remove/unload is devm and module framework driven.

State and persistence: no wrapper-local runtime state beyond clientdata and the core private struct. Dependencies include SPI, module infrastructure, shared regmap config, and exported `wm8731_init()`.

Risks: as with I2C, no explicit ID validation is possible here. SPI mode/word settings are not customized in this file, so board descriptions must supply suitable SPI wiring/configuration. Test signals include SPI probe, regmap allocation failure, OF matching, shared init propagation, and basic register writes after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731.c

Purpose: shared ALSA SoC core for WM8731 stereo codec, used by I2C and SPI wrappers. It provides playback/capture controls, DAPM topology, MCLK/XTAL clock selection, sample-rate constraints, deemphasis state, regulator and optional clock management, bias sequencing, and exported init/regmap symbols.

Important APIs/types/functions: `struct wm8731_priv` is declared in the header and stores regmap, optional `mclk`, four supplies, rate constraints, sysclk, playback rate, deemphasis flag, and mutex. `wm8731_set_dai_sysclk()` validates supported MCLKs and sets constraint lists. `wm8731_hw_params()` programs SRATE and word length from coefficient tables and updates deemphasis. `wm8731_set_deemph()`, get/put controls, and the mutex preserve user deemphasis settings. `wm8731_set_bias_level()` controls clock/regulators, power register, and cache dirty/sync behavior. `wm8731_init()` is exported for wrappers.

Control flow: wrapper probe creates regmap and calls `wm8731_init()`. Init obtains optional `mclk`, initializes mutex and regulators, enables supplies, resets, clears poweroff, latches update bits, disables bypass, marks cache dirty, and registers component/DAI. Runtime startup applies rate constraints; DAI ops program format, clock, params, and mute.

State and persistence: sysclk type controls DAPM OSC routes, deemphasis tracks playback rate, regcache persists write-only state, and OFF marks cache dirty after powering down. Dependencies include ALSA SoC, regmap, regulators, clk, I2C/SPI wrappers, and machine-driver clock setup.

Risks: `get_coeff()` returns index 0 on no match, so constraints and sysclk setup must prevent invalid combinations. Bias ON prepares/enables `mclk`, while STANDBY also handles supplies; unusual bias transitions need coverage. Test signals include optional/static MCLK, each supported MCLK constraint set, deemphasis control/rate changes, capture/playback formats, DAPM OSC conditional route, regulator failures, and suspend-bias-off cache restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731.h

Purpose: shared declarations for WM8731 bus wrappers and core. It exposes register addresses, clock IDs, supply count, private-state layout, regmap config, and the common initialization entry point.

Important APIs/types/functions: register constants cover line input volumes, output volumes, analog/digital path controls, power, interface, sample rate, active, and reset registers. `WM8731_SYSCLK_MCLK` and `WM8731_SYSCLK_XTAL` select clock source behavior. `struct wm8731_priv` contains regmap, optional clock, regulator array, current constraints, sysclk data, playback_fs, deemphasis flag, and mutex. `extern const struct regmap_config wm8731_regmap` and `int wm8731_init(struct device *, struct wm8731_priv *)` are consumed by I2C/SPI wrappers.

Control flow: wrappers allocate this private struct, fill `regmap`, then call `wm8731_init()`. State persists in the fields defined here across DAI callbacks and control operations.

Dependencies and integration points: includes mutex, regmap, regulator consumer headers, and forward declarations for clk and constraint list. It is the contract between bus-specific modules and the shared codec core.

Risks: any layout or symbol change affects both wrappers. `WM8731_CACHEREGNUM` is legacy metadata, while regmap defaults live in the C file. Test signals include both wrappers compiling against the declarations, init symbol export, sysclk type paths, and mutex-protected deemphasis control behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8731.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8737.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8737.c

Purpose: ALSA SoC capture-only driver for the WM8737 stereo ADC. It exposes mic/input PGA, ALC, noise gate, 3D, bias, and capture controls; a DAPM graph for line/mic/preamp/PGA/ADC paths; I2C/SPI support; regmap caching; regulator-managed supplies; and MCLK/rate/format DAI programming.

Important APIs/types/functions: `struct wm8737_priv` stores regmap, four supplies, and selected MCLK. `wm8737_hw_params()` searches `coeff_div` for rate/MCLK or half-rate MCLK support, then programs word length and clocking fields. `wm8737_set_dai_sysclk()` accepts only MCLKs present in the coefficient table or double those MCLKs. `wm8737_set_dai_fmt()` supports provider/consumer mode and I2S/right/left/DSP formats, but only normal clocks or frame inversion. `wm8737_set_bias_level()` sequences regulators, cache sync, VMID/VREF, and sleep delays.

Control flow: bus probe allocates private state, requests supplies, initializes regmap, stores drvdata, and registers the component. Component probe enables supplies, resets, latches PGA update bits, forces DAPM standby, then disables the extra regulator enable done during bias setup.

State and persistence: MCLK persists per device; register defaults are cached with reset volatile. Bias OFF disables VMID/VREF and regulators; standby re-enables and syncs cache. Dependencies include ALSA SoC, regmap, regulators, I2C/SPI, DAPM, and machine clock setup.

Risks: no runtime rate constraints are installed at startup, so invalid MCLK/rate combinations fail in `hw_params()` rather than negotiation. Format inversion support is narrower than many DAIs. The right bypass mux control is named `Left Bypass`, likely a user-visible naming bug. Test signals include all input mux routes, supply failures, reset and forced standby, supported MCLK/rate pairs including double-MCLK divider, width/format rejection, and bias OFF/STANDBY transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8737.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8737.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8737.h

Purpose: register and field-definition header for the WM8737 ADC driver. It enumerates the device's register map and detailed masks/shifts/widths for PGA volume, audio path, 3D, ADC, power, format, clocking, mic preamp, bias, noise gate, ALC, and reset fields.

Important APIs/types/functions: key registers include `WM8737_LEFT_PGA_VOLUME`, `RIGHT_PGA_VOLUME`, `AUDIO_PATH_L/R`, `3D_ENHANCE`, `ADC_CONTROL`, `POWER_MANAGEMENT`, `AUDIO_FORMAT`, `CLOCKING`, `MIC_PREAMP_CONTROL`, `MISC_BIAS_CONTROL`, `NOISE_GATE`, `ALC1-3`, and `RESET`. Important masks include LVU/RVU, input selectors, mic boost, power bits for VMID/VREF/PGA/ADC/AIF, format bits, MCLK divide/sample-rate bits, mic bias/preamp controls, and ALC parameters.

Control flow: no executable code; `wm8737.c` uses the masks for controls, DAPM widgets, bias updates, format selection, and clocking. State/persistence is driven by regmap defaults and update-bit preservation.

Dependencies and integration points: included only by the WM8737 implementation. Risks include generated-header drift, especially for power/bias fields where incorrect masks affect regulator sequencing and audible pops. Test signals include compile coverage and runtime exercise of each field group through controls, DAPM route changes, DAI format/hw_params, and bias state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8737.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8741.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8741.c

Purpose: ALSA SoC playback driver for the WM8741 stereo DAC. It supports I2C and SPI control, regulator-managed supplies, differential output mode platform/DT configuration, sample-rate constraints from MCLK, word-length and oversampling programming, soft mute, volume controls selected by stereo/mono differential mode, and DAPM output routes.

Important APIs/types/functions: `struct wm8741_priv` stores platform data, regmap, two supplies, sysclk, and the active sysclk constraint list. `wm8741_set_dai_sysclk()` maps supported MCLK values to constraint lists. `wm8741_startup()` installs constraints; `wm8741_hw_params()` requires sysclk, validates rate, programs IWL and OSR mode; `wm8741_set_dai_fmt()` supports slave I2S/right/left/DSP formats and clock inversion; `wm8741_configure()` applies diff mode and latches VU bits; `wm8741_add_controls()` chooses stereo or mono controls.

Control flow: bus probe allocates private data, requests supplies, creates regmap, reads `diff-mode` from OF or platform data, stores drvdata, and registers the component. Component probe enables supplies, resets, configures diff mode/VU, adds controls, and leaves supplies enabled until remove. Resume syncs the cache when PM is enabled.

State and persistence: sysclk constraints and diff mode persist per device. Register cache uses MAPLE; no volatile callback is declared for reset. Dependencies include ALSA SoC, regmap, regulators, OF/property/platform data, I2C/SPI.

Risks: `diff_mode` defaults to zero, which is valid stereo, but invalid DT values fail component probe. `hw_params()` hard-requires `set_sysclk()`. Reset is in-range but not marked volatile. Test signals include each supported MCLK constraint list, no-sysclk failure, diff-mode control selection, I2C/SPI probes, regulator cleanup, resume cache sync, and mute/format/width programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8741.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8741.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8741.h

Purpose: register, field, and platform-data definitions for the WM8741 DAC driver. It describes attenuation, volume, format, filter, mode, reset, and additional-control registers and exposes differential output mode values.

Important APIs/types/functions: register constants include `WM8741_DACLLSB_ATTENUATION`, `DACLMSB_ATTENUATION`, `DACRLSB_ATTENUATION`, `DACRMSB_ATTENUATION`, `VOLUME_CONTROL`, `FORMAT_CONTROL`, `FILTER_CONTROL`, `MODE_CONTROL_1`, `MODE_CONTROL_2`, `RESET`, and `ADDITIONAL_CONTROL_1`. Field masks cover volume update bits, attenuation fields, soft mute, zero flags, format/word length, powerdown, filter/deemphasis/DSD options, OSR/rate/mode, differential mode, and DSD additional controls. `struct wm8741_platform_data` carries `diff_mode`.

Control flow: no executable logic. The C driver reads `diff_mode`, validates it against the mode constants, and uses masks in DAI/control programming.

State and persistence: constants determine cached register range and update-bit behavior. Dependencies include `u32` from kernel types through normal include context.

Risks: typo comments do not affect behavior, but incorrect `DIFF` constants would change output topology and exposed mixer controls. Test signals include DT/platform-data diff-mode paths, all volume update masks, format/hw_params field writes, and datasheet comparison for max register `0x20`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8741.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8750.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8750.c

Purpose: ALSA SoC driver for WM8750/WM8987 stereo codec with playback, capture, analog routing, mixer, ALC/noise gate, EQ/3D, and multiple outputs. It supports I2C/SPI control over cached 7-bit/9-bit regmap and one bidirectional `wm8750-hifi` DAI.

Important APIs/types/functions: `struct wm8750_priv` stores selected sysclk. The large control set exposes volumes, switches, mux enums, ALC, deemphasis, ADC polarity, bypass, and output controls. DAPM widgets/routes model left/right/mono mixers, output PGAs, DACs, ADCs, mic bias, line/PGA/differential muxes, OUT3, and VREF. `coeff_div` maps supported MCLK/rate pairs to sample-rate register fields. DAI ops are `wm8750_pcm_hw_params()`, `wm8750_mute()`, `wm8750_set_dai_fmt()`, and `wm8750_set_dai_sysclk()`.

Control flow: bus probe allocates private data, initializes regmap, stores drvdata, and registers the component. Component probe resets and latches update bits for DAC/output/input volumes. `set_sysclk()` accepts common MCLKs; `hw_params()` programs word length and, if coefficient lookup succeeds, SRATE. Bias transitions sync cache on OFF-to-STANDBY, perform a 1 s VMID charge at 5 kOhm, then settle to 500 kOhm/VREF or power down.

State and persistence: sysclk is per-device; register cache carries write-only state. Dependencies include ALSA SoC, regmap, I2C/SPI, OF matching for `wlf,wm8750` and `wlf,wm8987`.

Risks: `hw_params()` returns success even when coefficient lookup fails, leaving SRATE unchanged after logging. One ALC noise-gate enum uses `wm8750_enum[4]`, which names a 3D cutoff rather than `ng_type`, suggesting a control-index bug. Test signals include route power paths, coefficient failures, supported formats/rates, bias ramp timing, reset/VU bits, both bus paths, and WM8987 compatible matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8750.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8750.h

Purpose: register-address and sysclk definitions for the WM8750/WM8987 codec driver. It names the analog/digital controls, power registers, mixers, output volumes, and cache range used by `wm8750.c`.

Important APIs/types/functions: constants cover input/output volume registers, ADCDAC, IFACE, SRATE, left/right DAC and ADC volumes, bass/treble/3D/ALC/noise gate, additional controls, power registers, ADC input muxes, output mixer registers, output volumes, and `WM8750_SYSCLK`. `WM8750_CACHE_REGNUM` records the legacy cache count.

Control flow: no executable code; the implementation uses the addresses for regmap defaults, controls, DAPM widgets/routes, reset, bias, and DAI callbacks.

State and persistence: addresses determine the cached register surface and max register (`WM8750_MOUTV`). Dependencies are none beyond normal kernel inclusion context.

Risks: the header intentionally contains only addresses, so masks are magic values in the implementation. Mismatched constants would affect a wide analog routing surface. Test signals include compile coverage, reset and cache defaults across the max register, and exercising controls for every declared register group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8750.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8753.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8753.c

Purpose: large ALSA SoC driver for WM8753, a low-power stereo codec with an integrated voice PCM interface. It exposes dual DAIs (`wm8753-hifi` and `wm8753-voice`), fast DAI mode switching, extensive analog routing, PLLs, clock dividers, playback/capture/voice controls, delayed VMID charge behavior, and I2C/SPI control using cached write-only regmap.

Important APIs/types/functions: `struct wm8753_priv` stores regmap, hifi/voice sysclks, saved DAI formats, current `dai_func`, and delayed `charge_work`. `wm8753_get_dai()`/`wm8753_set_dai()` implement a busy-checked DAI mode control and rewrite stored hifi/voice formats after mode changes. `pll_factors()` and `wm8753_set_dai_pll()` program PLL1/PLL2. `wm8753_set_dai_sysclk()`, `wm8753_set_dai_clkdiv()`, `wm8753_i2s_hw_params()`, and `wm8753_pcm_hw_params()` configure clocking and sample widths. Multiple helpers split hifi/voice/ADC format programming by DAI mode.

Control flow: bus probe allocates private data, initializes regmap, stores drvdata, and registers both DAIs. Component probe initializes delayed work, resets, sets default DAI mode 0, and latches VU bits across DAC/ADC/output/input registers. Runtime DAI calls configure PLL/sysclk/format/params; the DAI mode kcontrol refuses changes while active. Bias OFF cancels delayed work and powers down; STANDBY schedules a configurable capacitor charge before switching VMID to 500 kOhm; PREPARE flushes the work.

State and persistence: hifi/voice formats and DAI mode persist across mode switches; sysclk/pcmclk are separate; regcache syncs on resume. Dependencies include ALSA SoC, regmap, I2C/SPI, delayed work, module parameter `caps_charge`, and machine-driver clock setup.

Risks: complex mode-dependent clock/format interactions can regress easily; DAI mode changes are blocked only while component active. PLL factor warnings do not fail unsupported N ranges. Voice DAI may be externally connected and not CPU-readable despite ALSA exposure. Test signals include all four DAI modes, busy rejection, hifi and voice stream params, PLL disable/enable, divider IDs, delayed-work cancellation/flush, resume cache sync, route coverage, and both control buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm8753.c -->
