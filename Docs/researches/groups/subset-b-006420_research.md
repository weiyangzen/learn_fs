# subset-b-006420 codec research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ab8500-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ab8500-codec.c

## Purpose
ASoC component driver for the ST-Ericsson AB8500 PMIC audio codec. It exposes the AB8500 audio register bank through a custom regmap, declares a large DAPM graph for analog/digital microphone, headset, earpiece, lineout, handsfree, vibrator, sidetone, ANC, and TDM paths, and registers two DAIs for playback and capture on the IF0 digital interface.

## Important APIs, Types, and Functions
The private `struct ab8500_codec_drvdata` stores the audio regmap, a control mutex, and sidetone FIR state. `ab8500_codec_read_reg()` and `ab8500_codec_write_reg()` bridge regmap operations to `abx500_get_register_interruptible()` and `abx500_set_register_interruptible()` on the `AB8500_AUDIO` bank. `sid_status_control_get()` and `sid_status_control_put()` implement a user control for applying the sidetone FIR sequence. `ab8500_audio_setup_mics()`, `ab8500_audio_set_ear_cmv()`, and `ab8500_audio_init_audioblock()` perform probe-time PMIC/audio setup. DAI operations are `ab8500_codec_set_dai_fmt()` and `ab8500_codec_set_dai_tdm_slot()`. The platform probe allocates state, initializes regmap, and calls `devm_snd_soc_register_component()`.

## Control Flow
Platform probe creates driver data and the regmap, then ASoC component probe parses device-tree microphone and earpiece properties, adds microphone bias routes, configures microphone mode bits, initializes the audio block through sysctrl, writes hardware default overrides, disables the ANC configure input pin, and initializes the control mutex. Runtime DAI setup first validates provider/consumer mode and clock gating, then programs IF0 format, polarity, bit delay, word length, slot count, and TDM DA/AD slot mapping. Sidetone application checks the hardware busy bit, writes zeroed FIR coefficients across the sidetone address space, toggles the FIR set bit, and marks the in-memory state configured.

## State and Persistence
Persistent state is hardware register state plus `sid_status` in driver memory. The regmap has custom read/write callbacks but no cache policy in this file, so hardware access depends on AB8500 MFD calls. Device-tree choices for mic bias, mic type, and earpiece common-mode voltage are applied at probe and not reread. The sidetone state is protected by `ctrl_lock`.

## Dependencies and Integration Points
This file depends on AB8500 MFD/sysctrl APIs, ASoC component/DAI/DAPM APIs, device tree, and the local `ab8500-codec.h` register map. Machine drivers interact through DAI format and TDM slot callbacks plus ASoC controls and routes. Board data is expressed through `stericsson,*` device-tree properties and AB8500 platform devices.

## Risks
The DAPM/control surface is broad and register-bit dense, so bitfield mismatches can silently route or power the wrong path. TDM slot handling only accepts masks within 8 bits and only maps 0, 1, 2, or 8 active slots; other valid-looking masks fail. `ffs()`/`fls()` values are one-based, so slot math must stay aligned with AB8500 register encoding. The sidetone write path zeros coefficients rather than loading user-provided values and returns `-EIO` for unsupported enum writes. Device-tree property spelling includes `stericsson,earpeice-cmv`, which may be externally depended upon despite the typo.

## Test Signals
Useful tests are component probe on AB8500 hardware or emulated regmap callbacks, DAPM route enumeration, ALSA control read/write for sidetone and gains, DAI format matrix tests for I2S/DSP_A/DSP_B plus inversion/provider modes, TDM slot tests for 2/4/8/16 total slots and invalid masks, and boot logs for AB8500 MFD/sysctrl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ab8500-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ab8500-codec.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ab8500-codec.h

## Purpose
Local register and bitfield definition header for the AB8500 codec driver. It maps the AB8500 audio bank register addresses, supported PCM capabilities, TDM slot helper macros, and bit positions/ranges used by controls, DAPM widgets, and DAI setup in `ab8500-codec.c`.

## Important APIs, Types, and Functions
There are no functions or types. Key macros include `AB8500_SUPPORTED_RATE`, `AB8500_SUPPORTED_FMT`, `AB8500_ADSLOTSEL(slot)`, `AB8500_MASK_SLOT(slot)`, register address constants from `AB8500_POWERUP` through `AB8500_AUDREV`, and many field constants for analog power, digital microphone, digital interface, class-D, ANC, sidetone FIR, and burst FIFO registers.

## Control Flow
The header has no executable control flow. It influences runtime behavior through macro expansion in register writes, DAPM control declarations, TDM slot selection, ANC and sidetone controls, and DAI format programming.

## State and Persistence
It defines hardware state layout rather than storing state. The register constants describe persistent PMIC audio-bank state, while masks and max values constrain ALSA controls and driver validation.

## Dependencies and Integration Points
The header assumes ALSA PCM rate/format constants are available before inclusion. It is tightly coupled to the AB8500 silicon audio bank and to `ab8500-codec.c`; changing macros here changes the hardware ABI of the driver.

## Risks
Because most constants are raw bit positions, a single off-by-one or wrong mask can corrupt unrelated codec settings. Slot helper macros rely on the AB8500 even/odd nibble layout. The file exposes only local constants, so external users should not include it as a stable API.

