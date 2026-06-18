# subset-b-005959 Research

Grouped research for ALSA sound headers under `sources/distributed-fs/ceph-client/include/sound`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs42l42.h -->
# sources/distributed-fs/ceph-client/include/sound/cs42l42.h

## Purpose
This header is the register and timing contract for the Cirrus Logic CS42L42/CS42L83 ASoC codec driver. It defines the paged register address map, bit shifts/masks, encoded headset-detection switch patterns, interrupt masks/status values, PLL/audio serial-port controls, and driver timing constants.

## Important APIs, Types, and Constants
There are no C functions or structs. The public surface is macro-only: `CS42L42_PAGE_*`, `CS42L42_*_CTL*`, `CS42L42_*_MASK`, `CS42L42_*_SHIFT`, chip IDs `CS42L42_CHIP_ID` and `CS42L83_CHIP_ID`, and timing constants such as `CS42L42_BOOT_TIME_US`, `CS42L42_PLL_LOCK_TIMEOUT_US`, and `CS42L42_PDN_DONE_TIMEOUT_US`. Register groups cover global ID/clocking, power/headset detection, interrupts, PLL, load detect, headset bias, ADC/DAC, mixer/EQ, serial audio RX/TX, SRC, DMA reset, S/PDIF, and sub-revision ID.

## Control Flow
The header drives codec control flow indirectly through the implementation that programs these registers via regmap. Typical flows are: identify chip by DEVID registers, release reset and wait boot time, configure MCLK/PLL and serial port registers, power ADC/DAC/headphone blocks with `PWR_CTL*`, configure headset detect switches/comparator levels, enable or mask interrupts, and poll status bits for PLL lock, power-down completion, load-detect completion, or plug state. Macros like `CS42L42_FRAC0_VAL()` split multi-byte PLL fractional values across registers.

## State and Persistence
State lives in hardware registers and in the codec driver's regmap cache, not in this file. Power, PLL, bias, mute, and jack-detect state must survive runtime PM transitions through explicit save/restore or reinitialization. The header documents two hardware sequencing hazards: `PLL_START` and `DETECT_MODE` must be zero when both ADC and headphone blocks are powered down, otherwise the analog filter node may not charge correctly.

## Dependencies and Integration Points
The macros assume Linux bit helpers such as `BIT()` and `GENMASK()` are visible through the including driver. Integration is with the CS42L42 ASoC codec, regmap paging/windowing, IRQ/jack detection, DAPM power management, and ALSA DAI format/clock configuration.

## Risks and Edge Cases
The page/register map is dense and typo-prone; wrong masks can silently alter neighboring analog controls. `CS42L42_OSC_PDNB_STAT_MASK` uses `CS42L42_OSC_SW_SEL_STAT_SHIFT` rather than its own shift, which is worth validating against the implementation or datasheet. Headset-detection switch matrices and CTIA/OMTP comparators are hardware-sensitive and need sequencing tests. Timeout constants are part of user-visible probe/resume latency and can cause false failures on slow supplies or clocks.

## Test Signals
Probe should verify expected chip ID/revision and max-register access. Runtime tests should cover headset insertion/removal, CTIA/OMTP/headphone classification, ADC/DAC stream startup, suspend/resume, PLL lock polling, power-down done polling, and interrupt-mask/status handling with regmap traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs42l42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs42l43.h -->
# sources/distributed-fs/ceph-client/include/sound/cs42l43.h

## Purpose
This tiny public ASoC header exposes CS42L43 clock IDs and source IDs for machine drivers and codec users.

## Important APIs, Types, and Constants
It defines `CS42L43_SYSCLK` as the clock selector and source values `CS42L43_SYSCLK_MCLK` and `CS42L43_SYSCLK_SDW`. There are no structs or functions.

## Control Flow
Machine drivers pass these constants to the CS42L43 component/DAI clock setup path. The selected source determines whether the codec derives sysclk from a board master clock or from SoundWire.

## State and Persistence
Persistent state is in the codec driver and hardware clock tree. This file only names stable ABI-like values used across compilation units.

## Dependencies and Integration Points
Integration is with ASoC clock APIs, board machine drivers, and SoundWire-capable CS42L43 deployments.

## Risks and Edge Cases
Because values are simple integers, mismatched constants between codec and machine driver would lead to wrong clock-source selection. Test both MCLK and SoundWire configurations where supported.

## Test Signals
Build coverage of CS42L43 users, stream startup with MCLK source, stream startup with SoundWire source, and suspend/resume clock restoration are the useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs42l43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs48l32.h -->
# sources/distributed-fs/ceph-client/include/sound/cs48l32.h

## Purpose
This header exposes the CS48L32 codec driver's public clock/FLL IDs and the core private device container shared by CS48L32 implementation files.

## Important APIs, Types, and Constants
Constants include `CS48L32_FLL1_REFCLK`, FLL sources (`CS48L32_FLL_SRC_NONE`, `MCLK1`, `PDMCLK`, ASP BCLK/FSYNC variants), sysclk IDs (`CS48L32_CLK_SYSCLK_1` through `_4`, `CS48L32_CLK_DSPCLK`, `CS48L32_CLK_PDM_FLLCLK`), and clock sources (`MCLK1`, `FLL1`, ASP BCLK). `struct cs48l32` stores the device's `regmap`, `device`, reset GPIO, `mclk1`, two core bulk regulators, an additional `vdd_d` regulator, and IRQ number.

## Control Flow
The implementation allocates and fills `struct cs48l32` during probe, enables supplies and reset GPIO, brings up clocks, configures FLL/sysclk through the exported IDs, and services IRQs with the stored interrupt line. ASoC machine drivers use the clock and FLL constants via standard `snd_soc_component_set_pll()` and `snd_soc_component_set_sysclk()` calls.

## State and Persistence
Runtime state is in the `cs48l32` instance and hardware registers. Regulator, reset, clock, regmap, and IRQ resources are lifetime-managed by probe/remove and runtime/system PM. No persistent disk state exists.

