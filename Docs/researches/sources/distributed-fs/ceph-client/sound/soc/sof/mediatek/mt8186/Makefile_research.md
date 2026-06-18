# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/Makefile

Purpose: Builds the MT8186/MT8188 SOF platform module.

Important build rules: `snd-sof-mt8186-y` is composed of `mt8186.o`, `mt8186-clk.o`, and `mt8186-loader.o`; `CONFIG_SND_SOC_SOF_MT8186` builds `snd-sof-mt8186.o`.

Control flow and integration: The object split mirrors platform responsibilities: probe/ops/device table in `mt8186.c`, clock acquisition and gating in `mt8186-clk.c`, and HIFIxDSP boot/reset sequencing in `mt8186-loader.c`.

State and persistence: No runtime state in the Makefile; module composition determines which symbols are linked internally.

Risks: Missing any object breaks the `snd_sof_dsp_ops` callbacks or boot sequence. MT8188 support is compiled into the same module, so changes for one SoC can affect the other.

Test signals: Build `CONFIG_SND_SOC_SOF_MT8186=m/y`, verify module exports/import namespaces, and probe both `mediatek,mt8186-dsp` and `mediatek,mt8188-dsp` compatible tables.
