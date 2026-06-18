# subset-b-006452 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-spi.c

Purpose: SPI bus glue for the TI PCM1862/PCM1863/PCM1864/PCM1865 ADC family. It does not implement codec policy itself; it binds OF/SPI IDs to `enum pcm186x_type`, creates a SPI regmap with `pcm186x_regmap`, and delegates initialization to `pcm186x_probe()`.

Important APIs and functions: `pcm186x_spi_probe()` uses `spi_get_device_id(spi)->driver_data`, `devm_regmap_init_spi()`, and `pcm186x_probe(&spi->dev, type, spi->irq, regmap)`. `pcm186x_of_match[]` and `pcm186x_spi_id[]` advertise all four compatible variants. `module_spi_driver()` registers the bus driver named `pcm186x`.

Control flow: kernel SPI matching calls probe; probe maps the SPI control plane into regmap; shared core probe owns supplies, reset, ASoC component registration, DAI, DAPM, and controls. There is no remove path because all allocations are devm-managed by the bus and core paths.

State and persistence: persistent state is only the SPI driver's match metadata and the shared core's `pcm186x_priv`. Register cache and power state live in `pcm186x.c`, not here.

Dependencies and integration points: depends on Linux SPI, regmap, module infrastructure, and `pcm186x.h`. It integrates with device tree compatibles `ti,pcm1862` through `ti,pcm1865` and with ALSA SoC through the shared probe.

Risks: probe assumes `spi_get_device_id()` is available for the matched device; OF-only instantiation relies on SPI core supplying a usable id. The `irq` argument is passed through but the core currently does not use it. Bus-specific failures are limited to regmap setup.

Test signals: compile with SPI support, instantiate each compatible, verify `devm_regmap_init_spi()` succeeds, and confirm the shared component exposes the expected PCM1863 two-channel or PCM1865 four-channel DAI/control set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.c

Purpose: shared ALSA SoC codec implementation for TI PCM186x universal audio ADCs. It provides ADC input muxes, capture volumes, DAPM topology, DAI format/TDM/provider-mode handling, regulator-backed power control, and a paged regmap for the bus shims.

Important APIs and types: `struct pcm186x_priv` stores `regmap`, `supplies`, `sysclk`, `tdm_offset`, `is_tdm_mode`, and `is_provider_mode`. Public exports are `pcm186x_regmap` and `pcm186x_probe()`. DAI callbacks are `pcm186x_set_dai_sysclk()`, `pcm186x_set_tdm_slot()`, `pcm186x_set_fmt()`, and `pcm186x_hw_params()`. Variant-specific component/DAI definitions expose PCM1863/1862 as two-channel capture and PCM1865/1864 as four-channel capture.

Control flow: bus driver calls `pcm186x_probe()`, which allocates private data, requests `avdd`/`dvdd`/`iovdd`, briefly powers the chip, writes `PCM186X_RESET` through page select, powers back off, and registers the correct ASoC component. At runtime, `set_fmt()` validates clock provider and polarity, chooses I2S/left-justified/TDM, and writes format plus TDM offset. `set_tdm_slot()` requires a nonzero contiguous TX mask and records the first-slot offset. `hw_params()` programs word length, TDM channel selection, LRCLK duty, and provider-mode BCLK/LRCLK dividers.

State and persistence: regcache is `REGCACHE_RBTREE`; volatile status/page/MMAP registers are excluded. Power is bias-level driven: OFF powers down and sets cache-only; STANDBY from OFF enables regulators, syncs cache, and clears power-down. `tdm_offset` is mutable private state and `DSP_A` increments it by one bit clock after any explicit slot offset.

Dependencies and integration points: ALSA SoC, DAPM, TLV controls, regmap ranges, regulators, and the SPI/I2C-style bus wrappers. Integration with machine drivers happens through DAI format, sysclk, and TDM slot calls.

Risks: provider mode requires `sysclk` before `set_fmt()` and later divides `sysclk` by `div_lrck * rate` without explicit zero/remainder checks beyond supported params. `is_tdm_mode` is only set true, not cleared when returning to non-TDM formats. TDM supports only 2/4/6 transmit channels. `pcm186x_probe()` returns on reset failure without explicitly disabling regulators in that branch.

Test signals: exercise two- and four-channel variants, DAPM input mux routing, 16/20/24/32-bit capture formats, I2S/left-justified/DSP_A/DSP_B, contiguous and noncontiguous TDM masks, provider-mode divider programming, and suspend/bias cache sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.h