## Dependencies and Integration Points
This header depends on kernel types for regmap, device, GPIO descriptors, clocks, and regulators, supplied by including implementation files. It integrates with ASoC component/DAI clock control, regmap, regulator framework, gpiod reset handling, and IRQ handling.

## Risks and Edge Cases
Incorrect FLL source IDs can produce silent clocking failures. The private struct is included from multiple CS48L32 driver files, so field changes have broad compile-time impact. PM paths must restore regulators, reset state, and regmap cache coherently.

## Test Signals
Probe/remove on DT/ACPI boards, FLL source switching, sysclk selection, IRQ delivery, regulator failure injection, and suspend/resume with active streams are the primary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs48l32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs48l32_registers.h -->
# sources/distributed-fs/ceph-client/include/sound/cs48l32_registers.h

## Purpose
This is the CS48L32 register map and bit-field catalog. It gives the codec driver symbolic addresses and masks for device ID, clocks, FLL, GPIO, regulators/micbias, inputs, PDM, ASPs, mixers, ISRC/EQ/DRC/LHPF, tone/noise/ultrasonic blocks, DSP memory windows, and interrupt state.

## Important APIs, Types, and Constants
The header is macro-only. Address macros include `CS48L32_DEVID`, `CS48L32_SYSTEM_CLOCK1`, `CS48L32_FLL1_CONTROL*`, `CS48L32_INPUT*`, `CS48L32_ASP*`, mixer input bases, `CS48L32_DSP1_*` memory ranges, and `CS48L32_IRQ1_*`. Field macros pair masks/shifts for device revision, sysclk source/frequency/enables, FLL lock/reference/divider values, input modes/volumes, ASP formats/widths, mixer source/volume, ISRC enables/rates, EQ/DRC controls, ultrasonic detector settings, and IRQ bits such as boot done, DSP MPU error, watchdog expiry, DSP IRQ, and FLL lock status.

## Control Flow
The driver uses these definitions in regmap reads/writes and regmap field helpers. Initialization reads ID/revision, releases MCU/reset state, enables clocks and FLL, configures sample rates, powers input paths, configures ASP and mixer routing, loads or controls DSP memory regions, and unmasks/handles IRQ events.

## State and Persistence
All state is hardware register state, usually shadowed by regmap cache. DSP memories and firmware-visible scratch/control windows are volatile across reset and power loss. IRQ mask/status registers define transient event state. Regulator and clock configuration must be re-applied after suspend/resume or reset.

## Dependencies and Integration Points
The map is consumed by the CS48L32 codec/MFD-style implementation, ASoC widgets/routes/DAIs, regmap, firmware/DSP code, IRQ handlers, and clock/FLL setup helpers. No functions are declared here.

## Risks and Edge Cases
The file has a large address surface, including high DSP memory windows, so off-by-one range handling can corrupt firmware memory or expose invalid regmap ranges. Shared field macros such as `CS48L32_INx_*`, `CS48L32_ASP_*`, and `CS48L32_MIXER_*` intentionally apply to repeated register banks; callers must compute the correct bank address. IRQ status/mask naming spans multiple banks and can be easy to mis-pair.

## Test Signals
Regmap range/readability tests, boot done IRQ handling, FLL lock tests, stream playback/capture over both ASPs, mixer route validation, DSP firmware load/control tests, and suspend/resume register-cache sync are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs48l32_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs8403.h -->
# sources/distributed-fs/ceph-client/include/sound/cs8403.h

## Purpose
This header provides optional inline/static helper implementations to translate between CS8403/CS8404 S/PDIF transmitter control bits and ALSA IEC958 channel-status bytes.

## Important APIs, Types, and Functions
When `SND_CS8403` is defined, it emits `snd_cs8403_decode_spdif_bits()` and `snd_cs8403_encode_spdif_bits()` unless the caller overrides declaration/name macros. When `SND_CS8404` is defined, it similarly emits CS8404 variants. All functions operate on `struct snd_aes_iec958` and an 8-bit hardware control value.

## Control Flow
Decode functions inspect hardware bits, set consumer/professional IEC958 status, sample rate, emphasis, copyright/original flags, category/mode, and non-audio state. Encode functions reverse the mapping from ALSA status bytes to chip-specific bit layouts, with defaults for unsupported or unidentified values.

## State and Persistence
No state is stored in the header. The passed `snd_aes_iec958` structure is mutated during decode; callers should initialize/clear it before decoding to avoid stale bits. Encoded values are transient control bytes written to the device.

## Dependencies and Integration Points
The helpers depend on IEC958 constants from ALSA headers included by users. They integrate with legacy Cirrus S/PDIF transmitter drivers that compile this header with `SND_CS8403` or `SND_CS8404` to instantiate local helpers.

## Risks and Edge Cases
The header emits function bodies conditionally, so multiple compilation units using non-static declarations could duplicate symbols. Decode uses bitwise OR for many status fields, so an uncleared status buffer can retain stale values. A `CHECKME` comment notes uncertainty in CS8403 professional sample-rate bit order.

## Test Signals
Round-trip encode/decode tests for consumer/professional modes, 32/44.1/48 kHz, non-audio, emphasis, copyright/original flags, and category/mode values should catch regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs8403.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs8427.h -->
# sources/distributed-fs/ceph-client/include/sound/cs8427.h

## Purpose
This header defines the ALSA I2C interface and register map for the Cirrus Logic CS8427 AES3/S/PDIF receiver/transmitter/transceiver.

## Important APIs, Types, and Functions
It defines I2C base address `CS8427_BASE_ADDR`, autoincrement flag, all low register addresses, and bit masks for control, data flow, clock source, serial input/output formats, interrupt status/masks/modes, channel-status/user-data buffers, receiver errors, and ID/version. Exported functions are `snd_cs8427_init()`, `snd_cs8427_create()`, `snd_cs8427_reg_write()`, `snd_cs8427_iec958_build()`, `snd_cs8427_iec958_active()`, and `snd_cs8427_iec958_pcm()`.

