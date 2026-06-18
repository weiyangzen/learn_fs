# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.c

Purpose: Provides shared playback FIFO PCM operations for AIU I2S and SPDIF frontends. It handles DMA pointer reporting, FIFO enable/disable triggers, DMA boundary programming, IRQ registration, clock management, managed buffer allocation, and DAI private data allocation.

Important APIs and functions: `aiu_fifo_pointer()`, `aiu_fifo_trigger()`, `aiu_fifo_prepare()`, `aiu_fifo_hw_params()`, `aiu_fifo_startup()`, `aiu_fifo_shutdown()`, `aiu_fifo_pcm_new()`, `aiu_fifo_dai_probe()`, and `aiu_fifo_dai_remove()` are exported within the AIU module. `struct aiu_fifo` stores PCM limits, memory offset, FIFO block size, pclk, and IRQ.

Control flow: Startup applies PCM hardware constraints, enforces buffer and period byte step sizes based on `fifo_block`, enables pclk, and requests the FIFO IRQ. `hw_params` writes DMA start/read/end addresses, programs memory channel masks to read all channels, and sets FIFO memory boundaries. Prepare toggles the common FIFO init bit. Trigger toggles fill/empty enables. ISR calls `snd_pcm_period_elapsed()`. Shutdown frees the IRQ and disables pclk. `pcm_new` coerces a 32-bit DMA mask and installs a managed buffer sized to the FIFO hardware maximum.

State and persistence: Per-DAI FIFO state is allocated with `kzalloc_obj()` and attached as playback DMA data. Hardware DMA address registers persist until new hw_params or reset. IRQ registration is per open substream.

Dependencies and integration points: Called by `aiu-fifo-i2s.c` and `aiu-fifo-spdif.c`. Depends on ASoC component read/write APIs, Linux DMA mapping, clock APIs, and ALSA PCM runtime structures.

Risks: Pointer calculation casts runtime DMA address and hardware read pointer to 32-bit, matching the coerced DMA mask but unsuitable for wider addressing. Error cleanup depends on variant startup using common shutdown semantics. Period elapsed is raised on every IRQ without reading status in this common handler, so variant hardware must generate only intended period IRQs.

Test signals: PCM open/close leak checks, IRQ registration failures, 32-bit DMA mask setup, mmap playback pointer progression, period/buffer constraint tests, and underrun/stop/pause trigger behavior.