Purpose: shared public contract and register map for the PCM186x codec core and its bus drivers. It names device variants, supported PCM rates/formats, virtual paged register addresses, bit fields, and the exported probe/regmap objects.

Important APIs and types: `enum pcm186x_type` differentiates PCM1862 through PCM1865. `PCM186X_RATES` and `PCM186X_FORMATS` advertise 8 kHz to 192 kHz capture and 16/20/24/32-bit sample formats. `extern const struct regmap_config pcm186x_regmap` and `pcm186x_probe(struct device *, enum pcm186x_type, int irq, struct regmap *)` are the core entry points for bus shims.

Control flow contribution: the header encodes paged addressing through `PCM186X_PAGE_LEN`, `PCM186X_PAGE_BASE(n)`, and `PCM186X_PAGE`; the core regmap range config uses these definitions to translate virtual addresses into page-window accesses. Format, TDM, clock, power, status, supply, and memory-map bits are consumed by `pcm186x.c` DAI and power paths.

State and persistence: no runtime state is stored here, but the register definitions govern which fields are cached or volatile in the regmap configuration. `PCM186X_MAX_REGISTER` extends to page 253 current trim control, so a wide virtual register range is exposed.

Dependencies and integration points: depends on Linux PM/regmap declarations and on ALSA PCM bit macros through the including C file context. It is included by the shared core and SPI shim.

Risks: this header exposes many device registers not actively validated by the core, so future controls must respect page addressing and volatile behavior. `PCM186X_RESET` is a value written to the page register, which can be easy to misread as a normal reset register address.

Test signals: compile users of all macros, verify regmap page switching reaches page 0/1/3/253 addresses, and confirm DAI word-length/format bits match the hardware datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3008.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3008.c

Purpose: minimal platform-driver ASoC codec for the TI PCM3008 stereo ADC/DAC. It exposes fixed 16-bit stereo playback/capture at 32/44.1/48 kHz and controls external pins through GPIO descriptors rather than through a register bus.

Important APIs and types: `struct pcm3008` stores four GPIOs: `dem0`, `dem1`, `pdad`, and `pdda`. `pcm3008_dac_ev()` and `pcm3008_adc_ev()` are DAPM event callbacks that drive DAC/ADC power-down pins. `pcm3008_codec_probe()` allocates state, obtains GPIOs, and registers `soc_component_dev_pcm3008` with `pcm3008_dai`.

Control flow: platform probe requests de-emphasis GPIOs with defaults that turn de-emphasis off, requests ADC/DAC power GPIOs low, and registers the component. When DAPM powers DAC or ADC widgets, event callbacks call `gpiod_set_value_cansleep()` using `SND_SOC_DAPM_EVENT_ON(event)`. Audio routes connect `PCM3008 Playback` to DAC/VOUT and VIN to ADC/`PCM3008 Capture`.

State and persistence: there is no regmap or cache. Hardware state is the four GPIO output levels. The driver stores private data with `platform_set_drvdata()`, but event callbacks fetch `component->dev->platform_data`, which is a notable inconsistency with the allocated drvdata.

Dependencies and integration points: platform bus, GPIO descriptor API, and ALSA SoC DAPM/DAI. The driver binds as `platform:pcm3008-codec`; board code must provide the required GPIO descriptors.

Risks: DAPM callbacks dereference `component->dev->platform_data` instead of `platform_get_drvdata()` or component drvdata, so platforms that do not also populate `platform_data` may crash. De-emphasis mode is fixed at probe and not exposed as a control. Missing any GPIO fails probe.

Test signals: instantiate a platform device with all GPIOs, run playback/capture DAPM transitions, observe `pdda`/`pdad` levels, and verify the 16-bit rate constraints reject unsupported formats/rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3008.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060-i2c.c

Purpose: I2C transport wrapper for the PCM3060 shared codec core. It allocates the shared private structure, creates an I2C regmap, and delegates all codec registration to `pcm3060_probe()`.

Important APIs and functions: `pcm3060_i2c_probe()` allocates `struct pcm3060_priv`, stores it with `i2c_set_clientdata()`, initializes `devm_regmap_init_i2c(i2c, &pcm3060_regmap)`, then calls `pcm3060_probe(&i2c->dev)`. Device matching uses `pcm3060_i2c_id[]` and optional OF compatible `ti,pcm3060`.

Control flow: I2C core matches the device, probe sets driver data before the core reads it via `dev_get_drvdata()`, and all later DAI/control/power behavior is in `pcm3060.c`. There is no explicit remove callback because resources are devm-managed and the shared header's `pcm3060_remove()` is not implemented or used.

