# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-i2s.c

Purpose: Specializes the shared AIU FIFO implementation for I2S playback. It defines I2S FIFO PCM hardware limits, reset/prepare behavior, physical-width programming, IRQ periodicity, and DAI probe data binding.

Important APIs and functions: Exported `aiu_fifo_i2s_dai_ops` composes shared FIFO ops with I2S-specific `trigger`, `prepare`, `hw_params`, and probe. `aiu_fifo_i2s_dai_probe()` allocates common FIFO state and sets the I2S memory offset, block size, pclk, IRQ, and hardware constraints. Helpers are `aiu_fifo_i2s_trigger()`, `aiu_fifo_i2s_prepare()`, and `aiu_fifo_i2s_hw_params()`.

Control flow: Probe binds the FIFO to `AIU_MEM_I2S_START`, a 256-byte FIFO block, I2S pclk, and the I2S IRQ. Prepare runs the common FIFO reset then toggles `AIU_MEM_I2S_BUF_CNTL_INIT`. `hw_params` puts the I2S block in hold, configures DMA boundaries through common FIFO code, selects 16-bit or 32-bit memory mode, sets IRQ block count from period bytes divided by FIFO block size, forces left/right mode, and releases hold. Trigger resets the fast I2S path before delegating to the common FIFO enable/disable path.

State and persistence: The `struct aiu_fifo` attached to playback DMA data stores block size, IRQ, pclk, and register offset. Hardware state persists in I2S memory and misc registers until reconfigured.

Dependencies and integration points: Uses common `aiu_fifo.c`, AIU register offsets from `aiu.h`, AIU clock/IRQ fields from `struct aiu`, and ALSA PCM buffer management via `pcm_new`.

Risks: Period and buffer byte sizes must be multiples of 256 through the common constraints or IRQ block programming is invalid. Only physical widths 16 and 32 are accepted. Hold/release and fast reset sequencing is hardware-sensitive.

Test signals: I2S FIFO playback with mmap, pause/resume, period elapsed IRQ cadence, S16/S24/S32 containers, 2- and 8-channel streams, and register traces on `AIU_MEM_I2S_*` and `AIU_I2S_MISC`.
