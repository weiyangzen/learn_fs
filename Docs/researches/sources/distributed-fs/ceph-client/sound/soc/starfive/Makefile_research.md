# sources/distributed-fs/ceph-client/sound/soc/starfive/Makefile

Purpose: maps StarFive ASoC Kconfig symbols to build objects.

Important entries: `obj-$(CONFIG_SND_SOC_JH7110_PWMDAC) += jh7110_pwmdac.o` and `obj-$(CONFIG_SND_SOC_JH7110_TDM) += jh7110_tdm.o`.

Control flow and integration: when a symbol is `y`, the object links built-in; when `m`, it becomes part of a module for the corresponding driver. There are no composite objects or shared helpers in this directory.

State and persistence: no runtime state. The Makefile simply defines compilation inclusion for the two platform drivers.

Dependencies: paired with sibling Kconfig and the top-level sound/soc build traversal.

Risks: because each driver is a standalone object, any future shared StarFive audio helper would need explicit composite object handling. Current simplicity is low risk.

Test signals: build each Kconfig option as `y` and `m`, confirm the expected module/object names, and run `make M=sound/soc/starfive` style partial builds where supported.
