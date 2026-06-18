# sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s.h

## Purpose
Shared private header for BCM63XX Whistler I2S and PCM support. It defines TX/RX register offsets, bit masks, descriptor FIFO constants, private device state, and prototypes for the companion PCM platform hooks.

## Important APIs, Types, And Functions
- Register macros cover `I2S_MISC_CFG`, TX/RX config, IRQ, descriptor FIFO, and config-2 master/slave registers.
- `struct bcm_i2s_priv` stores device, regmap, clock, playback/capture substreams, and DMA descriptor pointers.
- Externs `bcm63xx_soc_platform_probe()` and `bcm63xx_soc_platform_remove()` connect the I2S DAI driver to the PCM implementation.

## Control Flow
No executable code. It is the compile/link contract between `bcm63xx-i2s-whistler.c` and the companion PCM source.

## State And Persistence
Defines the in-memory device state used by the BCM63XX module; lifetime is owned by platform probe/remove.

## Dependencies And Integration Points
Requires ASoC/platform-device types from including C files and an `i2s_dma_desc` type supplied by the companion PCM code or other included definitions.

## Risks
Header changes can break both I2S and PCM sides. Descriptor pointer fields are opaque here, making ownership and allocation rules dependent on the companion implementation. Hardcoded register offsets must match the target BCM63XX IP block.

## Test Signals
Build/link of `snd-soc-63xx`, register access tests for TX/RX offsets, and runtime DMA descriptor allocation/free through the companion PCM driver.
