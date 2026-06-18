# Research: subset-b-006451

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8824.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8824.c

Purpose: implements the Nuvoton NAU88L24 ASoC codec I2C driver, including regmap access control, mixer controls, DAPM graph, DAI setup, FLL/sysclk programming, jack/button IRQ reporting, DMI board quirks, and exported helpers used by machine drivers.

Important APIs, types, and functions: the file registers `nau8824_i2c_driver`, `nau8824_component_driver`, and `nau8824_dai`. Key exported APIs are `nau8824_enable_jack_detect()` and `nau8824_components()`. Main control points include `nau8824_dai_startup()`, `nau8824_hw_params()`, `nau8824_set_fmt()`, `nau8824_set_tdm_slot()`, `nau8824_set_pll()`, `nau8824_set_sysclk()`, `nau8824_set_bias_level()`, `nau8824_suspend()`, and `nau8824_resume()`. Regmap policy is defined by `nau8824_readable_reg()`, `nau8824_writeable_reg()`, `nau8824_volatile_reg()`, and `nau8824_reg_defaults`.

Control flow: probe reads device properties or platform data, creates the I2C regmap, initializes the semaphore and quirks, validates device ID, resets the chip, applies analog/digital defaults, sets IRQ defaults when an IRQ exists, then registers the component and DAI. Playback and capture startup enforce a sample-rate ceiling derived from the currently selected ADC/DAC oversampling ratio. `hw_params()` programs OSR clock source, master-mode BCLK/LRCLK dividers, and I2S word length. `set_fmt()` accepts codec bit/frame provider mode, normal or inverted BCLK, and I2S/left/right/DSP_A/DSP_B formats. TDM supports up to four slots with same-half TX/RX masks.

State and persistence: runtime state lives in `struct nau8824` from the header: regmap, DAPM, jack, deferred jack-detect work, jack-detect semaphore, optional `mclk`, active sample rate, IRQ number, resume lock, and firmware-property tuning values. Register state is cached with RBTREE regcache; suspend marks it dirty and resumes sync it. Jack-detect state is split across `nau8824->jack`, ALSA jack status, `jdet_work`, `resume_lock`, and interrupt masks. DMI quirks persist in the global `nau8824_quirk`, with module parameter override.

Dependencies and integration points: depends on Linux I2C, regmap, clk, ACPI/OF properties, DMI, semaphore, ALSA SoC component/DAI/DAPM/TLV/jack APIs, and `nau8824.h`. Machine drivers integrate through the component DAI name `nau8824-hifi`, `set_sysclk`, `set_pll`, `set_tdm_slot`, component `set_bias_level`, and the exported jack helper. ACPI ID `10508824`, OF compatible `nuvoton,nau8824`, and I2C ID `nau8824` bind the driver.

Risks: jack IRQ and PCM configuration share hardware clocks, so missed semaphore release during resume or jack detection can stall playback setup. `nau8824_set_tdm_slot()` programs only DACL/DACR RX selection but validates mixed shifted/unshifted masks tightly; board descriptions must match those assumptions. Device properties are read into a fixed eight-element SAR threshold array using `sar_threshold_num`; invalid firmware data could overrun if property validation is not done elsewhere. FLL programming assumes `freq_out == 256 * Fs`; bad machine-driver clock calls can produce unsupported VCO/ref values. Quirk behavior is global rather than per-device.

Test signals: build with `CONFIG_SND_SOC_NAU8824`, boot probe over I2C/ACPI/OF, check regmap cache sync across suspend/resume, run playback/capture at boundary sample rates for each exposed OSR, test I2S/left/right/DSP formats and four-slot TDM masks, verify `nau8824_components()` on DMI-quirked boards, and exercise headset insertion, ejection, microphone detection, and button press/release IRQs while audio streams are active and after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8824.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8824.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8824.h

Purpose: defines the NAU8824 register map, bit fields, private driver state, clock-source enums, FLL helper structures, OSR helper structure, DAI name, and public helper prototypes consumed by `nau8824.c` and machine drivers.

Important APIs, types, and functions: exported prototypes are `nau8824_enable_jack_detect()` and `nau8824_components()`. `struct nau8824` is the central state container. `enum` values `NAU8824_CLK_DIS`, `NAU8824_CLK_MCLK`, `NAU8824_CLK_INTERNAL`, `NAU8824_CLK_FLL_MCLK`, `NAU8824_CLK_FLL_BLK`, and `NAU8824_CLK_FLL_FS` are passed through component sysclk calls. `struct nau8824_fll`, `struct nau8824_fll_attr`, and `struct nau8824_osr_attr` describe computed PLL/FLL and oversampling choices.

