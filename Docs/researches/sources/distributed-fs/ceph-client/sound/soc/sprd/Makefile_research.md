# sources/distributed-fs/ceph-client/sound/soc/sprd/Makefile

Purpose: builds Spreadtrum ASoC platform objects.

Important APIs/types: `snd-soc-sprd-platform-y` combines `sprd-pcm-dma.o` and `sprd-pcm-compress.o` under `CONFIG_SND_SOC_SPRD`; `sprd-mcdt.o` is built under `CONFIG_SND_SOC_SPRD_MCDT`.

Control flow/state: no runtime state.

Dependencies/integration: links PCM DMA, compressed PCM, and optional MCDT support according to the Kconfig menu.

Risks/test signals: object grouping means the base platform module always includes both DMA and compress support. Build tests should ensure symbols resolve when MCDT is disabled and enabled.
