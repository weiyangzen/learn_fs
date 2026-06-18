<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x.c

## Purpose
Platform-level ASoC codec driver for Qualcomm WCD9390/WCD9395 audio codecs. It binds separate SoundWire RX/TX slave components into one codec component, exposes playback and capture DAIs, builds the analog and digital DAPM graph, configures microphone bias and MBHC headset detection, handles Type-C analog accessory integration, and wires codec interrupts through a regmap IRQ domain.

## Important APIs, Types, and Functions
The main private state is `struct wcd939x_priv`, which holds SoundWire child devices, regmap, component pointer, MBHC and class-H state, Type-C state, micbias reference counters, codec variant, reset GPIO, watchdog IRQs, compander flags, and LDOH state. Entry points are the platform `wcd939x_probe()` and `wcd939x_remove()`, component master callbacks `wcd939x_bind()` and `wcd939x_unbind()`, ASoC component callbacks in `soc_codec_dev_wcd939x`, and DAI ops `wcd939x_codec_hw_params()`, `wcd939x_codec_free()`, and `wcd939x_codec_set_sdw_stream()`.

Important internal routines include `wcd939x_io_init()`, `wcd939x_irq_init()`, `wcd939x_soc_codec_probe()`, `wcd939x_mbhc_init()`, `wcd939x_micbias_control()`, `wcd939x_mbhc_micb_adjust_voltage()`, `wcd939x_wcd_mbhc_calc_impedance()`, RX power event callbacks for HPHL/HPHR/EAR DACs and PAs, TX event callbacks for ADC/DMIC/SoundWire clock control, ALSA control get/put functions for TX mode, RX headphone mode, compander, LDOH, and SoundWire port enablement, plus optional Type-C callbacks `wcd939x_typec_mux_set()`, `wcd939x_typec_switch_set()`, and `wcd939x_swap_gnd_mic()`.

## Control Flow
`wcd939x_probe()` allocates state, parses reset/regulator/micbias/MBHC/Type-C data, registers Type-C mux and switch devices when a graph endpoint indicates analog USB-C routing, collects RX/TX SoundWire component matches from `qcom,rx-device` and `qcom,tx-device`, toggles reset, registers a component master, and enables runtime PM. `wcd939x_bind()` binds the RX/TX child drivers, resolves their SoundWire devices, links device PM order so TX stays available for CSR access, takes the TX regmap as the shared codec regmap, creates a one-entry virtual IRQ domain feeding regmap IRQs, assigns the nested IRQ to both SoundWire slaves, applies micbias register defaults, reads chip version, and registers the ASoC component and two DAIs.

Component probe waits up to two seconds for TX SoundWire initialization, initializes the component regmap, resumes runtime PM, reads the WCD9390/WCD9395 variant, allocates class-H control, applies analog/digital hardware initialization, makes interrupts edge-triggered, requests and initially disables PDM watchdog IRQs, adds variant-specific ALSA controls, and initializes MBHC. DAPM event callbacks then perform detailed sequencing for RX clocks, headphone and ear PA enable/disable, compander timing, watchdog IRQ masking, class-H state changes, ADC and DMIC clocks, SoundWire TX clock rate selection, and micbias power. DAI calls are thin wrappers into the companion SoundWire transport implementation.

## State and Persistence
Persistent state is held in `struct wcd939x_priv`, the two `struct wcd939x_sdw_priv` child structures, the regmap cache behind the TX SoundWire device, MBHC state allocated by `wcd_mbhc_init()`, and class-H state allocated by `wcd_clsh_ctrl_alloc()`. `micb_ref[]` and `pullup_ref[]` reference-count each micbias rail so DAPM and MBHC requests can coexist. `status_mask` tracks active ADC paths and pending headphone PA delay sequencing. `tx_mode[]`, `hph_mode`, `comp1_enable`, `comp2_enable`, and `ldoh` persist user control selections. Runtime PM and device links preserve ordering between the master device and RX/TX SoundWire children. Remove/unbind paths unregister the component, free watchdog IRQs, deinitialize MBHC/class-H, remove device links, release child device references, and remove the component master.

