# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/Makefile

Purpose: Kbuild file for Renesas R-Car ASoC support, aggregating the multi-file R-Car core driver and optional MSIOF driver.

Important targets: `snd-soc-rcar-y` combines core, generation support, DMA, ADG clocks, SSI/SSIU, SRC, CTU, MIX, DVC, command handling, and debugfs objects into `snd-soc-rcar.o`. `snd-soc-msiof-y` builds `msiof.o` into `snd-soc-msiof.o`.

Control flow and state: static Kbuild declarations only. Object inclusion is controlled by `CONFIG_SND_SOC_RCAR` and `CONFIG_SND_SOC_MSIOF`.

Dependencies and integration: this file is reached from the parent Renesas Makefile when R-Car support is enabled. It mirrors parent Kconfig symbols and groups a broad hardware pipeline into one module.

Risks: adding a new R-Car pipeline block requires updating this aggregate list or the code will not link. Because MSIOF lives under this directory, parent directory traversal must be enabled for MSIOF builds.

Test signals: R-Car configs link all listed objects, MSIOF config produces `snd-soc-msiof`, and module dependency output includes expected DMA/clock/regmap support selected by Kconfig.
