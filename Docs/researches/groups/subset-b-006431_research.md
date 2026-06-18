<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs43130.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs43130.c

## Purpose
`cs43130.c` is the ALSA SoC codec driver for the Cirrus Logic CS43130 family, covering CS43130, CS4399, CS43131, and CS43198 I2C codecs. It exposes PCM, DoP, and native DSD playback DAIs, configures the codec PLL and serial ports, builds the headphone DAC DAPM graph, manages jack detection and headphone-load impedance measurement, and integrates runtime PM, regulators, GPIO reset, and regmap caching.

## Important APIs, Types, and Functions
- The driver registers `cs43130_i2c_driver` through `module_i2c_driver()`, with OF compatibles `cirrus,cs43130`, `cirrus,cs4399`, `cirrus,cs43131`, and `cirrus,cs43198`, plus ACPI ID `CSC4399`.
- `cs43130_regmap` uses 24-bit register addresses with 8-bit values, maple cache, explicit readable/volatile/precious callbacks, and single read/write cache-sync behavior.
- `cs43130_i2c_probe()` allocates `struct cs43130_private`, initializes regmap, parses firmware properties, enables supplies, handles reset, verifies the Cirrus device ID, initializes completions/mutexes/IRQ/runtime PM, and registers the ASoC component with either analog or digital widget sets.
- `cs43130_probe()` is the ASoC component probe. It applies crystal bias, creates a `snd_soc_jack`, optionally creates headphone-load sysfs attributes and workqueue, unmasks jack interrupts, and enables headphone detect.
- Clock APIs include `cs43130_set_pll()`, `cs43130_pll_config()`, `cs43130_change_clksrc()`, `cs43130_component_set_sysclk()`, and DAI-level `cs43130_set_sysclk()`. They select external MCLK, PLL, or internal RCO and program PLL divider tables.
- DAI setup flows through `cs43130_pcm_set_fmt()`, `cs43130_dsd_set_fmt()`, `cs43130_hw_params()`, `cs43130_dsd_hw_params()`, `cs43130_hw_free()`, `cs43130_set_bitwidth()`, and `cs43130_set_sp_fmt()`.
- DAPM event handlers `cs43130_pcm_event()`, `cs43130_dsd_event()`, `cs43130_dac_event()`, and `cs43130_hpin_event()` apply silicon-specific power-up/down, mute, pop-suppression, and analog-input register sequences.
- Headphone load handling uses `cs43130_irq_thread()`, `cs43130_imp_meas()`, `cs43130_hpload_proc()`, `cs43130_update_hpload()`, `cs43130_set_hv()`, and read-only sysfs show methods for `hpload_dc_l`, `hpload_dc_r`, `hpload_ac_l`, and `hpload_ac_r`.

## Control Flow
Probe first initializes regmap and platform resources, then reads the device ID using `cirrus_read_device_id()`. If firmware-node data exists, `cs43130_handle_device_data()` reads optional crystal bias, measurement mode, AC frequencies, and DC thresholds. Regulators are bulk-enabled, reset is asserted high, revision ID is logged, completions and IRQs are set up, runtime PM is enabled, and the ASoC component is registered. Runtime operation is then split between DAI configuration, DAPM events, and IRQ/workqueue paths.

For playback, machine drivers set the serial format and system clock through ASoC callbacks. `hw_params` chooses a 22.5792 MHz or 24.576 MHz internal clock based on sample rate divisibility, configures or bypasses the PLL, changes the active clock source, increments the shared `clk_req` count, chooses PCM or DSD source registers, validates SCLK and channel bit width, then programs ASP/XSP frame, channel, and clock generator registers. `hw_free` decrements `clk_req`; when the last stream releases the clock it switches back to the RCO and disables PCM/DSD mixing.

DAPM power transitions apply the vendor sequences around codec power rails and data paths. PCM and DSD widgets unmute on post-power-up and mute before power-down; older CS43130/CS4399 variants use hidden DXD sequences and a 130 ms power-down delay, while CS43131/CS43198 mostly update path mute bits directly. The DAC event path contains the longest delay: CS43130/CS4399 wait around one second before clearing `DXD12` to meet THD+N and dynamic range expectations.