## Dependencies and Integration Points
The file depends on ALSA SoC component, DAI, DAPM, and control APIs; SoundWire slave and stream support; regmap and regmap IRQ; Linux component framework; runtime PM; GPIO and regulators; OF graph/phandle parsing; USB Type-C mux/switch APIs when enabled; and shared Qualcomm WCD helpers in `wcd-common`, `wcd-mbhc-v2`, and `wcd-clsh-v2`. It integrates with `wcd939x-sdw.c` through `wcd939x_sdw_hw_params()`, `wcd939x_sdw_free()`, `wcd939x_sdw_set_sdw_stream()`, channel metadata, `slave_irq`, and SoundWire port configuration. Machine/device-tree integration requires reset GPIO, five supplies, micbias data, MBHC properties, and RX/TX SoundWire phandles.

## Risks
Risk areas include complex analog sequencing with many unchecked register writes, strict timing delays for precharge, compander, PA, micbias, and impedance detection, fragile SoundWire child binding and PM dependency ordering, dependence on TX SoundWire availability for all CSR access, DAPM control paths that can mutate shared port masks and micbias counters, and manual watchdog IRQ enable/disable around PA events. `wcd939x_wcd_mbhc_calc_impedance()` temporarily disables MBHC FSM, surge protection, pull-downs, and jack-detect bits and must restore all saved registers even across unusual measurement results. Type-C callback ordering is sensitive because mux callbacks can arrive before MBHC exists and because orientation switching is used to request ground/mic swaps through USBSS. Some hardware failures may be hidden because many `snd_soc_component_write_field()` calls ignore return status.

## Test Signals
Useful signals are successful probe with both RX and TX SoundWire slaves, component bind/unbind without device-reference or PM-link leaks, regmap IRQ delivery for MBHC and watchdog interrupts, playback and capture stream setup across supported rates and sample formats, DAPM route activation for HPHL/HPHR/EAR, ADC1-4, DMIC1-8, micbias rails, and SoundWire port switches, ALSA control mutation of TX modes, headphone modes, companders, LDOH, and port enables, headset insertion/removal/button/moisture/impedance reporting through MBHC, Type-C audio plug/unplug and orientation swap behavior, suspend/runtime-PM resume with TX CSR access intact, and hardware audio validation for PA pop/noise timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x.h

## Purpose
Private WCD939X codec interface and register map. It provides the register addresses, bit masks, SoundWire port/channel identifiers, shared SoundWire child state, and transport helper prototypes used by the WCD939X platform codec and SoundWire slave driver.

## Important APIs, Types, and Functions
The header defines the WCD939X analog, digital, RX top, compander, and DSD register address space from `WCD939X_BASE` through `WCD939X_MAX_REGISTER`, with bitfield masks for bias, RX supplies, headphone/ear PA controls, TX ADC controls, micbias, MBHC mechanical/electrical/impedance/moisture blocks, class-H/flyback, interrupt status/mask/clear/level registers, DMIC, SoundWire clocking, PDM watchdogs, efuse, and RX path controls. It declares SoundWire TX port/channel enums, RX port/channel enums, `WCD939X_MAX_SWR_CH_IDS`, and `struct wcd939x_sdw_priv`.

`struct wcd939x_sdw_priv` is the key shared transport type: it stores the `sdw_slave`, stream config/runtime, per-port config array, channel metadata pointer, port enable flags, active port count, TX/RX role flag, back pointer to `struct wcd939x_priv`, nested IRQ domain, and regmap. When `CONFIG_SND_SOC_WCD939X_SDW` is enabled the header declares `wcd939x_sdw_free()`, `wcd939x_sdw_set_sdw_stream()`, and `wcd939x_sdw_hw_params()`; otherwise inline stubs return `-EOPNOTSUPP`.

## Control Flow
The header itself has no runtime control flow. It shapes compile-time flow by giving `wcd939x.c` concrete register and bitfield names for component controls and DAPM event sequencing, while allowing the SoundWire child driver to export stream setup/free helpers and the shared child state consumed by the master codec driver.

