# subset-b-006428 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-shared.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-shared.c

Purpose: shared support code for CS35L56/CS35L63 smart amplifier drivers used by ASoC and HDA-facing layers. It centralizes register patches/defaults, readable/volatile/precious regmap policy, firmware register address selection by silicon type/revision, mailbox commands, reset/hibernate sequencing, IRQ handling, DSP memory mapping, calibration storage/debugfs helpers, speaker-ID acquisition, BCLK validation, supply naming, TX source enumerations, and bus-specific regmap configurations for I2C, SPI, and SoundWire.

Important APIs and data: exported symbols include `cs35l56_set_asp_patch`, `cs35l56_set_patch`, `cs35l56_mbox_send`, `cs35l56_firmware_shutdown`, `cs35l56_wait_for_firmware_boot`, reset timing helpers, `cs35l56_system_reset`, `cs35l56_irq_request`, `cs35l56_irq`, runtime PM common helpers, `cs35l56_init_cs_dsp`, calibration functions, firmware-status/tuning log helpers, `cs35l56_hw_init`, speaker-ID helpers, `cs35l56_get_bclk_freq_id`, `cs35l56_fill_supply_names`, exported TX source tables, and exported `regmap_config` instances. Static tables define ASP/firmware patches, CS35L56/CS35L63 defaults, firmware register maps, reset sequences, hibernate sequence, calibration control names/algorithm IDs, BCLK PLL IDs, and supply names.

Control flow: probe callers create a regmap then call shared hardware init. `cs35l56_hw_init` wakes or waits after reset, reads revision, selects firmware register table, waits for firmware boot, validates device ID, enables cache access, detects secure mode, logs firmware/OTP identity, unmasks critical amp-short and overtemperature interrupts, and reads silicon UID. Runtime suspend waits for PS3, records boot-done state, enters cache-only, and optionally sends auto-hibernate. Runtime resume wakes I2C/SPI with bypassed dummy reads, waits for firmware boot, sends prevent-auto-hibernate, detects register reset through BOOT_DONE, and syncs the cache. System reset enters cache-only first; SPI uses a bus-locked two-write sequence, while non-SPI writes revision-specific reset sequences through bypassed regmap.

State and persistence: `cs35l56_base` carries init status, type/revision, security, firmware register table, calibration data validity, silicon UID, on-chip speaker-ID GPIO configuration, hibernate capability, IRQ number, and regmap cache state. Persistent tuning/calibration is external to the chip: EFI calibration is fetched/stored through `cs-amp-lib`, while register cache and firmware controls are repopulated after reset or hibernate. Secure devices intentionally skip driver-written calibration. The regmap cache policy treats firmware-owned and status registers as volatile and DSP packed memories as precious.

Dependencies and integration points: depends on Linux regmap, runtime PM, debugfs, GPIO, regulator, SPI, SoundWire-facing constants, Cirrus firmware/DSP libraries (`cs_dsp`, `wmfw`, `cs-amp-lib`), and exported namespace `SND_SOC_CS35L56_SHARED`. ASoC core (`cs35l56.c`) and bus wrappers consume the exported helpers/configs. Integration risk is high around reset/hibernate ordering: cache-only must bracket reset and hibernate commands, SPI reset must prevent other bus traffic, and SoundWire reset must tolerate re-enumeration. Other risks include incomplete register readable/volatile lists, invalid BCLK lookup failures, calibration target mismatch, and speaker-ID GPIO property validation. Test signals are mostly KUnit coverage in `cs35l56-test.c` for firmware naming and on-chip speaker-ID parsing; hardware behavior is validated by probe logs, IRQ critical logs, firmware boot polling, regcache sync errors, and calibration debugfs/control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-spi.c

Purpose: SPI bus binding for the CS35L56 ASoC smart amplifier core. It allocates the private codec object, builds the SPI regmap using the shared CS35L56 SPI configuration, initializes SPI-specific bus details, invokes the common ASoC probe/init sequence, and wires the optional SPI IRQ into the shared threaded IRQ handler.

Important APIs and data: `cs35l56_spi_probe` is the main entry point; `cs35l56_spi_remove` tears the core down. The file declares `cs35l56_id_spi`, ACPI match ID `CSC355C`, and a `spi_driver` named `cs35l56` using `cs35l56_pm_ops_i2c_spi`. It imports the `SND_SOC_CS35L56_CORE` and `SND_SOC_CS35L56_SHARED` namespaces. It relies on shared `cs35l56_regmap_spi`, `cs35l56_init_config_for_spi`, `cs35l56_common_probe`, `cs35l56_init`, `cs35l56_irq_request`, and `cs35l56_remove`.