Control flow support: the header is data-oriented. Register constants divide the chip into enable/clock/FLL, IRQ/SAR/key detect, I2S/TDM, ADC/DAC filters and gains, DRC, class G/D, analog controls, MICBIAS, FEPGA, and charge pump blocks. The C file uses these constants to constrain regmap access, initialize the chip, sequence DAPM events, derive clock settings, decode interrupts, and configure button thresholds.

State and persistence: `struct nau8824` records persistent driver configuration loaded from device properties: micbias voltage, VREF impedance, jack polarity/debounce, SAR thresholds and timing, key debounce, and optional `mclk`. It also holds live state such as the ALSA jack pointer, work item, semaphore, DAPM context, regmap, sample rate, IRQ, and resume lock. Because the header exposes the structure, platform-data users can allocate and prefill the same state consumed by I2C probe.

Dependencies and integration points: depends on Linux device/regmap/clk/workqueue/semaphore and ALSA SoC types through including C files. `NAU8824_CODEC_DAI` defines the DAI name expected by machine drivers. Register values must stay synchronized with data sheet definitions and with the readable/writeable/volatile ranges in `nau8824.c`.

Risks: duplicated macro names for class D enable fields and typoed naming such as `NAU8824_I2S_DF_RIGTH` can invite mistakes in future edits. Public exposure of the whole private struct makes layout changes visible to in-tree platform-data users. Register masks are untyped integers, so shifts and masks must be manually verified against register width.

Test signals: compile users of `nau8824.h`, check that all macros referenced by `nau8824.c` resolve, verify no register fields overlap incorrectly in init and DAPM updates, and use sparse/build warnings to catch type drift in exported helper signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8824.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8825.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8825.c

Purpose: implements the Nuvoton NAU8825/NAU8825C ASoC codec, covering I2C binding, regmap defaults and Rev C patching, DAPM path sequencing, DAI format/TDM/clock/FLL handling, jack detection, button reporting, high-impedance headset recovery, programmable BIQ coefficients, and deferred crosstalk suppression calibration.

Important APIs, types, and functions: registers `nau8825_driver`, `nau8825_component_driver`, and `nau8825_dai`. The exported API is `nau8825_enable_jack_detect()`, also wired to component `.set_jack`. Major flows include `nau8825_hw_params()`, `nau8825_set_dai_fmt()`, `nau8825_set_tdm_slot()`, `nau8825_set_pll()`, `nau8825_set_sysclk()`, `nau8825_interrupt()`, `nau8825_jack_insert()`, `nau8825_high_imped_detection()`, `nau8825_xtalk_work()`, and `nau8825_xtalk_measure()`. `nau8825_biq_coeff_get()` and `nau8825_biq_coeff_put()` expose 20 bytes of raw BIQ coefficients through ALSA controls.

Control flow: probe reads device properties, builds regmap, initializes crosstalk work/semaphore state, resets the chip, reads software ID, optionally registers the NAU8825C patch, applies register defaults, requests IRQ, and registers the component. Audio startup constrains rate based on selected OSR. `hw_params()` programs ADC/DAC clock source, master-mode BCLK/LRCLK divisors, and sample width. `set_tdm_slot()` supports 4 or 8 slots, with one ADC TX channel and two DAC RX channels. Jack IRQ handling first confirms insertion, then switches from manual insertion IRQs to automatic HSD mode; completion IRQ classifies no-mic, OMTP, CTIA, or high-impedance headsets and may launch crosstalk measurement.

State and persistence: private state stores regmap, DAPM, jack, optional MCLK, software ID, IRQ, clock rate, button status, jack/SAR properties, crosstalk flags, delayed event storage, impedance RMS samples, and ADC delay. RBTREE regcache preserves register state across suspend/resume. The crosstalk routine backs up a small table of volume/gain registers, owns clocks and analog paths while measuring, then restores them, optionally with headphone volume ramping to reduce pops.

Dependencies and integration points: depends on Linux I2C/regmap/clk/semaphore/workqueue/int_log/math64/ACPI, ALSA SoC component/DAI/DAPM/TLV/jack APIs, and `nau8825.h`. Machine drivers use DAI name `nau8825-hifi`, component sysclk/PLL/jack callbacks, and optional device properties under `nuvoton,*`. OF compatible is `nuvoton,nau8825`, ACPI ID is `10508825`, and I2C ID is `nau8825`.

