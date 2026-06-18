# subset-b-006504 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wsa883x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wsa883x.c

## Purpose
`wsa883x.c` is an ASoC codec driver for Qualcomm WSA883x SoundWire smart speaker amplifiers. It exposes one mono playback DAI named `SPKR`, initializes a large regmap-backed analog/digital register set, configures selectable SoundWire sink ports, controls the speaker power-amplifier path through DAPM and mute callbacks, and optionally registers a hwmon temperature sensor used by speaker-protection logic.

## Important APIs, Types, And Functions
The central state is `struct wsa883x_priv`, which keeps the SoundWire slave, regmap, regulator, reset or powerdown GPIO, stream config/runtime, port enable/prepared state, active port array, mode and compander offset controls, runtime-init state, and temperature/PA state protected by `sp_lock`. Key callbacks are `wsa883x_probe()`, `wsa883x_update_status()`, `wsa883x_port_prep()`, `wsa883x_hw_params()`, `wsa883x_hw_free()`, `wsa883x_set_sdw_stream()`, `wsa883x_digital_mute()`, `wsa883x_spkr_event()`, `wsa883x_get_temp()`, and runtime PM suspend/resume. `wsa883x_regmap_config`, `wsa883x_defaults`, and `reg_init` define the register cache and startup programming.

## Control Flow
Probe allocates state, enables `vdd`, obtains reset control or legacy `powerdown-gpios`, sets SoundWire properties and optional static port mapping, deasserts reset, creates a SoundWire regmap, registers hwmon when available, enables runtime PM, and registers the component/DAI. SoundWire attachment invokes `wsa883x_update_status()`, which runs `wsa883x_init()` once per attachment to read variant/version IDs, apply `reg_init`, and select a default compander offset. ALSA controls choose mode and enabled SoundWire ports. `hw_params()` compresses enabled ports into `port_config[]`, records the frame rate, and adds the SoundWire slave to the stream; `hw_free()` removes it. DAPM speaker events set PA-on state, tune receiver versus speaker path registers, enable VBAT filtering and PDM watchdog on power-up, and undo those settings on power-down. Mute toggles DRE gain and global PA enable.

## State And Persistence
Persistent state is devm-managed and mostly mirrored in regmap cache. `hw_init` is cleared on SoundWire unattached status and set after initialization. `port_enable[]`, `dev_mode`, and `comp_offset` are ALSA-control state that directly affect later stream and DAPM programming. Runtime PM switches the regmap into cache-only mode on suspend, marks it dirty, and syncs on resume. Temperature reads cache the last valid value and return it while the PA is on because direct temperature sampling is only safe when the amplifier is off.

## Dependencies And Integration Points
The driver depends on the SoundWire bus, regmap SoundWire backend, ASoC component/DAI/DAPM/control APIs, regulator framework, optional reset controller or `powerdown` GPIO, runtime PM, optional hwmon, and DT property `qcom,port-mapping`. It binds through SoundWire ID `0x0217:0x0202` and advertises simple clock-stop capability, sink ports, and SoundWire SCP interrupt masks.

## Risks And Edge Cases
The port mixer controls can leave no ports enabled, making `sdw_stream_add_slave()` operate with zero active ports. `port_prep()` indexes `prepare_ch->num - 1` without local bounds checks, relying on SoundWire core validity. Regmap writes in init and DAPM paths are mostly not checked, so hardware programming failures can be silent. Temperature conversion ignores intermediate read/update failures and filters only by plausible range; stale cached values are expected while PA is active. Regulator disable is handled manually only on probe failure, while reset is devm action based.

## Test Signals
Useful tests cover SoundWire probe and attachment, unattached reinitialization, reset-controller and legacy GPIO paths, missing `vdd`, static and absent `qcom,port-mapping`, toggling each port switch before `hw_params()`, stream add/remove with enabled ports, receiver/speaker DAPM register differences, mute/unmute register writes, runtime suspend/resume cache behavior, hwmon reads while PA is off/on, invalid OTP trim data, and variant-specific compander offset programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wsa883x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wsa884x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wsa884x.c

## Purpose
`wsa884x.c` is the ASoC SoundWire codec driver for Qualcomm WSA884x speaker amplifiers. It provides a mono `SPKR` playback DAI, register-cache backed initialization for the amplifier, six selectable SoundWire sink ports, speaker/receiver mode tuning, PA mute and DAPM power sequencing, regulator/reset handling, and an optional hwmon temperature input.