Control flow: probe allocates `struct cs35l56_private`, stores it with `spi_set_drvdata`, seeds `base.type` as `0x56`, creates a 32-bit big-endian SPI regmap, sets `base.dev`, marks `can_hibernate`, applies SPI bus configuration, runs the common probe, then performs hardware init and IRQ request. If init or IRQ setup fails after common probe, it calls `cs35l56_remove` to unwind registered ASoC/runtime-PM state. Remove simply delegates to the core remove path.

State and persistence: no persistent state is owned in this wrapper beyond the driver data pointer and initial `base` fields. Runtime/system PM behavior is inherited from `cs35l56_pm_ops_i2c_spi`, and regcache/firmware/calibration state belongs to the shared/core layers. The wrapper’s most important state decision is `can_hibernate = true`, enabling the shared runtime PM hibernate path.

Dependencies and integration points: integrates Linux SPI, ACPI, module tables, regmap, and the CS35L56 shared/core modules. Risks are mostly sequencing and unwind related: failures after common probe must not leave workqueues, supplies, runtime PM, or IRQs live; SPI reset correctness depends on the shared SPI bus-locking reset implementation. There are no local KUnit tests for this file; test signals are successful SPI probe/remove, ACPI/SPI modalias binding, firmware boot logs, IRQ delivery, and suspend/resume on SPI-attached systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-test.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-test.c

Purpose: KUnit coverage for CS35L56 firmware naming, SoundWire suffix selection, vendor-specific SSIDExV2 fallback behavior, SDCA function-extension parsing for on-chip speaker-ID GPIOs, and lazy on-chip speaker-ID reads in `cs35l56_set_fw_name`. It exercises KUnit-exported functions from `cs35l56.c` and shared speaker-ID helpers without real hardware.

Important APIs and data: the test defines `struct cs35l56_test_priv` with a faux device, minimal `cs35l56_private`, SSIDExV2 string, and stub-call booleans. `struct cs35l56_test_param` drives parameterized silicon type/revision and GPIO/pull cases. It uses faux devices, software nodes, KUnit resources/actions, static stubs for `cs_amp_devm_get_vendor_specific_variant_id`, EFI variable lookup hooks, and stubs for `cs35l56_configure_onchip_spkid_pads`/`cs35l56_read_onchip_spkid`.

Control flow: common init creates a faux amp device, allocates a minimal component/card/private-data graph, attaches driver data, and optionally sets type/revision. A SoundWire-specific init adds a dummy `sdw_slave` pointer. Test cases then set component prefixes, PCI SSIDs, software-node properties, speaker IDs, SoundWire link/unique IDs, and stubbed EFI responses before calling `cs35l56_get_firmware_uid`, `cs35l56_set_fw_name`, `cs35l56_set_fw_suffix`, or `cs35l56_process_xu_properties`.

State and persistence: all state is per-test and cleaned up by KUnit actions. The tests verify that `dsp.system_name`, `dsp.fwf_suffix`, `fallback_fw_suffix`, `speaker_id`, `base.onchip_spkid_gpios`, and `base.onchip_spkid_pulls` are mutated correctly. They explicitly check that existing speaker IDs are preserved and that on-chip GPIO reads happen only when a speaker ID is absent and on-chip GPIO descriptors were parsed.

Dependencies and integration points: depends on KUnit, faux devices, software nodes, static stubs, EFI test hooks in `cs-amp-lib`, minimal ASoC component/card structures, and SoundWire type definitions. Risks covered include firmware asset naming regressions, legacy CS35L56 B0 SoundWire suffix compatibility, bad precedence between firmware UID and PCI SSID, and incorrect SDCA XU GPIO indexing/pulls. Risks not covered include real regmap I/O, runtime PM failures around on-chip speaker reads, and hardware timing. Test signals are the two KUnit suites: `snd-soc-cs35l56-test-soundwire` and `snd-soc-cs35l56-test-not-soundwire`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56.c

Purpose: main ASoC component/core implementation for Cirrus CS35L56/CS35L63 smart amplifiers. It defines ALSA controls, DAPM topology, ASP and SoundWire DAI operations, DSP firmware loading/reinit/patch flows, calibration controls/debugfs integration, firmware naming, SDCA/XU speaker-ID parsing, common probe/init/remove, and runtime/system PM glue for I2C/SPI devices.