## Test Signals
Compile coverage catches missing macros, but meaningful validation requires register-write inspection from AB8500 DAI format, TDM slot, ANC, sidetone, and mixer-control tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ab8500-codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ac97.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ac97.c

## Purpose
Generic ASoC AC97 codec wrapper. It registers a simple stereo playback/capture DAI, creates an AC97 bus and mixer instance, and delegates rate programming and power management to the legacy ALSA AC97 core.

## Important APIs, Types, and Functions
`ac97_prepare()` programs either `AC97_PCM_FRONT_DAC_RATE` or `AC97_PCM_LR_ADC_RATE` using `snd_ac97_set_rate()`. `ac97_soc_probe()` creates an `snd_ac97_bus`, instantiates the mixer with `snd_ac97_mixer()`, and stores `struct snd_ac97` as component driver data. Optional PM callbacks call `snd_ac97_suspend()` and `snd_ac97_resume()`. `ac97_probe()` registers the component and `ac97-hifi` DAI.

## Control Flow
Platform probe registers the component. Component probe creates AC97 bus/mixer state. At PCM prepare, the stream direction selects DAC or ADC rate register and writes the runtime rate. PM suspend/resume forwards directly to AC97 core helpers.

## State and Persistence
The component stores an AC97 core pointer. Hardware mixer and rate state live in AC97 registers and are managed by the AC97 subsystem. There is no local regmap or custom cache.

## Dependencies and Integration Points
Depends on `soc_ac97_ops`, ALSA AC97 core, ASoC component/DAI APIs, and optional OF compatible `realtek,alc203`. Machine drivers bind to `platform:ac97-codec` or device-tree/platform registration.

## Risks
The driver is intentionally generic, so nonstandard AC97 codecs may need codec-specific controls not represented here. Probe can fail if global AC97 ops or bus creation is not provided by the platform. Rate support is `SNDRV_PCM_RATE_KNOT`, so runtime rate programming must be accepted by the AC97 link and codec.

## Test Signals
Boot/probe, mixer enumeration, AC97 playback and capture at multiple rates, and suspend/resume on systems with `CONFIG_PM` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad1836.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad1836.c

## Purpose
SPI ASoC codec driver for Analog Devices AD1835/AD1836/AD1837/AD1838/AD1839 family codecs. It registers the correct DAI capability for each chip variant, initializes DAC/ADC control registers, and exposes ALSA controls for DAC volume/mute, ADC mute, ADC high-pass, de-emphasis, and AD1836-specific ADC2 capture gain.

## Important APIs, Types, and Functions
`enum ad1836_type` selects channel counts. `struct ad1836_priv` stores variant type and regmap. `ad1836_set_dai_fmt()` accepts only DSP_A, inverted bit/frame clocks, and codec clock-provider mode. `ad1836_hw_params()` maps PCM width to AD1836 word-length fields for DAC and ADC. `ad1836_probe()` writes default codec setup and dynamically adds variant-specific controls, DAPM widgets, and routes based on DAC/ADC count. `ad1836_suspend()`, `ad1836_resume()`, and `ad1836_remove()` reset or restore ADC serial format. `ad1836_spi_probe()` creates a 4-bit register/12-bit value SPI regmap and registers the selected DAI.

## Control Flow
SPI probe allocates state, initializes regmap, stores variant ID from the SPI device table, and registers one component/DAI. Component probe writes default DAC/ADC power, serial, mute, and volume registers, configures AD1836 ADC3 differently from sibling parts, then installs the control and DAPM elements sized for that variant. PCM configuration validates the single supported serial mode and updates word length on hw_params.

## State and Persistence
Driver state is the variant enum and regmap pointer. Hardware state is cached with `REGCACHE_MAPLE` using `ad1836_reg_defaults`. PM suspend/resume manipulates ADC serial format, and remove leaves the chip clock mode reset.

## Dependencies and Integration Points
Depends on SPI, regmap, ASoC controls/DAPM/DAI APIs, and local register definitions from `ad1836.h`. Machine drivers must configure compatible DSP_A/TDM-style DAI format and 48 kHz streams.

## Risks
The accepted DAI format is narrow; unsupported machine-driver formats fail with `-EINVAL`. Register defaults include volume entries using zero-based `AD1836_DAC_L_VOL(0)` while controls are one-based, so future edits must keep macro semantics clear. The driver assumes register writes succeed in probe and does not check every initialization write.

## Test Signals
SPI probe for each ID table variant, ALSA control counts per variant, DAPM route counts, 16/20/24/32-bit hw_params, invalid DAI format rejection, and PM suspend/resume register-cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad1836.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad1836.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad1836.h

## Purpose
Register-map header for the AD1836-family SPI codec driver. It names DAC/ADC control registers, mute and volume helpers, serial format masks, and word-length encodings used by `ad1836.c`.

## Important APIs, Types, and Functions
There are no functions or structs. Key macros are `AD1836_DAC_CTRL1`, `AD1836_DAC_CTRL2`, `AD1836_ADC_CTRL1..3`, `AD1836_DAC_L_VOL(x)`, `AD1836_DAC_R_VOL(x)`, `AD1836_MUTE_LEFT(x)`, `AD1836_MUTE_RIGHT(x)`, `AD1836_ADC_AUX`, and word-length constants for 16/20/24-bit operation.