## Important APIs, Types, And Functions
`struct wsa884x_priv` stores the SoundWire slave, regmap, two bulk regulators (`vdd-io`, `vdd-1p8`), reset or `powerdown` GPIO, stream runtime/config, per-port controls, mode, init flag, and protected temperature/PA fields. Important functions include `wsa884x_probe()`, `wsa884x_init()`, `wsa884x_set_gain_parameters()`, `wsa884x_update_status()`, `wsa884x_port_prep()`, `wsa884x_hw_params()`, `wsa884x_hw_free()`, `wsa884x_mute_stream()`, `wsa884x_spkr_event()`, `wsa884x_get_temp()`, and runtime PM callbacks. The register surface is defined by `wsa884x_regmap_config`, `wsa884x_defaults`, and `wsa884x_reg_init`.

## Control Flow
Probe allocates state, gets/enables both regulators, installs a devm regulator-disable action, obtains reset control or legacy powerdown GPIO, initializes SoundWire stream parameters, parses optional `qcom,port-mapping`, advertises sink ports and interrupts to SoundWire, deasserts reset, builds a SoundWire regmap, starts in cache-only mode until enumeration, registers optional hwmon, enables runtime PM, and registers the component and DAI. On SoundWire `ATTACHED`, `wsa884x_update_status()` leaves cache-only mode, syncs cached defaults, and calls `wsa884x_init()` unless already initialized; on `UNATTACHED`, it marks the cache dirty and clears `hw_init`. `wsa884x_init()` applies the init sequence, detects haptics SKU through OTP ID, writes analog workorder controls, then applies speaker/receiver gain parameters. ALSA controls set mode and enabled ports. `hw_params()` builds active SoundWire port config and calls `sdw_stream_add_slave()`. DAPM speaker power-up sets PA state, applies mode/current-limit tuning, and enables PDM watchdog; power-down disables the watchdog and clears PA state. Mute toggles DRE gain and global PA enable.

## State And Persistence
The driver intentionally keeps regmap cache-only until the SoundWire device is enumerated, then uses cache sync as part of attachment. Runtime suspend also switches to cache-only and marks the cache dirty; resume syncs hardware from cache. `port_enable[]` and `dev_mode` are user-visible ALSA-control state. Temperature state is cached and mutex protected so hwmon reads can return a previous valid value when the PA is active.

## Dependencies And Integration Points
It integrates with SoundWire ID `0x0217:0x204`, regmap SoundWire, ASoC controls/DAPM/DAI, runtime PM, regulator bulk APIs, reset or GPIO descriptor APIs, optional hwmon, and DT `qcom,port-mapping`. The six sink ports are DAC, COMP, BOOST, PBR, VISENSE, and CPS with fixed channel masks.

## Risks And Edge Cases
No local validation prevents enabling zero ports before stream setup. Several regmap updates in init, gain setup, DAPM, mute, and temperature paths ignore return values, so hardware misprogramming may be hard to diagnose. `port_prep()` trusts SoundWire port numbers for array indexing. Temperature reads discard implausible values and can return `-EAGAIN`, which is expected before valid trim/sample data exist. Cache-only startup depends on proper SoundWire status transitions; missing `ATTACHED` handling would leave writes cached but not applied. Legacy `powerdown-gpios` cannot handle shared reset semantics as robustly as reset controllers.

## Test Signals
Tests should cover regulator acquisition/enabling and cleanup, reset-controller versus GPIO reset paths, SoundWire unattached/attached transitions and regcache sync, SKU-dependent init, speaker versus receiver gain/current-limit settings, each SoundWire port switch, stream add/remove with selected ports, mute/unmute PA state, DAPM power-up/down sequencing, runtime suspend/resume cache behavior, hwmon reads with PA off/on, invalid trim values, missing/partial DT port mapping, and probe deferral from supplies or reset resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wsa884x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/zl38060.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/zl38060.c

## Purpose
`zl38060.c` is an SPI ASoC codec driver for the Microsemi ZL38060 Connected Home Audio Processor. It implements a deliberately narrow firmware and audio configuration: host-boot firmware upload, 12 MHz crystal clocking, I2S master mode, stereo 16-bit playback/capture at 8, 16, or 48 kHz, stereo bypass routing, and a GPIO controller backed by the chip GPIO registers.

