# sources/distributed-fs/ceph-client/sound/soc/qcom/Makefile

Purpose: maps Qualcomm ASoC Kconfig symbols to platform, machine, common, offload, and QDSP6 subdirectory objects.

Important APIs/types/functions: builds LPASS CPU/CDC DMA/HDMI/platform/SoC-variant objects, machine drivers for APQ8016/APQ8096/SC/SDM/SM/X1E boards, `common.o`, SoundWire helpers, USB offload utils, and descends into `qdsp6/`.

Control flow: kernel build includes objects based on config symbols. Platform objects provide reusable exported symbols consumed by SoC-specific modules.

State and persistence: build-system object state only.

Dependencies and integration: aligned with `Kconfig`; LPASS APQ8016 object uses exported generic LPASS CPU probe/remove; machine drivers use `common.o` helpers.

Risks: object naming must match module aliases and Kconfig symbols. Missing common object selection causes unresolved machine helper references. QDSP6 subdirectory only builds under `CONFIG_SND_SOC_QDSP6`.

Test signals: modular and built-in builds for each Qualcomm SoC symbol and modpost coverage for exported LPASS/common symbols.