## State and Persistence
No state is allocated by the header, but the `struct wcd939x_sdw_priv` layout defines the persistent per-SoundWire-child state used for stream lifetime, port masks, regmap access, and nested IRQ routing. Register macros also encode persistent hardware state touched by the driver, including micbias levels, MBHC thresholds, efuse calibration, interrupt configuration, and RX/TX path settings.

## Dependencies and Integration Points
The file includes Linux SoundWire headers and relies on kernel bit macros such as `BIT()` and `GENMASK()`. It is included by the WCD939X master codec driver and SoundWire slave implementation. The fallback stubs let the codec build fail functionally rather than link-fail when the SoundWire helper implementation is disabled.

## Risks
Risks are mostly register-contract risks: incorrect addresses or masks can silently program the wrong analog block, duplicate or drifted bit definitions can mislead future edits, and the fixed array sizes must remain consistent with the SoundWire channel metadata in the companion implementation. Because the header exposes a large hardware surface, changes need cross-checking against datasheets and the event code that assumes specific masks.

## Test Signals
Build coverage with and without `CONFIG_SND_SOC_WCD939X_SDW` validates the prototype/stub contract. Runtime signals are successful SoundWire child probe, correct port mask programming for all RX/TX channels, valid nested IRQ propagation through `slave_irq`, and expected register writes for micbias, MBHC, PDM watchdog, DMIC, ADC, headphone, ear, compander, and Type-C related paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm0010.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm0010.c

## Purpose
ASoC SPI driver for the Wolfson WM0010 DSP. It exposes two bidirectional serial audio DAIs and manages DSP power, reset, interrupt-driven boot sequencing, PLL setup, stage-2 loader download, and application firmware download from `wm0010_stage2.bin` and `wm0010.dfw`.

## Important APIs, Types, and Functions
Important file-local types are the `.dfw` record layouts `struct dfw_binrec`, `struct dfw_inforec`, and `struct dfw_pllrec`, `enum dfw_cmd`, `enum wm0010_state`, `struct wm0010_priv`, and `struct wm0010_boot_xfer`. The driver entry points are `wm0010_spi_probe()`, `wm0010_spi_remove()`, `wm0010_probe()`, `wm0010_set_bias_level()`, `wm0010_set_sysclk()`, and threaded IRQ handler `wm0010_irq()`.

Boot helpers include `wm0010_halt()`, `wm0010_mark_boot_failure()`, `wm0010_boot_xfer_complete()`, `byte_swap_64()`, `wm0010_stage2_load()`, `wm0010_firmware_load()`, and `wm0010_boot()`. `pll_clock_map[]` chooses PLL SPI speed and `CLKCTRL1` values from the configured system clock. The component driver registers DAPM routes through a `CLKIN` supply, and `wm0010_dai[]` exposes `wm0010-sdi1` and `wm0010-sdi2` playback/capture paths.

## Control Flow
SPI probe allocates state, copies optional platform data, gets AVDD/DCVDD/DBVDD regulators, gets an active-high reset GPIO initially asserted, requests the SPI IRQ as a wake-capable threaded interrupt, records board maximum SPI speed, and registers the ASoC component and DAIs. Machine drivers call `set_sysclk`, which stores the DSP clock and derives whether the PLL can be used and the maximum SPI transfer frequency after PLL lock.

The DSP is booted from the ASoC bias transition into `SND_SOC_BIAS_ON` when the previous level was `PREPARE`. `wm0010_boot()` validates the maximum 26 MHz system clock, enables regulators, releases reset, waits for boot ROM IRQ completion, downloads the stage-2 loader synchronously, waits for loader IRQ completion, optionally sends a PLL record twice and scans for the PLL-active response, and then calls `wm0010_firmware_load()` for the application `.dfw`. The application loader validates the INFO record version and DSP target, creates DMA-safe SPI messages for each record, byte-swaps 64-bit chunks, submits asynchronous transfers, and uses the last transfer completion to finish. Bias transition back to standby from prepare halts the DSP by asserting reset and disabling supplies.

