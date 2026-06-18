# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/Makefile

Purpose: Builds the MT8195 SOF platform module.

Important build rules: `snd-sof-mt8195-y` combines `mt8195.o`, `mt8195-clk.o`, and `mt8195-loader.o`; `CONFIG_SND_SOC_SOF_MT8195` builds `snd-sof-mt8195.o`.

Control flow and integration: The object split separates platform driver/DSP ops, clock tree control, and HIFIxDSP boot/reset sequencing.

State and persistence: No runtime state; it defines link composition for the module.

Risks: Dropping any object breaks callbacks referenced from `mt8195.c`. The module depends on common MediaTek SOF helpers from the parent Makefile.

Test signals: Build as module and built-in, verify namespace imports and no unresolved `adsp_clock_*` or boot-sequence symbols.