## Control Flow
Drivers create or initialize an I2C CS8427 device, write register values to set data flow and clocks, build IEC958 controls tied to playback/capture substreams, activate/deactivate IEC958 handling, and update PCM rate-specific channel status. Interrupt bits signal slips, receiver errors, buffer transfers, and Q-subcode availability.

## State and Persistence
Hardware state includes control registers, CS/U data buffers, receiver error bits, PLL lock, and interrupt masks. ALSA control state is owned by the implementation. Reset or suspend requires restoring clock/dataflow/serial format and IEC958 channel-status programming.

## Dependencies and Integration Points
It depends on `sound/i2c.h`, forward-declares `snd_pcm_substream`, and integrates with ALSA PCM, IEC958 controls, I2C bus/device abstractions, and board drivers with reset timing.

## Risks and Edge Cases
Several register fields combine clocking and data routing; invalid combinations can mute or bypass audio. Receiver error flags include parity, biphase, confidence, validity, unlock, and CRC conditions that need careful masking. The U-data macros define `CS8427_DETUI` and `CS8427_EFTUI` with the same bit value, which may be intentional or a copy-paste risk to verify.

## Test Signals
Probe with ID/version readback, register-write smoke tests, IEC958 control creation, PCM rate changes, receiver lock/unlock handling, and interrupt/error injection provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/cs8427.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7213.h -->
# sources/distributed-fs/ceph-client/include/sound/da7213.h

## Purpose
This header describes platform data for the Dialog/Renesas DA7213 ASoC codec.

## Important APIs, Types, and Constants
It defines enum choices for micbias voltage, digital microphone data pin selection, DMIC sample phase, and DMIC clock rate. `struct da7213_platform_data` carries `micbias1_lvl`, `micbias2_lvl`, `dmic_data_sel`, `dmic_samplephase`, and `dmic_clk_rate`.

## Control Flow
Board code or firmware translation supplies the platform data during probe. The codec driver reads it to program micbias rails and digital microphone interface timing before capture paths are used.

## State and Persistence
The struct is static board configuration. Runtime state is in codec registers and should be restored by the codec driver after reset or PM events.

## Dependencies and Integration Points
Integration is with DA7213 codec probe, platform data or DT/ACPI parsing glue, and ASoC capture widgets for analog/digital microphones.

## Risks and Edge Cases
Wrong micbias voltage can damage board assumptions or break microphone detection. DMIC phase/rate mismatches manifest as silent or corrupted capture.

## Test Signals
Probe with platform data, analog mic capture, DMIC capture on both data selections, clock-rate validation, and suspend/resume capture tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7213.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7218.h -->
# sources/distributed-fs/ceph-client/include/sound/da7218.h

## Purpose
This header defines board/platform data for the DA7218 codec, including micbias, mic amp, DMIC, and headphone load/jack detection configuration.

## Important APIs, Types, and Constants
Enums cover micbias voltages, mic amp input selection, DMIC data selection/sample phase/clock rate, headphone load-detect jack rate/debounce/threshold. `struct da7218_hpldet_pdata` contains headphone load/jack-detect tuning, and `struct da7218_pdata` combines micbias/DMIC config plus an optional headphone-detect sub-struct pointer.

## Control Flow
The codec driver consumes pdata at probe to select analog input routing, micbias voltage, DMIC timing, and jack/load-detect parameters. Jack-detect settings then affect runtime headset insertion/removal handling.

## State and Persistence
Platform data is immutable board configuration. Hardware state is codec-register based; jack detection has runtime status and debounce timing that are not stored here.

## Dependencies and Integration Points
It integrates with the DA7218 ASoC codec, board firmware parsing, ALSA jack reporting, and DAPM input routing.

## Risks and Edge Cases
Optional `hpldet_pdata` must be NULL-checked by consumers. Incorrect debounce/rate/threshold values can cause false jack events. Mic amp input and DMIC pin selection must match the board schematic.

## Test Signals
Probe with and without `hpldet_pdata`, headset insertion/removal debounce, load detection thresholds, analog mic capture, DMIC capture, and PM resume are key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7218.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7219-aad.h -->
# sources/distributed-fs/ceph-client/include/sound/da7219-aad.h

## Purpose
This header defines DA7219 accessory-detection platform data for headset insert/remove, mic detection, and button detection.

## Important APIs, Types, and Constants
Enums define micbias pulse level, button configuration, mic detect threshold, jack insertion debounce and polarity, jack detect rate, removal debounce, button averaging, and ADC 1-bit repeat count. `struct da7219_aad_pdata` stores all these settings plus four button threshold values.

## Control Flow
The DA7219 accessory-detect driver reads this pdata during initialization and programs AAD hardware. Runtime interrupt handlers then use the programmed thresholds/debounce to classify jack presence, microphone presence, and button presses.

## State and Persistence
The structure is persistent board policy; event state and ADC/button status live in codec hardware and driver runtime state. On reset/resume the AAD registers must be reprogrammed from this data.

## Dependencies and Integration Points
It is included by DA7219 codec/accessory-detect code and referenced from `da7219.h` via a forward declaration. It integrates with ALSA jack/button reporting and platform firmware property parsing.

## Risks and Edge Cases
Button thresholds must be monotonic and calibrated to headset resistor ladders. Debounce and polarity choices are board-specific. Bad micbias pulse settings can prevent microphone classification or waste power.

## Test Signals
Insertion/removal, CTIA/OMTP or mic-present classification where supported, button press thresholds for all configured buttons, long debounce/noise scenarios, and resume after jack insertion should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7219-aad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7219.h -->
# sources/distributed-fs/ceph-client/include/sound/da7219.h

## Purpose
This header defines DA7219 codec platform data and public DAI clock IDs.

## Important APIs, Types, and Constants
It defines micbias voltage choices, mic amp input selection, forward-declares `struct da7219_aad_pdata`, and defines DAI clock IDs `DA7219_CLKSRC_MCLK`, `DA7219_CLKSRC_MCLK_SQRT`, and `DA7219_CLKSRC_MCLK_XTAL`. `struct da7219_pdata` stores wakeup source enable, micbias level, mic amp input, and optional accessory-detect pdata.