The IRQ thread reads all five interrupt status and mask registers, filters masked bits, and completes the matching wait object for crystal ready, PLL ready, or headphone-load events. It also reports jack unplug, mechanical plug, line-out/headphone classification, and queues load-measurement work on plug if enabled. If no IRQ line exists, `cs43130_wait_for_completion()` polls selected sticky interrupt bits for clock readiness, but headphone-load measurement still waits on `hpload_evt`, so load measurement depends on an IRQ-capable configuration.

## State and Persistence
Persistent runtime state lives in `struct cs43130_private`: device ID, crystal bias, IRQ availability, clock mutex, `clk_req`, PLL-bypass state, completions, current external/internal MCLK, active MCLK source, per-DAI SCLK/format/mode/inversion, headphone measurement configuration/results, workqueue, and jack object. Regmap cache persists register writes across runtime suspend; suspend sets cache-only, marks it dirty, pulls reset low, and disables supplies. Resume reenables supplies, releases reset, syncs regcache, and re-enables crystal error interrupts when needed.

The `clk_req` reference count is shared by all DAIs and the impedance work item. It is protected by `clk_mutex`, but the code assumes balanced `hw_params` and `hw_free` calls. Headphone load results persist in memory and become visible through sysfs only after `hpload_done` is set.

## Dependencies and Integration Points
The driver depends on Linux I2C, regmap, regulator, GPIO descriptor, runtime PM, completions, workqueues, IRQ, ALSA ASoC, DAPM, TLV controls, and jack reporting. It uses `cirrus_read_device_id()` from `cirrus_legacy.h`. Register constants, clock generator tables, supply names, and private state are defined in `cs43130.h`. Machine drivers interact with the four DAIs named `cs43130-asp-pcm`, `cs43130-asp-dop`, `cs43130-xsp-dop`, and `cs43130-xsp-dsd`, plus component `set_sysclk`/`set_pll` callbacks. Device tree or ACPI supplies reset, optional `cirrus,*` measurement properties, and possibly IRQ wiring.

## Risks and Edge Cases
- `cs43130_hw_params()` and `cs43130_dsd_hw_params()` increment `clk_req` before later validation failures. Unsupported rates, missing SCLK, or bad serial parameters after that point can leave the clock reference elevated unless ALSA later calls `hw_free`.
- `cs43130_imp_meas()` returns early on an invalid `dev_id` after incrementing `clk_req`, which would leak the clock reference if reached. Probe only enables measurement for CS43130/CS43131-like configurations, but the local switch still has a defensive `WARN()` path with no cleanup.
- The firmware property array handling appears inverted: defaults are copied only when `device_property_read_u16_array()` succeeds, not when it fails. That can leave zeroed AC frequencies or DC thresholds when properties are absent.
- Runtime remove calls `device_remove_file()` for attributes created through `sysfs_create_groups()`, which is asymmetric and risks incomplete group teardown compared with `sysfs_remove_groups()`.
- Headphone-load measurement waits only on interrupt completion. Platforms without `client->irq` may poll for clock readiness but cannot complete `hpload_evt` through the IRQ thread.
- Long DAPM sleeps, especially the one-second DAC post-power-up sequence, are expected by the silicon sequence but can surprise latency-sensitive power paths.
- Most regmap writes ignore return values, so bus failures can be silent until later state is visibly wrong.

## Test Signals
Useful validation includes probe/remove on each supported chip ID, regmap cache sync across runtime suspend/resume, PLL paths for every accepted MCLK/input-to-output pair, PCM rates from 32 kHz through 384 kHz, DoP/native DSD rates at 176.4 and 352.8 kHz, SCLK-too-low rejection, DAI master/slave and inversion combinations, jack plug/unplug IRQ reporting, line-out versus headphone threshold classification, sysfs load outputs before and after measurement, and IRQ-less operation for clock polling. Fault injection should cover missing regulators, reset GPIO errors, unsupported device IDs, regmap read/write failures, and interrupted or timed-out PLL/XTAL ready events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs43130.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs43130.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs43130.h

## Purpose
`cs43130.h` is the private hardware definition header for the CS43130-family codec driver. It maps the codec register space, bit masks, enumerations, DAI IDs, clock generator tables, supply names, and `struct cs43130_private` state used by `cs43130.c`.

