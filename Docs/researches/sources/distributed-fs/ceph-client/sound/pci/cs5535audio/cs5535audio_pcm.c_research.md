# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pcm.c

Purpose: PCM playback/capture implementation for CS5535/CS5536 audio, including ALSA hardware capabilities, DMA PRD ring construction, trigger handling, pointer reporting, and PCM device creation.

Important APIs and types: `snd_cs5535audio_playback` and `snd_cs5535audio_capture` define S16_LE stereo continuous-rate hardware constraints. `cs5535audio_build_dma_packets` allocates and fills PRD descriptors plus a trailing jump descriptor. `snd_cs5535audio_hw_params/free`, `snd_cs5535audio_trigger`, `snd_cs5535audio_pcm_pointer`, prepare/open/close callbacks, and `snd_cs5535audio_pcm` form the ALSA PCM surface. Direction-specific `cs5535audio_dma_ops` map to BM0 playback and BM1 capture registers.

Control flow: open selects direction hardware, clamps rates from AC97 capability masks, records the substream, and assigns runtime private DMA state. `hw_params` records buffer metadata and builds descriptors. `prepare` programs AC97 DAC/ADC sample rate. `trigger` enables, pauses, resumes, or disables the correct bus-master engine under `reg_lock`. `pointer` reads the hardware DMA pointer, bounds-checks it against runtime DMA buffer, and converts bytes to frames. `hw_free` powers down the relevant AC97 path and frees descriptor pages.

State and persistence: per-direction DMA state tracks descriptor buffer, active substream, buffer address/size, period size/count, saved PRD, and open flag. Descriptor memory is allocated with ALSA DMA APIs and freed on `hw_free`.

Dependencies and integration: used by core probe after AC97 mixer creation, relies on `struct cs5535audio` and register macros from the header, and calls OLPC capture hooks unconditionally via stubs or real implementations.

Risks and test signals: descriptor allocation reserves `CS5535AUDIO_DESC_LIST_SIZE+1`, which is byte-based but intended to include an extra descriptor; period count is capped at 128. Pointer errors reset to zero and log. Tests: mmap playback/capture, period interrupts, pause/resume, all accepted period sizes/counts, `hw_params` reuse with unchanged period geometry, and capture OLPC hooks.
