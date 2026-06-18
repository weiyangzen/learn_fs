# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-pxs2.c

## Purpose
SoC description and platform driver binding for UniPhier PXs2 AIO audio. It provides static routing, DAI, PLL, and compatible-table data for the shared AIO driver.

## Important APIs, Types, and Functions
The core declarations are `uniphier_aio_pxs2[]`, `uniphier_aio_pll_pxs2[]`, `uniphier_aio_dai_pxs2[]`, and `uniphier_aio_pxs2_spec`. The platform driver binds `socionext,uniphier-pxs2-aio` and delegates probe/remove to `uniphier_aio_probe()` and `uniphier_aio_remove()`. Referenced DAI ops are `uniphier_aio_i2s_pxs2_ops`, `uniphier_aio_spdif_pxs2_ops`, and `uniphier_aio_spdif_pxs2_ops2`.

## Control Flow, State, and Persistence
All behavior is data-driven. The common probe consumes the PXs2 spec to allocate AIO instances and DAIs for HDMI, line, auxiliary, S/PDIF, and compressed S/PDIF streams. The SW maps persist the ring-buffer, DMA channel, output/input interface, and real port selectors needed by runtime helper code.

## Dependencies and Integration Points
Depends on ALSA SoC DAI registration, OF matching, and common UniPhier AIO helpers. PXs2 differs from LD11 by exposing line/aux I2S paths and two S/PDIF output groups while omitting LD11 EVE/SRC entries.

## Risks and Test Signals
Risks include static route mismatches, duplicated S/PDIF hardware mappings between PCM and compress DAIs, and supported-rate declarations being narrower than hardware variants. Test signals are registration of seven DAIs, correct stream names, 48 kHz I2S playback/capture, HDMI S/PDIF PCM output, compressed output on both S/PDIF ports, and no regression in common AIO probe with `addr_ext = 0`.
