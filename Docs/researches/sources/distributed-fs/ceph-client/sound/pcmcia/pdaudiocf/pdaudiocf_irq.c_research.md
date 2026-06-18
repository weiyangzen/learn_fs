# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_irq.c

## Purpose

This file implements the PDAudioCF interrupt path and the PIO transfer routines that drain captured audio samples from the card SRAM FIFO into ALSA's vmalloc PCM buffer. It separates the hard IRQ status/rate check from the threaded IRQ bulk data movement.

## Important APIs, types, and functions

`pdacf_interrupt()` is the top-half handler. It validates chip status, reads `PDAUDIOCF_REG_ISR`, reports SRAM overrun, decides whether a threaded handler is needed, and asks AK4117 to check rate/errors when in real interrupt context. `pdacf_threaded_irq()` computes available FIFO frames from RDP/WDP, drains them, updates `pcm_tdone` and `pcm_hwptr`, and calls `snd_pcm_period_elapsed()`. `pdacf_transfer()` dispatches to mono/stereo, 16/24/32-bit, little/big-endian, and byte-swapped transfer helpers.

## Control flow

The top half ignores stale, unconfigured, or suspended chips, checks FIFO-level/overrun bits, and wakes the threaded handler only when a PCM substream exists. The threaded handler verifies the capture stream is running, computes FIFO occupancy modulo 64 KiB, leaves slack when more than 64 frames are pending, then copies wrapped regions into the ALSA ring buffer. Period notification is done under `reg_lock` only long enough to update counters; the lock is dropped before ALSA callback entry.

## State and persistence behavior

The transfer path mutates `chip->pcm_tdone`, `pcm_hwptr`, and indirectly the PCM ring buffer at `pcm_area`. Format interpretation comes from state precomputed by `pdaudiocf_pcm.c`: `pcm_sample`, `pcm_frame`, `pcm_channels`, `pcm_little`, `pcm_swab`, and `pcm_xor`. No persistent hardware state is created here beyond clearing FIFO data by reading the MD register.

## Dependencies and integration points

It depends on PCMCIA IRQ threading, raw port I/O, AK4117 rate/error checks, and ALSA PCM period notification. `pdaudiocf_pcm.c` sets the runtime fields this file consumes; the PCMCIA driver registers these handlers. It is tightly coupled to FPGA FIFO word packing documented by the transfer helpers.

## Risks and test signals

Risks include off-by-one FIFO occupancy, endian/sign conversion errors, non-atomic access to PCM state during stop/close, and underrun/overrun handling that logs but continues. Test with all advertised formats (`S16`, `S24_3`, `S32`, LE/BE), mono/stereo capture, ring-buffer wraparound, period interrupt cadence, hot-unplug while IRQs are pending, and forced SRAM overrun diagnostics.
