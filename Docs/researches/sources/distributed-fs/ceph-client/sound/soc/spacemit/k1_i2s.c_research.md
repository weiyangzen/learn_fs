# sources/distributed-fs/ceph-client/sound/soc/spacemit/k1_i2s.c

Purpose: ASoC CPU DAI driver for the SpacemiT K1 I2S/SSPA controller with DMAEngine PCM support.

Important APIs/functions: `spacemit_i2s_probe()` enables required clocks, maps registers, obtains an exclusive reset, derives playback/capture capability from `dma-names`, registers a dynamically cloned DAI, and registers DMAEngine PCM. `spacemit_i2s_init()` programs PSP frame format, FIFO thresholds, receive-without-transmit, and disables interrupts. DAI ops apply startup constraints based on I2S versus DSP_A/DSP_B, program sample width and DMA burst width, set BCLK/SSPA clock rates, set sysclk, configure frame-sync width/timing, refcount enable/disable triggers with `started_count`, and assert/deassert reset on DAI probe/remove.

Control flow/state: `struct spacemit_i2s_dev` persists MMIO, reset, clocks, DMA descriptors, supported stream directions, selected DAI format, and active stream count. Trigger refcounting lets playback/capture share the hardware enable bit.

Dependencies/integration: Device Tree compatible `spacemit,k1-i2s`, clocks `sysclk`, `bclk`, `sspa_bus`, `sspa`, reset controller, DMA channels named `tx`/`rx`, ASoC DAI format callbacks, and DMAEngine PCM.

Risks/test signals: `started_count` is not protected by a lock; simultaneous playback/capture trigger paths could race. DAI advertised rates include only 8/16/48 kHz while PCM hardware has a 192 kHz max constant, so constraints should be checked. Tests should cover tx-only, rx-only, full-duplex, I2S S16 stereo, DSP_A/B S32 mono, trigger refcounting, reset sequencing, clock rates, and missing DMA-name cases.
