# sources/distributed-fs/ceph-client/sound/soc/sof/imx/Makefile

Purpose: object composition for NXP i.MX SOF platform modules.

Important APIs/types/functions: builds `snd-sof-imx8.o` from `imx8.o`, `snd-sof-imx9.o` from `imx9.o`, and common support from `imx-common.o`.

Control flow: Kconfig symbols decide which platform/common objects are linked.

State and persistence: build-time only.

Dependencies and integration points: maps i.MX Kconfig to common and platform-specific source files.

Risks: platform modules depend on `imx-common.o` being built when selected; Kconfig handles this via `SND_SOC_SOF_IMX_COMMON`.

Test signals: module/built-in build for IMX8, IMX9, and common support.