## Important APIs, Types, and Data
- Register address macros span `CS43130_FIRSTREG` to `CS43130_LASTREG`, including device ID, system clock, serial port, PLL, ASP/XSP, PCM/DSD, headphone output, headphone-detect/load, and interrupt blocks.
- Device ID macros identify `CS43130_CHIP_ID`, `CS4399_CHIP_ID`, `CS43131_CHIP_ID`, and `CS43198_CHIP_ID`.
- Bitfield macros describe clock source selection, serial-port sizes and polarity, power-down bits, PLL divider fields, PCM/DSD mute and source fields, headphone load interrupts, and measurement value packing.
- Format/rate macros define supported PCM and DoP ALSA sample formats.
- Enumerations define DSD sources, ASP sample-rate register encodings, MCLK source choices, internal MCLK selector values, crystal bias settings, and DAI IDs.
- `struct cs43130_clk_gen` and the four static clock-generator tables map internal MCLK plus sample rate plus frame size to serial-port numerator/denominator values.
- `struct cs43130_dai` stores per-DAI SCLK, format, master/slave mode, and inversion.
- `struct cs43130_private` is the central driver instance state shared by probe, DAI callbacks, DAPM events, IRQ handling, runtime PM, and headphone-load work.

## Control Flow Role
This header has no executable control flow, but it controls the legal paths in `cs43130.c`. The PLL and clock-source functions depend on MCLK IDs and bit masks defined here. `cs43130_set_sp_fmt()` chooses one of the frame-size clock tables here. DAPM event paths write DXD and path-control registers named here. The headphone-load worker uses interrupt masks, measurement registers, threshold counts, and channel indexes declared here.

## State and Persistence Behavior
The header defines which state is persisted in memory and which state is mirrored through regmap. `struct cs43130_private` keeps clock reference state, per-DAI serial settings, measurement state, workqueue state, and jack state. The register defaults and regcache behavior in the C file rely on the register addresses and masks defined here.

## Dependencies and Integration Points
The header depends on ASoC/jack types through fields such as `struct snd_soc_component`, `struct snd_soc_jack`, `struct regmap`, `struct regulator_bulk_data`, `struct gpio_desc`, `struct completion`, `struct mutex`, and workqueue types included by the C file. It also uses `struct u16_fract`, supplied by kernel helper headers included in the codec build context. Machine-driver-visible DAI IDs and MCLK source definitions are indirectly exposed through the component and DAI callbacks in `cs43130.c`.

## Risks and Edge Cases
- Because the clock generator tables are static in the header, any file including it gets private copies. In this driver that is effectively limited to `cs43130.c`, but the pattern would be wasteful if reused elsewhere.
- Table coverage is strict. Unsupported frame sizes, rates, or internal MCLK values fail at runtime rather than falling back.
- The header mixes public-looking hardware IDs with private driver state; external users should not include it as a stable ABI.
- Several masks and shifts are used with full-register writes in the C file, so incorrect mask definitions could cause silent hardware misconfiguration.

## Test Signals
Build tests should compile `cs43130.c` with this header under the relevant kernel configs. Runtime tests should exercise every clock generator table for 16, 32, 48, and 64-bit frame sizes, confirm every DAI ID maps to the correct ASP/XSP register block, verify interrupt masks align with IRQ-thread handling, and inspect regmap traces for expected register addresses on power, PLL, serial-port, and headphone-load paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs43130.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4341.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4341.c

## Purpose
`cs4341.c` implements a compact ALSA SoC codec driver for the Cirrus Logic CS4341A stereo DAC. It supports I2C and SPI control transports, exposes playback-only DAI operations, basic volume/filter/de-emphasis controls, and a simple DAPM graph from DAC playback to two outputs.

## Important APIs, Types, and Functions
- `struct cs4341_priv` stores the selected DAI format, active regmap, and per-bus `regmap_config`.
- `cs4341_set_fmt()` accepts only codec bit-clock/frame-clock consumer mode, normal bit/frame polarity, and I2S/left-justified/right-justified formats.
- `cs4341_hw_params()` accepts 16-bit and 24-bit PCM, maps the selected DAI format plus width to `MODE2` DIF bits, and rejects unsupported combinations.
- `cs4341_mute()` updates mute bits for both volume registers.
- `cs4341_probe()` writes the default register values explicitly and registers the ASoC component and one DAI.
- `cs4341_i2c_probe()` and `cs4341_spi_probe()` allocate state, configure transport-specific regmap addressing, initialize regmap, and delegate to `cs4341_probe()`.
- `cs4341_init()` and `cs4341_exit()` manually register/unregister optional I2C and SPI drivers according to kernel configuration.