## Control Flow
No executable flow. The macro definitions drive control declarations, probe defaults, suspend/resume serial-format updates, and hw_params width programming.

## State and Persistence
The file describes codec register state and does not persist anything itself. Its constants define the hardware state layout cached by regmap in the C driver.

## Dependencies and Integration Points
It is private to the AD1836 driver and should track the AD183x register protocol exactly. The one-based mute macros are called out in a comment and are important for ALSA control indexing.

## Risks
Changing volume/mute helper semantics can break controls for all AD183x variants. Word-length and serial-format masks are shared by runtime and PM code, so incorrect values cause non-obvious audio bus failures.

## Test Signals
Compile checks plus hw_params and control-read/write tests across all AD183x variants are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad1836.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-i2c.c

## Purpose
I2C bus glue for AD1936/AD1937 codecs. It configures the shared AD193x regmap for 8-bit I2C register and value fields and delegates component registration to the shared `ad193x_probe()`.

## Important APIs, Types, and Functions
`ad193x_id[]` maps `"ad1936"` and `"ad1937"` to `AD193X`. `ad193x_i2c_probe()` copies `ad193x_regmap_config`, sets `val_bits = 8` and `reg_bits = 8`, creates a devm I2C regmap, and calls `ad193x_probe()`.

## Control Flow
The module registers an `i2c_driver`. Probe performs no chip-specific initialization itself; all codec controls, DAI registration, and default writes happen in `ad193x.c`.

## State and Persistence
No local persistent state. The shared core stores private state on `client->dev`; the regmap owns register cache behavior as configured by the core and bus wrapper.

## Dependencies and Integration Points
Depends on Linux I2C, regmap, ASoC, and `ad193x.h`. It integrates AD1936/AD1937 I2C devices into the shared AD193x ASoC component.

## Risks
This wrapper passes `(uintptr_t)i2c_get_match_data(client)` as the type, but the driver table shown is an `i2c_device_id` table without an OF match table in this file; on legacy ID matching, match data availability should be checked against kernel API behavior. A wrong regmap width prevents all core register access.

## Test Signals
I2C probe with AD1936/AD1937 IDs, regmap bus transactions with 8-bit addresses, and successful shared-core control/DAI registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-spi.c

## Purpose
SPI bus glue for AD193x-family codecs including AD1933/AD1934 DAC-only parts, AD1938/AD1939, and ADAU1328. It configures SPI regmap framing and delegates codec registration to the shared AD193x core.

## Important APIs, Types, and Functions
`ad193x_spi_probe()` fetches the SPI ID, copies `ad193x_regmap_config`, sets 8-bit values, 16-bit register framing, read flag `0x09`, write flag `0x08`, creates a devm SPI regmap, and calls `ad193x_probe()` with the ID's `driver_data`. The SPI ID table selects `AD193X`, `AD1933`, or `AD1934`.

## Control Flow
SPI driver probe only prepares the regmap and variant type. The shared core performs default register writes, DAPM/control setup, and DAI registration, choosing DAC-only DAI for AD1933/AD1934.

## State and Persistence
No bus-wrapper state. Core state and regmap cache live on the SPI device.

## Dependencies and Integration Points
Depends on SPI, regmap, ASoC, and `ad193x.h`. It is the integration path for SPI-attached AD193x/ADAU1328 devices.

## Risks
The regmap flag masks and 16-bit register framing are bus-protocol critical. Missing SPI IDs or wrong driver data will register the wrong DAI shape, especially for DAC-only parts.

## Test Signals
SPI probe per ID, read/write trace validation for command flags, DAC-only registration for AD1933/AD1934, and shared-core DAI/control tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x.c

## Purpose
Shared ASoC codec core for AD193x audio codecs. It defines controls, DAPM widgets/routes, DAI operations, default register initialization, and component registration for both ADC+DAC and DAC-only variants.

## Important APIs, Types, and Functions
`struct ad193x_priv` stores regmap, variant type, and selected sysclk. `ad193x_has_adc()` gates ADC controls/routes and DAI shape. DAI ops include `ad193x_startup()` for 32-bit sample-bit constraint, `ad193x_hw_params()` for rate/word length/PLL input ratio, `ad193x_set_dai_fmt()` for I2S/DSP_A, inversion, and clock-provider bits, `ad193x_set_tdm_slot()` for 2/4/8/16-channel TDM selection, `ad193x_set_dai_sysclk()` for PLL/MCLK source selection, and `ad193x_mute()` for DAC master mute. `ad193x_probe()` is exported for I2C/SPI wrappers.

## Control Flow
Bus wrappers create the regmap and call `ad193x_probe()`. The core allocates state, stores it on the device, and registers either `ad193x_dai` or `ad193x_no_adc_dai`. Component probe writes a default register sequence and conditionally adds ADC controls, widgets, and routes. Runtime setup validates serial format and sysclk, then programs DAC and ADC format registers and sample-rate fields.

## State and Persistence
Private state is `type`, `regmap`, and `sysclk`. The exported `ad193x_regmap_config` only sets `max_register`; wrappers provide bus-specific widths and flags. Hardware defaults are written in component probe rather than represented as a full regcache default table. DAPM route `ad193x_check_pll()` uses `sysclk` to gate SYSCLK from PLL power.