State and persistence: transport state is the I2C client's driver data and regmap. Runtime DAI state lives in `struct pcm3060_priv` managed by the shared core.

Dependencies and integration points: Linux I2C, regmap, ALSA SoC, and `pcm3060.h`. Integrates with DT when `CONFIG_OF` is enabled.

Risks: no bus-specific power management or reset sequencing beyond the shared soft reset. Failure modes are allocation/regmap initialization/shared probe errors.

Test signals: instantiate via I2C ID and OF compatible, verify regmap reads/writes registers 0x40-0x49, and check the shared probe exposes both `pcm3060-dac` and `pcm3060-adc` DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060-spi.c

Purpose: SPI transport wrapper for the PCM3060 shared codec core. It mirrors the I2C wrapper with SPI regmap initialization and shared probe delegation.

Important APIs and functions: `pcm3060_spi_probe()` allocates `struct pcm3060_priv`, stores it with `spi_set_drvdata()`, initializes `devm_regmap_init_spi(spi, &pcm3060_regmap)`, and calls `pcm3060_probe(&spi->dev)`. Matching is through `pcm3060_spi_id[]` and optional `ti,pcm3060` OF entry.

Control flow: SPI core calls probe; probe creates the control-plane regmap; the shared core performs soft reset, optional single-ended output configuration, and component/DAI registration. No explicit remove callback is present.

State and persistence: persistent transport state is only SPI driver data and regmap. Cached registers and DAI clock state live in `pcm3060_priv` used by the core.

Dependencies and integration points: Linux SPI, regmap, ALSA SoC, and `pcm3060.h`. Machine drivers interact through the DAIs registered by the core.

Risks: the wrapper adds no validation beyond regmap creation. SPI mode/word-size assumptions are left to the SPI/regmap defaults and board setup.

Test signals: bind a SPI PCM3060, confirm regmap initialization, verify shared register defaults and both ADC/DAC DAIs, and compare behavior with the I2C wrapper for parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060.c

Purpose: shared PCM3060 stereo DAC plus stereo ADC codec implementation. It provides two DAIs, master/slave clock mode handling, ADC/DAC sysclk source selection, ALSA mixer controls, DAPM widgets, and regmap defaults.

Important APIs and types: `struct pcm3060_priv` is defined in the header and carries a regmap, per-DAI `is_provider` and `sclk_freq`, and `out_se`. Main callbacks are `pcm3060_set_sysclk()`, `pcm3060_set_fmt()`, and `pcm3060_hw_params()`. Public export is `pcm3060_probe()`, with public `pcm3060_regmap`.

Control flow: bus shim allocates private data and calls core probe. Core writes `PCM3060_REG64` to clear master reset, reads `ti,out-single-ended`, optionally sets `PCM3060_REG_SE`, and registers two DAIs. `set_sysclk()` validates input clock direction, maps CLK1/CLK2/default to the ADC or DAC CSEL bit, and records frequency. `set_fmt()` validates non-inverted clocks, provider/consumer mode, and I2S/right-justified/left-justified format. `hw_params()` programs slave mode or maps `sclk_freq / sample_rate` to one of the supported master ratios.

State and persistence: per-DAI provider and sysclk state persists in `priv->dai[]`. Regmap is RBTREE-cached with register defaults for 0x40-0x49; register 0x40 is volatile. DAPM controls power-save bits for DAC/ADC.

Dependencies and integration points: ALSA SoC DAI ops, TLV controls, DAPM, regmap, OF property parsing, and I2C/SPI wrappers. Machine drivers must call `set_sysclk()` with a supported ratio before provider-mode streaming.

Risks: `hw_params()` divides by sample rate and assumes a meaningful `sclk_freq`; provider mode without prior sysclk can produce an unsupported ratio. `regmap_update_bits()` return values in several setup callbacks are not checked. The header declares `pcm3060_remove()` but no implementation is present.

Test signals: test both DAIs independently, CLK1/CLK2/default source selection, provider ratios 128-768, consumer mode, all supported formats, `ti,out-single-ended`, and volume/mute controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060.h

Purpose: public interface and register/bit definitions for the PCM3060 shared codec and its I2C/SPI bus wrappers.

Important APIs and types: exports `pcm3060_regmap`, `pcm3060_probe()`, and a declared `pcm3060_remove()`. Defines DAI IDs `PCM3060_DAI_ID_DAC` and `PCM3060_DAI_ID_ADC`, clock IDs `PCM3060_CLK_DEF`, `PCM3060_CLK1`, and `PCM3060_CLK2`, `struct pcm3060_priv_dai`, and `struct pcm3060_priv`.