## Control Flow
Probe code uses pdata to configure wake capability, microphone bias/input, and accessory detection. Machine drivers may use the clock IDs when configuring the DAI/sysclk source.

## State and Persistence
Pdata is static board configuration. Wake and AAD behavior persist as hardware/driver state and must be restored after reset/suspend.

## Dependencies and Integration Points
It integrates with DA7219 codec and AAD code, ASoC machine drivers, firmware parsing, and wakeup/jack reporting paths.

## Risks and Edge Cases
The optional `aad_pdata` pointer controls accessory detection setup and must be guarded. Wake source configuration affects system power behavior. Clock source mismatches break stream startup.

## Test Signals
Probe with and without AAD data, wake-from-jack behavior, mic capture, DAI clock-source switching, and suspend/resume with active jack state are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da7219.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da9055.h -->
# sources/distributed-fs/ceph-client/include/sound/da9055.h

## Purpose
This header defines platform data for the DA9055 codec microphone bias configuration.

## Important APIs, Types, and Constants
`enum da9055_micbias_voltage` lists four micbias levels from 1.6 V to 2.2 V. `struct da9055_platform_data` provides two micbias levels, one for each bias output.

## Control Flow
The codec driver reads these values during initialization and programs micbias registers before input paths are used.

## State and Persistence
The pdata is static board configuration. The programmed micbias state is held in codec registers and needs normal PM restore handling.

## Dependencies and Integration Points
It integrates with the DA9055 ASoC codec and board/platform data or firmware parsing.

## Risks and Edge Cases
Unsupported or mismatched micbias settings can break microphones. Because the enum values are direct configuration choices, validation in parser code is important.

## Test Signals
Probe with both micbias outputs configured, capture path enable/disable, and suspend/resume register restore are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/da9055.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/designware_i2s.h -->
# sources/distributed-fs/ceph-client/include/sound/designware_i2s.h

## Purpose
This header defines platform glue structures for Synopsys DesignWare I2S controllers used by ALSA/ASoC drivers.

## Important APIs, Types, and Constants
`struct i2s_clk_config_data` describes channel count, sample rate, and data width. `struct i2s_platform_data` contains capability flags, channel/fifo metadata, clock configuration callback, filter functions for DMA channel acquisition, optional playback/capture DMA data, optional I2S init hook, and quirks. `struct i2s_dma_data` stores DMA address, address width, max burst, and filter data. Constants include DMA register offsets `I2S_RXDMA`/`I2S_TXDMA` and max channel support markers from stereo to 7.1.

## Control Flow
Platform or glue code provides pdata to the DesignWare I2S driver. The driver invokes the init hook, configures clocks using `i2s_clk_cfg`, requests DMA channels using filters/data, and sets channel support/fifo handling based on pdata fields.

## State and Persistence
The structs describe controller capabilities and board wiring; runtime stream state is in the DesignWare driver and hardware registers. DMA channel state is external to this header.

## Dependencies and Integration Points
It depends on `linux/dmaengine.h` and `linux/types.h`. Integration points include DMAengine, ASoC DAI drivers, clock providers, and platform firmware data.

## Risks and Edge Cases
Incorrect FIFO depth or DMA burst/address-width values cause underruns/overruns. Capability flags and channel counts must match IP configuration. Callback pointers should be NULL-safe and must not sleep in inappropriate contexts if called from stream setup paths.

## Test Signals
Playback and capture DMA startup, all advertised channel counts, clock reconfiguration for multiple rates/widths, and underrun/overrun stress tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/designware_i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/dmaengine_pcm.h -->
# sources/distributed-fs/ceph-client/include/sound/dmaengine_pcm.h

## Purpose
This header exposes ALSA/ASoC helper APIs for implementing PCM devices backed by Linux DMAengine channels.

## Important APIs, Types, and Functions
Helpers include `snd_hwparams_to_dma_slave_config()`, `snd_dmaengine_pcm_trigger()`, open/close/sync-stop helpers, channel request/get helpers, config setup from DAI data, hwparams refinement, registration/unregistration, managed registration, and slave-config preparation. `snd_pcm_substream_to_dma_direction()` maps ALSA stream direction to DMA direction. `struct snd_dmaengine_dai_dma_data` describes addr, addr_width, maxburst, slave_id, filter_data, channel name, FIFO size, flags, peripheral config, and peripheral config length. `struct snd_dmaengine_pcm_config` provides callbacks, compatibility filters, channel names, PCM hardware, prealloc sizes, and flags. `struct dmaengine_pcm` embeds the ASoC component and per-stream channels.

## Control Flow
Drivers register a DMAengine PCM component for a device, provide DAI DMA metadata or config callbacks, open substreams to bind DMA channels, refine hwparams, prepare DMA slave config, and call the trigger helper for start/stop/pause/resume. Close paths release or keep channels depending on the helper variant and registration mode.

## State and Persistence
Per-substream runtime state includes the selected DMA channel, prepared slave config, cyclic DMA descriptor state, and ALSA runtime hw constraints. `dmaengine_pcm` persists for the component lifetime. No disk persistence exists.

## Dependencies and Integration Points
It depends on ALSA PCM, ASoC component APIs, and Linux DMAengine. It is a shared integration layer for many SoC audio drivers and DAI drivers.

## Risks and Edge Cases
Direction mapping assumes only playback and capture streams. Flag semantics matter: `SND_DMAENGINE_PCM_FLAG_COMPAT`, `NO_DT`, and `HALF_DUPLEX` change channel acquisition and concurrency. Incorrect `fifo_size`, `maxburst`, or `addr_width` can cause DMA corruption or audio glitches. Channel lifetime differs between `close` and `close_release_chan`.

## Test Signals
Build coverage for users, playback/capture open/close, trigger command matrix, cyclic DMA residue/position behavior, DT and non-DT channel acquisition, half-duplex enforcement, and suspend/resume sync-stop behavior are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/dmaengine_pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu10k1.h -->
# sources/distributed-fs/ceph-client/include/sound/emu10k1.h