## Control Flow
At module init, the I2C driver is registered first when enabled; if that succeeds, the SPI driver is registered when SPI master support is enabled. Each bus probe allocates `cs4341_priv`, sets bus driver data, configures an 8-bit I2C regmap or 16-bit-address SPI write-only regmap, and registers the codec component. During playback setup, the machine driver calls `set_fmt`, then `hw_params` writes the concrete DIF bits. Stream mute requests toggle both channel mute bits. Module exit unregisters only the buses that were compiled in.

## State and Persistence Behavior
The driver keeps only the selected serial format and regmap pointer. Device register state is cached in a flat regmap with five defaults. There is no runtime PM implementation, reset GPIO, regulator management, IRQ handling, or persistent calibration state.

## Dependencies and Integration Points
The file depends on Linux I2C, SPI, OF matching, regmap, ALSA PCM/ASoC/TLV helpers, and module registration. It exposes the compatible string `cirrus,cs4341a`, I2C ID `cs4341`, SPI ID `cs4341a`, and a single DAI named `cs4341a-hifi` with playback stream `DAC Playback`.

## Risks and Edge Cases
- `cs4341_init()` can leave the I2C driver registered if SPI registration later fails; there is no unwind of the already registered I2C driver in that error path.
- SPI regmap marks all registers unreadable, so cache behavior and diagnostics depend on write-only operation.
- `cs4341_probe()` ignores errors from the explicit default writes.
- Left-justified mode always programs the 24-bit encoding even when `S16_LE` is selected; this may match hardware expectations but is worth validating against the datasheet and machine format.
- The driver has no regulator/reset/runtime PM handling, so board-level power sequencing must be handled elsewhere.

## Test Signals
Validate I2C and SPI probe with regmap traces, `set_fmt` rejection for unsupported master/inversion/format modes, `hw_params` for S16/S24 in I2S/right-justified modes, mute/unmute writes to both volume registers, ALSA mixer controls for de-emphasis and soft-ramp/zero-cross behavior, and module init unwind behavior in a fault-injected SPI registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4349.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4349.c

## Purpose
`cs4349.c` is the ALSA SoC codec driver for the Cirrus Logic CS4349 stereo DAC. It provides I2C probing, regmap-backed controls, a playback-only DAI, DAPM DAC/output routing, reset GPIO handling, and runtime PM power-down/resume behavior.

## Important APIs, Types, and Functions
- `struct cs4349_private` stores the regmap, optional reset GPIO, selected DAI mode, and last sample rate.
- `cs4349_readable_register()` and `cs4349_writeable_register()` constrain regmap access to the CS4349 register range.
- `cs4349_set_dai_fmt()` accepts I2S, left-justified, and right-justified formats and stores the format mode.
- `cs4349_pcm_hw_params()` maps the selected DAI format and PCM width to digital interface format bits in `CS4349_MODE`; right-justified mode only accepts 16-bit or 24-bit widths.
- `cs4349_mute()` toggles both channel mute bits in `CS4349_MUTE`.
- Mixer controls expose master playback volume, functional mode, de-emphasis, soft-ramp/zero-cross mode, channel mixer, inversion, auto-mute, MUTEC linkage, ramp/filter, freeze, and popguard switches.
- `cs4349_i2c_probe()`, `cs4349_i2c_remove()`, `cs4349_runtime_suspend()`, and `cs4349_runtime_resume()` own lifecycle and power state.

## Control Flow
I2C probe allocates private state, creates a maple-cache 8-bit regmap, obtains an optional reset GPIO asserted low, drives reset high, stores client data, and registers the ASoC component and DAI. Playback setup records the serial format and later writes DIF bits during `hw_params`. Runtime suspend sets the power-down bit, enables regcache-only mode, and holds reset low. Runtime resume clears power-down, releases reset high, disables cache-only mode, and syncs the cache.

## State and Persistence Behavior
The selected DAI mode and last rate live in `struct cs4349_private`; the rate is currently recorded but not used for hardware mode selection. Register defaults are cached by regmap. Runtime suspend intentionally isolates hardware from cached writes while reset and power-down are active, then relies on `regcache_sync()` after resume.

## Dependencies and Integration Points
The driver depends on I2C, GPIO descriptors, PM runtime, regmap, ALSA ASoC/DAPM/TLV, and the companion `cs4349.h` register header. It exposes OF compatible `cirrus,cs4349`, I2C ID `cs4349`, and DAI `cs4349_hifi` with playback stream `DAC Playback`, 1-2 channels, rates 8 kHz to 192 kHz, and broad PCM format support.