Risks: the crosstalk path deliberately modifies clocking, I2S master mode, DAC/ADC power, charge pump, and volume registers; cancellation and semaphore release must be correct on eject, suspend, component remove, and IRQ races. `nau8825_sema_reset()` writes the semaphore count directly, which is fragile against kernel semaphore internals and concurrent waiters. Property-provided SAR threshold count is used as an array length for an eight-element array. IRQ handling assumes active-low threaded IRQ configuration. The polarity and high-impedance detection paths are sensitive to board wiring and MICBIAS/SAR settings.

Test signals: build with NAU8825/NAU8825C IDs, probe both software IDs, verify Rev C patch registration, exercise I2S/left/right/DSP formats and 4/8-slot TDM masks, run playback/capture under selected OSR rates, test suspend/resume with and without active jack, validate button thresholds, OMTP/CTIA/high-impedance headset detection, crosstalk enabled and disabled, ejection during crosstalk work, BIQ coefficient read/write, and MCLK-managed versus externally managed clock configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8825.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8825.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8825.h

Purpose: provides the NAU8825 register definitions, masks, clock-source enums, crosstalk state enum, private state layout, and exported jack-detect prototype used by the NAU8825 codec implementation.

Important APIs, types, and functions: public prototype is `nau8825_enable_jack_detect()`. `struct nau8825` contains all live and property-backed codec state. The clock enum is shared with component `.set_sysclk`; the crosstalk enum drives `nau8825_xtalk_measure()`. Register macros cover FLL, HSD, IRQ masks/status/disable, SAR/key detection, GPIO jack detect, I2S/TDM, BIQ, ADC/DAC rates, IMM measurement, class G, software ID, bias/test DAC, analog ADC, MICBIAS, boost, power-up stages, and charge pump.

Control flow support: this header is the contract for the implementation's bit operations. The C file combines these masks in regmap init, DAPM event callbacks, jack IRQ transitions, crosstalk measurement, and FLL programming. Software IDs `NAU8825_SOFTWARE_ID_NAU8825` and `NAU8825_SOFTWARE_ID_NAU8825C` select normal behavior or the Rev C patch and 24-bit FLL fraction handling.

State and persistence: `struct nau8825` tracks static board configuration from device properties, live ALSA objects, MCLK enable state, current jack/button/crosstalk state, backup-table initialization, impedance RMS samples, and ADC delay. The structure is private to the codec but sits in the header so platform-data users and the C file share the same layout.

Dependencies and integration points: depends on ALSA SoC and Linux kernel types included through the implementation. Machine drivers and board descriptions must use `nuvoton,*` properties whose values match the bit-field ranges here, especially jack polarity/debounce, SAR thresholds, crosstalk enable, ADC output drive strength, and ADC delay.

Risks: several masks encode polarity with inverted semantics, for example GPIO pull/output disable bits, so property translation is easy to invert. The typo `NAU8825_CHANRGE_PUMP_EN` is used consistently but can trip new code. Public private-state layout increases churn risk. Fixed-size SAR arrays require property bounds discipline.

Test signals: compile `nau8825.c` against the header, verify all register fields used by init, IRQ, TDM, BIQ, and crosstalk paths are covered, test software-ID dependent conditionals, and validate property values against data sheet bit ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8825.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntp8835.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ntp8835.c

Purpose: implements an ASoC I2C driver for Neofidelity NTP8835/NTP8835C three-channel amplifiers with reset sequencing, MCLK validation, optional EQ firmware loading through `ntpfw`, playback controls, DAPM outputs, and suspend/resume power sequencing.

Important APIs, types, and functions: private state is `struct ntp8835_priv`. Key functions are `ntp8835_reset_gpio()`, `ntp8835_load_firmware()`, `ntp8835_snd_suspend()`, `ntp8835_snd_resume()`, `ntp8835_probe()`, `ntp8835_set_component_sysclk()`, `ntp8835_hw_params()`, `ntp8835_set_fmt()`, and `ntp8835_i2c_probe()`. ALSA controls include playback volume and a custom playback switch that writes all three soft-mute bits.

Control flow: I2C probe allocates state, gets a shared reset control, deasserts and toggles reset using data-sheet delays, creates an 8-bit regmap, registers the component/DAI, and enables the `mclk`. Component probe adds controls and loads `eq_8835.bin` when present. `set_sysclk()` accepts only 12.288 MHz, 24.576 MHz, and 18.432 MHz. `hw_params()` writes the MCLK frequency code and, for left/right justified formats, writes GSA format bits based on sample width. Suspend bypasses regcache, writes sound-off sequence, asserts reset, marks cache dirty, and disables MCLK; resume reverses the sequence, reloads firmware, and syncs cache.