Control flow contribution: DAI callbacks in `pcm3060.c` use the register definitions to select master/slave ratios, I2S/left/right-justified formats, clock source selection, DAC/ADC power-save, single-ended output, mute bits, and attenuation ranges.

State and persistence: `struct pcm3060_priv` persists per-device regmap, per-DAI clock mode/frequency, and a one-bit `out_se` DT-derived setting. Register default/cache behavior is implemented in the C file using these constants.

Dependencies and integration points: includes Linux device/regmap declarations and is shared by both bus wrappers plus the codec core. Board integration uses the clock ID constants with `snd_soc_dai_set_sysclk()`.

Risks: the remove prototype is unused/stale. Macros use raw register values starting at 0x40, so future users must respect the regmap readable/writeable range. Some bit naming reflects datasheet fields and can be terse for maintainers.

Test signals: compile all bus/core users, verify DAI IDs match the array order in the core, and validate each register field against actual hardware behavior for format, mute, and power-save controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3060.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-i2c.c

Purpose: I2C bus driver for the PCM3168A shared codec core. It creates an I2C regmap, delegates probe/remove to the core, and wires runtime PM for I2C/OF/ACPI matched devices.

Important APIs and functions: `pcm3168a_i2c_probe()` calls `devm_regmap_init_i2c()` with `pcm3168a_regmap` and then `pcm3168a_probe()`. `pcm3168a_i2c_remove()` calls `pcm3168a_remove()`. Matching includes I2C ID `pcm3168a`, ACPI IDs `PCM3168A`/`104C3168`, and OF compatible `ti,pcm3168a`.

Control flow: bus probe only prepares transport; the core owns clocks, regulators, reset GPIO, DAI constraints, controls, regcache, and runtime PM. Driver `.pm` points at `pm_ptr(&pcm3168a_pm_ops)`.

State and persistence: no private I2C state beyond regmap and devres. Runtime state is stored by `pcm3168a_probe()` with `dev_set_drvdata()`.

Dependencies and integration points: Linux I2C, ACPI/OF matching, regmap, ALSA SoC, and `pcm3168a.h`.

Risks: core remove must be called for reset/runtime-PM cleanup; this wrapper does so. I2C-specific failures are limited to regmap initialization.

Test signals: bind via I2C, OF, and ACPI IDs; exercise runtime suspend/resume through the core PM ops; verify component registration and regmap access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-spi.c

Purpose: SPI bus driver for the PCM3168A shared codec core. It initializes a SPI regmap and connects SPI matching/removal/runtime PM to the common implementation.

Important APIs and functions: `pcm3168a_spi_probe()` creates `devm_regmap_init_spi(spi, &pcm3168a_regmap)` and calls `pcm3168a_probe(&spi->dev, regmap)`. `pcm3168a_spi_remove()` delegates to `pcm3168a_remove()`. Matching uses SPI ID `pcm3168a` and OF compatible `ti,pcm3168a`; `.pm` uses `pcm3168a_pm_ops`.

Control flow: all codec behavior is in `pcm3168a.c`; this file is the SPI transport adapter. Probe failure returns directly from regmap/core calls.

State and persistence: only devres-managed regmap is created here. Core private data persists in the device drvdata.

Dependencies and integration points: Linux SPI, regmap, ALSA SoC, OF module tables, and the shared header.

Risks: no SPI-specific mode constraints are set here; board data and regmap defaults must match device requirements. Runtime PM correctness depends on shared core remove/resume/suspend.

Test signals: instantiate on SPI, validate register reads/writes, runtime suspend/resume, and parity with the I2C transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a.c

Purpose: shared PCM3168A codec core for 8-channel DAC plus 6-channel ADC operation. It provides extensive mixer controls, DAPM topology, dual DAI drivers, format/TDM/sysclk programming, reset/power sequencing, and runtime PM.

Important APIs and types: `struct pcm3168a_priv` stores supplies, regmap, optional `scki` clock, optional reset GPIO, `sysclk`, per-side `pcm3168a_io_params`, and mutable DAI driver copies. Exported symbols are `pcm3168a_regmap`, `pcm3168a_probe()`, `pcm3168a_remove()`, and `pcm3168a_pm_ops`. DAI ops include `set_fmt`, `set_sysclk`, `set_tdm_slot`, `hw_params`, and `mute_stream`.

