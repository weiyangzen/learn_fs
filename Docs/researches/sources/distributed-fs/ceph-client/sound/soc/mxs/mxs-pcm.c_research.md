# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.c

Purpose: provides the MXS DMAEngine PCM registration helper and hardware constraints used by the SAIF DAI.

Important APIs/types/functions: `snd_mxs_hardware` defines MMAP, pause/resume, interleaved, half-duplex, period, buffer, and FIFO limits. `mxs_dmaengine_pcm_config` wraps it. `mxs_pcm_platform_register` exports registration via `devm_snd_dmaengine_pcm_register`.

Control flow: SAIF probe calls `mxs_pcm_platform_register`, which registers the DMAEngine PCM component with `SND_DMAENGINE_PCM_FLAG_HALF_DUPLEX`.

State and persistence: no mutable state here; DMAEngine PCM core owns runtime PCM buffers after registration.

Dependencies and integration: depends on `sound/dmaengine_pcm.h` and is consumed by `mxs-saif.c` through `mxs-pcm.h`.

Risks: hardware constraints are conservative but shared for playback/capture; incorrect period/buffer sizes can cause DMA underrun or ALSA constraint failures. Half-duplex flag prevents simultaneous independent PCM operation.

Test signals: PCM device creation after SAIF probe, DMAEngine channel binding, ALSA hw_params constraint negotiation, and playback/capture smoke tests around min/max period sizes.