## State and Persistence
`struct wm0010_priv` persists component/device pointers, mutex and IRQ spinlock, copied platform data, reset GPIO, regulators, system clock, boot state, boot failure flag, ready/PLL flags, computed SPI speeds, IRQ number, and boot completion. State transitions move through `POWER_OFF`, `OUT_OF_RESET`, `BOOTROM`, `STAGE2`, and `FIRMWARE`; the IRQ handler completes boot waits only in the intermediate states. Firmware contents are not persisted beyond download, but boot failures are remembered during a boot attempt and abort remaining transfers.

## Dependencies and Integration Points
The driver depends on SPI, firmware loading, GPIO descriptors, regulators, IRQ/wakeup APIs, completions, work-safe mutex/spinlock protection, and ASoC component/DAI/DAPM APIs. It consumes optional `struct wm0010_pdata` from `sound/wm0010.h`, firmware files declared by `MODULE_FIRMWARE`, and machine-driver sysclk configuration. It is a DSP-style codec with no regmap; all device communication during boot is raw SPI transfer traffic.

## Risks
Risk areas include firmware parser trust in 24-bit record lengths and offsets, asynchronous transfer lifetime and DMA buffer allocation, byte order assumptions in `byte_swap_64()`, boot completion timeouts that log errors but allow subsequent boot steps to continue, cleanup paths after allocation or SPI submission failure, and broad state changes split between a mutex and spinlock. If `request_firmware()` succeeds but the first `WARN_ON(!list_empty(&xfer_list))` path ever triggers, it returns without releasing firmware. The boot code also relies on platform sysclk setup before bias ON and on IRQ signaling from the DSP boot ROM/loader.

## Test Signals
Useful validation includes successful SPI probe/remove, regulator and reset sequencing, IRQ wake setup, sysclk values across the PLL map including below-PLL mode, bias ON boot to `WM0010_FIRMWARE`, bias standby halt to `POWER_OFF`, stage-2 and `.dfw` firmware download success, detection of bad INFO version or DSP target, handling of boot ROM and stage-2 error words, correct SPI speed change after PLL activation, and playback/capture stream routing through both SDI DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm0010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm1250-ev1.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm1250-ev1.c

## Purpose
Minimal ASoC I2C driver for the Wolfson WM1250-EV1 audio I/O evaluation module. It verifies the board ID, optionally drives board-control GPIOs from platform data, exposes one playback/capture DAI, and selects the board clocking GPIO state from the PCM sample rate.

## Important APIs, Types, and Functions
`struct wm1250_priv` stores GPIO descriptors for clock enable, two clock select lines, oversampling-rate select, and master/slave control. Driver entry points are `wm1250_ev1_probe()` and `wm1250_ev1_pdata()`. ASoC callbacks are `wm1250_ev1_set_bias_level()` and DAI op `wm1250_ev1_hw_params()`. The component driver supplies DAPM ADC/DAC/input/output widgets and routes, and `wm1250_ev1_dai` exposes 1-2 channel 16-bit playback/capture at 8, 16, 32, and 64 kHz.

## Control Flow
I2C probe clears driver data, reads byte register 0 through SMBus, derives board ID from bits 7:2 and revision from bits 1:0, rejects non-ID-1 boards, logs the revision, initializes optional platform-data GPIO state, and registers the component and DAI. If platform data is absent, no private GPIO state is allocated. Bias standby enables the board clock via `clk-ena`, and bias off disables it. `hw_params()` maps the selected sample rate to `clk-sel0` and `clk-sel1` GPIO values.

## State and Persistence
The only persisted runtime state is the optional `struct wm1250_priv` stored as device driver data. GPIO values persist in hardware across callbacks: `clk_ena` reflects ASoC bias, and `clk_sel0`/`clk_sel1` reflect the most recent hardware parameters. The `osr` and `master` GPIOs are requested with initial low values but are not modified later in this driver.

## Dependencies and Integration Points
The file depends on I2C/SMBus, GPIO descriptors, platform data type `struct wm1250_ev1_pdata`, and ASoC component/DAI/DAPM APIs. It integrates with legacy I2C ID matching for `"wm1250-ev1"` and with board files that provide platform data plus GPIO mappings.

