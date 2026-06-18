# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.h

Purpose: shared register map, bit definitions, data structures, and cross-file declarations for the CS5535/CS5536 audio driver.

Important APIs and types: I/O helpers `cs_writel`, `cs_writeb`, `cs_readl`, `cs_readw`, and `cs_readb` add register offsets to `cs5535audio.port`. Register constants cover AC97 codec control/status, IRQ status, bus-master command/status/PRD/pointer registers, AC97 command bits, and PRD control bits. `struct cs5535audio_dma_ops` abstracts playback versus capture register operations; `struct cs5535audio_dma_desc` describes PRD entries; `struct cs5535audio_dma` holds per-direction DMA state; `struct cs5535audio` is the driver-private card state.

Control flow and integration: the header lets `cs5535audio_pcm.c` use a common DMA operation table while `cs5535audio.c` owns device creation and IRQs. `CONFIG_OLPC` switches between real OLPC helper declarations and no-op inline stubs, allowing the same PCM/core code to call OLPC hooks unconditionally.

State and persistence: declares in-memory runtime state only: saved PRD on suspend, DMA buffer metadata, PCM open flags, and substream pointers. Hardware state is volatile register state.

Risks and test signals: register offsets and bit definitions are a single point of correctness. PRD addresses are 32-bit, matching the core driver's DMA mask. Compile-test with and without `CONFIG_OLPC` and `CONFIG_PM_SLEEP`; runtime-test playback/capture register access and PM resume PRD restoration.