## Dependencies and Integration Points
Depends on ASoC, regmap, and local `ad193x.h`. It is integrated by `ad193x-i2c.c` and `ad193x-spi.c`, and by machine drivers through DAI format, sysclk, and TDM-slot callbacks.

## Risks
`ad193x_set_dai_fmt()` uses `if (fmt & SND_SOC_DAIFMT_DSP_A)` instead of masking and comparing the format field, so future format-bit definitions could interact unexpectedly. `ad193x_hw_params()` lacks a default error for unsupported sample widths, leaving `word_len = 0` for unknown widths. MCLK mode requires exactly 24.576 MHz and input direction. Capture rates are fixed to 48 kHz while playback supports 48/96/192 kHz.

## Test Signals
Core tests should cover ADC and DAC-only variants, sysclk frequencies 12.288/18.432/24.576/36.864 MHz, MCLK mode rejection, DAI format combinations, TDM slot counts, playback rates, capture 48 kHz, 32-bit sample-bit constraints, and mute control writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x.h

## Purpose
Shared public/private header for AD193x core and bus wrappers. It declares variant IDs, the exported regmap config and probe function, register addresses, bit masks, channel-count encodings, and sysclk IDs.

## Important APIs, Types, and Functions
`enum ad193x_type` distinguishes generic ADC+DAC from DAC-only AD1933/AD1934. `ad193x_regmap_config` and `ad193x_probe()` are exported to I2C/SPI wrappers. Macros cover PLL controls, DAC and ADC serial format registers, mute/volume registers, TDM channel encodings, `AD193X_NUM_REGS`, and `AD193X_SYSCLK_PLL/MCLK`.

## Control Flow
No executable flow. The declarations connect bus wrappers to `ad193x.c`; macros drive default writes, DAI ops, controls, and DAPM power bits.

## State and Persistence
Defines the hardware register state layout. Runtime state is held in `struct ad193x_priv` in the C file, not here.

## Dependencies and Integration Points
Includes `<linux/regmap.h>` and forward-declares `struct device`. It is intentionally shared by bus modules and the core driver.

## Risks
The header is the cross-module ABI for AD193x wrappers. Wrong register widths or bit masks affect both SPI and I2C variants. Variant enum values are stored in ID-table `driver_data`, so reordering without updating all tables would break binding.

## Test Signals
Compile all AD193x modules, probe I2C/SPI variants, and exercise core format/sysclk/TDM paths that consume these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad1980.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad1980.c

## Purpose
Obsolete ASoC codec driver for the Analog Devices AD1980 AC97 codec. It provides AD1980-specific AC97 controls, DAPM routing, reset handling, regmap-over-AC97 setup, and a fixed 48 kHz DAI.

## Important APIs, Types, and Functions
`ad1980_readable_reg()` and `ad1980_writeable_reg()` define the AC97 register access policy for regmap. `ad1980_reset()` repeatedly calls `snd_ac97_reset()` with vendor ID matching and writes `AC97_AD_SERIAL_CFG` between attempts to recover 16-slot mode. `ad1980_soc_probe()` creates the AC97 component, initializes regmap, resets the codec, warns on AD1981 ID, unmutes key paths, and powers surround/center/LFE DACs. `ad1980_soc_remove()` frees regmap and AC97 component resources.

## Control Flow
Platform probe registers one component/DAI. Component probe creates AC97 state, initializes the regmap, performs reset/recovery, applies initial unmute and power settings, then returns ready. Remove tears down the AC97 component. There are no DAI ops; the DAI advertises fixed AC97 formats and 48 kHz playback/capture.

## State and Persistence
Regmap uses `REGCACHE_MAPLE` with explicit AC97 defaults and AC97 volatile handling. Component driver data stores the `snd_ac97` pointer. Hardware state persists in AC97 registers until reset/remove.

## Dependencies and Integration Points
Depends on ASoC, ALSA AC97 core, regmap AC97 helpers, and platform registration under `"ad1980"`. Machine drivers consume `ad1980-hifi`.

## Risks
The file states the chip is discontinued and unsupported. Reset recovery is specialized and may hide link timing issues. Vendor matching uses a mask and logs AD1981 as partially supported. Many initialization writes ignore return status after reset.

## Test Signals
AC97 reset/vendor detection on real hardware, regmap readable/writeable tests, mixer control enumeration, fixed 48 kHz playback/capture, surround/center/LFE output smoke tests, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad1980.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad73311.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad73311.c

## Purpose
Minimal ASoC platform codec driver for AD73311 voiceband codec use. It exposes mono 8 kHz 16-bit playback and capture streams and a simple DAPM graph for analog input/output pins.

## Important APIs, Types, and Functions
The file defines DAPM widgets for `VINP`, `VINN`, `VOUTN`, and `VOUTP`, routes those pins to generic `Capture` and `Playback` streams, declares one `ad73311-hifi` DAI, and registers the component in `ad73311_probe()`.

## Control Flow
Platform probe calls `devm_snd_soc_register_component()`. There are no DAI ops, register writes, or power callbacks in this file; runtime behavior is limited to ASoC stream constraints and DAPM pin routing.

## State and Persistence
No private state, no regmap, and no cached hardware registers. Any actual AD73311 control-word programming must be performed elsewhere, likely by board or serial-interface code using definitions from `ad73311.h`.

