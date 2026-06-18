# sources/distributed-fs/ceph-client/sound/soc/stm/Makefile

Purpose: maps STM32 ASoC Kconfig symbols to controller objects.

Important entries: SAI builds both `stm32_sai_sub.o` as `snd-soc-stm32-sai-sub.o` and `stm32_sai.o` as `snd-soc-stm32-sai.o`. I2S builds `snd-soc-stm32-i2s.o`. SPDIFRX builds `snd-soc-stm32-spdifrx.o`. DFSDM builds `stm32_adfsdm.o`.

Control flow and integration: enabled symbols produce standalone modules/objects per controller. SAI is split into parent controller and sub-block implementations.

State and persistence: no runtime state. The object layout controls module boundaries and autoload names.

Dependencies: sibling Kconfig and top-level ASoC build traversal.

Risks: SAI uses two objects under one Kconfig symbol; both must be present for a functional SAI hierarchy. The Makefile includes SPDIFRX and SAI sub files outside this research subset, so changes to those files can affect build of researched symbols.

Test signals: build each symbol as `m` and `y`, verify module names and dependencies, and ensure SAI parent/sub-device autoload works with device-tree population.
