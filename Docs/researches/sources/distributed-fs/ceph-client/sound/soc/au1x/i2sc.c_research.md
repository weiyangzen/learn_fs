# sources/distributed-fs/ceph-client/sound/soc/au1x/i2sc.c

## Purpose
ASoC CPU DAI for the older Au1000/Au1500/Au1100 I2S controller. It configures the controller format, clock inversion, sample width, and direction-specific FIFO enable bits, and passes legacy DMA IDs to the PCM DMA component.

## Important APIs, Types, And Functions
- Uses `struct au1xpsc_audio_data` for MMIO/config/DMA IDs.
- `au1xi2s_set_fmt()` maps ASoC I2S/MSB/LSB and inversion flags into controller CFG bits; it only accepts CPU bit/frame-clock provider mode.
- `au1xi2s_hw_params()` maps sample bit widths 8/16/18/20/24 through `msbits_to_reg`.
- `au1xi2s_trigger()` powers the block on/off and toggles TX/RX FIFO enables.
- Probe maps MEM, reads DMA resources, and registers DAI/component.

## Control Flow
Probe maps controller registers and records DMA IDs. Startup attaches DMA data. `set_fmt` updates the cached config. `hw_params` updates sample-size bits. Trigger start enables clock/controller and writes the cached config with the relevant FIFO enabled; stop clears that FIFO and disables the block.

## State And Persistence
Format and sample size are cached in `ctx->cfg`. There is no hardware configuration until trigger start. Suspend/remove disables the controller.

## Dependencies And Integration Points
Integrates with `alchemy-pcm-dma` and older Alchemy platform MEM/DMA resources. Platform driver name is `alchemy-i2sc`.

## Risks
Requires the I2S controller to provide clocks and an external clock at 256x sample rate. Powering off on any stop may affect simultaneous opposite-direction streams. Format naming maps MSB to right-justified and LSB to left-justified per hardware bits, which is easy to misread.

## Test Signals
Format/inversion rejection tests, sample-width programming, DMA ID handoff, playback/capture trigger sequencing, suspend disabling clock, and full-duplex stop behavior.
