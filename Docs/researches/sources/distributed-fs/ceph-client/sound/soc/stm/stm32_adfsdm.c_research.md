# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_adfsdm.c

Purpose: bridges STM32 DFSDM IIO ADC data into an ASoC capture DAI/PCM platform, mainly for digital microphone capture.

Important APIs and types: `struct stm32_adfsdm_priv` owns a DAI driver copy, substream pointer, IIO channel/callback buffer state, ALSA PCM buffer pointer/position, and a mutex for IIO active state. DAI ops implement shutdown, prepare, and set_sysclk. Component ops implement PCM open/close/hw_params/trigger/pointer/pcm_new. `stm32_afsdm_pcm_cb()` is the data path callback from DFSDM/IIO into the ALSA ring buffer.

Control flow: probe registers the DAI component, obtains all IIO channels, obtains an IIO callback buffer with a dummy callback, registers cleanup, manually initializes/adds a second component for PCM platform ops, and enables runtime PM. PCM open sets hardware constraints and stores the substream. hw_params stores the DMA-area pointer and sets IIO watermark to ALSA period size. DAI prepare stops any active callback, writes sample frequency to the IIO channel, and starts callbacks. Trigger START/RESUME resets position and registers the optimized DFSDM buffer callback; STOP/SUSPEND releases it. The callback copies 32-bit DFSDM samples directly for S32 or decimates 32-to-16 for S16, wraps in the ALSA buffer, advances position, and calls `snd_pcm_period_elapsed()` when a period boundary is crossed.

State and persistence: `iio_active` is protected by a mutex in DAI prepare/shutdown. `pos` and `pcm_buff` are stream state used by callback and pointer without explicit locking. The IIO channel persists for device lifetime and is released via devm action.

Dependencies and integration points: compatible `st,stm32h7-dfsdm-dai`, IIO consumer and STM32 DFSDM ADC APIs, IIO callback buffers, ASoC DAI/component APIs, managed PCM buffers, and DMIC codec selection from Kconfig.

Risks: callback position updates can race with pointer/trigger stop unless upper layers serialize sufficiently. `stm32_memcpy_32to16()` treats source as `u16 *` and skips every other halfword, so endian/sample alignment assumptions are critical. Period elapsed detection compares `old_pos % period_size < size`, using original callback `size` rather than adjusted `src_size` in S16 mode. Manual component allocation/addition is less common than devm registration and remove unregisters all components for the device.

Test signals: capture S16 and S32 at 8 kHz through 192 kHz, period sizes near max and wrap boundaries, trigger stop while callback is active, sample-rate programming failures from IIO, set_sysclk `spi_clk_freq` writes, and period-elapsed cadence under ftrace.