## Purpose
This is the main internal ALSA header for Creative EMU10K1/SB Live!/Audigy and E-MU Digital Audio System drivers. It defines PCI and indexed-register maps, hardware bit-field helpers, DSP/voice/memory structures, card capability data, FPGA routing constants, and exported driver-internal entry points.

## Important APIs, Types, and Functions
Macro groups cover PCI registers (`PTR`, `DATA`, `IPR`, `INTE`, `WC`, `HCFG`, AC97, P16V), voice/channel registers, DSP microcode/TRAM/GPR ranges, Audigy-specific registers, E-MU Hana FPGA registers, and E-MU source/destination routing IDs. `SUB_REG*` encodes sub-register metadata; `REG_SHIFT/SIZE/MASK/VAL_*` manipulate those encoded fields. Core types include `snd_emu10k1_voice`, `snd_emu10k1_pcm`, `snd_emu10k1_pcm_mixer`, `snd_emu10k1_memblk`, `snd_emu10k1_fx8010_ctl`, `snd_emu10k1_fx8010_irq`, `snd_emu10k1_fx8010_pcm`, `snd_emu10k1_fx8010`, `snd_emu10k1_midi`, `snd_emu_chip_details`, `snd_emu1010`, and the central `struct snd_emu10k1`.

Exported entry points cover device creation, PCM devices, mixer/timer/FX8010 setup, interrupt handling, voice init/allocation/free, pointer register I/O, SPI/I2C, E-MU FPGA access/routing/clock/firmware, interrupt enable/ack helpers, AC97 access, PM save/restore, memory allocation/mapping, MIDI, procfs, and FX8010 IRQ registration.

## Control Flow
Driver probe calls `snd_emu10k1_create()` with PCI/card details, then creates PCM/mixer/timer/MIDI/FX components depending on card capability flags. Stream startup allocates voices and memory pages, maps them into the hardware page table, programs per-voice registers, enables channel loop/half-loop interrupts, and handles buffer interrupts through the main IRQ path. Capture paths use ADC/MIC/EFX/P16V register groups. E-MU cards additionally load FPGA firmware, configure Hana routing matrices, select word clock/optical modes, and update source/destination mappings.

## State and Persistence
`struct snd_emu10k1` owns nearly all runtime state: PCI port, DMA masks, page tables, mapped memory lists, SPDIF bits, I2C capture settings, FX8010 program/control state, AC97, PCM handles, synth pointer, locks, voices, E-MU routing/clock cache, kcontrols, interrupt callbacks, firmware handles, and PM save buffers. Hardware register state is volatile and explicitly saved/restored under `CONFIG_PM_SLEEP`. Memory blocks persist across stream lifetime and must be unmapped/freed in coordinated order.

## Dependencies and Integration Points
The header pulls ALSA PCM/rawmidi/hwdep/AC97/util_mem/timer APIs, Linux PCI/firmware/io/interrupt/mutex primitives, and UAPI EMU10K1 definitions. It integrates with the ALSA PCI driver, FX8010 DSP hwdep/control interfaces, sequencer/synth support, AC97 codecs, P16V, E-MU FPGA firmware, procfs, and PM.

## Risks and Edge Cases
This file is high-risk hardware code. Register definitions encode real side effects, including comments warning that some legacy or debug bits can cause unstable hardware behavior or destroy chip state. Voice/cache loop handling is timing-sensitive. DMA masks differ between EMU10K1 and Audigy. Lock ordering across `reg_lock`, `emu_lock`, `voice_lock`, `spi_lock`, `i2c_lock`, FX8010 mutexes, and FPGA lock must be preserved. E-MU routing constants overlap by sample-rate mode, so routing tables must account for 1x/2x/4x constraints. PM save buffers must cover all active engines.

## Test Signals
Useful tests include probe on SB Live, Audigy, P16V, and E-MU variants; playback/capture/MIC/EFX/multichannel streams; MIDI I/O; voice allocation exhaustion; loop/half-loop IRQs; FX8010 load/control/IRQ paths; AC97 read/write; suspend/resume with streams and DSP program; E-MU clock-source switching and FPGA routing; and memory allocation/free leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu10k1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu10k1_synth.h -->
# sources/distributed-fs/ceph-client/include/sound/emu10k1_synth.h

## Purpose
This header defines the sequencer device ID and argument block used to bind EMU10K1 hardware to the generic emux wavetable synth layer.

## Important APIs, Types, and Constants
It includes `sound/emu10k1.h` and `sound/emux_synth.h`, defines `SNDRV_SEQ_DEV_ID_EMU10K1_SYNTH`, `EMU10K1_MAX_MEMSIZE`, and `struct snd_emu10k1_synth_arg` containing the EMU chip pointer, sequence ports, maximum voices, and index.

## Control Flow
The EMU10K1 driver passes this argument block when registering a sequencer synth device. The emux layer then calls back into EMU10K1-specific allocation and voice programming routines.

## State and Persistence
The argument struct is setup-time glue. Persistent synth state lives in `struct snd_emu10k1`, emux structures, and allocated sample memory.

## Dependencies and Integration Points
It directly bridges EMU10K1 core driver internals with the ALSA sequencer/emux synth subsystem.

## Risks and Edge Cases
`max_voices` and `seq_ports` must not exceed hardware/emux limits. `EMU10K1_MAX_MEMSIZE` constrains sample memory exposure; mismatches with actual card memory handling can fail sample loading.

## Test Signals
Sequencer device registration, soundfont loading up to memory limits, MIDI note playback, voice exhaustion, and unregister paths validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu10k1_synth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu8000.h -->
# sources/distributed-fs/ceph-client/include/sound/emu8000.h

## Purpose
This header defines the ALSA internal interface for the EMU8000 wavetable synth used on AWE-style cards.

## Important APIs, Types, and Functions
Constants define DRAM size/offset, channel count, DRAM voice count, and RAM transfer modes. `struct snd_emu8000` stores card pointer, index, hardware ports, memory size, emux pointer, raw register cache fields, DRAM-present flag, DMA channels, sequence ports, chorus/reverb/equalizer settings, FM initialization flag, and callbacks. Functions include `snd_emu8000_new()`, register poke helpers, DMA channel selection, FM init, effect/equalizer updates, and user-loadable chorus/reverb effect loaders.

