# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5514-spi.c

`rt5514-spi.c` is the SPI companion for RT5514. It exports burst read/write helpers for DSP firmware and calibration access, and registers a mono 16 kHz DSP capture CPU DAI backed by periodic SPI copies from the DSP voice ring buffer.

Key state is `rt5514_spi`, a global SPI device pointer, and `struct rt5514_dsp`, which stores the component device, delayed copy work, DMA mutex, active PCM substream, DSP ring base/limit/read pointer, buffer size, copied size, and DMA offset. Exported APIs are `rt5514_spi_burst_read()` and `rt5514_spi_burst_write()`. PCM callbacks provide open, hw_params, hw_free, pointer, pcm_new, and component probe behavior.

Control flow: SPI probe records the global device and registers an ASoC component/DAI. Component probe allocates stream state and requests an optional IRQ. IRQ or pending IRQ status calls `rt5514_schedule_copy()`, which reads voice buffer base/limit/write pointer and schedules copy work. Copy work waits for enough data, reads one ALSA period over SPI, handles ring wrap, advances DMA offset, calls `snd_pcm_period_elapsed()`, and reschedules.

State persists while the SPI component is loaded and while a PCM substream is active. Suspend enables IRQ wake when allowed; resume disables it and restarts copying if needed. Dependencies include SPI, ASoC PCM/DAI, delayed work, IRQ, and `rt5514-spi.h`. Risks include single-device global state, 8-byte alignment assumptions, ignored `spi_write()` errors, `false` returned from an `int` read helper, and polling-based overrun/underrun sensitivity. Test signals include firmware helper transfers, DSP capture start, ring wrap, period callbacks, pointer movement, suspend/resume wake, and SPI error injection.