State and persistence: stores current DAI format and MCLK rate in driver state. Regmap uses MAPLE cache. Firmware is not persistent across reset or suspend because resume reloads it. Mute and PWM state are driven by explicit sound-on/off register sequences.

Dependencies and integration points: depends on I2C, regmap, reset controller, clock framework, ALSA SoC, TLV controls, and `ntpfw_load()`. OF compatible is `neofidelity,ntp8835`, DAI name is `ntp8835-amplifier`, firmware name is `eq_8835.bin`, and magic is `"8835"`.

Risks: missing firmware is downgraded to warning, so systems can boot without intended EQ tuning. MCLK must be supplied through component `set_sysclk()` before `hw_params()`, otherwise audio setup fails. Reset timing and shared reset semantics affect multi-amp boards. Only I2S/right/left justified formats are accepted; no explicit master mode support is configured beyond clearing master bit.

Test signals: probe with reset and MCLK resources, run playback over 1 to 3 channels, verify accepted MCLKs and rejected invalid MCLKs, test I2S/left/right justified formats at 16/20/24/32-bit widths, suspend/resume with firmware present and absent, and confirm soft mute and PWM sound-off state on power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntp8835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntp8918.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ntp8918.c

Purpose: implements an ASoC I2C driver for the Neofidelity NTP8918 two-channel amplifier with BCLK management, reset timing, optional firmware loading, playback controls, DAI format programming, soft mute, DAPM outputs, and suspend/resume support.

Important APIs, types, and functions: private state is `struct ntp8918_priv`. Key functions are `ntp8918_reset_gpio()`, `ntp8918_load_firmware()`, `ntp8918_snd_suspend()`, `ntp8918_snd_resume()`, `ntp8918_probe()`, `ntp8918_hw_params()`, `ntp8918_set_fmt()`, `ntp8918_digital_mute()`, and `ntp8918_i2c_probe()`. The DAI is `ntp8918-amplifier`; controls expose playback volume and playback switch.

Control flow: probe allocates state, acquires shared reset, toggles reset with data-sheet delays, initializes 8-bit regmap, registers component/DAI, and enables the `bck` clock. Component probe adds controls and loads `eq_8918.bin` if available. `hw_params()` derives the chip MCLK frequency code from the calculated bit clock, then configures normal I2S or GSA left/right justified mode and width bits. `mute_stream()` toggles both soft-mute bits. Suspend writes the sound-off sequence, asserts reset, marks regcache dirty, and disables BCK; resume enables BCK, resets the chip, writes sound-on sequence, reloads firmware, disables cache-only mode, and syncs regcache.

State and persistence: only current serial format and BCK/reset/I2C handles are held in private state. Regmap cache is MAPLE. Firmware is replayed after resume because reset clears chip state. Playback volume default sound-on/off sequences use `MASTER_VOL` values rather than the NTP8835 PWM switch sequence.

Dependencies and integration points: depends on I2C, regmap, reset, clock framework, ALSA SoC, TLV, and `ntpfw_load()`. OF compatible is `neofidelity,ntp8918`; firmware name is `eq_8918.bin` with magic `"8918"`.

Risks: BCLK values are whitelisted to 3.072 MHz, 2.8224 MHz, 6.144 MHz, and 2.048 MHz; unusual rates or slot widths fail. Missing firmware is non-fatal but may remove board-specific EQ. Reset timing and clock availability directly affect resume reliability. The driver does not expose capture or complex routing, only a simple playback DAI.

Test signals: verify probe with `bck` and reset resources, accepted rates 32/44.1/48/96 kHz, I2S/left/right justified formats at supported widths, mute toggling, firmware-present and firmware-missing cases, and suspend/resume audio recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntp8918.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.c

Purpose: provides a shared firmware loader for Neofidelity amplifier drivers. It requests a firmware file, validates a big-endian magic header, parses variable chunks, and sends chunk payloads over I2C in fixed step sizes.

Important APIs, types, and functions: packed `struct ntpfw_header` contains a big-endian magic value. Packed `struct ntpfw_chunk` contains a big-endian payload length, an I2C transfer step, and payload bytes. Internal helpers are `ntpfw_verify()`, `ntpfw_verify_chunk()`, and `ntpfw_send_chunk()`. Public exported API is `ntpfw_load(struct i2c_client *i2c, const char *name, u32 magic)`.