Control flow: core probe obtains optional nonexclusive active-low reset GPIO, optional `scki`, regulators, enables clock/supplies, resets by GPIO delay or internal reset, enables runtime PM, copies static DAI templates into private mutable storage, and registers the component. `set_fmt()` records provider mode and base format; `set_tdm_slot()` records slot count/width and active mask. `pcm3168a_update_fixup_pcm_stream()` narrows channels/formats for right-justified and TDM cases. `hw_params()` validates sysclk ratios, slot widths, provider/consumer limitations, TDM modes, and writes DAC or ADC mode/format fields.

State and persistence: per-side `io_params` persist format, provider mode, slots, masks, and width. Runtime PM suspend makes regmap cache-only and disables regulators/clock; resume re-enables, resets, marks cache dirty, and syncs. Regmap is flat-cached, with reset/DAC-zero/ADC-overflow volatile.

Dependencies and integration points: Linux clk, regulators, GPIO, runtime PM, regmap, ALSA SoC, TLV controls, and bus wrappers. Machine drivers drive configuration through DAI ops and optional `scki` clock.

Risks: reset sleep divides by `sysclk`, so the fallback/default path is important. Provider mode requires valid sysclk ratios and has different DAC/ADC ratio counts. The code mutates per-device DAI driver capabilities, so using the copied `dai_drv` is necessary. Remove asserts reset GPIO and disables PM, with non-PM builds doing explicit disable.

Test signals: probe with/without reset GPIO and clock, regulator failures, runtime suspend/resume cache sync, DAC/ADC DAI format negotiation, right-justified 16-bit constraints, TDM slot counts over two, mute register writes, and volume/DAPM controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a.h

Purpose: public shared header for PCM3168A bus wrappers and core. It exports the PM ops, regmap config, probe/remove entry points, and register field definitions for DAC/ADC control.

Important APIs and types: declarations for `pcm3168a_pm_ops`, `pcm3168a_regmap`, `pcm3168a_probe(struct device *, struct regmap *)`, and `pcm3168a_remove(struct device *)`. Register macros define reset/sample mode, DAC power/master/format, filter, inversion, mute, zero flags, de-emphasis, volumes, ADC mode/format, high-pass/power-save, connection type, overflow, and capture volumes.

Control flow contribution: the core uses these constants to reset the device, expose mixer controls, define regmap defaults/volatility, and program DAI `hw_params()` mode and format fields.

State and persistence: no runtime state, but the max register and volatile/writeable choices in the C file derive from this contiguous register definition set.

Dependencies and integration points: included by I2C/SPI shims and the core. It assumes Linux device/regmap types are available through including files or transitive includes.

Risks: bit-field macros are low-level and do not encode valid value combinations; misuse in future changes can create unsupported slot/format states. Header does not include `<linux/device.h>` or `<linux/regmap.h>` directly, so standalone include robustness is limited.

Test signals: compile each user, verify reset/mute/volume registers match datasheet, and confirm exported PM/probe symbols resolve for both bus modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm3168a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm5102a.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm5102a.c

Purpose: very small platform ASoC codec for the TI PCM5102A DAC. The hardware has no software control bus in this driver; it simply advertises playback capabilities and registers a component.

Important APIs and functions: `pcm5102a_dai` exposes stereo playback at 8 kHz to 384 kHz and 16/24/32-bit little-endian formats. `soc_component_dev_pcm5102a` sets idle bias, power-down timing, and endianness. `pcm5102a_probe()` calls `devm_snd_soc_register_component()`. OF matching uses `ti,pcm5102a`.

Control flow: platform probe registers one playback-only DAI named `pcm5102a-hifi`. No DAPM routes, controls, clocks, regulators, or reset handling are defined in this file.

State and persistence: none beyond the registered component/DAI. Any board-level power or clocking must be handled outside this codec driver.

Dependencies and integration points: platform bus, OF matching, ALSA SoC component/DAI registration. Machine drivers connect CPU DAI playback to this codec DAI.

Risks: because no regulators/clocks/GPIOs are modeled, power sequencing and mute behavior are board responsibility. There is no capture path or format negotiation callback beyond static constraints.

Test signals: DT/platform binding, `aplay` with supported stereo formats/rates, rejection of capture streams, and machine-driver DAI link startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm5102a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-i2c.c

Purpose: I2C wrapper for the PCM512x/PCM514x/PCM5242/TAS575x shared codec core. It adapts regmap flags for I2C auto-increment and delegates lifecycle to `pcm512x_probe()`/`pcm512x_remove()`.

