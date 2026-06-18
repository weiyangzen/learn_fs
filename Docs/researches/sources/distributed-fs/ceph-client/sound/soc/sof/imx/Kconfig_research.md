# sources/distributed-fs/ceph-client/sound/soc/sof/imx/Kconfig

Purpose: NXP i.MX SOF platform configuration for common OF support, i.MX8, and i.MX9.

Important APIs/types/functions: `SND_SOC_SOF_IMX_TOPLEVEL` gates NXP i.MX DSP support and depends on ARM64/compile-test plus SOF OF enumeration. `SND_SOC_SOF_IMX_COMMON` selects OF device glue, SOF core, IPC3, Xtensa, and compressed audio. `SND_SOC_SOF_IMX8` and `SND_SOC_SOF_IMX9` select common support and depend on their firmware/control frameworks.

Control flow: selecting a platform pulls in common i.MX support and the relevant platform driver.

State and persistence: build-time only.

Dependencies and integration points: OF device probing, i.MX DSP IPC, i.MX SCU or SCMI LMM management, Xtensa architecture, and compressed SOF support.

Risks: platform dependencies must match SoC firmware services. Common selection always enables compress support for i.MX.

Test signals: build coverage for i.MX8/i.MX9 and OF probe on matching device trees.
