# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/msiof.c

## Purpose

`msiof.c` is a standalone ASoC platform driver that uses the R-Car MSIOF SPI-oriented hardware as an I2S-like audio interface on Gen4. It is separate from the `rsnd` module graph and supports DMAEngine playback/capture in clock/frame consumer mode only.

## Important APIs, types, and functions

`struct msiof_priv` stores device/MMIO/reset state, active substreams, a spinlock, physical base address, active stream count, error counters, and format flags. `msiof_probe()` validates sound-mode graph presence, maps MMIO, gets reset and IRQ, asserts reset, registers the IRQ handler, enables runtime PM, and registers the component plus one DAI. `msiof_dai_set_fmt()` accepts only clock/frame consumer mode, NB_NF polarity, and I2S or left-justified format. Component callbacks implement DMA open/close, PCM buffer preallocation, `hw_params` DMA slave config, trigger start/stop, and DMA pointer. `msiof_hw_start()` and `msiof_hw_stop()` program MSIOF registers and reset state. `msiof_interrupt()` records FIFO/frame-sync errors.

## Control Flow

Open requests the `rx` or `tx` DMA channel and opens DMAEngine PCM. `hw_params` converts ALSA params to DMA slave config and points DMA to `SITFDR`/`SIRFDR`. Trigger start records the active substream, deasserts reset for the first user, starts DMA, programs both TX and RX mode registers to avoid cross-direction FSERR, enables DMA/error interrupts for the target direction, clears status, and enables TXE or RXE. Trigger stop disables interrupts, clears TXE/RXE, stops DMA, logs accumulated errors, decrements the active count, and asserts reset when both directions are idle.

## State and Persistence Behavior

The driver persists active substream pointers under `priv->lock`, shared reset state through `count`, per-direction error counters, and the I2S data-delay flag. It deliberately ignores the first FSERR by initializing `err_syc` to `-1` on start and normalizing it on stop. It does not stop streams on error currently; `snd_pcm_stop_xrun()` calls are commented out and errors are counted/logged.

## Dependencies and Integration Points

It depends on `linux/spi/sh_msiof.h` register definitions, OF graph to distinguish sound mode from SPI mode, OF DMA channel names `rx` and `tx`, reset controls, DMAEngine PCM helpers, and ASoC component/DAI registration. It exposes a simple `msiof-dai` with 2-channel 16/32-bit audio and symmetric rate/channel/sample bits.

## Risks and Test Signals

Risks are inherent in consumer-clock operation: unavoidable FSERR windows, possible R/L capture reversal, no 24-bit format due to missing data shift, and unsupported provider mode. Other risks include reset coordination for full-duplex, not stopping on hardware errors, DMA channel leaks on open failure, and register updates while clocks are present. Tests should cover I2S and left-justified formats, playback/capture/full-duplex start-stop loops, suspend/resume-like reset cycles, DMA pointer movement, error-counter logging, and rejection of provider/inverted/24-bit configurations.