Important APIs and data: exported core functions are `cs35l56_common_probe`, `cs35l56_init`, `cs35l56_remove`, system suspend/resume stages, and KUnit-visible `cs35l56_set_fw_suffix`, `cs35l56_set_fw_name`, `cs35l56_process_xu_properties`, `cs35l56_get_firmware_uid`. Key static objects include CS35L56/CS35L63 mixer controls, DAPM widgets/routes, ASP/SoundWire DAI ops, three DAI drivers (`cs35l56-asp1`, `cs35l56-sdw1`, `cs35l56-sdw1c`), calibration debugfs fops, optional calibration restore/perform controls, component driver, and PM ops.

Control flow: `cs35l56_common_probe` initializes completions/locks, obtains supplies/reset GPIO, powers/reset the amp, discovers speaker ID from vendor/property/GPIO or broken SDCA ACPI workaround, builds firmware UID/XU state, initializes `wm_adsp`, and registers the component. `cs35l56_init` enables runtime PM, runs shared hardware init, applies patches, fetches calibration, optionally soft-resets when no reset GPIO exists, handles SoundWire re-enumeration, prevents firmware auto-hibernate, syncs regcache, sets ASP DOUT Hi-Z behavior, marks init complete, and completes waiters. Component probe waits for init, builds DSP part/name/suffix, registers wm_adsp, creates debugfs/controls, disables the calibration pin, and queues DSP work.

The DSP work path reads firmware missing/version state, selects version-qualified firmware/coefficient names, then either downloads/patches missing firmware with shutdown and soft reset or does a cheaper reinit/tuning path for already patched firmware. Calibration flows power DAPM’s `Calibrate` pin, write/read coefficients through `cs-amp-lib`, and send AUDIO_REINIT after applying data. ASP ops enforce codec-consumer clocking, I2S/DSP_A formats, slot constraints, BCLK PLL ID validation, word length/slot width programming, and optional sysclk override. SoundWire ops map masks to SDW port configs and add/remove slave streams.

State and persistence: `struct cs35l56_private` holds DSP/workqueue/component, SoundWire attachment/IRQ fields, firmware fallback suffix, speaker ID, ASP slot/sysclk/TDM state, SoundWire masks, init completion, and ambient calibration value. Persistent device state is mostly register cache, firmware patch status, calibration data, and firmware naming fields. System suspend flushes DSP work, temporarily disables shared IRQ, force-suspends runtime PM, asserts reset late, and disables supplies; resume re-enables supplies/reset early, force-resumes, re-enables IRQ, checks whether firmware reload is needed, and queues DSP reload if required.

Dependencies and integration points: integrates ASoC controls/DAPM/DAI, SoundWire stream APIs, runtime PM, ACPI/fwnode/GPIO/regulator, debugfs, `wm_adsp`, `cs_dsp`, and shared CS35L56 helpers. Main risks are race-prone DSP work vs suspend/remove, SoundWire interrupt masking around reset/re-enumeration, firmware filename compatibility, BCLK/slot validation, calibration access while DSP power state changes, and ACPI speaker-ID quirks. Test signals include KUnit coverage for naming/XU parsing, plus runtime evidence from component probe completion, firmware logs, regcache sync errors, DAPM playback PS0/PS3 polls, SoundWire stream failures, and calibration controls/debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56.h

Purpose: private header for the CS35L56 ASoC smart amplifier driver. It binds the main component implementation, bus wrappers, shared helper module, and KUnit tests by defining the private driver state, SoundWire interrupt constants, PCM capability macros, PM/exported function prototypes, and KUnit-visible helper prototypes.

Important APIs and data: `CS35L56_RX_FORMATS`, `CS35L56_TX_FORMATS`, and `CS35L56_RATES` describe the 48 kHz S16/S24 playback and S16/S24/S32 capture capabilities. `struct cs35l56_private` is the central per-device state object; `struct wm_adsp dsp` is intentionally first, followed by `struct cs35l56_base`, DSP workqueue/work item, component pointer, supplies, SoundWire peripheral and IRQ state, firmware fallback suffix, soft reset/attachment flags, init completion, speaker ID, ASP/SoundWire masks and slot state, SoundWire link/unique IDs, and calibration ambient control value. `cs35l56_private_from_base` recovers the enclosing private object from shared-base pointers.

Control flow and integration: bus drivers allocate `struct cs35l56_private`, fill `base.dev`, `base.regmap`, bus-specific flags, then call `cs35l56_common_probe`, `cs35l56_init`, and `cs35l56_irq_request`; remove calls `cs35l56_remove`. System PM stages are declared for bus wrappers and exported from the core. Under `CONFIG_KUNIT`, firmware naming and XU parsing helpers are declared for direct unit tests.

