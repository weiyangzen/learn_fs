# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.c

## Purpose
This file implements the Atmel SSC ASoC CPU DAI. It configures SSC serial audio timing for I2S, left-justified, and DSP_A formats, coordinates playback/capture direction ownership, supplies DMA/PDC parameters to PCM transports, handles SSC interrupts, and exports `atmel_ssc_set_audio()` for machine drivers.

## Important APIs, Types, And Functions
Key static data includes PDC register descriptors, TX/RX masks, `ssc_dma_params[NUM_SSC_DEVICES][2]`, and `ssc_info[NUM_SSC_DEVICES]`. Important functions are `atmel_ssc_interrupt()`, `atmel_ssc_hw_rule_rate()`, `atmel_ssc_startup()`, `atmel_ssc_shutdown()`, `atmel_ssc_set_dai_fmt()`, `atmel_ssc_set_dai_clkdiv()`, `atmel_ssc_hw_params()`, `atmel_ssc_prepare()`, `atmel_ssc_trigger()`, `atmel_ssc_suspend()`, `atmel_ssc_resume()`, `asoc_ssc_init()`, `atmel_ssc_set_audio()`, and `atmel_ssc_put_audio()`.

## Control Flow
Machine drivers call `atmel_ssc_set_audio(id)`, which requests an SSC device and registers the DAI plus either DMAengine or PDC PCM based on `ssc->pdata->use_dma`. Startup enables the SSC clock, resets hardware if needed, installs a rate hw-rule, assigns per-direction DMA params, and enforces one substream per direction. `hw_params` computes BCLK/frame dividers, sample size, PDC transfer size, clock/frame mode registers, and format registers; it requests the SSC IRQ on first initialization and writes CMR/RCMR/RFMR/TCMR/TFMR. Trigger writes SSC enable/disable commands. The IRQ handler masks status with IMR and calls the PCM transport's registered `dma_intr_handler` for endx/endbuf events.

## State And Persistence
Persistent state is global per SSC ID: requested SSC device, direction mask, initialized flag, DAI format, dividers, forced-divider bitmap, DMA params, saved suspend registers, and master clock rate. Hardware state includes SSC clock mode, receive/transmit clock and frame mode registers, interrupt masks, PDC registers, and CR enable/disable state.

## Dependencies And Integration Points
It depends on `linux/atmel-ssc.h`, `linux/atmel_pdc.h`, `atmel-pcm.h`, and machine drivers such as `atmel_wm8904.c`. It exports symbols to allow board drivers to allocate/release SSC audio use.

## Risks And Test Signals
Risk areas include global arrays limited to three SSC devices, divider conflicts between simultaneous playback/capture, request/free IRQ lifecycle, uncommon slave-clock rate rules, and format limitations. Test signals are machine-driver probe with each SSC ID, I2S/LJ/DSP_A playback and capture, suspend/resume restoring registers, PDC and DMA modes receiving interrupts, and correct `-EBUSY` for direction conflicts.