## Important APIs, Types, And Functions
`struct zl38_codec_priv` stores the device, regmap, duplex stream-use flags, and gpiochip pointer. Firmware flow is handled by `zl38_load_firmware()`, `zl38_fw_enter_boot_mode()`, `zl38_fw_send_data()`, `zl38_fw_send_xaddr()`, `zl38_fw_issue_command()`, and `zl38_fw_go()`. Audio callbacks are `zl38_set_fmt()`, `zl38_hw_params()`, and `zl38_hw_free()`. GPIO operations are `chip_gpio_get()`, `chip_gpio_set()`, `chip_direction_input()`, and `chip_direction_output()`. SPI-to-register translation lives in `zl38_bus_read()` and `zl38_bus_write()` behind `zl38_regmap_bus`.

## Control Flow
Probe optionally asserts and releases a `reset` GPIO, allocates state, initializes a custom 16-bit regmap over SPI HBI commands, requests `zl38060.fw`, enters boot mode, writes each ihex record to firmware page space or execution-address register, sends load-complete and firmware-go commands, verifies firmware product/revision, registers a devm gpiochip, programs crosspoint registers for stereo bypass, selects the crystal clock source, and registers the ASoC component and DAI. `set_fmt()` accepts only I2S, normal polarity, and codec bit/frame-clock provider mode, then configures 32-bit frames. `hw_params()` sets sample-rate bits and triggers a software reset unless the opposite-direction stream is already active, because both directions must use symmetric audio parameters. `hw_free()` clears the stream-in-use flag.

## State And Persistence
Firmware and audio configuration are applied to chip registers and persist until reset or power loss. The driver tracks whether playback or capture is active in `is_stream_in_use[]` to avoid resetting the chip while the other direction is running. GPIO state persists in the chip GPIO direction/data registers. There is no runtime PM path; state restoration depends on reprobe or hardware reset followed by firmware reload.

## Dependencies And Integration Points
The driver depends on SPI, custom regmap bus operations, firmware loader with ihex support, optional reset GPIO, gpiolib, and ASoC component/DAI/DAPM APIs. It binds to OF compatible `mscc,zl38060` or SPI ID `zl38060` and exposes a DAI named `zl38060-tdma`. The firmware file `zl38060.fw` must be supplied externally in kernel ihex binary format.

## Risks And Edge Cases
Firmware is mandatory and probe fails if missing, malformed, or rejected by the boot command protocol. The custom SPI framing validates transfer size but assumes even 16-bit register/value access. `hw_params()` skips setup while the opposite stream is active, relying on ASoC symmetric constraints to prevent mismatched full-duplex parameters. Software reset during parameter changes can corrupt active audio if stream-use tracking is wrong. Revision policy rejects firmware with unexpected major or too-old minor versions. The bypass-only routing omits most chip features.

## Test Signals
Test missing/reset GPIO paths, firmware request failure, malformed ihex records, command timeout behavior, revision rejection/acceptance, SPI page-zero and nonzero register reads/writes, DAI format rejection for non-I2S or non-master modes, sample-rate programming for 8/16/48 kHz, rejection of other rates/formats/channels through DAI constraints, full-duplex symmetric startup, GPIO get/set/direction behavior, and DAPM route exposure for DAC1/DAC2/DMICL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/zl38060.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/dwc/Kconfig

## Purpose
This Kconfig fragment defines the DesignWare ASoC driver menu. It offers the Synopsys DesignWare I2S controller driver and an optional PIO PCM extension for controllers without DMA support.

## Important APIs, Types, And Functions
The file defines `SND_DESIGNWARE_I2S` as a tristate option depending on `HAVE_CLK` and selecting `SND_SOC_GENERIC_DMAENGINE_PCM`. It also defines `SND_DESIGNWARE_PCM` as a bool depending on `SND_DESIGNWARE_I2S`, used to compile the custom PIO backend in `dwc-pcm.c`.

## Control Flow
Kconfig selection controls whether `designware_i2s.o` is built and whether `dwc-pcm.o` is linked into it. Enabling the I2S driver pulls in generic DMAengine PCM support; enabling the PCM extension adds an IRQ/PIO fallback for non-DMA devices.

## State And Persistence
There is no runtime state. The configuration persists in the kernel build config and determines compiled code paths and helper stubs exposed through `local.h`.

## Dependencies And Integration Points
`SND_DESIGNWARE_I2S` integrates with the ASoC sound subsystem and common clock framework. `SND_DESIGNWARE_PCM` integrates with the local DesignWare driver and is consumed by `Makefile` and `local.h` conditional declarations.