## Control Flow
Card setup calls `snd_emu8000_new()` with port, sequencer port, voice, hardware, memory, and DMA configuration. Synth operation then routes through emux callbacks to program EMU8000 voice registers and DRAM. Effect controls update chorus/reverb/equalizer state and may load user-provided effect data.

## State and Persistence
The `snd_emu8000` struct holds runtime synth hardware state and cached effect parameters. Sample memory is on-board DRAM and volatile. Suspend/resume or reset requires reinitializing hardware and possibly reloading samples/effects.

## Dependencies and Integration Points
It depends on emux synth and sequencer kernel APIs. Integration is with ISA/legacy sound card setup, emux voice allocation, user soundfont loading, and effect controls.

## Risks and Edge Cases
Legacy I/O port programming and DMA channel selection are hardware-sensitive. On-board memory size detection must respect `EMU8000_MAX_DRAM` and offset. User effect loading must validate lengths and user pointers.

## Test Signals
Synth creation, register poke/readback via lower layer, soundfont load/playback, DRAM transfer modes, chorus/reverb/equalizer controls, and teardown should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu8000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu8000_reg.h -->
# sources/distributed-fs/ceph-client/include/sound/emu8000_reg.h

## Purpose
This header maps EMU8000 hardware register operations into readable read/write macros.

## Important APIs, Types, and Constants
It defines port accessors `EMU8000_DATA*()` and `EMU8000_PTR()`, command composition `EMU8000_CMD(reg, chan)`, a full set of `*_READ()` and `*_WRITE()` macros for channel registers, hardware config registers, sample memory address/data registers, envelope/LFO/filter/pitch registers, and initialization registers.

## Control Flow
The EMU8000 implementation uses these macros to route all hardware register I/O through lower-level `snd_emu8000_peek/poke` and word/dword variants. Per-channel operations pass a channel number into command encoding, while global operations pass fixed register IDs.

## State and Persistence
State is entirely in EMU8000 hardware registers and on-board RAM. The macros do not cache state or validate sequencing.

## Dependencies and Integration Points
The macros require a `struct snd_emu8000` pointer and lower-level poke/peek functions declared in `emu8000.h`/implementation. They integrate with voice programming, sample memory transfer, effects, and initialization code.

## Risks and Edge Cases
Macros evaluate arguments directly and perform hardware I/O side effects. Wrong channel/register values program unrelated voice state. There is no locking in the macros, so callers must serialize access around shared hardware ports.

## Test Signals
Unit-style compile coverage, register access smoke tests on hardware/emulator, concurrent voice programming under driver locks, and suspend/resume reprogramming are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emu8000_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emux_legacy.h -->
# sources/distributed-fs/ceph-client/include/sound/emux_legacy.h

## Purpose
This header defines legacy OSS/emux control command numbers and effect identifiers for the ALSA emux synthesizer compatibility layer.

## Important APIs, Types, and Constants
It defines `_EMUX_OSS_*` command IDs for debug, reverb/chorus, chip initialization, effects, channel termination/reset, volume/attenuation, drum/channel modes, release/note-off, pressure, and equalizer controls. Enums define modulation/control targets and raw effect IDs, with `EMUX_NUM_EFFECTS` and effect flag values.

## Control Flow
OSS sequencer compatibility code interprets legacy command IDs and maps them into emux control/effect updates. Effect flags describe whether a raw effect is off, set, or added.

## State and Persistence
The header stores no state. State lives in emux ports, voices, and effect tables maintained by `emux_synth.h` consumers.

## Dependencies and Integration Points
It includes `sound/seq_oss_legacy.h` and is included by `emux_synth.h`. Integration is with ALSA sequencer OSS compatibility and wavetable synth drivers such as EMU8000 and EMU10K1 synth.

## Risks and Edge Cases
Legacy numeric command IDs are ABI-sensitive. Changing values can break OSS applications. Some cooked/raw effect modes are explicitly unsupported or constrained by hardware-specific effect tables.

## Test Signals
OSS sequencer compatibility tests, legacy reverb/chorus/effect ioctl/event handling, channel reset/terminate commands, and ABI value preservation checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emux_legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emux_synth.h -->
# sources/distributed-fs/ceph-client/include/sound/emux_synth.h

## Purpose
This header defines the generic ALSA emux wavetable synthesizer core used by multiple hardware backends.

## Important APIs, Types, and Functions
`struct snd_emux_operators` provides hardware callbacks for owner setup, sample memory reset/load/free, note trigger/release/update/terminate, voice-volume calculation, and optional OSS hooks. `struct snd_emux` is the root object containing card/hw pointers, max voices, voice array, ports, callback table, soundfont list, sequencer client/ports, timers, memory header, proc entry, and OSS synth pointer. `struct snd_emux_port` tracks per-port MIDI channel state, mode, attenuation, drum flags, controls, and optional effect table. `struct snd_emux_voice` tracks each hardware voice, state flags, note/key/velocity, soundfont zone, MIDI channel, port, backend pointer, timing, raw registers, and computed modulation targets. Public functions create/register/free emux instances and lock/unlock/terminate voices.

## Control Flow
Backend drivers allocate `snd_emux`, fill operators and voice limits, then register it with ALSA sequencer. Incoming MIDI/OSS events allocate voices, select soundfont zones, call backend trigger/update callbacks, and later release or terminate voices. Timers manage pending note-offs and voice aging.

## State and Persistence
Emux maintains in-memory synth state: soundfont zones, active voices, ports, MIDI channel state, effect tables, timers, and memory allocation metadata. Hardware sample memory is backend-specific and volatile. There is no disk persistence.

## Dependencies and Integration Points
It depends on ALSA sequencer, soundfont, MIDI emulation, OSS sequencer compatibility, and virtual MIDI APIs. Backends include EMU8000 and EMU10K1 synth drivers.

