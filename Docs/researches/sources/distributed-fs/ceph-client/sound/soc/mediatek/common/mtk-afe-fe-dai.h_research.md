# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-fe-dai.h

## Purpose
Declares shared MediaTek AFE FE DAI operations and memif helper APIs.

## Important APIs, Types, And Functions
The header declares the FE lifecycle callbacks, `extern const struct snd_soc_dai_ops mtk_afe_fe_ops`, dynamic IRQ acquire/release, AFE suspend/resume, and memif setters for enable, address, channel, rate, format, and pbuf size.

## Control Flow, State, And Persistence
No direct control flow or state. The declarations expose the shared implementation for SoC-specific DAI tables and platform code.

## Dependencies And Integration Points
Uses forward declarations for ASoC and MediaTek base types, allowing SoC drivers to include the header without pulling in all definitions.

## Risks And Test Signals
Risks are prototype drift and missing includes for `snd_pcm_format_t`, `dma_addr_t`, or `size_t` when include order changes. Test signals are compile coverage across all MediaTek SoC users.