## Risks and Edge Cases
- `cs4349_set_dai_fmt()` ignores master/slave and polarity masks; machine drivers can pass unsupported clock-provider or inversion combinations without immediate rejection.
- Runtime resume writes `PWR_DWN` before releasing reset and before disabling cache-only mode. Depending on regcache state, that first write may be cached rather than reaching hardware.
- `regcache_sync()` return value is ignored on resume.
- The stored `rate` is unused, and functional mode can be changed manually through a mixer control rather than automatically derived from sample rate.
- Probe does not verify chip ID or revision even though the header defines chip ID values.

## Test Signals
Exercise probe/remove with and without reset GPIO, runtime suspend/resume with regmap cache inspection, format setup for I2S/left-justified/right-justified at all supported widths, rejection of unsupported right-justified widths, mute control writes, all user controls, and fault injection for regmap update/sync failures. Board-level tests should confirm actual clock polarity and provider assumptions because the driver does not validate those masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4349.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4349.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4349.h

## Purpose
`cs4349.h` defines CS4349 register addresses, revision IDs, bit masks, and symbolic register values consumed by `cs4349.c`. It is a private hardware-description header for the CS4349 codec driver.

## Important APIs, Types, and Data
- Register macros define chip ID, mode, volume/mixing/inversion, mute, channel volumes, ramp/filter, and miscellaneous power/freeze/popguard registers.
- Revision macros define expected chip ID register values for revisions A, B, and C2.
- Mode-register macros define digital interface format values, de-emphasis choices, functional mode values, rate thresholds, and masks.
- VMI macros define volume linkage, channel inversion, and ATAPI channel-mixer encodings.
- Mute, ramp/filter, and misc macros provide the bit masks used by the C driver controls and runtime PM.

## Control Flow Role
This header has no executable control flow. It controls the legal register writes in `cs4349.c`: `cs4349_pcm_hw_params()` uses `DIF_*`, `DIF_MASK`, and `MODE_FORMAT()`, `cs4349_mute()` uses `MUTE_AB_MASK`, runtime PM uses `PWR_DWN`, and mixer controls rely on the volume, de-emphasis, ramp, freeze, and popguard bit definitions.

## State and Persistence Behavior
The header defines hardware state fields that are persisted in the codec registers and mirrored by regmap. It does not define any software state struct; that is local to `cs4349.c`.

## Dependencies and Integration Points
The header is included directly by `cs4349.c` and does not require external kernel types. Its constants align with ALSA controls, DAPM power handling, and I2C regmap access in the driver.

## Risks and Edge Cases
- Several defined capabilities, including TDM DIF values, functional-mode thresholds, revision IDs, and `PDN_POLL_MAX`, are not currently used by `cs4349.c`.
- Duplicate semantic definitions such as `VOLBISA` and `VOLAISB` sharing bit 7 are useful aliases but can confuse future edits.
- Because chip revision IDs are defined but not checked, users of the driver cannot rely on the header values being enforced at probe.

## Test Signals
Compile tests should confirm the header matches `cs4349.c` masks. Runtime regmap traces should verify that format, mute, ramp/filter, de-emphasis, freeze, popguard, and power-down operations write the expected bits. A future chip-ID validation change should test the revision macros against real or mocked register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4349.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l15.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l15.c

## Purpose
`cs47l15.c` is the ALSA SoC codec driver for the Cirrus Logic CS47L15 Madera-family audio codec. It binds as a platform child of the Madera MFD core, declares the CS47L15-specific control surface and DAPM routing graph, initializes one ADSP2 DSP, maps FLL operations, exposes AIF and compressed trace DAIs, and connects shared Madera helpers for clocks, inputs, outputs, IRQs, overheat protection, and DSP firmware.