State and persistence behavior: the header makes ownership boundaries clear. The shared `cs35l56_base` owns hardware/regmap/firmware/calibration state, while this ASoC-private wrapper owns ALSA/DSP/workqueue/SoundWire stream state and transient formatting choices. The init completion is critical for component probe and SoundWire re-enumeration synchronization.

Dependencies and risks: depends on Linux completion, container macros, regulator, runtime PM, workqueue, public `sound/cs35l56.h`, and `wm_adsp.h`. Risks are layout-sensitive: `dsp` must stay first for wm_adsp assumptions, and `cs35l56_private_from_base` depends on the embedded `base` member. Field additions must preserve initialization/removal paths and KUnit-visible prototypes. Test signals come indirectly from compilation, bus wrapper linkage, KUnit helper access, and successful ASoC/SoundWire lifecycle coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs40l50-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs40l50-codec.c

Purpose: ASoC codec sidecar for the CS40L50 MFD haptic device, exposing an I2S/ASP playback interface that can drive haptic/audio playback through the parent device regmap and DSP command interface. It is a platform child driver named `cs40l50-codec`.

Important APIs and data: local state is `struct cs40l50_codec` containing device, parent regmap, cached DAI format bits, BCLK ratio, and sample rate. `cs40l50_pll_cfg` maps supported reference frequencies to PLL config IDs. Key functions are `cs40l50_get_clk_config`, `cs40l50_swap_ext_clk`, DAPM event `cs40l50_clk_en`, DAI ops `cs40l50_set_dai_fmt`, `cs40l50_hw_params`, `cs40l50_set_dai_bclk_ratio`, component probe, and platform probe. DAPM provides `ASP PLL`, `ASPRX1/2`, and `OUT`; the single DAI `cs40l50-pcm` supports 48 kHz, 1-2 channels, S16/S24 playback.

Control flow: platform probe gets the parent `struct cs40l50` driver data, allocates codec state, points to the parent regmap, and registers the ASoC component/DAI. Component probe initializes a default BCLK ratio of 32. DAI format validation accepts only codec bit/frame consumer mode and I2S with supported clock inversion combinations, caching the register bits. `hw_params` records rate, writes ASP RX word length, folds sample width into cached ASP format, and writes ASP control. The DAPM supply event stops any DSP playback, starts I2S mode, switches the PLL reference from MCLK to BCLK on power-up, and restores MCLK before power-down.

State and persistence: all codec state is volatile runtime configuration cached in `struct cs40l50_codec`; hardware state is register-map-backed through the parent MFD. The PLL reference source changes with DAPM stream power, so playback depends on `rate` and `bclk_ratio` already being valid before `ASP PLL` powers up. No runtime PM is implemented locally.

Dependencies and integration points: depends on `linux/mfd/cs40l50.h`, parent MFD regmap, `cs40l50_dsp_write`, ASoC DAPM/DAI, and PCM params. Risks include unsupported BCLK-rate combinations causing PLL switch failure, `codec->daifmt` accumulating width bits across repeated `hw_params` calls without clearing, and DAPM event ordering if rate/ratio are not set before the PLL switch. Test signals are binding of the platform child, successful DAPM transitions, DSP command return codes, PLL register writes, and 48 kHz I2S playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs40l50-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4234.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4234.c

Purpose: I2C ASoC codec driver for the Cirrus CS4234 multi-channel audio codec. It exposes five DAC playback paths, four ADC capture paths, controls for volume/mute/noise gate/delay/filter/inversion, DAI format and TDM-slot programming, MCLK-derived sample-rate constraints, reset/supply/MCLK sequencing, VQ ramp handling, and runtime PM.

Important APIs and data: private state `struct cs4234` stores device/regmap/reset GPIO, VA/VL supplies, VQ ramp completion/delayed work, MCLK handle/rate, current LRCLK/format, and ALSA ratnum constraints. Key functions include `cs4234_dac14_grp_delay_put`, `cs4234_set_bias_level`, `cs4234_dai_set_fmt`, `cs4234_dai_hw_params`, `cs4234_dai_rule_rate`, `cs4234_dai_startup`, `cs4234_dai_set_tdm_slot`, register access predicates, `cs4234_powerup`, `cs4234_shutdown`, I2C probe/remove, and runtime suspend/resume.

