# sources/distributed-fs/ceph-client/sound/soc/renesas/Makefile

Purpose: maps Renesas ASoC Kconfig symbols to build objects for legacy DMA/audio units, R-Car subdirectory, board drivers, and RZ SSIF.

Important targets: builds `snd-soc-dma-sh7760.o` from `dma-sh7760.o`, `snd-soc-hac.o`, `snd-soc-ssi.o`, `snd-soc-fsi.o`, and combined `snd-soc-siu.o` from `siu_pcm.o siu_dai.o`. It descends into `rcar/` for `CONFIG_SND_SOC_RCAR`, builds `snd-soc-sh7760-ac97.o` and `snd-soc-migor.o` board drivers, and builds `snd-soc-rz-ssi.o`.

Control flow and state: static Kbuild declarations only. The Makefile determines which compilation units are linked into modules or built-in objects based on config symbols.

Dependencies and integration: mirrors `Kconfig` symbols and groups multi-file drivers under conventional `*-y` variables.

Risks: Kconfig/Makefile drift would produce selectable but unbuilt drivers or orphaned objects. The R-Car directory is only entered for `SND_SOC_RCAR`; MSIOF is built inside that subdirectory under its own config, so directory traversal depends on the broader R-Car symbol.

Test signals: `make M=sound/soc/renesas` with selected configs, module names matching expected aliases, and no orphan object warnings in Kbuild.
