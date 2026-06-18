# sources/distributed-fs/ceph-client/sound/soc/mxs/Makefile

Purpose: maps MXS ASoC Kconfig symbols to kernel objects.

Important APIs/types/functions: builds `snd-soc-mxs.o` from `mxs-saif.o`, `snd-soc-mxs-pcm.o` from `mxs-pcm.o`, and `snd-soc-mxs-sgtl5000.o` from `mxs-sgtl5000.o`.

Control flow: when `CONFIG_SND_MXS_SOC` is set, both SAIF and PCM helper modules are linked; when `CONFIG_SND_SOC_MXS_SGTL5000` is set, the machine driver is linked.

State and persistence: build-only state in object lists.

Dependencies and integration: aligned with `Kconfig` and the SAIF driver’s call to `mxs_pcm_platform_register`.

Risks: separating PCM and SAIF into two objects means symbol export/import must stay correct. Missing object selection would leave unresolved machine-driver or platform registration symbols.

Test signals: module build for `CONFIG_SND_MXS_SOC=m`, built-in build, and modpost symbol checks.