Control flow: probe allocates state, requests reset GPIO, VA/VL regulators, and MCLK, validates MCLK range, initializes regmap, powers the chip, reads and validates the three-byte device ID, logs revision, configures VA voltage selection based on regulator voltage, enables runtime PM, initializes rate divider constraints, and registers the component/DAI. Power-up enables MCLK and supplies, releases reset after required delay, waits for boot, then queues delayed VQ ramp completion. Shutdown cancels VQ work, sets VQ ramp, waits, enters cache-only, clears cached VQ bit for next boot, asserts reset, disables supplies, and disables MCLK.

DAI behavior: `set_fmt` accepts left-justified, I2S, or DSP_A/TDM, codec consumer or provider mode with DSP_A forbidden in master mode, and only normal or inverted bit clock. `hw_params` derives MCLK/LRCLK ratio, handles double-speed rates, writes base-rate advisory and sample-width fields, and rejects unsupported sample widths. Startup constrains rates from MCLK and further restricts playback in I2S/left-justified modes to 24-bit formats and 1-4 channels. TDM slot programming requires 32-bit slots and 4 or 5 consecutive TX slots aligned to groups of four; optional DAC5 slot selection updates SDIN masks.

State and persistence: register defaults are cached with REGCACHE_MAPLE; interrupt notify registers are volatile and ID/notify registers are non-writable. Runtime resume powers up, marks cache dirty, exits cache-only, and syncs. Bias prepare waits for VQ ramp completion after standby. DAPM powers ADC/DAC widgets via powerdown bits. Risks include deadlocks or long waits around VQ ramp completion, invalid MCLK-derived constraints, failure to unwind power on probe errors, unsupported TDM allocations, and group-delay changes while ADC/DAC are active. There are no local KUnit tests; test signals are device ID/revision logs, regcache sync success, runtime PM cycles, ALSA constraint behavior, and playback/capture with supported MCLK ratios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4234.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4234.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4234.h

Purpose: register and bitfield definition header for the CS4234 codec driver. It gives `cs4234.c` symbolic names for device ID/revision registers, serial-port and sample-width controls, ADC/DAC controls, volume registers, interrupt mask/notify registers, power timing constants, PCM capabilities, and small enums for supplies, VA voltage selection, serial-port format, and base-rate advisory.

Important APIs and data: defines register addresses from `CS4234_DEVID_AB` through `CS4234_INT_NOTIFY2`, `CS4234_MAX_REGISTER`, supported device ID `0x423400`, reset/boot/VQ timing constants, rate mask for 32/44.1/48/64/88.2/96 kHz, and PCM format mask for 16/18_3/20/24/24_3-bit samples. Bitfields cover MCLK/base-rate/speed mode, serial format, DAC/ADC powerdown/mute/inversion, low-latency controls, DAC5 controls, ramp delays, volume, and interrupt status/masks.

Control flow and integration: the `.c` file consumes these macros for regmap defaults, control definitions, DAPM power bits, DAI format programming, hw_params sample-width/rate selection, TDM slot masks, VA regulator voltage configuration, readable/writeable/volatile register callbacks, and runtime PM power sequencing. The enums provide stable indexes into supply arrays and register value choices.

State and persistence behavior: the header itself has no state, but it defines the hardware state surface that is cached in regmap. Correct masks and shifts are required to avoid corrupting adjacent hardware fields, especially shared registers like `CLOCK_SP`, `SAMPLE_WIDTH`, `SP_CTRL`, `DAC_CTRL*`, and interrupt notify/mask registers.

Dependencies, risks, and tests: depends on ALSA PCM bit macros being visible through the including `.c` file. Risks are off-by-one or duplicate bit masks causing incorrect controls; one notable review target is that some interrupt bit masks overlap in the definitions, matching the driver’s current source but worth hardware-doc verification. Test signals are compile-time use, successful chip ID validation, ALSA control operation, and register-level behavior in playback/capture/runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4234.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4265.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4265.c

Purpose: I2C ASoC driver for the CS4265 stereo audio codec with DAC/ADC, S/PDIF output, loopback, two DAI instances, mixer controls, DAPM routing, reset GPIO support, and MCLK/sample-rate programming.

Important APIs and data: private state `struct cs4265_private` stores regmap, reset GPIO, selected DAI format, and sysclk. Register defaults and access callbacks define the regcache surface. Controls include PGA/DAC volume, de-emphasis, inversion, soft ramp/zero-cross, ADC HPF, S/PDIF controls, C data buffer, and DAPM mux/switch controls. `clk_map_table` maps MCLK and sample rate pairs to functional mode and MCLK divisor. DAI ops are `cs4265_set_sysclk`, `cs4265_set_fmt`, `cs4265_pcm_hw_params`, and `cs4265_mute`.