## Dependencies and Integration Points
Depends on ASoC and platform-driver binding named `"ad73311"`. Includes `ad73311.h`, though this C file does not program those register macros.

## Risks
The driver is only a skeleton codec representation. It cannot configure AD73311 control registers, sample modes, gains, or power state by itself. Systems expecting full codec initialization need additional platform support.

## Test Signals
Probe, DAI constraint visibility, mono 8 kHz stream startup, and DAPM route enumeration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad73311.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad73311.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ad73311.h

## Purpose
Register/control-word macro header for AD73311. It defines the 16-bit command flags and control register bitfields for mode, clock dividers, power, gains, data advance, and serial options.

## Important APIs, Types, and Functions
There are no functions or types. Important macros include `AD_CONTROL`, `AD_DATA`, `AD_READ`, `AD_WRITE`, `CTRL_REG_A..F`, mode constants such as `REGA_MODE_PRO`, power bits such as `REGC_PUADC`, gain helpers `REGD_IGS()` and `REGD_OGS()`, and serial options like `REGF_SEEN`, `REGF_INV`, and `REGF_ALB`.

## Control Flow
No executable flow. These macros are intended to construct AD73311 control words for code that programs the serial codec.

## State and Persistence
The header describes hardware control state but stores none. The current `ad73311.c` driver does not use the macros to persist configuration.

## Dependencies and Integration Points
It is included by `ad73311.c` and can support board/codec setup code that sends AD73311 commands over a serial bus.

## Risks
Macros do not validate ranges beyond masking helper arguments. Since the C driver does not use them, drift between intended hardware setup and actual runtime behavior is possible.

## Test Signals
Any code using this header should be tested by inspecting emitted 16-bit control words and verifying codec mode, power, and gain behavior on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ad73311.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.c

## Purpose
Shared helper module for ADAU-family codec drivers. It currently exports a single PLL configuration calculator used by drivers such as ADAU1372 and ADAU1373.

## Important APIs, Types, and Functions
`adau_calc_pll_cfg(freq_in, freq_out, regs[5])` computes five PLL register bytes. It handles disabled output by zeroing all fields, integer ratios by setting `r` only, and fractional ratios by reducing the input clock with a divider, calculating fractional `n/m` with `gcd()`, and setting the fractional-mode bit.

## Control Flow
The function validates output frequency and ratio constraints after computing `r`, `n`, `m`, and `div`. It returns `-EINVAL` for unsupported divisors, feedback ratios outside 2..8, or 16-bit fraction fields. On success it writes bytes `[m_hi, m_lo, n_hi, n_lo, control]`.

## State and Persistence
No persistent state. The caller owns the output buffer and writes the resulting bytes to hardware.

## Dependencies and Integration Points
Depends on Linux `gcd`, `DIV_ROUND_UP`, and module export infrastructure. `EXPORT_SYMBOL_GPL(adau_calc_pll_cfg)` makes it available to other GPL codec modules.

## Risks
The function assumes `freq_in` is nonzero when `freq_out` is nonzero; callers must validate or provide a real input clock. Integer division choices directly affect PLL lock behavior, so boundary frequencies need hardware validation.

## Test Signals
Unit-style tests for integer ratio, fractional ratio, disabled output, invalid high/low ratio, excessive divider, and zero input protection in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.h

## Purpose
Header declaring shared ADAU PLL helper functionality.

## Important APIs, Types, and Functions
Declares `adau_calc_pll_cfg(unsigned int freq_in, unsigned int freq_out, uint8_t regs[5])`, which fills five hardware PLL configuration bytes.

## Control Flow
No executable flow. The declaration is consumed by ADAU codec drivers before calling into `adau-utils.c`.

## State and Persistence
No state. The output buffer belongs to the caller.

## Dependencies and Integration Points
Requires `uint8_t` to be available from included kernel headers in callers. It is included by ADAU-family codec drivers that need PLL programming.

## Risks
The header does not document input constraints; callers need to know the helper can reject unsupported ratios and that nonzero output requires nonzero input.

## Test Signals
Build coverage in all users and direct tests of the implementation function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-i2c.c

## Purpose
I2C bus wrapper for the ADAU1372 codec core. It creates an I2C regmap with the shared ADAU1372 configuration and delegates all codec setup to `adau1372_probe()`.

## Important APIs, Types, and Functions
`adau1372_i2c_probe()` calls `adau1372_probe(&client->dev, devm_regmap_init_i2c(...), NULL)`. The ID table contains `"adau1372"`, and the I2C driver uses the shared `adau1372_of_match` table.

## Control Flow
I2C probe is a one-step delegation. There is no remove callback because all resources are devm-managed and the shared component handles bias/power callbacks.

## State and Persistence
No local state. The core stores private state on the device and owns regcache behavior.

## Dependencies and Integration Points
Depends on I2C, regmap, ASoC headers, and `adau1372.h`. It binds both legacy I2C ID and OF compatible devices.

## Risks
Any I2C regmap initialization error is propagated through the core's `IS_ERR(regmap)` check. I2C mode does not need a switch-mode callback, unlike SPI.

## Test Signals
I2C probe, OF match with `adi,adau1372`, register access with 16-bit addresses/8-bit values, and shared-core DAI/control registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-spi.c