Control flow: `ntpfw_load()` calls `request_firmware()`, validates the image header, then iterates from the first chunk after the header until no bytes remain. Each chunk must have step 2 or 5, length not exceeding remaining firmware bytes, and length divisible by step. The sender loops over payload bytes and calls `i2c_master_send()` with exactly `step` bytes. Any short send returns `-EIO`; negative I2C errors are propagated. Firmware is always released through the `done` path.

State and persistence: the helper holds no persistent state. All state is in the firmware buffer and local parsing pointers. Calling amplifier drivers decide whether missing firmware is fatal and when to reload after reset or resume.

Dependencies and integration points: depends on Linux firmware loader, I2C core, endian helpers, module exports, and `ntpfw.h`. It is used by `ntp8835.c` and `ntp8918.c` with different firmware names and magic values.

Risks: chunk-size validation allows `chunk_size == buf_size`, but later pointer arithmetic subtracts `chunk_size + sizeof(*chunk)` from `leftover`; malformed images can underflow `size_t` if there is no room for the chunk header plus data. The image format trusts packed unaligned casts. Only step sizes 2 and 5 are supported. Errors log but do not identify chunk offsets.

Test signals: unit or fault-injection tests with too-small images, bad magic, invalid steps, non-divisible lengths, short I2C writes, exact-boundary chunks, multiple chunks, and firmware release on every error path. Integration tests should confirm NTP8835/NTP8918 firmware blobs are accepted and sent in the expected transfer widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.h

Purpose: declares the shared Neofidelity firmware-loading API used by NTP amplifier codecs.

Important APIs, types, and functions: exposes `int ntpfw_load(struct i2c_client *i2c, const char *name, const u32 magic);`, which loads and validates a firmware image, then writes it to the amplifier over I2C. The header includes Linux I2C and firmware declarations.

Control flow support: callers provide the I2C client, firmware file name, and expected magic. The implementation owns request, parse, transfer, and release operations. The return value is zero on success or a negative errno from firmware loading, validation, allocation-free parsing, or I2C transmission.

State and persistence: no persistent state is declared. Firmware state is transient and owned by `ntpfw.c`; callers must reload after hardware reset when needed.

Dependencies and integration points: included by `ntp8835.c`, `ntp8918.c`, and `ntpfw.c`. The prototype uses `const u32 magic`, while the implementation accepts `u32 magic`; this is ABI-compatible in C but not text-identical.

Risks: the header does not document the binary chunk format beyond "load firmware"; format changes require synchronized implementation and firmware generation. Callers must decide whether `-ENOENT` is fatal.

Test signals: compile users against the declaration, verify exported symbol availability when built as modules, and test callers' error handling for `-ENOENT`, `-EINVAL`, and I2C failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1681.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1681.c

Purpose: implements a TI PCM1681 eight-channel DAC ASoC I2C codec with register defaults, playback volume controls, de-emphasis control, soft mute, DAI format setup, and simple DAPM output routing.

Important APIs, types, and functions: private state is `struct pcm1681_private`. Key functions are `pcm1681_set_deemph()`, `pcm1681_get_deemph()`, `pcm1681_put_deemph()`, `pcm1681_set_dai_fmt()`, `pcm1681_mute()`, `pcm1681_hw_params()`, and `pcm1681_i2c_probe()`. Regmap policy is handled by `pcm1681_accessible_reg()` and `pcm1681_writeable_reg()`. Controls include four stereo volume pairs and a de-emphasis switch.

Control flow: probe allocates state, initializes an 8-bit I2C regmap with defaults and access filters, stores client data, and registers one playback DAI. `set_fmt()` requires codec clock consumer mode. `hw_params()` records the rate, maps right-justified/I2S/left-justified plus width to format register values, writes `PCM1681_FMT_CONTROL`, and applies de-emphasis if enabled and the sample rate is one of 44.1, 48, or 32 kHz. Mute writes all bits in the soft-mute register.

State and persistence: driver state stores regmap, current serial format, de-emphasis enable, and current rate. Register defaults seed regmap cache but no explicit suspend/resume callbacks are present. De-emphasis is recomputed on each parameter change so the control follows the active sample rate.

Dependencies and integration points: depends on I2C, regmap, OF, ALSA SoC/TLV/DAPM. OF compatible is `ti,pcm1681`, I2C ID is `pcm1681`, DAI name is `pcm1681-hifi`, playback supports 2 to 8 channels, 8 kHz to 192 kHz fixed rates, and S16/S24 formats.

Risks: only clock-consumer mode is allowed. De-emphasis silently disables for unsupported rates even if the user switch remains set. Register 0x0e is readable but not writeable; access masks must match the data sheet. No reset GPIO or regulator handling is present, so board integration must ensure power and reset externally.