Important APIs and functions: `pcm512x_i2c_probe()` copies `pcm512x_regmap`, sets `read_flag_mask` and `write_flag_mask` to `0x80`, initializes `devm_regmap_init_i2c()`, and calls the shared probe. Matching includes I2C IDs, OF compatibles, and ACPI IDs. `.pm` points to `pcm512x_pm_ops`.

Control flow: I2C probe prepares the regmap and shared core; remove calls the core cleanup. The shared core owns regulators, clocks, PLL configuration, DAI ops, controls, DAPM, and runtime PM.

State and persistence: no transport-private state beyond devres regmap. The copied regmap config prevents mutating the global config when enabling I2C auto-increment.

Dependencies and integration points: Linux I2C, ACPI, OF, regmap, and the PCM512x core. Supports `ti,tas5754` and `ti,tas5756` only on I2C in this set.

Risks: I2C auto-increment relies on the MSB flag masks; mistakes here would corrupt multi-register operations. Device-specific TAS575x `force_pll_on` behavior is decided in the shared core using OF node name.

Test signals: probe all IDs, verify multi-register regmap transactions auto-increment, runtime suspend/resume, and PLL/master-mode playback through the shared DAI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-spi.c

Purpose: SPI wrapper for the PCM512x/PCM514x/PCM5242 shared codec core. It initializes the SPI regmap, delegates probe/remove, and attaches shared runtime PM ops.

Important APIs and functions: `pcm512x_spi_probe()` calls `devm_regmap_init_spi(spi, &pcm512x_regmap)` and `pcm512x_probe(&spi->dev, regmap)`. `pcm512x_spi_remove()` calls `pcm512x_remove()`. Matching supports `pcm5121`, `pcm5122`, `pcm5141`, `pcm5142`, and `pcm5242`.

Control flow: SPI core calls probe; the shared core handles reset, supplies, optional SCLK, DAI/PLL/control registration, and PM. Remove unwinds through the core.

State and persistence: transport state is devres regmap plus core private data in drvdata. No bus-specific mutable state is kept here.

Dependencies and integration points: Linux SPI, regmap, ALSA SoC through `pcm512x.h`, and OF matching.

Risks: unlike the I2C wrapper, this wrapper does not include TAS5754/TAS5756 IDs. SPI mode and timing are not set here and depend on board/controller configuration.

Test signals: SPI bind/probe, regmap read/write, shared runtime PM, playback DAI setup, and ID/OF matching coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.c

Purpose: shared ASoC codec core for PCM512x-class DACs. It implements mixer controls, DAPM, register defaults, regulator and SCLK management, runtime PM, DAI format handling, muting, and a substantial clock/PLL/divider algorithm for consumer/provider operation.

Important APIs and types: `struct pcm512x_priv` stores regmap, optional `sclk`, supplies/notifiers, DAI format, PLL input/output GPIOs, PLL coefficients, overclock allowances, mute state, mutex, BCLK ratio, and TAS575x `force_pll_on`. Exports are `pcm512x_regmap`, `pcm512x_probe()`, `pcm512x_remove()`, and `pcm512x_pm_ops`. Key functions include `pcm512x_find_pll_coeff()`, `pcm512x_set_dividers()`, `pcm512x_hw_params()`, `pcm512x_set_fmt()`, `pcm512x_mute()`, and startup constraints for master/slave.

Control flow: probe allocates state, registers regulator disable notifiers, enables supplies, resets registers, enables optional SCLK, requests standby, enables runtime PM, parses OF `pll-in`/`pll-out`, handles TAS575x PLL quirk, and registers the component. Startup applies master constraints based on SCLK/PLL or fixed slave rates. `hw_params()` sets word length; consumer mode enables clock autoset and skips PLL setup, while provider mode programs PLL coefficients, clock dividers, GPIO PLL routing, DAC/NCP/OSR/BCLK/LRCLK/IDAC dividers, FS speed, and clock synchronization halt/resume.

State and persistence: mute state is software-combined from stream mute and user digital switch bits under a mutex. Overclock controls persist in private fields and are only writable while bias is OFF/STANDBY. Regcache is RBTREE with paged range mapping; regulator notifiers mark cache dirty/cache-only on supply disable. Runtime suspend powers down and disables supplies/SCLK; resume restores cache and clears powerdown.

Dependencies and integration points: Linux clk, regulators, regmap, runtime PM, gcd math, ALSA SoC controls/DAPM/DAI ops, OF properties, and I2C/SPI wrappers.

Risks: PLL coefficient search can fall back to approximate rates. Master mode requires a valid SCLK; slave mode can switch PLL reference to BCLK when SCLK is absent. Device tree `pll-in` and `pll-out` must be both set or both absent and not equal. Several control changes are bias-level constrained. Error paths in resume can leave supplies or clocks enabled on late failures.