Control flow: probe allocates state, creates the I2C regmap, optionally toggles reset GPIO, reads and validates `CS4265_CHIP_ID`, logs revision, writes powerdown reset state, and registers two DAIs. `set_sysclk` accepts only clock ID 0 and validates that the supplied MCLK appears in the map. `set_fmt` supports codec provider or consumer clocking, and I2S/right-justified/left-justified formats. `hw_params` rejects right-justified capture, looks up the exact MCLK/rate pair, writes ADC functional mode and MCLK divisor, then writes DAC/ADC/S/PDIF interface format bits. `mute_stream` toggles DAC and S/PDIF mute bits for playback only. Bias transitions power down/up through `CS4265_PWRCTL_PDN`.

State and persistence: regmap uses REGCACHE_MAPLE with the interrupt-status register volatile. `sysclk` and `format` must be set before `hw_params`; invalid or missing sysclk causes runtime `-EINVAL`. Reset GPIO is asserted on remove. The driver does not manage regulators or runtime PM, so board power must be available externally.

Dependencies and integration points: depends on Linux I2C, regmap, optional GPIO reset, ASoC controls/DAPM, and `cs4265.h` macros. Risks include unsupported MCLK/rate combinations, stale `format` if machine driver omits `set_fmt`, no explicit supply management, and two DAIs sharing one format/sysclk state. There are no local unit tests; test signals are chip ID probe, DAI negotiation at all mapped rates, S/PDIF/DAC mute behavior, and DAPM loopback/ADC/DAC routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4265.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4265.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4265.h

Purpose: private register definition header for the CS4265 codec driver. It supplies register addresses and masks used by `cs4265.c` for chip identification, power control, DAC/ADC format programming, MCLK divisor selection, signal routing, volume/PGA controls, interrupt status/mask registers, S/PDIF controls, C data buffer, and max register.

Important APIs and data: key definitions include `CS4265_CHIP_ID`, `CS4265_CHIP_ID_VAL`, `CS4265_PWRCTL_PDN`, DAC/ADC DIF masks, `CS4265_ADC_MASTER`, `CS4265_ADC_FM`, MCLK frequency mask, S/PDIF mute/DIF masks, and `CS4265_MAX_REGISTER`. These constants are used directly in regmap defaults, DAPM widgets, ALSA controls, DAI format programming, and chip-ID validation.

Control flow and state: this header has no executable flow or runtime state. Its masks define how the `.c` driver mutates hardware state during probe, bias changes, mute, format selection, and hw_params. Since several registers pack multiple fields, the correctness of each mask is required to keep update_bits operations bounded.

Dependencies and risks: the header is only intended for the CS4265 implementation and does not include external headers. Risks are silent hardware misconfiguration from incorrect masks/shifts, especially where `cs4265.c` writes literal shifted values into fields defined here. Test signals are compile coverage, successful device ID validation, and behavior of ALSA controls/DAI formats against hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4265.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4270.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4270.c

Purpose: I2C ASoC codec driver for the CS4270 stereo ADC/DAC. It supports software control mode over I2C, master/slave operation, I2S and left-justified data formats, power management, regulators, reset GPIO, volume/mute/de-emphasis/loopback controls, and continuous-rate DAI operation constrained by MCLK/LRCLK ratios.

Important APIs and data: private state `struct cs4270_private` stores regmap, MCLK, data mode, slave/master flag, manual mute mask, three regulators (`va`, `vd`, `vlc`), and reset GPIO. Ratio table `cs4270_mode_ratios` maps MCLK/LRCLK ratios to mode/divider bits, with an optional Kconfig erratum excluding divide-by-1.5. Main functions include `cs4270_set_dai_sysclk`, `cs4270_set_dai_fmt`, `cs4270_hw_params`, `cs4270_dai_mute`, `cs4270_soc_put_mute`, component probe/remove/suspend/resume, and I2C probe/remove.

Control flow: I2C probe obtains regulators, optional reset GPIO, releases reset, waits briefly, initializes regmap, validates chip ID high nibble `0xC0`, stores client data, and registers the component. Component probe disables auto-mute and automatic volume control defaults, then enables regulators. DAI sysclk stores MCLK; format selection accepts I2S/left-justified and codec consumer/provider clocking. `hw_params` computes `mclk / sample_rate`, finds a supported ratio, programs speed/divider or slave mode, and writes DAC/ADC format bits. Mute ops preserve manual user mute state across stream mute/unmute. Suspend powers down ADC/DAC/core and disables regulators; resume re-enables regulators, syncs regcache, and clears powerdown bits.