## Purpose
SPI bus wrapper for the ADAU1372 codec core. It switches the chip into SPI mode, configures SPI regmap read flags, and delegates to `adau1372_probe()`.

## Important APIs, Types, and Functions
`adau1372_spi_switch_mode()` performs three dummy `spi_w8r8()` reads because the codec enters SPI mode when CLATCH is pulled low three times. `adau1372_spi_probe()` copies `adau1372_regmap_config`, sets `read_flag_mask = 0x1`, initializes a SPI regmap, and passes the switch callback to the core.

## Control Flow
SPI probe prepares the bus-specific regmap and callback. The core calls the switch callback during power enable before register access.

## State and Persistence
No local state. SPI mode selection is a hardware side effect performed at runtime by the core's power sequence.

## Dependencies and Integration Points
Depends on SPI, regmap, ASoC, OF/ID tables, and `adau1372.h`. It binds `"adau1372"` SPI devices and `adi,adau1372` OF nodes.

## Risks
Ignoring return values from dummy reads means a failed SPI-mode switch may surface later as regmap failures. The read flag is protocol-critical.

## Test Signals
SPI probe, logic-analyzer confirmation of three dummy reads before register access, shared-core power-up, PLL lock, and DAI operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372.c

## Purpose
Shared ASoC codec core for ADAU1372. It provides controls and DAPM routing for four ADC/PGA inputs, digital mics, ASRCs, eight serial inputs/outputs, two DACs, headphone outputs, clock/PLL management, power sequencing, and DAI operations.

## Important APIs, Types, and Functions
`struct adau1372` stores regmap, optional bus switch callback, PLL/power/clock-provider flags, rate constraints, slot width, MCLK, powerdown GPIO, and device pointer. DAI ops are `adau1372_set_dai_fmt()`, `adau1372_hw_params()`, `adau1372_set_tdm_slot()`, `adau1372_set_tristate()`, and `adau1372_startup()`. Power helpers are `adau1372_enable_pll()`, `adau1372_set_power()`, and `adau1372_set_bias_level()`. `adau1372_setup_pll()` uses `adau_calc_pll_cfg()`. `adau1372_probe()` is exported to I2C/SPI wrappers. The exported `adau1372_regmap_config` includes defaults, volatile PLL status, and maple cache.

## Control Flow
Bus wrappers call `adau1372_probe()` with a regmap and optional switch callback. The core obtains `mclk` and optional `powerdown` GPIO, computes whether the external clock can be divided directly or needs PLL setup to reach 49.152 MHz, sets regcache cache-only before clocks are available, preloads mux/mode defaults, and registers the component/DAI. Bias transition to standby enables MCLK, releases powerdown, switches SPI mode if needed, enables PLL if configured, selects clock source, syncs regcache, and marks enabled. Bias off powers down through GPIO or clock bits, disables MCLK, marks regcache dirty if hardware reset occurred, and enters cache-only mode.

## State and Persistence
Driver state tracks power enabled, PLL use, clock-provider mode, current rate constraint mask, and slot width. Register state is cached while the chip is inaccessible and synchronized after clocks are enabled. `ADAU1372_REG_PLL(5)` is volatile for PLL lock status.

## Dependencies and Integration Points
Depends on clk, optional GPIO, regmap, ASoC, `adau-utils`, and bus wrappers. Machine drivers configure serial format and TDM slot layout; OF supplies `mclk`, optional powerdown GPIO, and compatible matching through `adau1372_of_match`.

## Risks
PLL lock waits only three 1-2 ms iterations; slow hardware or clock issues return timeout. Rate constraints change with TDM slot count and provider mode, so machine-driver ordering matters. `regmap_write(SOUT_CTRL, ~tx_mask)` relies on hardware-inverted masking and writes an unmasked complement into an 8-bit register. Power sequencing is sensitive to cache-only state and GPIO reset side effects.

## Test Signals
Probe with 12.288 MHz, 24.576 MHz, and arbitrary PLL-driven MCLKs; power bias transitions; PLL timeout path; I2S and TDM2/4/8 slot constraints; 16/24/32-bit slot widths; tristate control; DAPM route activation for ADC/DMIC/ASRC/DAC paths; SPI and I2C wrapper coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372.h

## Purpose
Shared header connecting ADAU1372 bus wrappers to the core driver.

## Important APIs, Types, and Functions
Forward-declares `struct device`, exports `adau1372_of_match`, declares `adau1372_probe(struct device *dev, struct regmap *regmap, void (*switch_mode)(struct device *dev))`, and exports `adau1372_regmap_config`.

## Control Flow
No executable flow. Bus wrappers call `adau1372_probe()` with bus-specific regmaps and optional switch-mode callbacks.

## State and Persistence
No state. Core state is allocated in `adau1372.c`; regmap configuration is declared here for wrapper use.

## Dependencies and Integration Points
Includes `<linux/regmap.h>` and is used by both I2C and SPI wrappers.

## Risks
This header is the module boundary for ADAU1372. Signature or regmap-config changes must be coordinated with both wrappers.

## Test Signals
Build all ADAU1372 modules and probe both buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1373.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1373.c

## Purpose
I2C ASoC codec driver for ADAU1373. It implements a large analog/digital routing graph, three stereo AIF DAIs, PLL and sample-rate-divider setup, DRC and DSP controls, firmware/device-property parsing, reset handling, and component registration.