Test signals: provider/consumer modes, I2S/left/right/DSP_A/DSP_B formats, BCLK ratio boundaries, SCLK absent/present, PLL GPIO routing, overclock control EBUSY behavior, mute polling, runtime PM cache sync, and TAS575x force-PLL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.h

Purpose: shared PCM512x register and API header for bus wrappers and the core codec driver. It defines the paged virtual register address space, bit fields for power/PLL/I2S/GPIO/volume/clocking, and shared lifecycle exports.

Important APIs and types: exports `pcm512x_pm_ops`, `pcm512x_regmap`, `pcm512x_probe()`, and `pcm512x_remove()`. `PCM512x_PAGE_BASE()` maps hardware pages into virtual regmap space starting at `PCM512x_VIRT_BASE`. Bit macros cover reset, power, mute, PLL lock/enable, clock references, dividers, error detection, I2S word length/format, GPIO functions, analog gain, and boost.

Control flow contribution: `pcm512x.c` uses these macros throughout DAI setup, PLL coefficient programming, divider writes, mute handling, bias transitions, runtime PM, and regmap range configuration.

State and persistence: no state is stored in the header; however, `PCM512x_MAX_REGISTER` and the page/register macros define the cacheable virtual address range. Volatile status/PLL/GPIO registers are selected in the C file from these constants.

Dependencies and integration points: Linux PM and regmap declarations. Included by I2C/SPI shims and the shared core.

Risks: virtual register numbers intentionally differ from raw 8-bit page-window addresses; future code must use these macros rather than raw offsets for paged registers. Several bit fields use compact datasheet abbreviations that can be misapplied without the C-file context.

Test signals: compile all users, verify regmap range page switching, and validate representative bit fields for I2S format, clock references, GPIO output selection, and mute/power controls against hardware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm512x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm6240.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm6240.c

Purpose: multi-device I2C ASoC driver for a broad TI PCM/ADC/PCMD/TAA/TAD family. It aggregates up to four I2C addresses as one codec, dynamically adds per-device gain controls, loads a firmware register-bin profile file, and applies register blocks on stream mute/unmute.

Important APIs and types: `struct pcmdevice_priv` in the header is the central state. Core helpers include `pcmdev_change_dev()`, `pcmdev_dev_read/write/update_bits/bulk_write()`, dynamic control builders `pcmdev_gain_ctrl_add()` and `pcmdev_profile_ctrl_add()`, firmware parser `pcmdev_regbin_ready()`, config executor `pcmdevice_select_cfg_blk()`, DAI ops `pcmdevice_mute()`/`pcmdevice_hw_params()`, component probe/remove, and `pcmdevice_i2c_probe()`.

Control flow: I2C probe determines `chip_id`, names, regmap, OF `reg` addresses, IRQ, reset GPIO or software reset, then registers one component/DAI. Component probe adds gain controls for each aggregated device, picks a firmware filename from `name_prefix` or `<dev>-i2c-<bus>-<ndev>dev.bin`, requests firmware, parses the regbin header/config/block/subblock layout, and adds a profile selector. Stream mute selects pre-shutdown blocks; unmute selects pre-power-up blocks for the current profile.

State and persistence: `codec_lock` serializes multi-address client switching, controls, and firmware state. `client->addr` is mutated to access each device, and page select is reset after switching. Parsed firmware configs persist in heap memory until component remove. `cur_conf`, `fw_state`, device addresses, and names persist in `pcmdevice_priv`. Regmap uses MAPLE cache and page ranges.

Dependencies and integration points: Linux I2C, OF register/IRQ parsing, firmware loader, GPIO reset, regmap ranges, ALSA SoC controls/DAPM/DAI, TLV metadata, and unaligned big-endian parsing.

Risks: changing `client->addr` for multi-device access is unusual and must remain locked. Firmware is mandatory at component probe for profile support; missing firmware aborts component probe after gain control attempts. Subblock write errors are logged and skipped for later operations/devices, while structural parser errors fail. `pcmdevice_select_cfg_blk()` adds negative return values to `length` without an immediate guard, which can make error accounting fragile. Reset GPIO error handling treats `IS_ERR(hw_rst)` as no reset and performs software reset instead of returning the error.

Test signals: probe one and multiple addresses, missing/malformed firmware, boundary checks for regbin sizes, profile selection, mute/unmute block execution, gain controls per chip family, 44.1/48 kHz and 16/20/24/32-bit params, reset GPIO present/absent/error, and address-switch race checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm6240.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm6240.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm6240.h