State and persistence: regcache defaults cover writable registers except volatile chip ID. Manual playback mute is stored separately so stream unmute does not override user mute. MCLK must be set by the machine driver before hw_params. Regulator state is tied to component probe/remove and PM callbacks, while reset GPIO is asserted on I2C remove.

Dependencies and integration points: depends on I2C, regmap, regulators, optional GPIO reset, ASoC DAI/control/DAPM APIs, and optional PM. Risks include component probe enabling regulators after I2C probe has already talked to the chip, machine drivers omitting sysclk, unsupported ratios at runtime despite continuous advertised rates, and manual mute/state synchronization. Test signals are chip ID/revision probe logs, successful ratio programming for board MCLK, suspend/resume regcache sync, and ALSA mute/volume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4270.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271-i2c.c

Purpose: I2C transport wrapper for the shared CS4271 ASoC codec core. It configures the generic CS4271 regmap for 8-bit I2C register addresses, creates an I2C regmap, and delegates all codec probing to `cs4271_probe`.

Important APIs and data: `cs4271_i2c_probe` copies `cs4271_regmap_config`, sets `reg_bits = 8`, and passes `devm_regmap_init_i2c` to the common probe. The file defines I2C device ID `cs4271`, an `i2c_driver` named `cs4271`, and uses `cs4271_dt_ids` for OF matching.

Control flow and state: the wrapper owns no codec state beyond transport registration. The common core allocates private state, regulators, clock, reset GPIO, and ASoC component. Errors from regmap creation or common probe propagate directly. Removal is devm-managed through the registered component and resources.

Dependencies, risks, and tests: depends on Linux I2C/regmap, ASoC headers, and `cs4271.h` shared declarations. The main risk is regmap transport configuration mismatch; the I2C path must keep address width and cache settings aligned with the core register layout. Test signals are OF/I2C modalias binding, regmap I2C I/O, and successful common CS4271 component probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271-spi.c

Purpose: SPI transport wrapper for the shared CS4271 ASoC codec core. It adapts the generic CS4271 regmap configuration to the device’s SPI command format and delegates probing to the common codec implementation.

Important APIs and data: `cs4271_spi_probe` copies `cs4271_regmap_config`, sets `reg_bits = 16`, `read_flag_mask = 0x21`, and `write_flag_mask = 0x20`, then calls `cs4271_probe` with `devm_regmap_init_spi`. The `spi_driver` is named `cs4271` and uses `cs4271_dt_ids` for OF matching.

Control flow and state: the wrapper does no state management beyond constructing the SPI regmap and invoking the common probe. The core handles reset GPIO, regulators, MCLK, regcache, DAI controls, suspend/resume, and component registration. Probe errors return directly to SPI core.

Dependencies, risks, and tests: depends on Linux SPI/regmap and `cs4271.h`. The critical integration point is the SPI register protocol: wrong register width or flag masks would make all core register accesses fail or target wrong addresses. There is no local test suite; test signals are SPI bus transactions during common probe, OF modalias binding, and normal CS4271 playback/capture behavior through the common core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271.c

Purpose: shared ASoC codec core for CS4271 devices on either I2C or SPI. It implements register definitions/defaults, DAI format and MCLK/sample-rate programming, de-emphasis, mute/volume controls, DAPM endpoints, regulator/clock/reset sequencing, optional soft reset workaround, suspend/resume, and a common probe entry consumed by transport wrappers.

Important APIs and data: exported interfaces are `cs4271_dt_ids`, `cs4271_regmap_config`, and `cs4271_probe`. Private state `struct cs4271_private` stores MCLK, master mode, deemphasis flag/current rate, regmap, reset GPIO, optional soft-reset flag, regulators (`vd`, `vl`, `va`), and optional MCLK. `cs4271_clk_tab` maps master/slave, speed mode, MCLK/Fs ratio, and divider mask. Key functions include `cs4271_set_dai_sysclk`, `cs4271_set_dai_fmt`, `cs4271_set_deemph`, `cs4271_hw_params`, `cs4271_mute_stream`, `cs4271_reset`, component probe/remove, PM callbacks, common probe, and exported probe.

