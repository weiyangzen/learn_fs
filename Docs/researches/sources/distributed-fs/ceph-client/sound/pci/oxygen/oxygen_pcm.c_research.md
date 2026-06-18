
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_pcm.c

Purpose: shared ALSA PCM implementation for Oxygen DMA channels: analog capture A/B/C, SPDIF playback/capture, multichannel playback, and AC97/front-panel playback/capture.

Important functions: `oxygen_open/close` assign channel runtime state and active bits; `oxygen_hw_params` writes DMA base/count/period registers; channel-specific hw_params program formats, I2S rate/MCLK/bits, SPDIF rate/source, and model DAC/ADC params; `oxygen_prepare`, `oxygen_trigger`, `oxygen_pointer`, and hw_free control DMA interrupts, status, pause, flush, and pointer reporting. `oxygen_pcm_init` creates ALSA PCM devices based on model `device_config`.

Control flow: open applies hardware constraints and notifies SPDIF PCM control activation. hw_params programs hardware and model codecs. trigger groups synchronized substreams, updating `pcm_running` and DMA status/pause registers. interrupts in `oxygen_lib.c` call `snd_pcm_period_elapsed`.

State/persistence: active/running stream masks and `streams[]` link ALSA substreams to IRQ handling; DMA registers are saved through write helpers.

Risks: DMA count units are dwords, multichannel uses 24-bit counters, pointer arithmetic assumes 32-bit DMA address behavior, and lock ordering with mixer/SPDIF state matters. Test signals: playback/capture at all rates/formats/channel counts, no-period-wakeup, pause/resume, sync-start groups, hw_free flush, and SPDIF/multichannel source interaction.
