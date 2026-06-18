# sources/distributed-fs/ceph-client/sound/soc/kirkwood/kirkwood-dma.c

## Purpose
Provides the PCM/DMA component for Kirkwood/MVEBU audio, programming hardware buffer registers, MBUS windows, interrupts, and PCM buffer constraints.

## Important APIs, Types, And Functions
`kirkwood_priv()` fetches controller private data from the CPU DAI. `kirkwood_dma_irq()` handles byte-count and error interrupts. `kirkwood_dma_conf_mbus_windows()` configures MBUS DRAM windows. Component ops implement `open`, `close`, `hw_params`, `prepare`, `pointer`, and `pcm_new`; exported component driver is `kirkwood_soc_component`.

## Control Flow, State, And Persistence
Open applies PCM constraints tied to burst size and requests a shared IRQ only when the first stream opens. It stores active playback/capture substreams in `kirkwood_dma_data`. `hw_params` sets MBUS windows for the DMA buffer. `prepare` writes byte interrupt count, DMA address, and size registers. Close clears substream pointers and frees the IRQ when the last stream closes.

## Dependencies And Integration Points
Depends on `struct kirkwood_dma_data` from `kirkwood.h`, MVEBU MBUS DRAM info, raw MMIO registers, ALSA PCM core, and the I2S driver that registers this component together with DAIs.

## Risks And Test Signals
Risks include MBUS window matching using coarse high address comparisons, IRQ sharing with substream pointers that must be valid for period callbacks, `NO_PERIOD_WAKEUP` interactions, and byte-count wrap handling in `pointer()`. Test signals include period interrupts for playback/capture, error interrupt logging, buffer alignment enforcement by burst size, and DMA operation on systems with multiple DRAM chip-select windows.
