# sources/distributed-fs/ceph-client/sound/soc/google/chv3-i2s.c

Purpose: ASoC component/DAI and custom PCM implementation for the Google Chameleon v3 I2S interface, backed by MMIO ring-buffer registers and a shared IRQ block.

Important APIs/types/functions: `struct chv3_i2s_dev` stores register bases, active substreams, and TX fetch size. DAI capabilities support 1-128 channels, continuous 8-96 kHz, S32_LE. PCM callbacks include `chv3_dma_open()`, `close()`, `pcm_new()`, `hw_params()`, `prepare()`, `pointer()`, and `ack()`. `chv3_i2s_isr()` reports periods. `chv3_i2s_probe()` maps resources, requests IRQ, and registers the component.

Control flow: probe maps two MMIO regions, reads TX IRQ constant, registers an IRQ handler, then registers one DAI/component. PCM open sets hardware constraints and stores the active RX/TX substream. `pcm_new()` allocates maximum-size managed DMA buffers manually. Prepare resets RX or TX, writes DMA base/size/IRQ period registers, enables the stream, and unmasks IRQs. ALSA ack writes consumer/producer indices from `appl_ptr`; pointer reads hardware producer/consumer index and lags playback by one frame to avoid full-buffer deadlock.

State and persistence: runtime state is active RX/TX substream pointers and `tx_bytes_to_fetch`. Hardware state consists of ring base/size, producer/consumer indices, enables, reset bits, and IRQ masks. Buffers are allocated per PCM substream and retained by ALSA until device teardown.

Dependencies/integration: depends on two platform MMIO resources, one IRQ, ASoC component registration, ALSA DMA buffer allocation, and DT compatible `google,chv3-i2s`. It does not use dmaengine; hardware directly consumes physical DMA buffer addresses.

Risks: ISR calls `snd_pcm_period_elapsed()` on stored substream pointers without null checks, relying on IRQ masking/stream lifecycle. `frame_bytes` is computed as `runtime->frame_bits * 8`, which appears dimensionally suspect because ALSA frame bits normally convert to bytes by dividing by 8; this may affect playback pointer lag. Manual DMA allocation must fit hardware address width. TX IRQ period divides by `tx_bytes_to_fetch`, so a zero or unexpected hardware constant would fault or misprogram.

Test signals: hardware or emulator tests for ring index wraparound, playback full-buffer behavior, ack/pointer monotonicity, IRQ period generation, open/close races, and max buffer allocation. Static tests should flag null substream ISR paths and frame-size arithmetic.