Purpose: shared definitions for the PCM6240-family I2C driver. It enumerates supported device IDs, register addresses, firmware command/block formats, runtime state structures, and dynamic mixer-control descriptors.

Important APIs and types: `enum pcm_device` indexes all supported variants and the large `pcmdev_gain_ctl_info` table in the C file. Constants define max I2C/regbin devices, config count, bin filename size, supported rates/formats/channels, page-register mapping, per-family gain registers, command IDs, `enum pcmdevice_bin_blk_type`, `enum pcmdevice_fw_state`, and structures for regbin headers/configs/blocks/private state/mixer controls.

Control flow contribution: `pcm6240.c` uses this header to parse firmware binary headers, allocate config/block data, dynamically construct ALSA controls, switch device addresses, and execute register-write/delay/field-write subblocks.

State and persistence: `struct pcmdevice_priv` stores component/client/device pointers, lock, optional reset GPIO, regmap, parsed firmware, IRQ, up to four device addresses, chip ID, current profile, firmware state, device count, firmware filename, and name strings. Firmware parse results persist in `struct pcmdevice_regbin`.

Dependencies and integration points: relies on ALSA PCM format macros and `snd_kcontrol_get_t`/`put_t` types from including C context. It is tightly coupled to `pcm6240.c` and not a standalone public API for other subsystems.

Risks: array indexes depend on `enum pcm_device` order matching the C-file control info table and I2C ID table. Firmware constants encode binary ABI expectations; incompatible firmware versions or config counts fail parse. Header lacks include guards for ALSA type declarations beyond the guard itself.

Test signals: compile with all enum/table entries, validate each chip ID maps to expected gain controls, parse representative regbin files for version/config/block boundaries, and test multi-device address limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm6240.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/peb2466.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/peb2466.c

Purpose: Infineon PEB2466 four-channel voice codec ASoC driver over SPI. It implements a custom SPI-backed regmap for XOP/SOP commands, direct COP coefficient writes, A/u-law 8 kHz DAI operation, tone generators, DAPM routing, optional firmware coefficient loading, and a 28-line GPIO controller.

Important APIs and types: `struct peb2466` stores SPI, MCLK, reset GPIO, DMA-safe SPI buffers, regmap, per-channel lookup controls/tone state, max playback/capture channels, and GPIO cache/lock. Key functions include SPI helpers `peb2466_write_byte/read_byte/write_buf()`, regmap callbacks, lookup/tone control callbacks, DAI ops `peb2466_dai_set_tdm_slot()`, `peb2466_dai_set_fmt()`, `peb2466_dai_hw_params()`, firmware parsers, `peb2466_reset_audio()`, GPIO operations, and `peb2466_spi_probe()`.

Control flow: SPI probe sets 8-bit words, creates custom regmap, gets optional reset and required `mclk`, toggles reset, maps MCLK rate to XR5, registers the ASoC component/DAI, then registers GPIOs if enabled. Component probe resets audio coefficients/registers and optionally loads `firmware-name` from DT. DAI TDM slot setup writes CR5 playback and CR4 capture slot indexes, controlling stream channel constraints. DAI format only supports DSP_A/DSP_B; hw_params selects A-law or mu-law for every channel.

State and persistence: regmap has no cache; GPIO output/direction state uses a private cache because reads and writes address different internal signals. Firmware AX/AR tables are devm-allocated and referenced by runtime mixer controls. Tone frequency selections and max channel counts persist in `struct peb2466`. Reset audio initializes default IM/R1 coefficients and clears other filters.

Dependencies and integration points: Linux SPI, clk, firmware loader, GPIO descriptor and gpiochip APIs, regmap custom callbacks, ALSA SoC controls/DAPM/DAI, OF `firmware-name`, and unaligned big-endian parsing.

Risks: custom SPI read requires ident byte `0x81`; failures return `-EILSEQ`. COP writes bypass regmap and are limited to eight data bytes. Streams are disabled until TDM slots configure nonzero max channels. Firmware parser rejects unknown tags/lengths and logs coefficient bytes at info level. GPIO semantics are nonuniform: SI read-only, SO write-only via cache, SB bidirectional.

Test signals: SPI probe at all supported MCLK rates, reset GPIO timing, DSP_A/B TDM slot programming, A-law/mu-law hw_params, firmware magic/version/tag validation, AX/AR dynamic volume controls, tone frequency controls, DAPM power/mixer routes, and gpiochip get/set/direction behavior for SI/SO/SB offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/peb2466.c -->