## Risks and Edge Cases
Voice states combine bit flags and require careful locking to avoid double allocation or stale note release. Raw effect support is conditional. Backend callbacks must tolerate termination during pending note-off timers. OSS modes add compatibility constraints.

## Test Signals
Sequencer registration, MIDI polyphony, sustain/release behavior, voice locking, soundfont load/free, port modes, OSS compatibility, and stress with max voices/ports validate this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/emux_synth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/es1688.h -->
# sources/distributed-fs/ceph-client/include/sound/es1688.h

## Purpose
This header defines the ALSA internal interface and register constants for ESS ES688/ES1688 legacy audio chips.

## Important APIs, Types, and Functions
It defines hardware IDs, `struct snd_es1688` containing ALSA card, I/O resources, MPU port/IRQ, DMA, version/hardware, trigger/dma fields, PCM substreams, and register/mixer locks. Macros map I/O ports and DSP/mixer commands. Exported functions cover mixer write, chip creation, PCM setup, mixer setup, and reset.

## Control Flow
Legacy probe creates a chip with ports/IRQs/DMA, resets it, registers PCM and mixer devices, and uses DSP commands to start/stop DMA. Mixer functions program source/volume registers through mixer address/data ports.

## State and Persistence
Driver state lives in `struct snd_es1688`, including current trigger value and substream pointers. Hardware mixer/DSP registers are volatile and protected by spinlocks.

## Dependencies and Integration Points
It depends on ALSA control/PCM APIs and Linux interrupt types. Integration is with ISA/PNP sound drivers, PCM DMA handling, mixer controls, and optional MPU-401 routing.

## Risks and Edge Cases
Legacy I/O port access has no discovery safety by itself. Register and mixer locks must be used around shared ports. DMA and IRQ values must match hardware resources. Mixer source masks can select invalid capture sources if not validated.

## Test Signals
Reset/probe, playback/capture DMA start-stop, mixer controls, IRQ handling, MPU configuration, and suspend/resume or module unload resource cleanup are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/es1688.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/graph_card.h -->
# sources/distributed-fs/ceph-client/include/sound/graph_card.h

## Purpose
This header exposes ASoC audio graph card parsing helpers for device-tree described audio links, including graph-card2 customization hooks.

## Important APIs, Types, and Functions
`GRAPH2_CUSTOM` is a callback type taking `simple_util_priv`, a link node, and link info. `struct graph2_custom_hooks` allows pre/post hooks and custom handlers for normal, DPCM, and codec-to-codec links. Functions include `audio_graph_parse_of()`, `audio_graph2_parse_of()`, and built-in link parsers for normal, DPCM, and C2C links.

## Control Flow
Machine drivers call parse helpers during probe. The graph parser walks OF graph links, fills simple-card utilities, optionally invokes hooks before/after parsing, and dispatches link nodes to normal/DPCM/C2C handlers.

## State and Persistence
Parsing populates in-memory ASoC card/link structures from device tree. No persistent state is kept in this header.

## Dependencies and Integration Points
It depends on `sound/simple_card_utils.h` and integrates with OF graph bindings, ASoC simple-card infrastructure, DAI link construction, and machine driver customization.

## Risks and Edge Cases
Hook callbacks can override link behavior and must maintain simple-card invariants. Device-tree graph mistakes can produce partial cards or probe deferral. Link-type dispatch must match binding semantics.

## Test Signals
DT binding examples for normal, DPCM, and C2C links; custom hook invocation; probe deferral; and card registration with multiple links are relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/graph_card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/gus.h -->
# sources/distributed-fs/ceph-client/include/sound/gus.h

## Purpose
This is the main ALSA internal header for Gravis UltraSound/GF1-family cards. It defines I/O ports, GF1 registers, memory/DMA/voice/card state, inline port helpers, and exported functions for memory, DMA, mixer, PCM, MIDI, timers, reset, IRQ, and DRAM access.

## Important APIs, Types, and Functions
Macro groups define GUS I/O port offsets, GF1 global and voice registers, ICS mixer devices, LFO modes, DMA flags, volume ranges, memory-owner flags, interrupt-handler flags, and voice types/flags. Core types include `snd_gf1_mem_block`, `snd_gf1_mem`, `snd_gf1_dma_block`, `snd_gus_port`, `snd_gus_voice`, `snd_gf1`, and `snd_gus_card`. Inline helpers select active voice and access the MIDI UART. Exports cover GF1 register I/O, memory allocation/free/init/proc, DMA transfer/suspend, volume/frequency conversion, voice allocation/start/stop/suspend/resume, mixer/PCM/card creation, IRQ handling, rawmidi, DRAM read/write, and timers.

## Control Flow
Card creation initializes hardware resources, memory banks, GF1 voices, DMA queues, mixer, PCM, MIDI, and timers. Playback/synth code allocates voices and GF1 memory blocks, programs voice registers, and handles voice/DMA/timer interrupts. DMA transfers enqueue `snd_gf1_dma_block` objects and acknowledge through callbacks. MIDI UART helpers directly access port registers.

## State and Persistence
`struct snd_gus_card` owns card-wide state, locks, PCM capture position, MIDI substreams, and a nested `snd_gf1` with hardware ports, memory allocator, active voices, timer/MIDI/DMA queues, PCM volume levels, and interrupt callbacks. GUS DRAM/ROM contents and GF1 registers are hardware state; DRAM sample contents are volatile.

## Dependencies and Integration Points
The header depends on ALSA PCM/rawmidi/timer/sequencer APIs and Linux I/O. It integrates with legacy ISA/PNP GUS drivers, GF1 synth/PCM code, raw MIDI, timers, procfs memory reporting, and userspace DRAM read/write operations.

## Risks and Edge Cases
Hardware port access is immediate and requires correct locks around active voice, registers, DMA queues, UART, and PCM volume. Memory sharing uses share IDs and owner classes; incorrect free paths can leak or release active samples. Equal IRQ/DMA and optional codec/ICS/InterWave/ESS flags complicate resource setup. User DRAM read/write must validate addresses and ROM selection.