## Important APIs, Types, and Functions
`struct adau1373_dai` stores per-DAI clock source, sysclk, SRC enable flag, and clock-provider mode. `struct adau1373` stores regmap, three DAI states, input/output topology flags, DRC settings, and mic-bias selections. DAI ops are `adau1373_hw_params()`, `adau1373_set_dai_fmt()`, and `adau1373_set_dai_sysclk()`. Component ops include `adau1373_set_pll()`, `adau1373_probe()`, `adau1373_set_bias_level()`, and `adau1373_resume()`. `adau1373_parse_fw()` reads device properties for differential inputs, lineout mode, mic-bias voltages, and DRC byte arrays.

## Control Flow
I2C probe allocates state, creates the regmap, obtains optional powerdown GPIO, performs hardware or software reset, parses firmware properties, and registers the component with three DAIs. Component probe loads configured DRC blocks, adds DRC controls, programs input/output topology, programs mic-bias fields, conditionally exposes Lineout2 controls, and forces ADC reset/peak-detect bits. Machine drivers configure PLLs through component `.set_pll`, choose each DAI sysclk source, then hw_params validates sysclk-to-rate ratios, decides whether SRC is needed, programs BCLK dividers, and writes word length. DAPM route predicates gate AIF clocks and SRC paths based on per-DAI state.

## State and Persistence
State is split between device properties retained in `struct adau1373`, per-DAI runtime clock settings, and hardware registers cached by `REGCACHE_MAPLE`. Resume syncs regcache. Bias standby/off toggles the global power enable bit. DRC settings are copied from firmware properties and written at component probe.

## Dependencies and Integration Points
Depends on I2C, GPIO descriptors, device property APIs, regmap, ASoC, and `adau-utils`. The local `adau1373.h` provides PLL source and clock IDs for machine drivers. Integrates through OF compatible `adi,adau1373`, optional `powerdown` GPIO, `adi,*` topology properties, ASoC controls, and three named DAIs.

## Risks
The driver has many muxes and DAPM route predicates, so per-DAI sysclk/SRC state must be set before routes are expected to power. PLL setup validates input/output ranges but relies on caller-provided frequencies. Firmware DRC arrays must be exact multiples of 13 bytes and at most three blocks. There is a duplicated `ADAU1373_FDSP_SEL2` default entry where `FDSP_SEL3` may have been intended, which should be reviewed before relying on defaults.

## Test Signals
Probe with and without powerdown GPIO, software reset path, property parsing for differential inputs/mic-bias/DRC, PLL source/range validation, each DAI's I2S/left/right/DSP_B formats, supported sysclk-to-rate ratios, DAPM route activation with/without SRC, suspend/resume regcache sync, and mixer/control enumeration including optional Lineout2 and DRC controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1373.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1373.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1373.h

## Purpose
Machine-driver-facing enum header for ADAU1373 PLL and clock source IDs.

## Important APIs, Types, and Functions
Defines `enum adau1373_pll_src` with MCLK, BCLK, LRCLK, and GPIO PLL input choices, `enum adau1373_pll` for PLL1/PLL2, and `enum adau1373_clk_src` for selecting PLL1 or PLL2 as DAI sysclk.

## Control Flow
No executable flow. Enum values are consumed by `adau1373_set_pll()` and `adau1373_set_dai_sysclk()` in the C driver.

## State and Persistence
No state. Values become hardware register fields when passed to the driver callbacks.

## Dependencies and Integration Points
Included by ADAU1373 machine drivers and the codec driver. The enum numeric values are hardware encodings and part of the callback contract.

## Risks
Reordering enum values would break existing machine-driver clock setup. The header does not document valid frequency ranges; callers must follow the C driver's validation.

## Test Signals
Machine-driver builds and runtime PLL/sysclk setup across each advertised clock source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1373.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1701.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1701.c

## Purpose
I2C ASoC driver for ADAU1701/ADAU1401 SigmaDSP codecs. It provides custom-width register access, SigmaDSP firmware loading with safeload support, regulator/reset/PLL-mode GPIO handling, DAI format and hw_params programming, and basic DAC/ADC DAPM.

## Important APIs, Types, and Functions
`struct adau1701` stores reset GPIO, PLL-mode GPIO array, current DAI format, PLL clock divider, sysclk, regmap, I2C client, pin configuration, SigmaDSP handle, and regulators. `adau1701_reg_write()` and `adau1701_reg_read()` implement variable-size I2C register access for regmap. `adau1701_safeload()` writes SigmaDSP safeload data/address registers and triggers IST. `adau1701_reset()` resets SigmaDSP, sets PLL mode GPIOs, toggles reset, optionally loads firmware with `sigmadsp_setup()`, initializes DAC/DSP registers, marks regcache dirty, and syncs. DAI/component callbacks cover sysclk, DAI format, hw_params, mute, startup parameter restriction, bias, probe/remove, and PM.

## Control Flow
I2C probe obtains regulators, temporarily enables them, creates regmap, reads optional OF `adi,pll-clkdiv` and `adi,pin-config`, obtains reset and PLL-mode GPIOs, creates a SigmaDSP instance for `adau1701.bin`, registers the component, then disables regulators until component probe. Component probe attaches SigmaDSP, enables regulators, sets an unset PLL divider sentinel, resets the chip without firmware until stream parameters are known, and writes pin configuration. On hw_params, if the MCLK/LRCLK divider changes, the chip is reset and firmware is loaded for the stream rate; sample-rate and word-length fields are then programmed.

