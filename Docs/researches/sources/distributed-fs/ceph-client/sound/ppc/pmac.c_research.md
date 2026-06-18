# sources/distributed-fs/ceph-client/sound/ppc/pmac.c

## Purpose

This file is the low-level PowerMac sound engine. It detects supported Open Firmware audio devices, maps AWACS/DBDMA resources, manages PCM playback/capture through DBDMA command rings, handles interrupts, exposes common automute controls, controls power/suspend state, and provides beep DMA helpers.

## Important APIs, types, and functions

Exports include `snd_pmac_new()`, `snd_pmac_pcm_new()`, `snd_pmac_rate_index()`, `snd_pmac_beep_dma_start()`, `snd_pmac_beep_dma_stop()`, `snd_pmac_add_automute()`, `snd_pmac_suspend()`, and `snd_pmac_resume()`. Core internals include `snd_pmac_detect()`, `snd_pmac_pcm_prepare()`, `snd_pmac_pcm_trigger()`, `snd_pmac_pcm_update()`, `snd_pmac_pcm_dead_xfer()`, DBDMA alloc/free/reset helpers, and IRQ handlers for TX/RX/control.

## Control flow

`snd_pmac_new()` allocates `struct snd_pmac`, detects model/capabilities/sample rates, allocates DBDMA command buffers, maps MMIO resources, requests control/TX/RX IRQs, enables the platform sound feature, handles PowerBook-specific input latches, resets DBDMA, and registers a low-level ALSA device. PCM prepare builds a circular DBDMA command ring for periods and constrains the opposite stream to the same rate/format. Trigger programs AWACS rate/byteswap and starts/stops DBDMA. TX/RX interrupts scan completed DBDMA commands, recover from `DEAD` transfers with an emergency command, advance periods, and notify ALSA.

## State and persistence behavior

`struct snd_pmac` persists Open Firmware nodes/resources, mapped registers, stream structures, IRQs, DBDMA command memory, active format/rate, feature flags, automute controls, and codec callback pointers. `struct pmac_stream` persists ring command state and current period. Static `emergency_dbdma` and `emergency_in_use` are global recovery state shared by streams.

## Dependencies and integration points

It depends on PCI/mac-io/Open Firmware resource APIs, PowerMac feature calls, DBDMA definitions, ALSA PCM/control APIs, and codec files that install `set_format`, mixer, suspend/resume, and automute callbacks. `powermac.c` calls this file to create the hardware object and later dispatches codec-specific init.

## Risks and test signals

Risks include fragile platform detection, missing resource cleanup on rare map/request failures, DBDMA DEAD recovery loops, global emergency DBDMA contention, half-duplex constraints, hardware byteswap quirks, and suspend/resume ordering with active streams. Test model detection, playback/capture formats and rates, IRQ period cadence, DEAD recovery, open constraints for duplex, hot suspend/resume, and cleanup after partial probe failure.
