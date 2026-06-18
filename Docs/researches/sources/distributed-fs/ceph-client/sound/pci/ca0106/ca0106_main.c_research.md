# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_main.c

## Purpose

`ca0106_main.c` is the main ALSA PCI driver for Creative CA0106-based cards such as Audigy LS, Live 24-bit, Audigy SE, X-Fi Extreme Audio, and several onboard variants. It owns PCI probing, chip identification, low-level pointer register access, SPI/I2C helper implementations, PCM playback/capture devices, DMA period-list setup, interrupt handling, MIDI initialization, chip initialization/stop, and suspend/resume.

## Important APIs, Types, and Functions

The driver uses `struct snd_ca0106` from `ca0106.h` as its central state. `ca0106_chip_details[]` maps subsystem serials to board names and capability flags: AC97 presence, GPIO type, I2C ADC, and SPI DAC channel map.

`snd_ca0106_ptr_read()` and `snd_ca0106_ptr_write()` are the fundamental indexed-register accessors, serializing `CA0106_PTR`/`CA0106_DATA` cycles with `emu_lock`. `snd_ca0106_spi_write()` writes 16-bit SPI DAC commands and polls completion. `snd_ca0106_i2c_write()` writes ADC register/value pairs through the I2C engine with retry/abort handling.

PCM code is split by logical stereo pairs: front, rear, center/LFE, and side/unknown. Playback/capture open functions allocate `struct snd_ca0106_pcm`, bind channel state, set hardware constraints, and power SPI DACs for non-front playback channels. Prepare functions program rates, formats, DMA addresses, period lists, and buffer pointers. Trigger functions update `BASIC_INTERRUPT` and `EXTENDED_INT_MASK`. Pointer callbacks read hardware pointer registers.

Probe/setup functions include `snd_ca0106_create()`, `ca0106_init_chip()`, `ca0106_stop_chip()`, `snd_ca0106_pcm()`, `snd_ca0106_ac97()`, `snd_ca0106_midi()`, `__snd_ca0106_probe()`, and `snd_ca0106_probe()`.

## Control Flow

Probe allocates an ALSA card, enables PCI, sets a 32-bit DMA mask, requests BARs, records the I/O port, requests a shared IRQ, allocates a 1024-byte DMA buffer for playback period tables, enables bus mastering, reads subsystem IDs, selects board details, initializes the chip, creates four PCM devices, optionally creates an AC97 mixer, creates CA0106 mixer controls, initializes MIDI UART A, optionally initializes procfs diagnostics, registers the card, and stores driver data.

Chip initialization disables interrupts, initializes SPDIF status words, mutes playback/capture paths, configures SPDIF/analog routing, capture feedback, routing registers, capture source defaults, GPIO mode, base interrupt enables, HCFG audio enable, optional I2C ADC register defaults and cached volumes, and optional SPI DAC defaults plus front DAC power-up.

Playback prepare writes a per-channel period table into the shared DMA table buffer, sets rate fields in `BASIC_INTERRUPT` and `CAPTURE_CONTROL`, sets global S16/S32 HCFG playback format, writes playback list/address/size/pointer registers, and unmutes output. Capture prepare sets capture rate/format, updates I2C oversampling for ADC boards, and writes capture DMA address/size/pointer.

Playback trigger walks all linked playback substreams in the sync group, sets their running state, accumulates channel start and period interrupt bits, and then updates hardware once. Capture trigger handles a single channel. The IRQ handler reads `CA0106_IPR` and `EXTENDED_INT`, calls `snd_pcm_period_elapsed()` for active playback/capture channels whose extended bits fired, delegates MIDI A interrupts through `ca_midi`, acknowledges extended and global interrupt status, and returns shared IRQ status.

Suspend changes power state, suspends AC97 if present, saves mixer volumes, stops the chip, and resume reinitializes hardware, resumes AC97, restores mixer state, rewrites SPI registers, and returns to D0.

## State and Persistence Behavior

The driver caches board identity, SPDIF defaults and stream bits, capture source selections, I2C volumes, SPI DAC register images, channel use/running state, and PM volume snapshots. The playback period table DMA buffer is persistent for the card lifetime and partitioned per channel. Runtime PCM private data is allocated per open substream and freed through `runtime->private_free`.

Some hardware settings are global despite per-channel APIs, including HCFG S32 playback/capture bits and parts of rate programming. SPI DAC power is managed on playback open/close to reduce power, with front kept powered.

## Dependencies and Integration Points

The file integrates with ALSA core, PCM, AC97, procfs, PCI, DMA mapping, interrupts, PM, and the shared `ca_midi` helper. It depends heavily on `ca0106.h` register definitions and calls mixer/proc functions implemented in sibling files.

## Risks and Edge Cases

Known comments mention unload stability problems, incomplete capture channel coverage, limited capture rates, and global format conflicts. `snd_ca0106_midi()` appears to set MIDI A `rx_enable` to `INTE_MIDI_TX_B`, which is suspicious because receive status uses `IPR_MIDI_RX_A`. `snd_ca0106_i2c_write()` has a cumulative timeout counter across retries. Playback prepare writes `PLAYBACK_PERIOD_SIZE` twice, ending with zero, which is intentional or experimental but fragile. Concurrent streams at different rates/formats can race global register fields.

## Test Signals

Validate probe across supported subsystem IDs and forced `subsystem=`. Test four PCM devices, sync-start grouped playback, period interrupts, pointer stability warnings, S16/S32 formats, 48/96/192 kHz playback and capture, SPDIF AC3/DTS routing, analog output on SPI and non-SPI boards, I2C ADC capture source and oversampling, AC97 boards, MIDI UART A RX/TX, module unload, and suspend/resume with mixer/SPI/SPDIF state restored.
