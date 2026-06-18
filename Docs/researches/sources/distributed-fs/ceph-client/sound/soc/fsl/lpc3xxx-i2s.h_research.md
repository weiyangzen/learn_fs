# sources/distributed-fs/ceph-client/sound/soc/fsl/lpc3xxx-i2s.h

## Purpose
Register and private-state header for the LPC3xxx/LPC32xx I2S driver.

## APIs, Types, and Functions
Defines register offsets for DAO/DAI, TX/RX FIFOs, status, DMA controls, IRQ, and TX/RX rate registers. Defines control bits for word width, half-period word select, mono, stop/reset, and DMA thresholds. `struct lpc3xxx_i2s_info` stores device, clock, regmap, DMA configs, base clock rate, requested frequency, stream-in-use mask, and mutex. Declares `lpc3xxx_pcm_register()`.

## Control Flow, State, and Persistence
The header has no control flow; it declares the state persisted by `lpc3xxx-i2s.c` across probe and active streams. DMA config fields are initialized at probe and consumed by DAI DMA setup.

## Dependencies and Integration
Used by `lpc3xxx-i2s.c` and `lpc3xxx-pcm.c`. Depends on regmap, clk, mutex, and `snd_dmaengine_dai_dma_data` types.

## Risks and Test Signals
Risks are stale register offsets/bit masks, especially DMA0/DMA1 naming for TX/RX depth fields, and state-field misuse without holding the mutex. Test signals are compile coverage and correct register writes visible during I2S playback/capture.
