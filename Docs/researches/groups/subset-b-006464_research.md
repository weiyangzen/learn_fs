# subset-b-006464 research

Grouped research for:
- `sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670.h`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.c`
- `sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.h`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670.h

## Purpose

`rt5670.h` is the public/private driver contract for the Realtek RT5670/RT5671/RT5672 ALSA SoC codec driver. It defines the codec register map, private register indexes, bit masks, shifts, enum values, exported helper prototypes, and the `struct rt5670_priv` runtime state consumed by `rt5670.c`. The header is not executable on its own; its main role is to keep register programming in the codec implementation readable and consistent across DAPM routes, mixer controls, clock setup, jack detection, GPIO/DMIC pin muxing, DSP/ASRC setup, and suspend/resume handling.

## Important APIs, types, and definitions

The top of the file enumerates normal codec registers such as `RT5670_RESET`, output/input controls, ADC/DAC volume controls, digital mixers, PDM controls, power registers, private-register access registers, serial data port controls, clock/PLL/ASRC controls, jack/IRQ/GPIO controls, and general control registers. These constants are the addresses passed to regmap helpers in `rt5670.c`.

The private register index block defines indirect register numbers used through `RT5670_PRIV_INDEX` and `RT5670_PRIV_DATA`. These include ALC, bias/current, class-D, mixer, wind detection, headphone calibration, EQ, 3D speaker, and dipole-speaker private controls.

Most of the file is grouped by hardware register and provides `*_MASK`, `*_SFT`, and enumerated field values. Important groups include:

- Global mute and stereo volume masks (`RT5670_L_MUTE`, `RT5670_R_MUTE`, `RT5670_L_VOL_MASK`, `RT5670_R_VOL_MASK`).
- Combo jack, input boost, ADC/DAC volume, sidetone, and mixer routing controls.
- Digital interface selection for IF1-IF4, DSP path controls, PDM output controls, I2S master/slave, format, data length, bit clock, and clock dividers.
- Power bits for digital blocks, analog blocks, mixers, volume blocks, PLL, micbias, jack detection, PDM, ADC, and DAC resources.
- Clock and PLL constants including `RT5670_SCLK_SRC_*`, `RT5670_PLL1_SRC_*`, PLL M/N/K masks, and the declared PLL input range.
- ASRC filter clock-source masks and filter-mask enum values used by `rt5670_sel_asrc_clk_src()`.
- DMIC enable/data-pin selectors and GPIO pin mux definitions for GPIO1-GPIO10.
- Jack detection, IRQ polarity/sticky controls, and jack-detection selector values.
- DSP, VAD, EQ, DRC/AGC, scramble, baseback, MP3 plus, 3D HP, HP calibration, soft-volume, and zero-cross controls.

The header exports these callable interfaces:

- `rt5670_sel_asrc_clk_src(struct snd_soc_component *component, unsigned int filter_mask, unsigned int clk_src)` to select ASRC clock sources for one or more filter blocks.
- `rt5670_jack_suspend()` and `rt5670_jack_resume()` for machine/codec integration around jack-detect power state.
- `rt5670_set_jack_detect()` to connect an ASoC jack object to the codec jack-detection flow.
- `rt5670_components()` to return a component-description string derived from DMI/module quirk state.

The key type is `struct rt5670_priv`, which persists per-device state: the component pointer, regmap, jack and optional GPIO jack helper, board quirk outcomes, DMIC pin selections, clock rates and master flags for `RT5670_AIF1` through `RT5670_AIF4`, PLL source/input/output, DSP expected switch/rate, current and saved jack type, and cached DAC mixer/playback switch booleans.

## Control flow

This header contributes symbolic control flow to `rt5670.c`. Probe allocates `struct rt5670_priv`, initializes `regmap`, validates the device ID via `RT5670_VENDOR_ID2`, resets the chip through `RT5670_RESET`, applies register patches, and then uses the register and bitfield constants here to apply DMI/module quirks for GPIO1, IN2 differential mode, DMIC routing, and jack-detect modes. DAI operations use the clock, PLL, I2S, and ASRC definitions when setting system clocks, PLLs, TDM/I2S formats, and hardware parameters. Mixer controls and DAPM events use the mixer, volume, mute, power, and path constants to update individual fields without ad hoc numeric literals.

The ASRC path is represented by filter-mask enum bits, allowing a caller to select one clock source for several filters in one call. Jack-detect control flow uses `jd_mode`, `jack_type`, saved jack state, GPIO/IRQ bits, and the analog/digital jack-detect masks to preserve detection across runtime and suspend/resume paths.

## State and persistence behavior

Register state itself is owned by the hardware and the regmap cache in `rt5670.c`; this header defines the addresses and bit layouts used to mutate it. `struct rt5670_priv` is the persistent software state attached to the I2C client/component for the device lifetime. It caches board configuration and runtime clock/mixer/jack choices so callbacks can reconcile ALSA control state, DAPM state, and hardware programming.

There is no filesystem persistence. State is lost on driver unload or device removal and reconstructed on probe from DMI quirks, module parameter override, ACPI/I2C match data, and default initialization.

## Dependencies and integration points

The declarations depend on ALSA SoC types (`struct snd_soc_component`, `struct snd_soc_jack`, `struct snd_soc_jack_gpio`) and regmap (`struct regmap`). The header is included by `rt5670.c`, which integrates with the I2C bus, regmap, ASoC component/DAI registration, DAPM widgets/routes, ALSA controls, DMI quirks, ACPI IDs, and platform machine drivers. The exported `rt5670_components()` string is intended for machine-driver component matching/description. The jack helpers integrate codec jack reporting with ASoC jack infrastructure and optional GPIO behavior.

## Risks and edge cases

The largest risk is register-field drift. A wrong mask, shift, or register address can silently program the wrong analog path, power block, or GPIO mux and produce hard-to-debug audio or suspend issues. The private register index definitions are especially sensitive because they route through indirect register access. Some definitions expose overlapping or similar bit positions across related registers; updates must verify the comment/register address context before reuse.

Board-quirk state is encoded as combinations of bit definitions consumed by the implementation. Inconsistent DMIC and GPIO pin definitions can cause pinmux conflicts, missing microphone input, or a stuck jack IRQ. Clock and PLL constants influence rate programming; invalid PLL range handling would surface as no audio, bad sample rate, or failed DAI startup. Since this header does not enforce type safety, review should look for regmap writes using masks from the wrong register group.

## Test signals

Useful validation signals include successful compile coverage of `rt5670.c`, probe logs showing the expected RT5670/RT5672 ID, working ASoC card registration, `amixer` visibility for codec controls, playback/capture on each exposed DAI, jack insertion/removal events, suspend/resume jack state retention, DMIC capture on quirked platforms, and regmap/debugfs inspection confirming expected register fields. For changes to this header, targeted hardware tests are more valuable than pure unit tests because most failures require real codec register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.c

## Purpose

`rt5677-spi.c` implements the SPI-side support for the Realtek RT5677 codec DSP. It provides two related services: exported SPI memory access helpers used by the main `rt5677.c` codec driver to load and communicate with DSP memory, and an ASoC component/DAI that exposes a mono 16 kHz S16_LE DSP capture stream backed by the DSP microphone ring buffer. The driver binds as an SPI device named `rt5677spi` and ACPI IDs `10EC5677`/`RT5677AA`.

## Important APIs, types, and functions

The exported symbols are:

- `rt5677_spi_read(u32 addr, void *rxbuf, size_t len)` reads DSP address space over SPI. Both address and length must be 4-byte aligned.
- `rt5677_spi_write(u32 addr, const void *txbuf, size_t len)` writes DSP address space over SPI. The address must be 4-byte aligned; non-4-byte length is padded with zero bytes for the final transfer.
- `rt5677_spi_write_firmware(u32 addr, const struct firmware *fw)` writes firmware contents by delegating to `rt5677_spi_write()`.
- `rt5677_spi_hotword_detected(void)` is called by the main codec interrupt/event path when the DSP reports a hotword; it marks the next capture copy as a fresh hotword and schedules immediate buffer draining.

The local `struct rt5677_dsp` stores the ASoC/SPI capture state: device pointer, delayed copy work, `dma_lock`, active PCM substream pointer, current runtime DMA write offset, bytes accumulated toward the next ALSA period, the DSP microphone-buffer read offset, and a `new_hotword` flag.

The ASoC-facing pieces are `rt5677_spi_pcm_hardware`, `rt5677_spi_dai`, and `rt5677_spi_dai_component`. The PCM is capture-only, mono, S16_LE, fixed at 16 kHz, with eight periods and a maximum buffer size matching the DSP buffer size. Component callbacks implement open, close, hw_params, hw_free, prepare, pointer, pcm_new, and probe.

The SPI transfer helpers are:

- `rt5677_spi_select_cmd()` chooses 32-bit or burst read/write commands based on 8-byte alignment and remaining length.
- `rt5677_spi_reverse()` reverses byte order per transfer word because SPI address/data phases are MSB-first while the DSP CPU memory is little-endian.
- The file-level `g_spi` pointer and `spi_mutex` serialize access to the single bound SPI device.

## Control flow

Probe stores the matched `spi_device` in `g_spi` and registers the ASoC component and one DAI via `devm_snd_soc_register_component()`. Component probe allocates `struct rt5677_dsp`, initializes `dma_lock` and delayed work, then stores the DSP state as component driver data. `pcm_new` asks ALSA to allocate managed vmalloc buffers.

Capture setup starts when ALSA opens and configures the DSP capture stream. `open` installs the hardware constraints. `hw_params` records the active substream under `dma_lock`; `hw_free` clears it. `prepare` looks up the main `rt5677` codec component in the runtime, calls `rt5677->set_dsp_vad(..., true)` to enable DSP VAD, resets the runtime DMA offset, and clears accumulated period bytes. `close` cancels pending copy work and disables DSP VAD through the same callback.

Hotword flow starts in `rt5677.c`, which calls `rt5677_spi_hotword_detected()`. That function gets `struct rt5677_dsp` from the SPI device, marks `new_hotword`, and schedules `copy_work` immediately. The work function locks `dma_lock`, verifies an active substream, reads the DSP write pointer from `RT5677_MIC_BUF_ADDR`, and if this is the first read for the hotword, starts reading two seconds back (`RT5677_MIC_BUF_FIRST_READ_SIZE`) from the current DSP write offset. It computes the unread byte count in the DSP ring buffer, copies data into the ALSA DMA buffer one period at a time, calls `snd_pcm_period_elapsed()` when a period is filled, and reschedules itself based on the current period duration.

SPI read/write flow uses the selected command to construct a 5-byte command/address header. Reads use a two-transfer SPI message: header plus four dummy bytes, then an RX body up to 240 bytes. Writes use a single TX buffer containing the header, reversed data body, and a dummy byte. Both loops update the offset by the selected transfer length and serialize `spi_sync()` with `spi_mutex`.

## State and persistence behavior

All state is in memory. `g_spi` is a module-global pointer to the single active SPI device and is required by exported helpers; no remove callback clears it in this file. `spi_mutex` protects concurrent SPI transactions from exported read/write callers and the PCM copy worker. `rt5677_dsp` persists for the component lifetime through devm allocation. The active PCM substream, DMA offset, period accumulation, DSP mic read offset, and `new_hotword` are runtime-only state protected by `dma_lock`.

The DSP microphone ring buffer layout is fixed by constants: `RT5677_MIC_BUF_ADDR` contains a four-byte write pointer followed by `RT5677_MIC_BUF_BYTES` of audio data, with `RT5677_BUF_BYTES_TOTAL` total bytes. `RT5677_MODEL_ADDR` is defined but not used in this file. Firmware bytes are not persisted by this driver; firmware loading is delegated from `rt5677.c` through exported write helpers.

## Dependencies and integration points

This file depends on Linux SPI, firmware, workqueue, mutex, module, ACPI, and ALSA SoC/PCM APIs. It includes `rt5677.h` for `struct rt5677_priv` and `set_dsp_vad`, and `rt5677-spi.h` for the exported helper declarations. It is built only when `CONFIG_SND_SOC_RT5677_SPI` is enabled (`snd-soc-rt5677-spi.o` in the codec Makefile). The main codec driver integrates by calling `rt5677_spi_write()` while parsing/loading DSP firmware and by calling `rt5677_spi_hotword_detected()` from the DSP interrupt/hotword path. The ASoC machine link sees the registered SPI component/DAI, whose actual DAI name follows the SPI device name because legacy DAI naming is enabled.

## Risks and edge cases

The exported helpers depend on `g_spi`; calls before probe return `-ENODEV`, but a missing remove cleanup could leave stale assumptions if the device is unbound while callers still exist. SPI status is accumulated with bitwise OR across transfers, which preserves nonzero failure but can obscure the original negative errno if multiple errors occur. `rt5677_spi_read()` copies from the body buffer after `spi_sync()` even if the transfer failed, although the failure status is returned.

Alignment and length handling are critical. Reads reject non-4-byte-aligned lengths, while writes pad the tail. `rt5677_spi_select_cmd()` may choose a 4-byte transfer when fewer than four bytes remain, relying on read alignment or write padding. Burst transfers are rounded up to 8-byte multiples and capped at 240 bytes. Any mismatch with the DSP SPI protocol can corrupt firmware or captured audio.

The PCM copy path assumes the DSP write pointer is sane after subtracting the four-byte header; invalid pointers return `-EFAULT` and stop the work. If no new data arrives, the worker still schedules based on period duration after a hotword only when it reaches the scheduling path. The delay calculation uses integer seconds (`bytes_to_frames(period_bytes) / runtime->rate`) and then `secs_to_jiffies()`, so common 16 kHz period sizes under one second can produce a zero-delay reschedule; this is worth inspecting for CPU churn or immediate requeue behavior. The copy code intentionally drops old data when the incoming chunk exceeds the ALSA buffer minus one frame.

## Test signals

Build coverage should include both `CONFIG_SND_SOC_RT5677_SPI=y/m` and disabled configurations with users of `rt5677-spi.h`. Runtime signals include successful SPI probe, ASoC component/DAI registration, DSP firmware loading through `rt5677_spi_write()`, hotword logs, creation of a `DSP Capture` PCM stream, monotonic PCM pointer movement, period-elapsed notifications, and valid mono 16 kHz S16_LE audio around a hotword. Fault-injection targets include unaligned read/write calls, no-SPI-device calls, invalid DSP write pointer, SPI transfer failure, open/close while copy work is queued, and ring-buffer wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.h

## Purpose

`rt5677-spi.h` is the small integration header between the main RT5677 codec driver and the optional SPI DSP support module. It declares the SPI memory access and hotword notification helpers when `CONFIG_SND_SOC_RT5677_SPI` is enabled, and provides harmless fallback stubs when that support is disabled.

## Important APIs and definitions

When `IS_ENABLED(CONFIG_SND_SOC_RT5677_SPI)` is true, the header declares:

- `rt5677_spi_read(u32 addr, void *rxbuf, size_t len)` for aligned DSP memory reads.
- `rt5677_spi_write(u32 addr, const void *txbuf, size_t len)` for DSP memory writes.
- `rt5677_spi_write_firmware(u32 addr, const struct firmware *fw)` for writing firmware contents to a DSP physical address.
- `rt5677_spi_hotword_detected(void)` for notifying the SPI PCM bridge that DSP hotword audio should be copied.

When the config is disabled, the read/write/firmware helpers are static inline functions returning `-EINVAL`, and `rt5677_spi_hotword_detected()` is an empty inline function. This lets `rt5677.c` compile without preprocessor conditionals around every call site, while still making runtime attempts fail clearly for operations that require SPI support.

## Control flow

There is no standalone runtime control flow in the header. Compile-time configuration selects either external symbol declarations implemented by `rt5677-spi.c` or local inline fallback bodies. Callers such as DSP firmware loading and hotword interrupt handling in `rt5677.c` can call the helpers unconditionally. With SPI enabled, those calls cross into the SPI driver. With SPI disabled, memory-access calls return failure immediately and hotword notification becomes a no-op.

## State and persistence behavior

The header stores no state. State lives in `rt5677-spi.c` (`g_spi`, `struct rt5677_dsp`, copy work, PCM offsets) or in the main codec private data. The fallback stubs do not persist anything and do not mutate caller buffers.

## Dependencies and integration points

The prototypes use kernel fixed-width type `u32`, `size_t`, and `struct firmware`; including files must have appropriate kernel type declarations available through surrounding includes. The compile-time gate uses `IS_ENABLED()` and `CONFIG_SND_SOC_RT5677_SPI`. The main integration point is `rt5677.c`, which includes this header for DSP firmware loading and hotword notification, while the SPI implementation includes the same header to match exported signatures.

## Risks and edge cases

The fallback return value is `-EINVAL`, not `-ENODEV` or `-EOPNOTSUPP`, so callers need to treat it as a generic failure rather than a precise absence-of-device signal. The empty hotword fallback intentionally drops hotword notifications when SPI support is disabled. Because the header only declares behavior and does not document alignment requirements, callers must rely on `rt5677-spi.c` semantics: reads require 4-byte aligned address and length, and writes require 4-byte aligned address with zero padding for tail bytes.

## Test signals

Compile both enabled and disabled configurations. In the enabled configuration, `rt5677-spi.c` must provide all exported symbols and the main codec should load/link cleanly. In the disabled configuration, `rt5677.c` should still compile, firmware load paths should see `-EINVAL` if they attempt SPI transfer, and hotword notification should not dereference any SPI state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.h -->
