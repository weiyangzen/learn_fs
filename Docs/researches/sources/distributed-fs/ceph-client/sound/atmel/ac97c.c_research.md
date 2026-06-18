# sources/distributed-fs/ceph-client/sound/atmel/ac97c.c

## Purpose
This file implements the ALSA driver for the Atmel AT91 AC97C controller. It registers an ALSA card, AC97 bus/mixer, and PCM device, uses the Atmel PDC DMA engine registers for period transfers, handles AC97 codec-channel access, and services channel events in an IRQ handler.

## Important APIs, Types, And Functions
The platform driver entry points are `atmel_ac97c_probe()`, `atmel_ac97c_remove()`, and simple PM suspend/resume callbacks. AC97 bus callbacks are `atmel_ac97c_write()` and `atmel_ac97c_read()`. PCM operations are split for playback and capture: open/close, `hw_params`, prepare, trigger, and pointer callbacks. `atmel_ac97c_interrupt()` handles channel A playback/capture period events and codec-channel events. `atmel_ac97c_pcm_new()`, `atmel_ac97c_mixer_new()`, and `atmel_ac97c_reset()` set up ALSA and hardware state.

## Control Flow
Probe obtains MMIO and IRQ resources, enables the peripheral clock, allocates an ALSA card with private `struct atmel_ac97c`, requests IRQ, maps registers, optionally gets an AC97 reset GPIO, resets the controller/codec, enables codec-channel overrun interrupt, creates AC97 bus and mixer, assigns AC97 PCM slots, creates playback/capture PCM streams with managed DMA buffer, registers the card, and stores driver data. Open increments a global opened count under `opened_mutex`, installs hardware constraints, and pins rate/format to any currently active duplex stream. `hw_params()` records current rate/format. Prepare assigns AC97 slots, programs channel A mode/endian/DMA/event bits, sets VRA and codec rate, and primes current/next PDC descriptors. Trigger enables or disables PDC TX/RX and channel A. IRQ handles ENDTX/ENDRX by advancing period counters, loading next PDC descriptors, and notifying ALSA.

## State And Persistence
`struct atmel_ac97c` persists clock/device/card/PCM/AC97 objects, current duplex format and rate, period indices, MMIO, IRQ, open count, and reset GPIO. The global `opened_mutex` serializes open-count and current format/rate updates. PDC current/next pointer/count registers persist hardware DMA state across interrupts until stopped or reprogrammed.

## Dependencies And Integration Points
The driver depends on platform devices, AT91 PDC register definitions, clocks, GPIO descriptors, ALSA core/PCM/AC97, and local `ac97c.h` register macros. It integrates with device tree compatible `atmel,at91sam9263-ac97c`, AC97 mixer/PCM assignment, and ALSA managed DMA buffers.

## Risks And Test Signals
The driver shares one channel A between playback and capture, so joint-duplex format/rate pinning and `opened` accounting are important. IRQ code dereferences playback/capture substreams when ENDTX/ENDRX bits are enabled, so tests should stop streams while interrupts are pending. Period size is fixed at 4096 bytes and PDC counts use `block_size / 2`, making format/channel assumptions worth validating. Test signals include codec read/write timeouts, successful variable-rate programming, PDC descriptor cycling for all periods, overrun/underrun event logging, clean probe failure unwinds, suspend/resume clock behavior, and GPIO reset fallback.