Test signals: probe on I2C/OF, run 2/4/6/8-channel playback at all advertised rates, verify I2S/left/right justified format register values, test mute and volume TLV controls, toggle de-emphasis at 32/44.1/48 kHz and an unsupported rate, and inspect regmap access to zero-detect status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1681.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1754.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1754.c

Purpose: implements a simple platform ASoC driver for the TI PCM1754 stereo DAC, which has no register bus and is controlled by optional mute and format GPIOs plus a regulator-backed DAPM supply.

Important APIs, types, and functions: private state is `struct pcm1754_priv`. Key functions are `pcm1754_set_dai_fmt()`, `pcm1754_hw_params()`, `pcm1754_mute_stream()`, and `pcm1754_probe()`. The DAI is `pcm1754`, and the component uses DAPM widgets for `VCC`, two DAC channels, and `VOUTL/VOUTR`.

Control flow: platform probe duplicates the DAI template, allocates state, obtains optional `mute` GPIO default-high and `format` GPIO default-low, stores state, and registers the component. `set_fmt()` records the requested serial format. `hw_params()` maps right-justified 16-bit to format GPIO high, I2S 16/24-bit to format GPIO low, and rejects unsupported widths/formats. `mute_stream()` directly drives the mute GPIO.

State and persistence: only current DAI format and GPIO descriptors are stored. There is no regmap, firmware, cache, or explicit suspend/resume state. DAPM controls the `VCC` regulator supply if provided by the board.

Dependencies and integration points: depends on platform bus, GPIO consumer API, regulator-backed DAPM supply, and ALSA SoC. OF compatible is `ti,pcm1754`. Playback is stereo only, continuous 5 kHz to 200 kHz, S16/S24 formats.

Risks: no validation of clock provider flags occurs, only serial data format and width. Optional GPIO absence means mute or format hardware controls may be unavailable without failing probe. DAI driver is duplicated at probe, but no per-instance changes are made. Board polarity must match GPIO descriptor configuration.

Test signals: probe with and without optional GPIOs and VCC regulator, verify mute GPIO state on stream mute/unmute, check format GPIO for right-justified 16-bit and I2S 16/24-bit, reject invalid widths, and run power DAPM sequencing through VCC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1754.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789-i2c.c

Purpose: provides the I2C transport wrapper for the common TI PCM1789 codec core.

Important APIs, types, and functions: `pcm1789_i2c_probe()` creates an I2C regmap using `pcm1789_regmap_config` and calls `pcm1789_common_init()`. `pcm1789_i2c_remove()` calls `pcm1789_common_exit()` to flush deferred work. The driver binds I2C ID `pcm1789` and OF compatible `ti,pcm1789`.

Control flow: probe allocates only the regmap. All codec state allocation, reset GPIO handling, workqueue initialization, DAI/component registration, and controls are delegated to `pcm1789_common_init()`. Remove delegates cleanup to the common core.

State and persistence: no transport-specific state beyond device-managed regmap resources. Common state is stored as device drvdata by `pcm1789_common_init()`.

Dependencies and integration points: depends on I2C, OF, regmap, and `pcm1789.h`. This split lets the same common codec core be shared with other buses if added later.

Risks: remove assumes common init succeeded and drvdata exists. Any regmap bus quirks must be represented in the shared config. Probe error handling only logs regmap allocation failure.

Test signals: I2C probe on `ti,pcm1789`, regmap creation failure path, successful component registration, remove with pending PCM trigger work, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789.c

Purpose: implements the bus-independent TI PCM1789 stereo DAC ASoC codec core with format programming, volume control, soft mute, reset GPIO handling, a deferred software reset trigger workaround, DAPM outputs, and exported common init/exit helpers.

Important APIs, types, and functions: private state is `struct pcm1789_private`. Public exports are `pcm1789_regmap_config`, `pcm1789_common_init()`, and `pcm1789_common_exit()`. Key DAI functions are `pcm1789_set_dai_fmt()`, `pcm1789_mute()`, `pcm1789_hw_params()`, and `pcm1789_trigger()`. `pcm1789_work_queue()` performs the delayed software reset bit update.

Control flow: common init allocates state, stores the regmap and device, obtains optional reset GPIO asserted high, deasserts it, waits 300 ms, initializes work, and registers the component/DAI. `set_fmt()` records the chosen serial format. `hw_params()` maps right-justified 24/16, I2S 16/24/32, and left-justified 16/24/32 to format bits. `mute_stream()` updates soft-mute bits. PCM start/resume/pause-release schedules work that writes the SRET reset bits to recover from a desynchronized state; common exit flushes that work.

