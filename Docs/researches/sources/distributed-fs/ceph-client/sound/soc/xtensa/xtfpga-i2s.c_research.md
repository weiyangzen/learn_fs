# sources/distributed-fs/ceph-client/sound/soc/xtensa/xtfpga-i2s.c

## Purpose
ASoC I2S master and PIO PCM driver for Cadence/Xtensa XTFPGA I2S hardware. It provides playback-only FIFO feeding, interrupt-driven period notification, runtime PM clock control, and DAI format/hw_params setup.

## Important APIs, Types, and Functions
Driver state is `struct xtfpga_i2s`. Generated FIFO writers are `xtfpga_pcm_tx_1x16()`, `xtfpga_pcm_tx_2x16()`, `xtfpga_pcm_tx_1x32()`, and `xtfpga_pcm_tx_2x32()`. Key helpers/callbacks include `xtfpga_pcm_push_tx()`, `xtfpga_pcm_refill_fifo()`, `xtfpga_i2s_threaded_irq_handler()`, DAI callbacks `xtfpga_i2s_startup()`, `xtfpga_i2s_hw_params()`, `xtfpga_i2s_set_fmt()`, PCM callbacks `xtfpga_pcm_open()`, `xtfpga_pcm_close()`, `xtfpga_pcm_hw_params()`, `xtfpga_pcm_trigger()`, `xtfpga_pcm_pointer()`, `xtfpga_pcm_new()`, runtime PM callbacks, and platform probe/remove.

## Control Flow, State, and Persistence
Probe maps registers, creates a regmap, gets the clock, initializes config/status/mask registers, requests a threaded shared IRQ, registers component/DAI, and enables runtime PM. DAI hw_params sets sample resolution, programs MCLK to 256 * rate, computes I2S clock ratio, and chooses FIFO interrupt watermarks based on period size. PCM hw_params selects the PIO writer for channel count and format. Trigger start resets `tx_ptr`, publishes the substream with RCU, and refills the FIFO; stop clears the RCU pointer. IRQ handling validates enabled status, estimates FIFO level from level/underrun bits, calls `snd_pcm_period_elapsed()`, refills FIFO, adjusts interrupt masks, and toggles TX/IRQ enable. Close uses `synchronize_rcu()` before userspace can free stream state.

## Dependencies and Integration Points
Depends on ALSA SoC DAI/component/PCM APIs, Linux regmap MMIO, clocks, IRQs, runtime PM, and OF platform matching. It uses managed PCM buffers but transfers samples by programmed I/O rather than DMA.

## Risks and Test Signals
Risks include PIO throughput limits, approximate FIFO level accounting, interrupt masking complexity around underrun recovery, no capture support, RCU pointer correctness, and ratio math relying on supported 16/32-bit mono/stereo formats. Test signals are runtime PM clock balance, 8-96 kHz playback, mono/stereo 16/32-bit FIFO writes, underrun recovery, period elapsed cadence, pointer wrap behavior, and remove clearing config/interrupt registers.
