# sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood.h

## Purpose
Defines register offsets, bit fields, PCM limits, and shared private data for the Kirkwood/MVEBU audio controller.

## Important APIs, Types, And Functions
Macros describe DMA windows, playback/record control registers, buffer registers, DCO and clock source registers, interrupt and error registers, I2S format registers, and PCM buffer constraints. `struct kirkwood_dma_data` holds mapped register bases, clocks, cached playback/record control words, active substreams, IRQ, and burst size. It declares `kirkwood_soc_component`.

## Control Flow, State, And Persistence
No direct control flow. The structure is the persistent state shared by the I2S DAI and DMA component.

## Dependencies And Integration Points
Included by both `kirkwood-dma.c` and `kirkwood-i2s.c`. The constants encode the hardware ABI for the MVEBU audio block.

## Risks And Test Signals
Risks are incorrect register definitions, stale comments about Marvell ALSA-derived limits, and shared control bits being misused by either DAI or DMA code. Test signals include register dumps matching expected offsets and successful operation across playback/record, I2S/SPDIF, and burst sizes.