## Risks And Edge Cases
The PIO option is bool, not tristate, so it follows the built module/object shape of the parent and cannot be independently loaded. DMAengine support is selected even when platforms will use PIO, which is harmless but broadens build dependencies.

## Test Signals
Build-test combinations should include I2S disabled, I2S built-in, I2S modular, and I2S plus PIO extension. Config tests should verify `dwc-pcm.o` is included only when `SND_DESIGNWARE_PCM=y` and that stubs are used otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/dwc/Makefile

## Purpose
This Makefile maps DesignWare ASoC Kconfig symbols to build objects. It builds the core I2S driver and conditionally folds in the PIO PCM extension.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SND_DESIGNWARE_I2S) += designware_i2s.o` emits the aggregate driver object. `designware_i2s-y := dwc-i2s.o` always includes the platform/DAI driver. `designware_i2s-$(CONFIG_SND_DESIGNWARE_PCM) += dwc-pcm.o` conditionally adds the PIO component implementation.

## Control Flow
Kbuild evaluates the configuration symbols, builds `dwc-i2s.o`, optionally builds `dwc-pcm.o`, links them into `designware_i2s.o`, and then links that aggregate as built-in or module according to `SND_DESIGNWARE_I2S`.

## State And Persistence
There is no runtime state. The Makefile encodes build-time composition of the driver.

## Dependencies And Integration Points
It integrates directly with `sound/soc/dwc/Kconfig` symbols and the local `local.h` conditional prototypes. The resulting object provides the platform driver named `designware-i2s`.

## Risks And Edge Cases
If `SND_DESIGNWARE_PCM` is disabled, the core can still call `dw_pcm_register()` only through the inline `-EINVAL` stub in `local.h`; platforms requiring PIO will fail PCM registration at runtime. Object aggregation means symbol visibility and module metadata come from `dwc-i2s.c`.

## Test Signals
Inspect generated build commands for both config states. Runtime smoke tests should verify DMAengine registration when PIO is absent and custom PCM registration when `dwc-pcm.o` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/dwc-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/dwc/dwc-i2s.c

## Purpose
`dwc-i2s.c` is the core ASoC CPU DAI/platform driver for Synopsys DesignWare I2S controllers. It maps controller registers, derives capabilities from platform data or component parameter registers, configures playback/capture channels and clocks, supports DMAengine or local PIO PCM backends, handles IRQs, and contains StarFive JH7110 clock/reset/syscon special cases.

## Important APIs, Types, And Functions
The driver uses `struct dw_i2s_dev` from `local.h` for MMIO base, clock/reset handles, capability and quirk bits, component parameter registers, DAI/DMA data, TDM settings, PIO hooks, and active stream count. Important functions are `dw_i2s_probe()`, `dw_i2s_remove()`, `dw_configure_dai()`, `dw_configure_dai_by_dt()`, `dw_configure_dai_by_pd()`, `dw_i2s_hw_params()`, `dw_i2s_prepare()`, `dw_i2s_trigger()`, `dw_i2s_set_fmt()`, `dw_i2s_set_tdm_slot()`, `i2s_start()`, `i2s_stop()`, `i2s_irq_handler()`, and runtime/system PM callbacks. JH7110 helpers initialize clock/reset topology and RX syscon state.

## Control Flow
Probe allocates private data and a DAI driver instance, maps MMIO, runs optional platform-data init, deasserts reset when not JH7110, requests an optional IRQ, configures DAI capabilities and DMA addresses from platform data or hardware component registers, obtains/enables the I2S clock for master mode, registers the ASoC component/DAI, then registers either PIO PCM when an IRQ is present or generic DMAengine PCM otherwise. `hw_params()` validates sample format/channels, programs transfer resolution and FIFO thresholds, writes `CCR`, and configures bit clock through platform callback or `clk_set_rate()`. `trigger()` increments/decrements `active`, starts or stops stream hardware, enables/disables DMA handshakes except for PIO/JH7110, and gates global I2S only when no streams remain. IRQ handling services PIO TX empty/RX data for channel 0 and logs FIFO overruns. Suspend/resume gates clocks and reconfigures active streams.

## State And Persistence
Runtime state includes `active`, DAI capability fields, cached component parameter registers, `ccr`, transfer resolution, FIFO threshold, TDM slot/mask/frame offset, DMA data, and PIO stream pointers in the shared struct. Hardware state is programmed in MMIO registers and must be restored after reset or some resumes; `dw_i2s_resume()` re-runs stream configuration for active streams. Runtime PM disables/enables the master clock but does not snapshot registers.

## Dependencies And Integration Points
The driver integrates with platform devices, OF match data (`snps,designware-i2s` and StarFive compatibles), platform-data `struct i2s_platform_data`, reset and clock frameworks, syscon/regmap for JH7110 RX, ASoC DAI/component registration, DMAengine PCM, the optional local PIO component, and Sound PCM parameter APIs. It consumes register definitions and helper declarations from `local.h`.

## Risks And Edge Cases
`active` is a plain counter and can underflow if trigger ordering is wrong. PIO is chosen solely from IRQ presence in DT/no-platform-data cases, so an IRQ-enabled DMA design may unexpectedly use PIO. JH7110 bypasses normal reset/DMA handling and has custom trigger order, making regressions platform-specific. FIFO size calculations use shifts and word-size tables; bad component parameter values return `-EINVAL` only for array overrun. TDM requires 32-bit slots, equal TX/RX masks, and nonzero mask; unsupported masks fail. Several error paths assert an optional reset pointer that may be NULL, relying on reset API tolerance.

## Test Signals
Test DT and platform-data probing, missing clocks/resets/resources, IRQ and no-IRQ backend selection, DMA address/fifo setup, master/slave `set_fmt()`, supported and rejected formats/channels, TDM slot validation, trigger start/stop ordering for playback/capture/full-duplex, PIO IRQ TX/RX paths, FIFO overrun logging, runtime/system suspend/resume with active streams, JH7110 master/slave/RX init, and probe cleanup on component or PCM registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/dwc-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/dwc-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/dwc/dwc-pcm.c

## Purpose
`dwc-pcm.c` implements the optional PIO PCM backend for the DesignWare I2S driver. It registers an ASoC PCM component that uses CPU-driven FIFO reads/writes from the I2S IRQ handler instead of DMAengine transfers.

## Important APIs, Types, And Functions
The file generates 16-bit and 32-bit TX/RX transfer functions through `dw_pcm_tx_fn()` and `dw_pcm_rx_fn()`. `dw_pcm_transfer()` is the shared IRQ-side transfer engine used by exported `dw_pcm_push_tx()` and `dw_pcm_pop_rx()`. Component callbacks include `dw_pcm_open()`, `dw_pcm_close()`, `dw_pcm_hw_params()`, `dw_pcm_trigger()`, `dw_pcm_pointer()`, and `dw_pcm_new()`. `dw_pcm_register()` registers the component with the platform device.

## Control Flow
`dw_pcm_open()` applies fixed hardware constraints, stores the parent `dw_i2s_dev` in runtime private data, and enforces integer periods. `hw_params()` accepts only stereo streams and selects 16-bit or 32-bit transfer functions; 24-bit samples are moved through the 32-bit path. `trigger()` resets the software pointer and publishes the active substream through RCU on start/resume/unpause, or clears it on stop/suspend/pause. The I2S IRQ handler calls push/pop helpers when TX FIFO empty or RX data available; `dw_pcm_transfer()` reads the RCU substream, verifies it is running, transfers `fifo_th` stereo frames through `l_reg`/`r_reg`, atomically updates the pointer with `cmpxchg()`, and signals period elapsed when needed. `pointer()` reports the current frame index. `pcm_new()` allocates a managed continuous buffer.

## State And Persistence
State is shared with `struct dw_i2s_dev`: RCU substream pointers, selected transfer function pointers, TX/RX frame pointers, FIFO threshold, and left/right register offsets. Buffer contents are ALSA-managed continuous memory. There is no hardware persistence beyond FIFO accesses; stream state is reset on trigger start.

## Dependencies And Integration Points
This backend depends on `CONFIG_SND_DESIGNWARE_PCM`, ASoC component PCM callbacks, ALSA PCM runtime and constraints, RCU synchronization, MMIO FIFO accessors, and the parent `dwc-i2s.c` IRQ handler. It is linked into `designware_i2s.o` only when selected by Kconfig.

## Risks And Edge Cases
PIO supports only two channels despite the controller supporting more channels elsewhere. Transfer functions write/read `fifo_th` frames per IRQ without checking actual FIFO level beyond the interrupt cause. `cmpxchg()` protects pointer update but does not retry on race; concurrent IRQ contexts could drop pointer progress if misconfigured. `period_elapsed` is set based on local period position after a batch and can skip exact boundaries if period/fifo sizes are poorly matched. 24-bit samples use 32-bit memory access, matching common ALSA storage but requiring correct format expectations.

## Test Signals
Test open constraints, stereo-only rejection, 16/24/32-bit format selection, trigger publication/removal through RCU, pointer wraparound, period elapsed signaling, playback FIFO writes and capture FIFO reads, close-time RCU synchronization, managed buffer allocation, and integration with `dwc-i2s.c` IRQ handling under playback, capture, and pause/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/dwc-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/local.h -->
# sources/distributed-fs/ceph-client/sound/soc/dwc/local.h

## Purpose
`local.h` is the private interface for the DesignWare I2S ASoC driver. It defines register offsets/bitfields, hardware capability decoding macros, common constants, the shared device state structure, and conditional prototypes/stubs for the optional PIO PCM backend.

## Important APIs, Types, And Functions
Important definitions include common I2S registers (`IER`, `IRER`, `ITER`, `CER`, `CCR`, FIFO flush registers), per-channel register macros (`TER()`, `RER()`, `TCR()`, `RCR()`, `ISR()`, `IMR()`, FIFO threshold/status registers), component parameter registers, DMA control bits, parameter decoding macros such as `COMP1_TX_ENABLED()` and `COMP2_RX_WORDSIZE_0()`, and channel limits. `union dw_i2s_snd_dma_data` supports either platform-data DMA fields or DMAengine DAI data. `struct dw_i2s_dev` is shared by `dwc-i2s.c` and `dwc-pcm.c`.

## Control Flow
The header does not run code, but it defines the contract used by runtime paths. `dwc-i2s.c` programs registers and derives capabilities from these macros; `dwc-pcm.c` uses the shared PIO fields and FIFO register offsets. The `IS_ENABLED(CONFIG_SND_DESIGNWARE_PCM)` block selects real PIO function declarations or inline no-op/`-EINVAL` stubs.

## State And Persistence
`struct dw_i2s_dev` captures persistent per-device state: MMIO base, clock/reset, active count, capability/quirks, component parameters, cached audio config, FIFO/format parameters, DMA data, PIO mode and callbacks, TDM settings, RCU substreams, and software frame pointers. Hardware state itself lives in the MMIO register map described by the macros.

## Dependencies And Integration Points
The header depends on Linux clock/device/types headers, reset declarations through included users, ALSA PCM, DMAengine PCM, and public `sound/designware_i2s.h`. It is the local bridge between the core driver and optional PIO component.

## Risks And Edge Cases
Many register macros assume four register banks for up to eight channels, while constants expose `MAX_CHANNEL_NUM` as eight. PIO stubs compile successfully when the backend is disabled but cause runtime registration failure for IRQ/PIO-selected devices. Shared state fields are broad and mutable from both IRQ and PCM/DAI callbacks, so synchronization discipline must be maintained by users.

## Test Signals
Compile tests should cover both PIO-enabled and PIO-disabled configs. Driver tests should validate component-parameter decoding, register offset correctness, DMA data union use in platform-data and DT paths, TDM fields, and safe interaction of RCU substream fields between IRQ and PCM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/dwc/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/Kconfig

## Purpose
This Kconfig file defines Freescale/NXP ASoC controller, platform, DMA, utility, and machine-driver options for PowerPC MPC52xx/P1022 and i.MX families. It controls which low-level audio blocks and board cards are compiled.

## Important APIs, Types, And Functions
Key symbols include controller/platform blocks such as `SND_SOC_FSL_ASRC`, `SND_SOC_FSL_SAI`, `SND_SOC_FSL_MQS`, `SND_SOC_FSL_AUDMIX`, `SND_SOC_FSL_SSI`, `SND_SOC_FSL_SPDIF`, `SND_SOC_FSL_ESAI`, `SND_SOC_FSL_MICFIL`, `SND_SOC_FSL_EASRC`, `SND_SOC_FSL_XCVR`, `SND_SOC_FSL_AUD2HTX`, `SND_SOC_FSL_UTILS`, and RPMSG support. Architecture group symbols include `SND_POWERPC_SOC`, `SND_IMX_SOC`, `SND_SOC_IMX_PCM_DMA`, `SND_SOC_IMX_PCM_FIQ`, `SND_SOC_IMX_AUDMUX`, and machine-card options such as `SND_MPC52xx_SOC_EFIKA` and `SND_SOC_EUKREA_TLV320`.

## Control Flow
The file first declares common Freescale audio IP options, then enters a PowerPC-specific block gated by `SND_POWERPC_SOC`, then i.MX-specific options gated by `SND_IMX_SOC`. Board options select the controller, DMA, audmux, codec, and utility symbols needed by their machine drivers. Hidden helper symbols are selected by higher-level drivers rather than user-visible menus.

## State And Persistence
There is no runtime state. The selected Kconfig symbols persist in kernel configuration and drive object inclusion in the companion Makefile, plus transitive dependencies on DMA, regmap, codecs, clocks, I2C/SPI, RPMSG, and architecture support.

## Dependencies And Integration Points
The file integrates Freescale/NXP ASoC code with architecture symbols (`ARCH_MXC`, `FSL_SOC`, `PPC_MPC52xx`, board symbols), codec drivers, DMAengine, regmap MMIO, compressed audio support, RPMSG, I2C/SPI, common clock, and simple-card helpers.

## Risks And Edge Cases
Several options are intended mainly for in-tree automatic selection but remain user-visible. Broad `select` chains can force many codec/controller dependencies into builds. Architecture guards and `COMPILE_TEST` coverage vary by option, so allmodconfig coverage is uneven. Some legacy machine drivers depend on old board macros or non-DT paths, increasing bitrot risk.

## Test Signals
Build matrices should cover PowerPC-only, i.MX-only, COMPILE_TEST, module and built-in configurations, key board selections (`SND_MPC52xx_SOC_EFIKA`, `SND_SOC_EUKREA_TLV320`), and dependency closure for selected codecs, DMA backends, AUDMUX, and controller drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/Makefile

## Purpose
This Makefile maps Freescale/NXP ASoC Kconfig symbols to controller, platform, DMA, utility, RPMSG, and machine-driver objects.

## Important APIs, Types, And Functions
It defines aggregate objects such as `snd-soc-fsl-asrc-y`, `snd-soc-fsl-sai-y`, `snd-soc-fsl-ssi-y`, `snd-soc-fsl-rpmsg-y`, and machine-card aggregates like `snd-soc-eukrea-tlv320-y`. `obj-$(CONFIG_...)` lines include the appropriate aggregate or single object. `snd-soc-fsl-ssi-$(CONFIG_DEBUG_FS)` conditionally adds debugfs support.

## Control Flow
Kbuild evaluates each config symbol and builds the associated object list. Controller support is grouped first, followed by MPC5200 platform/machine support and i.MX platform/machine support. Board-card objects are included only when the corresponding Kconfig machine option is enabled.

## State And Persistence
There is no runtime state. The file persists build composition, including which source files are linked into aggregate modules.

## Dependencies And Integration Points
It integrates with the FSL Kconfig symbols, ASoC controller source files, codec-selected machine drivers, debugfs optional SSI support, MPC5200 DMA/PSC drivers, i.MX AUDMUX/PCM backends, and RPMSG audio components.

## Risks And Edge Cases
Because many modules are aggregate objects, missing one source in the `*-y` list can silently omit required functionality. Debugfs object inclusion changes the SSI aggregate shape. Legacy and modern cards live together, so symbol naming consistency matters for module aliases and dependencies.

## Test Signals
Build-test representative symbols across each group, verify aggregate object membership with and without `CONFIG_DEBUG_FS`, and smoke-load modules for selected controllers and machine drivers to confirm expected platform driver names and module metadata are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/efika-audio-fabric.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/efika-audio-fabric.c

## Purpose
`efika-audio-fabric.c` is a legacy ASoC machine driver for the bplan Efika PowerPC platform using MPC5200 PSC AC97 interfaces and an STAC9766 codec. It creates an ASoC card with separate analog and IEC958 AC97 links.

## Important APIs, Types, And Functions
The file defines two `SND_SOC_DAILINK_DEFS()` blocks for `analog` and `iec958`, a two-entry `efika_fabric_dai[]` array, and a static `snd_soc_card` named `Efika`. The only runtime entry point is `efika_fabric_init()`, registered with `module_init()`.

## Control Flow
At module init, the driver checks `of_machine_is_compatible("bplan,efika")`. Non-Efika systems return `-ENODEV`. On Efika, it allocates a `soc-audio` platform device, stores the static card as driver data, and adds the platform device. The generic soc-audio machinery then consumes the card and its DAI links.

## State And Persistence
State is mostly static: the card and DAI link definitions are global. The allocated platform device persists after successful module init; there is no explicit module exit or device unregister path in this file.

## Dependencies And Integration Points
It depends on OF machine compatibility, platform device APIs, ASoC card/link definitions, MPC5200 PSC AC97 CPU DAIs (`mpc5200-psc-ac97.0` and `.1`), STAC9766 codec DAIs, and `mpc5200-pcm-audio` platform DMA.

## Risks And Edge Cases
The file uses static card/link data and a legacy `soc-audio` platform-device registration style. There is no cleanup function after successful init, which is acceptable for old built-in board support but less flexible for unload scenarios. Hard-coded component names must match the PSC, codec, and platform drivers exactly.

## Test Signals
Test that non-Efika machines skip cleanly, Efika creates the `soc-audio` device, both analog and IEC958 links bind to expected CPU/codec/platform components, and failure paths from allocation/addition release the platform device. Build tests should include `SND_MPC52xx_SOC_EFIKA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/efika-audio-fabric.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/eukrea-tlv320.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/eukrea-tlv320.c