## Test Signals
Probe across classic GUS/MAX/InterWave/ACE variants, memory allocator ownership/share behavior, DMA transfers for PCM and synth, voice allocation/free, MIDI UART, timers, IRQ profile under stress, DRAM read/write bounds, and suspend/resume are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/gus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda-mlink.h -->
# sources/distributed-fs/ceph-client/include/sound/hda-mlink.h

## Purpose
This header declares Intel HD-audio extended multi-link management helpers used by SOF/HDA systems, with no-op stubs when the feature is disabled.

## Important APIs, Types, and Functions
When `CONFIG_SND_SOC_SOF_HDA_MLINK` is enabled it declares initialization/free, extended-link count, interrupt enable/check, sync period programming, sync prepare/go/check, power up/down, SoundWire sublink helpers, LSDIID get/set, stream-channel mapping, put/reset/resume/suspend, hlink getters for SSP/DMIC/SoundWire, mutex access, offload enable, and ACE3+ microphone privacy helpers. Disabled builds provide inline stubs returning success, false, NULL, or doing nothing.

## Control Flow
HDA/SOF bus setup initializes multi-link state, powers up/down extended links around usage, maps SoundWire stream channels, coordinates synchronization, and handles privacy/offload/link interrupts. Callers can compile unconditionally and rely on stubs if the feature is off.

## State and Persistence
State lives in `struct hdac_bus` and `struct hdac_ext_link` implementation internals. Power/sync/privacy/link state is hardware-backed and must be managed during runtime/system PM. This header stores no state.

## Dependencies and Integration Points
It forward-declares HDA bus/link types and integrates with SOF HDA, SoundWire, SSP, DMIC, HD-audio extended link power management, and microphone privacy controls.

## Risks and Edge Cases
The stub behavior mostly returns success, which can hide disabled-feature paths if callers expect actual hardware action. Functions with `_unlocked` suffix require external locking, and misuse can race link power/sync state. Privacy state is platform-specific and needs careful event handling.

## Test Signals
Builds with config enabled/disabled, link power sequencing, SoundWire stream mapping, sync-go timing, suspend/resume, interrupt handling, offload enable/disable, and mic privacy event tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda-mlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda-sdw-bpt.h -->
# sources/distributed-fs/ceph-client/include/sound/hda-sdw-bpt.h

## Purpose
This header declares the HDA/SoundWire Bulk Payload Transport helper API and disabled-feature stubs.

## Important APIs, Types, and Functions
Enabled builds expose `hda_sdw_bpt_open()`, `hda_sdw_bpt_send_async()`, `hda_sdw_bpt_wait()`, `hda_sdw_bpt_close()`, and `hda_sdw_bpt_get_buf_size_alignment()`. The open/close APIs manage TX/RX `hdac_ext_stream` objects and DMA BDL buffers with byte counts and bandwidth values. Disabled builds warn once and return `-EOPNOTSUPP`, with alignment returning zero.

## Control Flow
Callers open a BPT session for a SoundWire link, launch asynchronous TX/RX transfer, wait for completion, then close and release streams/buffers. Alignment helper lets callers size DMA buffers according to bandwidth requirements.

## State and Persistence
BPT session state is represented by returned HDA extended stream pointers and DMA buffers. It is transient and should not persist beyond open/send/wait/close.

## Dependencies and Integration Points
It depends on `linux/device.h`, forward-declared HDA stream and ALSA DMA buffer types, SOF HDA SoundWire support, and DMA buffer management.

## Risks and Edge Cases
Callers must handle `-EOPNOTSUPP` stubs and avoid using uninitialized stream pointers after failed open. TX/RX bandwidth and buffer sizes must match hardware alignment. Async send requires disciplined wait/close ordering.

## Test Signals
Enabled/disabled build coverage, failed-open cleanup, buffer alignment checks, async completion timeout/error paths, and repeated open/send/wait/close cycles validate the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda-sdw-bpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_chmap.h -->
# sources/distributed-fs/ceph-client/include/sound/hda_chmap.h

## Purpose
This header defines HD-audio HDMI/DisplayPort channel-map support: CEA speaker allocation data, operation callbacks, and helper APIs for channel allocation, mapping, and ALSA controls.

## Important APIs, Types, and Functions
`struct hdac_cea_channel_speaker_allocation` stores CEA channel-allocation index, up to eight speakers, and derived channel count/speaker mask. `struct hdac_chmap_ops` provides overridable callbacks for TLV map generation, validation, speaker allocation lookup, get/set channel map, PCM attachment check, pin slot channel get/set, and channel count programming. `struct hdac_chmap` stores max channels, ops, and hdac device. Functions register ops, compute channel allocation, active channel count, set up mapping, print allocation, map CA to allocation records, convert channel/speaker encodings, and add ALSA channel-map controls.

## Control Flow
HD-audio HDMI codecs register chmap ops, expose controls on PCM devices, validate user channel maps, compute CEA allocation from speaker allocation/channel count/non-PCM status, program converter/pin slot assignments, and report current maps through ALSA TLVs.

## State and Persistence
Current channel maps and speaker allocations are maintained by codec hardware and driver state. `hdac_chmap` persists for the codec/device lifetime. User-selected maps may be runtime control state and need restore across stream prepare/resume as implemented by codec drivers.

## Dependencies and Integration Points
It depends on ALSA PCM and `sound/hdaudio.h`. It integrates with HDMI/DP audio codecs, ELD/speaker allocation, ALSA channel-map controls, and HDA pin/converter programming.

## Risks and Edge Cases
CEA allocation validation is subtle, especially for non-PCM streams and devices with non-standard mapping. Ops callbacks may be partially overridden; defaults must remain coherent. Channel count and slot mapping must be synchronized with stream prepare state to avoid wrong speaker output.

## Test Signals
Channel-map ALSA control tests for 2/6/8 channels, CEA allocation conversion, invalid user maps, non-PCM mode, HDMI ELD speaker masks, and prepare/resume mapping restoration are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/hda_chmap.h -->