## State and Persistence
Driver state tracks sysclk, DAI format, current PLL divider, pin config, and firmware handle. Regmap uses `REGCACHE_MAPLE` with custom IO and volatile DSP/DAC registers. Hardware reset clears device state, so reset paths mark the cache dirty and sync. Regulators are enabled during active component lifetime and disabled on remove/suspend or after failed probe.

## Dependencies and Integration Points
Depends on I2C, GPIO, regulators, regmap, ASoC, OF, and SigmaDSP firmware infrastructure. Machine drivers call component `.set_sysclk` and configure DAI format. Firmware file `adau1701.bin` controls DSP program behavior.

## Risks
Firmware loading is deferred until a valid runtime PLL divider is known; stream startup can fail if firmware is missing or incompatible. `sysclk` must be set before hw_params or divider calculation may be invalid. GPIO PLL mode supports specific dividers and has a fallback mapping for 0/512. Custom I2C register sizing only accepts known control registers; unsupported regmap accesses return errors.

## Test Signals
Probe with regulators/GPIOs present and absent, firmware load success/failure, sysclk source selection, 48/96/192 kHz hw_params, 16/20/24-bit formats, I2S/left/right-justified DAI formats, reset divider changes, suspend/resume, SigmaDSP safeload writes, and pin-config programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1701.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1701.h

## Purpose
Small header defining ADAU1701 clock source IDs for machine-driver sysclk configuration.

## Important APIs, Types, and Functions
Defines `enum adau1701_clk_src` with `ADAU1701_CLK_SRC_OSC` and `ADAU1701_CLK_SRC_MCLK`.

## Control Flow
No executable flow. Values are consumed by `adau1701_set_sysclk()` to choose oscillator or external MCLK mode.

## State and Persistence
No state. The enum influences the `ADAU1701_OSCIPOW` hardware bit when applied by the C driver.

## Dependencies and Integration Points
Included by `adau1701.c` and potentially by machine drivers configuring sysclk.

## Risks
The enum is small but ABI-like for machine drivers. Reordering or changing values can misprogram clock source selection.

## Test Signals
Build machine drivers and exercise `set_sysclk()` with both enum values and invalid IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1701.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-i2c.c

## Purpose
I2C bus wrapper for ADAU1361/ADAU1461/ADAU1761/ADAU1961 codec core. It configures bus-specific regmap widths and delegates probe/remove to the shared ADAU1761/ADAU17x1 implementation.

## Important APIs, Types, and Functions
`adau1761_i2c_probe()` copies `adau1761_regmap_config`, sets `val_bits = 8` and `reg_bits = 16`, creates an I2C regmap, and calls `adau1761_probe()` with the matched variant ID and no switch-mode callback. `adau1761_i2c_remove()` calls `adau17x1_remove()`. ID and OF tables cover ADAU1361, ADAU1461, ADAU1761, and ADAU1961.

## Control Flow
I2C probe performs bus setup then delegates all codec registration and initialization to the core. Remove delegates shared cleanup.

## State and Persistence
No local persistent state. Shared core stores device state and regmap cache.

## Dependencies and Integration Points
Depends on I2C, regmap, ASoC, and `adau1761.h` from the same codec family. Integrates through legacy IDs and OF compatible strings.

## Risks
Variant IDs must remain aligned with the shared core's enum. If OF match data is not supplied, this code relies on the I2C ID table path for variant data.

## Test Signals
Probe/remove for each ID, OF matching, regmap transaction width validation, and shared-core controls/DAI operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-spi.c

## Purpose
SPI bus wrapper for ADAU1361/ADAU1461/ADAU1761/ADAU1961 codec core. It performs the required SPI-mode switch sequence, configures SPI regmap framing, and delegates to the shared ADAU1761 core.

## Important APIs, Types, and Functions
`adau1761_spi_switch_mode()` sends three dummy `spi_w8r8()` reads to pull CLATCH low three times and enter SPI mode. `adau1761_spi_probe()` validates an SPI ID, copies `adau1761_regmap_config`, sets 8-bit values, 24-bit register framing, read flag `0x1`, and calls `adau1761_probe()` with variant ID and switch callback. `adau1761_spi_remove()` calls `adau17x1_remove()`.

## Control Flow
SPI probe prepares bus-specific configuration and delegates core setup. The shared core invokes the switch-mode callback when it needs the device in SPI mode. Remove performs shared ADAU17x1 cleanup.

## State and Persistence
No local state. SPI mode is a hardware side effect; core state lives on the device.

## Dependencies and Integration Points
Depends on SPI, regmap, ASoC, module device tables, and `adau1761.h`. Supports both SPI ID table and OF compatible matching for four ADAU variants.

## Risks
Dummy read failures are not checked in the switch function, so a failed mode switch may appear later as regmap errors. The 24-bit register framing and variant driver data are protocol/behavior critical.

## Test Signals
SPI probe/remove for each variant, verification of dummy-read mode switch, regmap read/write traces, and shared-core playback/capture/control tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-spi.c -->
