# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Makefile

Purpose: maps MediaTek/Airoha Kconfig symbols to PM-domain driver objects.

Important build rules: `mtk-mfg-pmdomain.o` for `CONFIG_MTK_MFG_PM_DOMAIN`, `mtk-scpsys.o` for legacy `CONFIG_MTK_SCPSYS`, `mtk-pm-domains.o` for generic `CONFIG_MTK_SCPSYS_PM_DOMAINS`, and `airoha-cpu-pmdomain.o` for `CONFIG_AIROHA_CPU_PM_DOMAIN`.

Control flow: kbuild includes only selected objects. A conditional removes ftrace profiling flags from `airoha-cpu-pmdomain.o` when building a Thumb2 kernel with Clang because SMCCC use of R7 conflicts with Clang's frame pointer/profiling use.

State and dependencies: no runtime state. It depends on Kconfig to ensure required headers and subsystems are available.

Risks: the Airoha flag removal is narrow and should be preserved with any object rename. Whitespace around assignments is cosmetic but keep kbuild syntax intact.

Test signals: build with Thumb2+Clang+ftrace and with each config symbol toggled. Confirm selected objects match expected platform driver availability.
