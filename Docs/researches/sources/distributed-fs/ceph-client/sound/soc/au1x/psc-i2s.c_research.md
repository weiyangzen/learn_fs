# sources/distributed-fs/ceph-client/sound/soc/au1x/psc-i2s.c

## Purpose
ASoC CPU DAI for Au12x0/Au1550 PSC in I2S mode. It supports I2S, left-justified, and right/LSB-justified framing, provider/consumer clock modes, sample-width/rate validation, late hardware configuration when external clocks are present, and PSC DBDMA integration.

## Important APIs, Types, And Functions
- `au1xpsc_i2s_set_fmt()` converts ASoC format/inversion/provider flags to PSC I2S config bits.
- `au1xpsc_i2s_hw_params()` validates active configuration or caches sample length and rate.
- `au1xpsc_i2s_configure()` enables PSC, waits for ready, writes I2S config, and waits for device-ready.
- `au1xpsc_i2s_start/stop()` start or stop per-direction FIFOs and suspend PSC when both directions are idle.
- Probe maps resources, records DMA IDs, selects PSC I2S mode, clones the DAI template, and registers the component.

## Control Flow
Probe preserves clock selection, disables PSC, selects I2S mode, clears I2S config, and caches FIFO thresholds. Startup attaches DMA IDs. `hw_params` only programs cached fields unless the hardware is active, where mismatched width/rate is rejected. Trigger start configures the PSC if no stream is busy, clears FIFO, starts the requested direction, and waits for busy confirmation. Trigger stop stops one direction and powers down PSC if both directions are idle.

## State And Persistence
`cfg`, `rate`, PM save registers, and DMA IDs persist in driver memory. Hardware is deliberately configured late because codec-provided clocks may be absent until stream start.

## Dependencies And Integration Points
Depends on Alchemy PSC registers and the `au1xpsc-pcm` DBDMA platform. Platform driver name is `au1xpsc_i2s`.

## Risks
Comments say only PSC slave mode was originally supported, while code accepts both provider and consumer modes; board-clock realities need testing. Late configuration can time out if external clocks are missing. Only S16_LE and S24_LE are advertised. Full-duplex streams must use the same rate and sample width.

## Test Signals
Codec-master and PSC-master startup, timeout path when clocks are absent, rate/width mismatch rejection with one active stream, suspend/resume preserving PSC selection, and FIFO busy transitions.