State and persistence: private state stores current format, rate, reset GPIO, work item, regmap, and device. Regmap defaults cover format, mute, and left/right volume registers. No explicit suspend/resume callbacks exist; device-managed resources and regmap defaults handle initialization.

Dependencies and integration points: depends on GPIO consumer, workqueue, regmap, ALSA SoC/TLV/DAPM, and `pcm1789.h`. The DAI name is `pcm1789-hifi`, playback is stereo, continuous 10 kHz to 200 kHz, with S16/S24/S32 formats.

Risks: mute logic writes `mute ? 0 : PCM1789_MUTE_MASK`, which relies on chip semantics where clearing bits mutes or enables specific state; tests should confirm user-visible polarity. The trigger workaround runs asynchronously and must be flushed on remove. No clock-provider validation is done in `set_fmt()`. Optional reset GPIO absence is accepted.

Test signals: probe through I2C wrapper, playback in right/I2S/left formats at supported widths, volume and mute controls, trigger start/resume/pause-release scheduling, remove while work is pending, reset GPIO polarity, and regmap access boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789.h

Purpose: declares the shared PCM1789 codec interface for bus wrappers.

Important APIs, types, and functions: defines `PCM1789_FORMATS` as S32, S24, and S16 little-endian PCM formats. Declares exported `pcm1789_regmap_config`, `pcm1789_common_init()`, and `pcm1789_common_exit()`.

Control flow support: I2C or future bus drivers include this header, create a regmap using `pcm1789_regmap_config`, call common init at probe, and call common exit at remove to flush work.

State and persistence: no state is declared here. Common state is private to `pcm1789.c` and attached to the device by common init.

Dependencies and integration points: relies on including code to provide `struct device` and `struct regmap` definitions. The header is included by `pcm1789.c` and `pcm1789-i2c.c`.

Risks: bus wrappers must remember to call `pcm1789_common_exit()` if they support removal; otherwise deferred reset work could outlive the device. Format macro must stay synchronized with the DAI formats in `pcm1789.c`.

Test signals: compile the I2C wrapper and common core as modules/built-in, verify exported symbol resolution, and add any future bus wrapper using the same init/exit sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm1789.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-i2c.c

Purpose: provides the I2C transport wrapper for the shared TI PCM179x codec core.

Important APIs, types, and functions: `pcm179x_i2c_probe()` initializes an I2C regmap with `pcm179x_regmap_config` and delegates to `pcm179x_common_init()`. It binds OF compatible `ti,pcm1792a` and I2C ID `pcm179x`.

Control flow: probe does no codec logic beyond regmap creation and common-core registration. There is no remove callback because common state uses device-managed allocation and the PCM179x core has no deferred work cleanup hook.

State and persistence: no I2C-specific persistent state. The common core stores private state in device drvdata.

Dependencies and integration points: depends on I2C, OF, regmap, and `pcm179x.h`. It provides one of two bus front ends for `pcm179x.c`, with SPI handled by `pcm179x-spi.c`.

Risks: only `ti,pcm1792a` is listed in OF despite the generic driver name. Any transport-specific register formatting must be compatible with the shared 8-bit regmap config.

Test signals: I2C probe on compatible hardware, regmap allocation failure, component registration through common init, and playback smoke tests through the shared DAI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-spi.c

Purpose: provides the SPI transport wrapper for the shared TI PCM179x codec core.

Important APIs, types, and functions: `pcm179x_spi_probe()` initializes an SPI regmap using `pcm179x_regmap_config` and calls `pcm179x_common_init()`. It binds OF compatible `ti,pcm1792a` and SPI IDs `pcm1792a` and `pcm179x`.

Control flow: probe allocates only the regmap and delegates all codec registration and behavior to the common core. Module registration uses `module_spi_driver()`.

State and persistence: no SPI-specific private state. The shared core owns state and component registration through device-managed resources.

Dependencies and integration points: depends on SPI, OF, regmap, and `pcm179x.h`. It allows the same codec programming path as I2C while using `devm_regmap_init_spi()`.

Risks: shared regmap configuration must be valid for SPI framing on all supported PCM179x variants. There is no remove hook, matching the common core's lack of deferred resources. OF compatible is narrow.

Test signals: SPI probe by ID and OF compatible, regmap allocation failure path, shared component registration, and playback format/mute/volume testing over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.c