## Purpose
`eukrea-tlv320.c` is an ASoC machine driver for Eukrea CPUIMX boards using an i.MX SSI interface connected to a TLV320AIC23 codec in I2S mode. It supports both device-tree probing and legacy machine-ID based configuration, including AUDMUX routing setup for older i.MX variants.

## Important APIs, Types, And Functions
The main card is `eukrea_tlv320` with one DAI link `eukrea_tlv320_dai`. `eukrea_tlv320_hw_params()` configures codec sysclk, CPU TDM slot mask, and CPU SSI clocking. `eukrea_tlv320_probe()` parses DT or legacy component names, configures AUDMUX through `imx_audmux_v1_configure_port()` or `imx_audmux_v2_configure_port()`, and registers the card. The platform driver matches `eukrea,asoc-tlv320` and has alias `platform:eukrea_tlv320`.

## Control Flow
On probe, the driver attaches the card to the platform device. With DT, it parses `eukrea,model`, resolves `ssi-controller`, follows the SSI `codec-handle`, reads `fsl,mux-int-port` and `fsl,mux-ext-port`, converts one-based DT port numbers to zero-based AUDMUX API values, and assigns CPU/platform/codec OF nodes. Without DT, it hard-codes `imx-ssi.0`, `tlv320aic23-codec.0-001a`, and card name `cpuimx-audio`. It then selects AUDMUX v1 routing for i.MX27 or `fsl,imx21-audmux`, AUDMUX v2 routing for i.MX25/35/51 or `fsl,imx31-audmux`, or exits successfully on unrelated legacy machines. Finally it registers the card. During stream setup, `hw_params()` sets the TLV320 clock to 12 MHz output, programs stereo SSI TDM slots, and tolerates `-EINVAL` from CPU `set_sysclk()` because `fsl_ssi` lacks that op.

