# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677-spi.c

## Purpose

`rt5677-spi.c` implements the SPI-side support for the Realtek RT5677 codec DSP. It provides two related services: exported SPI memory access helpers used by the main `rt5677.c` codec driver to load and communicate with DSP memory, and an ASoC component/DAI that exposes a mono 16 kHz S16_LE DSP capture stream backed by the DSP microphone ring buffer. The driver binds as an SPI device named `rt5677spi` and ACPI IDs `10EC5677`/`RT5677AA`.

## Important APIs, types, and functions

The exported symbols are `rt5677_spi_read(u32 addr, void *rxbuf, size_t len)`, `rt5677_spi_write(u32 addr, const void *txbuf, size_t len)`, `rt5677_spi_write_firmware(u32 addr, const struct firmware *fw)`, and `rt5677_spi_hotword_detected(void)`. Reads require a 4-byte-aligned address and length. Writes require a 4-byte-aligned address and pad a non-4-byte tail with zero bytes. Firmware writes delegate to the normal write helper. Hotword notification marks the next capture copy as a fresh hotword and schedules immediate buffer draining.

The local `struct rt5677_dsp` stores the ASoC/SPI capture state: device pointer, delayed copy work, `dma_lock`, active PCM substream pointer, current runtime DMA write offset, bytes accumulated toward the next ALSA period, the DSP microphone-buffer read offset, and a `new_hotword` flag. The ASoC-facing pieces are `rt5677_spi_pcm_hardware`, `rt5677_spi_dai`, and `rt5677_spi_dai_component`. The PCM is capture-only, mono, S16_LE, fixed at 16 kHz, with eight periods and a maximum buffer size matching the DSP buffer size.

The SPI transfer helpers are `rt5677_spi_select_cmd()`, which chooses 32-bit or burst read/write commands based on 8-byte alignment and remaining length, and `rt5677_spi_reverse()`, which reverses byte order per transfer word because SPI address/data phases are MSB-first while the DSP CPU memory is little-endian. The file-level `g_spi` pointer and `spi_mutex` serialize access to the single bound SPI device.

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