Purpose: implements the bus-independent TI PCM179x/PCM1792A stereo DAC ASoC core with regmap defaults, format setup, mute, playback volume and DAC controls, DAPM current outputs, and exported common init/regmap configuration for I2C and SPI wrappers.

Important APIs, types, and functions: private state is `struct pcm179x_private`. Public exports are `pcm179x_regmap_config` and `pcm179x_common_init()`. Core functions are `pcm179x_set_dai_fmt()`, `pcm179x_mute()`, `pcm179x_hw_params()`, `pcm179x_accessible_reg()`, and `pcm179x_writeable_reg()`.

Control flow: bus wrapper creates a regmap and calls common init, which allocates private state, stores the regmap, attaches drvdata, and registers the component/DAI. `set_fmt()` records serial format. `hw_params()` maps right-justified 16/24/32 and I2S 16/24/32 to format bits, enables ATLD, and writes `PCM179X_FMT_CONTROL`. `mute_stream()` updates the soft-mute bit. Controls expose left/right DAC volume, output inversion, and rolloff filter.

State and persistence: private state stores regmap, current format, and current rate. Regmap defaults cover registers 0x10 through 0x17; status registers 0x16 and 0x17 are readable but not writeable. No explicit suspend/resume callbacks or reset resources are present.

Dependencies and integration points: depends on ALSA SoC/TLV/DAPM, regmap, OF declarations, and `pcm179x.h`. DAI name is `pcm179x-hifi`; playback is stereo, continuous 10 kHz to 200 kHz, using the format mask from `PCM1792A_FORMATS`. Bus integration is through `pcm179x-i2c.c` and `pcm179x-spi.c`.

Risks: only I2S and right-justified formats are accepted; left-justified is unsupported despite similar sibling drivers supporting it. No clock-provider validation is performed. Hardware reset and power sequencing are delegated entirely to board design. Format macro names PCM1792A specifically while common driver is generic.

Test signals: probe through both I2C and SPI, verify accepted and rejected serial formats/widths, confirm ATLD and format bits in regmap, test mute polarity, volume TLVs, invert and rolloff controls, and regmap read/write access masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.h

Purpose: declares the shared PCM179x codec interface and supported PCM formats for I2C/SPI wrappers.

Important APIs, types, and functions: defines `PCM1792A_FORMATS` as S32, S24, and S16 little-endian PCM. Declares exported `pcm179x_regmap_config` and `pcm179x_common_init()`.

Control flow support: bus drivers include this header, construct a regmap with the exported config, and call common init to register the ASoC component and DAI.

State and persistence: no state is declared in the header. Common state is private to `pcm179x.c` and is attached to the device.

Dependencies and integration points: included by `pcm179x.c`, `pcm179x-i2c.c`, and `pcm179x-spi.c`. The header assumes including files provide `struct device` and `struct regmap` declarations.

Risks: there is no common exit hook because the core has no deferred work, so future additions that need cleanup must extend the interface. The format macro name is variant-specific and should stay aligned with the DAI in the common core.

Test signals: build both bus wrappers, verify exported symbols resolve in module configurations, and ensure future wrappers use the same regmap/init contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm179x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-i2c.c

Purpose: provides the I2C transport wrapper for the TI PCM186x universal audio ADC common driver.

Important APIs, types, and functions: `pcm186x_i2c_probe()` obtains the matched `enum pcm186x_type`, creates an I2C regmap with exported `pcm186x_regmap`, passes the device, type, IRQ, and regmap to `pcm186x_probe()`, and registers the I2C driver. OF compatibles map `ti,pcm1862`, `ti,pcm1863`, `ti,pcm1864`, and `ti,pcm1865` to type constants; I2C IDs mirror those names.

Control flow: matching supplies chip type through `i2c_get_match_data()`. Probe does transport setup only; the common core owns ADC controls, DAI registration, IRQ behavior, and device-specific feature handling.

State and persistence: no wrapper-private state. Regmap is device-managed, and common state is allocated by `pcm186x_probe()`.

Dependencies and integration points: depends on I2C and the common `pcm186x.h` declarations. It integrates board descriptions through OF/I2C IDs and forwards the physical IRQ to the common ADC driver.

Risks: if match data is absent or mismatched for non-OF I2C IDs, the cast result must still be a valid `enum pcm186x_type`; this depends on I2C core match-data behavior. All bus-specific register IO assumptions are captured by the shared regmap config. Probe returns raw regmap errors without contextual logging.

Test signals: probe each compatible/ID variant, verify type passed into common probe, test IRQ and no-IRQ configurations, validate regmap creation failure handling, and run common PCM186x ADC capture tests through the I2C wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-i2c.c -->