## State And Persistence
Card and DAI link structures are static and mutated during probe with OF nodes or legacy component names. AUDMUX routing persists in SoC mux registers after configuration. There is no explicit remove path; devm card registration handles cleanup for bound devices.

## Dependencies And Integration Points
The driver depends on ASoC card/link APIs, TLV320AIC23 codec DAI, i.MX SSI, i.MX AUDMUX v1/v2 helpers, DT phandles/properties, legacy machine macros, I2C codec presence, and clocking assumptions around a 12 MHz codec clock. Kconfig selects TLV320 I2C, AUDMUX, FSL SSI, and i.MX PCM DMA.

## Risks And Edge Cases
Static global DAI/card mutation limits multi-instance safety. DT parsing returns errors for missing model, SSI, or mux properties, but a missing codec handle only logs an error and continues with a NULL codec OF node. The `tmp_np` assignment inside conditionals must be balanced with `of_node_put()`, which the code does in each matching branch. Legacy no-DT probing returns success on unrelated machines to avoid failing module load. CPU `set_tdm_slot()` return is ignored.

## Test Signals
Test DT success and each missing-property failure, codec-handle absence behavior, one-based to zero-based AUDMUX conversion, AUDMUX v1 and v2 register calls, legacy CPUIMX27/25/35/51 paths, unrelated legacy machine no-op success, `hw_params()` codec sysclk failure, tolerated CPU `set_sysclk()` `-EINVAL`, card registration failure logging, and module alias/OF match binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/eukrea-tlv320.c -->
