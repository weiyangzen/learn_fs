# sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.c

Purpose: shared SPEAr ASoC PCM DMAEngine registration helper.

Important APIs/functions: `devm_spear_pcm_platform_register()` copies a default `snd_dmaengine_pcm_config`, installs a legacy DMA filter callback, and registers DMAEngine PCM with `NO_DT` and `COMPAT` flags. The default hardware profile enables interleaved block-transfer mmap pause/resume with 16 KiB buffers and fixed 2 KiB periods.

Control flow/state: stateless after registration except for the caller-provided config object that is filled before `devm_snd_dmaengine_pcm_register()`.

Dependencies/integration: used by SPEAr S/PDIF input/output drivers with `sound/spear_dma.h` platform DMA data.

Risks/test signals: hard-coded period/buffer sizes may constrain modern use cases. Tests should verify DMA channel filtering, mmap playback/capture, pause/resume, and both S/PDIF drivers using independent config storage.