## Important APIs, Types, and Functions
- `struct cs47l15` embeds `struct madera_priv`, two `struct madera_fll` instances, and an `in1_lp_mode` flag.
- `cs47l15_dsp1_regions` describes DSP1 PM/ZM/XM/YM memory windows for the wm_adsp/cs_dsp core.
- `cs47l15_adsp_power_ev()` reads the DSP clock register, programs the ADSP clock through `madera_set_adsp_clk()`, and delegates to `wm_adsp_early_event()`.
- `cs47l15_in1_adc_get()` and `cs47l15_in1_adc_put()` implement the custom "IN1 LP Mode Switch" by updating DMIC OSR and mid-mode bias registers and persisting `in1_lp_mode`.
- `cs47l15_snd_controls` exposes input, EQ, DRC, LHPF, ISRC, DSP, noise, output, PDM speaker, noise gate, AIF mixer, SPDIF, and firmware controls through Madera and wm_adsp macros.
- `cs47l15_dapm_widgets` and `cs47l15_dapm_routes` define the clock domains, regulators, analog/digital inputs, AIFs, DSP, EQ/DRC/LHPF/ISRC/PWM/SPDIF blocks, output mixers, mono/earpiece demux paths, and activity/trigger outputs.
- `cs47l15_set_fll()` maps ASoC PLL IDs to Madera FLL reference and sync-clock helpers.
- `cs47l15_open()` maps the compressed DSP trace DAI to ADSP index 0.
- `cs47l15_adsp2_irq()` services compressed-data IRQs through `wm_adsp_compr_handle_irq()`.
- `cs47l15_component_probe()` initializes component regmap, Madera DAPM pointer, inputs, outputs, ADSP component, and ADSP rate controls.
- `cs47l15_probe()` performs platform-level allocation, Madera core/overheat/DSP/FLL/DAI setup, IRQ request, runtime PM enablement, digital volume update latching, and ASoC component registration.

## Control Flow
Platform probe first waits for the Madera IRQ chip, then allocates state and initializes shared Madera core state with four inputs. It initializes overheat handling, requests the DSP compressed-data IRQ, marks it wake-capable, configures ADSP1 metadata and memory regions, initializes the DSP and bus-error IRQ, initializes FLL1 and FLLAO, initializes all DAI descriptors, latches digital volume update bits, enables runtime PM, and registers the component. Component probe then binds the MFD regmap into ASoC, records the DAPM pointer under lock, initializes inputs/outputs, disables HAPTICS, adds ADSP rate controls, and probes the ADSP component.

During audio routing, DAPM supplies and widgets call shared Madera event helpers for SYSCLK, DSPCLK, domain clocks, input PGAs, headphone/speaker/output power, and ADSP power. Mixer controls and DAPM routes determine how signal generators, AIF inputs, physical inputs, EQ/DRC/LHPF/ISRC blocks, DSP channels, PWM, SPDIF, and outputs are connected. Compressed stream open accepts only `cs47l15-dsp-trace` and routes it to ADSP1.

Remove unwinds runtime PM, bus-error IRQ, ADSP, DSP IRQ wake/free, overheat, and Madera core state. Component remove clears the Madera DAPM pointer and removes the ADSP component.

## State and Persistence Behavior
Most state is shared through `madera_priv`, the parent MFD regmap, DAPM graph state, and wm_adsp firmware/runtime state. Local persistent state is limited to two FLL structs and `in1_lp_mode`. The low-power input switch persists in both hardware registers and the local boolean so ALSA reads report the last requested mode. Digital volume update bits are latched during probe and remain in hardware until reset or reconfiguration. Runtime PM is enabled at platform-device level, while actual register caching and power behavior are largely implemented by the Madera core.

## Dependencies and Integration Points
The driver depends on the Madera MFD core, `irq-madera`, Madera register definitions, shared `madera.h` ASoC helpers, `wm_adsp`, regmap, runtime PM, ALSA ASoC/DAPM/compress APIs, and module platform-driver infrastructure. It exposes platform alias `cs47l15-codec`, DAI names `cs47l15-aif1`, `cs47l15-aif2`, `cs47l15-aif3`, `cs47l15-cpu-trace`, and `cs47l15-dsp-trace`, and declares a soft dependency on `madera irq-madera arizona-micsupp`.

## Risks and Edge Cases
- The platform probe requires `madera->irq_dev`; deferred probing is expected if the IRQ child has not completed.
- The "IN1 LP Mode Switch" updates multiple registers without checking return values, so partial failures can desynchronize hardware and `in1_lp_mode`.
- Compressed stream routing depends on codec DAI name string comparison; DAI renames can break stream open.
- The ADSP IRQ handler reports `IRQ_NONE` only for `-ENODEV`; other unexpected errors are treated as handled.
- The driver owns a large DAPM graph generated by macros. Route/control mismatches are easy to introduce and often only visible through path activation tests.
- Error unwind is detailed but crosses Madera, ADSP, IRQ, overheat, and runtime PM subsystems; probe-failure fault injection is important.