## Risks
The component callbacks assume private GPIO state exists, but `wm1250_ev1_pdata()` returns success without allocating state when platform data is absent. If the component is then used without platform data, bias and hw_params paths can dereference `NULL`. The rate table is intentionally narrow and rejects all other rates. `gpiod_set_value()` is used in `hw_params()` rather than the cansleep variant, so GPIO providers that sleep would be inappropriate there. The driver does not use the requested `osr` or `master` GPIOs after initialization.

## Test Signals
Test signals are successful SMBus ID/revision read, rejection of unknown board IDs, GPIO acquisition from platform data, component registration, DAPM route creation, bias standby/off clock enable toggling, hw_params GPIO selection at each supported rate, and `-EINVAL` for unsupported rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm1250-ev1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm2000.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm2000.c

## Purpose
ASoC I2C driver for the Wolfson WM2000 active noise cancellation device. It verifies chip identity, loads a calibrated ANC image from firmware, manages regulators and MCLK, exposes ANC controls and DAPM routing, and transitions the device among active, bypass, standby, and off modes.

## Important APIs, Types, and Functions
`enum wm2000_anc_mode` defines `ANC_ACTIVE`, `ANC_BYPASS`, `ANC_STANDBY`, and `ANC_OFF`. `struct wm2000_priv` stores I2C, regmap, MCLK, three supplies, current mode, ANC engine/speaker/user active flags, speech clarity flag, prebuilt ANC download image, and a mutex. Low-level helpers are `wm2000_write()`, `wm2000_reset()`, and `wm2000_poll_bit()`. Mode helpers include `wm2000_power_up()`, `wm2000_power_down()`, `wm2000_enter_bypass()`, `wm2000_exit_bypass()`, `wm2000_enter_standby()`, `wm2000_exit_standby()`, transition table `anc_transitions[]`, `wm2000_anc_transition()`, and `wm2000_anc_set_mode()`.

User-facing controls are `"ANC Volume"`, `"WM2000 ANC Switch"`, and `"WM2000 Switch"`, backed by `wm2000_anc_mode_get/put()` and `wm2000_speaker_get/put()`. DAPM uses input pins `LINN`/`LINP`, output pins `SPKN`/`SPKP`, and an `"ANC Engine"` PGA whose power event toggles the ANC engine flag. Probe and lifecycle callbacks include `wm2000_i2c_probe()`, component `wm2000_probe()` and `wm2000_remove()`, and PM callbacks `wm2000_suspend()` and `wm2000_resume()`.

## Control Flow
I2C probe allocates state, initializes regmap, obtains supplies, temporarily enables supplies to read ID/revision, validates ID `0x2000`, obtains MCLK, reads optional platform data for speech clarity and firmware filename, requests the ANC firmware, allocates a download buffer with the starting register address prepended, initializes default flags to engine enabled, ANC active, speaker enabled, resets the chip, registers the component, and disables supplies before returning. Component probe calls `wm2000_anc_set_mode()`, which normally transitions from off to active or standby based on the flags.

Mode selection is table-driven. `wm2000_anc_set_mode()` chooses active when both ANC engine and speaker are enabled and user ANC is active, bypass when engine and speaker are enabled but user ANC is off, and standby otherwise. `wm2000_anc_transition()` finds a source/destination entry, enables MCLK if leaving off, runs one or two step functions, and disables MCLK if entering off. Power up enables regulators, sets the MCLK divider based on clock rate, resets and starts the ANC engine, waits for idle and boot-complete status, downloads the ANC image with `i2c_master_send()`, configures analog sequencing and speech clarity, starts MOUSE/ANC processing, clears interrupt state, waits for active status, and records active mode. Other step functions use status polling to move between active, bypass, standby, and off while setting RAM and standby bits.

## State and Persistence
`wm2000_priv` persists control choices and current hardware mode. The preprocessed ANC download image remains allocated for the device lifetime. Hardware state includes regulator enablement, MCLK prepare state, RAM set/clear, ANC engine state, analog sequencing, speech clarity bit, ANC volume register, and system mode bits. The mutex serializes user controls, DAPM power events, and mode transitions. Suspend forces off, while resume re-applies the desired mode from persisted flags.

