# sources/distributed-fs/ceph-client/sound/soc/dwc/dwc-pcm.c

## Purpose
`dwc-pcm.c` implements the optional PIO PCM backend for the DesignWare I2S driver. It registers an ASoC PCM component that uses CPU-driven FIFO reads/writes from the I2S IRQ handler instead of DMAengine transfers.

## Important APIs, Types, And Functions
The file generates 16-bit and 32-bit TX/RX transfer functions through `dw_pcm_tx_fn()` and `dw_pcm_rx_fn()`. `dw_pcm_transfer()` is the shared IRQ-side transfer engine used by exported `dw_pcm_push_tx()` and `dw_pcm_pop_rx()`. Component callbacks include `dw_pcm_open()`, `dw_pcm_close()`, `dw_pcm_hw_params()`, `dw_pcm_trigger()`, `dw_pcm_pointer()`, and `dw_pcm_new()`. `dw_pcm_register()` registers the component with the platform device.

## Control Flow
`dw_pcm_open()` applies fixed hardware constraints, stores the parent `dw_i2s_dev` in runtime private data, and enforces integer periods. `hw_params()` accepts only stereo streams and selects 16-bit or 32-bit transfer functions; 24-bit samples are moved through the 32-bit path. `trigger()` resets the software pointer and publishes the active substream through RCU on start/resume/unpause, or clears it on stop/suspend/pause. The I2S IRQ handler calls push/pop helpers when TX FIFO empty or RX data available; `dw_pcm_transfer()` reads the RCU substream, verifies it is running, transfers `fifo_th` stereo frames through `l_reg`/`r_reg`, atomically updates the pointer with `cmpxchg()`, and signals period elapsed when needed. `pointer()` reports the current frame index. `pcm_new()` allocates a managed continuous buffer.

## State And Persistence
State is shared with `struct dw_i2s_dev`: RCU substream pointers, selected transfer function pointers, TX/RX frame pointers, FIFO threshold, and left/right register offsets. Buffer contents are ALSA-managed continuous memory. There is no hardware persistence beyond FIFO accesses; stream state is reset on trigger start.

## Dependencies And Integration Points
This backend depends on `CONFIG_SND_DESIGNWARE_PCM`, ASoC component PCM callbacks, ALSA PCM runtime and constraints, RCU synchronization, MMIO FIFO accessors, and the parent `dwc-i2s.c` IRQ handler. It is linked into `designware_i2s.o` only when selected by Kconfig.

## Risks And Edge Cases
PIO supports only two channels despite the controller supporting more channels elsewhere. Transfer functions write/read `fifo_th` frames per IRQ without checking actual FIFO level beyond the interrupt cause. `cmpxchg()` protects pointer update but does not retry on race; concurrent IRQ contexts could drop pointer progress if misconfigured. `period_elapsed` is set based on local period position after a batch and can skip exact boundaries if period/fifo sizes are poorly matched. 24-bit samples use 32-bit memory access, matching common ALSA storage but requiring correct format expectations.

## Test Signals
Test open constraints, stereo-only rejection, 16/24/32-bit format selection, trigger publication/removal through RCU, pointer wraparound, period elapsed signaling, playback FIFO writes and capture FIFO reads, close-time RCU synchronization, managed buffer allocation, and integration with `dwc-i2s.c` IRQ handling under playback, capture, and pause/resume.