## Test Signals
Validate deferred probe before IRQ-chip readiness, full probe/remove order, ADSP firmware load and compressed trace capture, DSP IRQ wake and compressed IRQ service, FLL1/FLLAO reference and sync-clock programming, AIF1/2/3 playback and capture constraints, IN1 low-power switch readback and register effects, DAPM paths from each input/source through EQ/DRC/LHPF/ISRC/DSP to outputs, HPOUT/EPOUT demux behavior, speaker/PDM/SPDIF outputs, runtime PM idle/resume, and error unwinds for failed IRQ, ADSP init, bus-error IRQ, and component registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l24.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l24.c

## Purpose
`cs47l24.c` is the ALSA SoC codec driver for the Cirrus Logic CS47L24 Arizona-family audio codec. It binds as a platform child of the Arizona MFD core, declares CS47L24 controls and DAPM routes, initializes two ADSP2 cores, maps FLL operations, exposes AIF, voice-control, and trace DAIs, and integrates speaker, GPIO, mono-output, volume-limit, IRQ, and compressed-stream services from the shared Arizona and wm_adsp layers.

## Important APIs, Types, and Functions
- `struct cs47l24_priv` embeds `struct arizona_priv` and two `struct arizona_fll` instances.
- `cs47l24_dsp2_regions`, `cs47l24_dsp3_regions`, and `cs47l24_dsp_regions` describe PM/ZM/XM/YM memory maps for DSP2 and DSP3.
- `cs47l24_adsp_power_ev()` reads SYSCLK frequency selection, sets the DSP clock through `wm_adsp2_set_dspclk()`, and delegates to `wm_adsp_early_event()`.
- `cs47l24_snd_controls` exposes input, EQ, DRC, LHPF, ISRC, ASRC, DSP preload/firmware, noise, output, noise-gate, and AIF mixer controls using Arizona and wm_adsp macros.
- `cs47l24_dapm_widgets` and `cs47l24_dapm_routes` define SYSCLK/ASYNCCLK domains, regulators, inputs, AIFs, ASRC/ISRC, DSP2/DSP3, EQ/DRC/LHPF/PWM blocks, AEC loopback, headphone/speaker outputs, mic supplies, voice trigger, and signal/activity outputs.
- `cs47l24_set_fll()` maps `CS47L24_FLL1`, `CS47L24_FLL2`, `CS47L24_FLL1_REFCLK`, and `CS47L24_FLL2_REFCLK` IDs to Arizona FLL helpers.
- `cs47l24_open()` maps compressed DAIs by name: `cs47l24-dsp-voicectrl` to ADSP index 2 and `cs47l24-dsp-trace` to ADSP index 1.
- `cs47l24_adsp2_irq()` services compressed-data IRQs for both ADSP cores and emits an Arizona voice-trigger notifier when wm_adsp reports a voice trigger.
- `cs47l24_component_probe()` initializes regmap, speaker/GPIO/mono helpers, ADSP component probes, ADSP rate controls, and disables HAPTICS.
- `cs47l24_probe()` handles platform allocation, OF audio pdata loading, ADSP and FLL setup, fixed sample-rate register programming, DAI initialization, volume update latches, runtime PM, DSP IRQ, common Arizona init, speaker IRQs, and component registration.

## Control Flow
Platform probe allocates `cs47l24_priv`, optionally loads OF audio platform data into the parent Arizona device, stores driver data, and attaches the parent core. It initializes two ADSP cores in a loop for DSP2 and DSP3, sets FLL VCO multipliers, initializes FLL1/FLL2, fixes sample-rate slots SR2 and SR3 to 8 kHz and 16 kHz, initializes all DAIs, latches digital volume update bits, enables runtime PM, requests the compressed-data IRQ, enables it as a wake source, runs common Arizona init, initializes volume limits and speaker IRQs, then registers the component.

Component probe binds the Arizona regmap to ASoC, initializes speaker/GPIO/mono facilities, probes both ADSP components, adds ADSP rate controls for DSP2 and DSP3, and disables the HAPTICS pin. DAPM then uses the declared graph to gate clocks, regulators, DSPs, ASRC/ISRC blocks, AIF endpoints, and physical outputs as routes are activated. Compressed stream open selects the target DSP by codec DAI name. The shared IRQ handler iterates DSP2 and DSP3, handles compressed data, and forwards voice-trigger notifications.