## Dependencies and Integration Points
The driver depends on I2C, regmap with 16-bit register addresses and 8-bit values, firmware loading, clocks, regulators, delays, PM, and ASoC controls/DAPM. It consumes `struct wm2000_platform_data` from `sound/wm2000.h` for optional firmware filename and speech-enhancement policy. It uses the local `wm2000.h` register definitions and declares no DAI because it sits in an analog path controlled by DAPM pins.

## Risks
Risk areas include long synchronous polling loops up to roughly four seconds per status bit, direct bulk I2C firmware download that must match the device's expected flat image format, state-table coverage for every transition, MCLK disable only when the destination is off, and incomplete rollback if a multi-step transition fails after leaving the previous mode. `wm2000_anc_transition()` iterates with `ARRAY_SIZE(anc_transitions[j].step)` instead of indexing the selected entry for the array size expression, which is type-equivalent here but fragile. Several probe error paths after supply enable return directly without disabling supplies, while other paths use `err_supplies`. The header spells `WM2000_REG_REVISON`, so spelling must remain consistent.

## Test Signals
Test signals include ID/revision read, firmware acquisition and download size preparation, MCLK divider selection below/above 13.5 MHz, transitions for all mode pairs in `anc_transitions[]`, DAPM ANC engine on/off events, ANC and speaker control toggles, ANC volume writes, suspend-to-off and resume-to-selected-mode behavior, timeout/error handling for boot, MOUSE active, ANC disabled, power down, and engine idle bits, and regulator/MCLK enable counts after failures and removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm2000.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm2000.h

## Purpose
Private register-definition header for the WM2000 ANC ASoC driver. It gives `wm2000.c` symbolic names for the system, ANC, analog sequencing, status, mode, and control registers plus the bit masks used during power and mode transitions.

## Important APIs, Types, and Functions
The file defines register addresses for the ANC download/start region, ANC gain, MSE thresholds, speech clarity, watchdog, analog VMID timing, CAT controls, system status/mode/start, ID/revision, system control registers, ANC status, interface control, analog mic control, and speaker control. Important masks include `WM2000_SPEECH_CLARITY`, system status bits such as `WM2000_STATUS_MOUSE_ACTIVE`, `WM2000_STATUS_ANC_DISABLED`, `WM2000_STATUS_POWER_DOWN_COMPLETE`, and `WM2000_STATUS_BOOT_COMPLETE`, mode bits such as `WM2000_MODE_ANA_SEQ_INCLUDE`, `WM2000_MODE_MOUSE_ENABLE`, `WM2000_MODE_BYPASS_ENTRY`, `WM2000_MODE_STANDBY_ENTRY`, and `WM2000_MODE_POWER_DOWN`, plus `WM2000_SYS_STBY`, SYS_CTL2 command bits, and `WM2000_ANC_ENG_IDLE`.

## Control Flow
The header has no executable flow. It supports the driver's table-driven mode flow by naming the exact bits written and polled in power-up, power-down, standby, bypass, speech clarity, RAM, MCLK divider, and ANC engine operations.

## State and Persistence
No state is allocated in this header. The constants identify persistent device registers that hold mode, status, RAM/engine control, gain, speech clarity, and analog sequencing settings across individual I2C transactions while power remains applied.

## Dependencies and Integration Points
It is included by `wm2000.c` and guarded by `_WM2000_H`. The register definitions pair with the `wm2000_regmap` readability table and the ANC transition helpers in the C file. External board policy is not declared here; platform data comes from `include/sound/wm2000.h`.

## Risks
Risks are address or bit-mask drift from the hardware specification and the misspelled `WM2000_REG_REVISON` symbol becoming part of the local contract. Because `wm2000.c` uses these constants in blocking status polls, an incorrect status mask can cause long timeouts or false success.

## Test Signals
Build coverage of `wm2000.c` validates all symbols. Runtime signals are successful ID/revision read, readable-reg filtering, correct status polling for boot/active/disabled/powerdown/idle, valid speech clarity toggling, ANC gain writes, and successful mode transitions driven by these masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm2000.h -->
