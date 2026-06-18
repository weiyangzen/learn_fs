# sources/distributed-fs/ceph-client/sound/soc/spear/Makefile

Purpose: maps SPEAr ASoC Kconfig symbols to module objects.

Important APIs/types: builds `spear_pcm.o` into `snd-soc-spear-pcm.o`, `spdif_in.o` into `snd-soc-spear-spdif-in.o`, and `spdif_out.o` into `snd-soc-spear-spdif-out.o`.

Control flow/state: no runtime state.

Dependencies/integration: links shared PCM support and S/PDIF interfaces according to Kconfig.

Risks/test signals: module build should verify S/PDIF objects resolve `devm_spear_pcm_platform_register()` from the shared PCM module.