Remove disables runtime PM, removes both ADSPs, frees speaker IRQs, clears DSP IRQ wake, and frees the DSP IRQ. Component remove removes ADSP component state and clears the parent `dapm` pointer.

## State and Persistence Behavior
Persistent driver state is mostly in `arizona_priv`, the parent Arizona regmap, ADSP state, FLL structs, DAPM state, and IRQ registrations. The driver explicitly programs fixed sample-rate slots and digital volume update bits during probe. Runtime PM is enabled on the platform child, while deeper register caching and power sequencing are provided by the Arizona core. Voice-trigger events are transient IRQ notifications rather than stored state.

## Dependencies and Integration Points
The driver depends on the Arizona MFD core, Arizona register definitions and ASoC helpers, `wm_adsp`, regmap, PM runtime, ALSA ASoC/DAPM/compress APIs, and the local `cs47l24.h` FLL ID header. It exposes platform alias `cs47l24-codec` and DAIs `cs47l24-aif1`, `cs47l24-aif2`, `cs47l24-aif3`, `cs47l24-cpu-voicectrl`, `cs47l24-dsp-voicectrl`, `cs47l24-cpu-trace`, and `cs47l24-dsp-trace`.

## Risks and Edge Cases
- The ADSP initialization loop returns immediately on failure without removing any ADSP core initialized in a previous iteration.
- If DSP IRQ request fails after runtime PM is enabled, the error path returns without disabling runtime PM or removing initialized ADSP cores.
- Compressed-stream routing uses codec DAI name string comparisons; renames or topology changes can break voice/trace stream selection.
- `cs47l24_adsp2_irq()` counts any result other than `-ENODEV` as serviced, so unexpected errors may still produce `IRQ_HANDLED`.
- Several setup writes, including fixed sample-rate registers and volume update latches, ignore regmap return values.
- The graph is large and macro-heavy; missing or mismatched routes can disable entire signal paths without compiler help.

## Test Signals
Validate probe/remove with OF platform-data loading, ADSP2 and ADSP3 firmware/component probe, voice-control and trace compressed streams, voice-trigger notifier delivery, FLL1/FLL2 and REFCLK programming, fixed SR2/SR3 behavior, AIF1/2/3 playback and capture channel limits, ASRC/ISRC paths, DAPM activation from inputs/AIFs/DSPs to headphone and speaker outputs, runtime PM idle/resume behavior, speaker IRQ setup, volume-limit initialization, and fault-injected failures for each ADSP init, DSP IRQ request, speaker IRQ init, and component registration stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l24.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l24.h

## Purpose
`cs47l24.h` is the tiny private header for the CS47L24 codec driver. It includes the shared Arizona definitions and declares the numeric FLL IDs accepted by `cs47l24_set_fll()` in `cs47l24.c`.

## Important APIs, Types, and Data
- `CS47L24_FLL1` and `CS47L24_FLL2` identify the two main FLLs for direct `arizona_set_fll()` programming.
- `CS47L24_FLL1_REFCLK` and `CS47L24_FLL2_REFCLK` identify reference-clock programming for the two FLLs through `arizona_set_fll_refclk()`.
- The include guard `_CS47L24_H` prevents duplicate inclusion.

## Control Flow Role
The header has no executable code. Its constants drive the `switch` in `cs47l24_set_fll()`, allowing ASoC machine drivers to select whether they are programming the FLL output or its reference clock.

## State and Persistence Behavior
The header defines no state. Hardware FLL state is stored in Arizona registers and tracked by the `struct arizona_fll` instances in `struct cs47l24_priv`.

## Dependencies and Integration Points
The header includes `arizona.h`, so it is tied to the shared Arizona codec helper layer. It is included by `cs47l24.c`; machine-driver code that needs these numeric FLL IDs may also include it depending on tree conventions.

## Risks and Edge Cases
- The constants are simple integers and are not namespaced by an enum type, so invalid IDs are only caught at runtime by `cs47l24_set_fll()`.
- The header exposes FLL IDs but not the DAI IDs or compressed stream names, so users still need driver/source knowledge for full integration.

## Test Signals
Compile tests should verify inclusion with the Arizona headers. Runtime tests should call component `set_pll` with all four valid IDs and one invalid ID, confirming that FLL1/FLL2 output and reference-clock paths are dispatched correctly and invalid IDs return `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs47l24.h -->