Control flow: common probe allocates state, gets optional reset and MCLK, requests regulators, and returns state to `cs4271_probe`, which stores the transport regmap and registers the component/DAI. Component probe reads OF/platform properties, enables regulators and clock, hardware-resets the codec, syncs regcache, powers up with CPEN and PDN sequencing, waits 85 us, and optionally ties AMUTEC/BMUTEC. DAI format writes master/slave and I2S/left-justified DAC/ADC bits. `hw_params` optionally toggles soft reset when only one stream is active, derives speed mode from sample rate, computes MCLK/Fs ratio, finds a legal table entry for master/slave, writes mode/divider bits, and updates de-emphasis. Suspend powers down, marks cache dirty, disables clock/regulators; resume reverses that sequence, resets, syncs cache, and clears powerdown.

State and persistence: regcache is REGCACHE_FLAT with chip ID volatile. Runtime state includes selected MCLK, master/slave mode, current rate, de-emphasis switch, and optional soft reset workaround. Hardware state is restored from regcache after suspend/resume and after component probe reset. The DAI advertises fixed stereo playback/capture with 8-192 kHz and S16/S24/S32 formats.

Dependencies and integration points: depends on ASoC, regmap, GPIO, regulators, optional clock, OF/platform data (`sound/cs4271.h`), and transport wrappers. Risks include missing MCLK causing invalid ratio math, unsupported ratio combinations, soft reset workaround disrupting simultaneous streams if active-state checks regress, and transport regmap config mismatches. There is no local KUnit coverage; test signals are common probe success on I2C/SPI, regulator/clock sequencing, valid ratio programming, de-emphasis control changes, suspend/resume cache restoration, and stereo playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271.h

Purpose: private bridge header for CS4271 transport wrappers and the common codec core. It declares the OF match table, shared regmap configuration, and `cs4271_probe` common entry point used by I2C and SPI bus drivers.

Important APIs and data: `extern const struct of_device_id cs4271_dt_ids[]` allows wrappers to share compatible matching. `extern const struct regmap_config cs4271_regmap_config` provides the transport-neutral cache/default/register policy. `int cs4271_probe(struct device *dev, struct regmap *regmap)` lets wrappers pass an initialized bus regmap into the shared core.

Control flow and state: this header has no runtime logic. Its declarations define the call boundary: bus wrappers are responsible for transport regmap creation; `cs4271.c` owns allocation of private codec state and ASoC component registration.

Dependencies, risks, and tests: depends on Linux regmap declarations and, through the exported OF symbol, device-tree matching types. Risks are linkage/API drift between wrappers and core; any change to common probe signature or regmap config visibility must update both wrappers. Test signals are successful module builds for I2C and SPI variants and runtime binding through `cs4271_dt_ids`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs4271.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42-i2c.c

Purpose: I2C bus wrapper for the CS42L42 ASoC codec core. It allocates the common private object, creates the I2C regmap, seeds device identity/IRQ fields, delegates common probe/init/remove, and provides I2C-specific system resume behavior that restores registers after the shared resume path.

Important APIs and data: `cs42l42_i2c_probe`, `cs42l42_i2c_remove`, and `cs42l42_i2c_resume` are local entry points. The driver uses shared objects/functions from `cs42l42.h`: `cs42l42_regmap`, `cs42l42_common_probe`, `cs42l42_init`, `cs42l42_common_remove`, `cs42l42_resume`, `cs42l42_resume_restore`, `cs42l42_soc_component`, and `cs42l42_dai`. Match tables include OF compatible `cirrus,cs42l42`, ACPI ID `10134242`, and I2C ID `cs42l42`.

Control flow: probe allocates `struct cs42l42_private`, initializes an I2C regmap, fills `devid`, `dev`, `regmap`, and `irq`, runs common probe with the component/DAI descriptors, then calls common init. Remove fetches drvdata and delegates cleanup. System resume first calls shared `cs42l42_resume`; if successful, it calls `cs42l42_resume_restore` to restore I2C register state.

State and persistence: this wrapper stores no bus-private state beyond the common object fields. Register cache, jack/interrupt/component state, and PM state live in the shared CS42L42 core. I2C system PM uses `SYSTEM_SLEEP_PM_OPS`, not runtime PM in this file.

Dependencies and integration points: depends on Linux I2C/regmap/module infrastructure and the `SND_SOC_CS42L42_CORE` namespace. Risks are thin-wrapper risks: common probe must set drvdata before remove, IRQ number must be valid for common interrupt setup, and resume ordering must match the core’s expectations. There are no local tests here; test signals are OF/ACPI/I2C binding, successful common init, interrupt handling through the passed IRQ, and suspend/resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l42-i2c.c -->
