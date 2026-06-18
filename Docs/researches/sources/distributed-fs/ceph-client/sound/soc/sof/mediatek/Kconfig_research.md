# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/Kconfig

Purpose: Defines build-time enablement for SOF on MediaTek audio DSP platforms.

Important symbols: `SND_SOC_SOF_MTK_TOPLEVEL` is the user-visible ARM64/compile-test gate and depends on `SND_SOC_SOF_OF`. `SND_SOC_SOF_MTK_COMMON` is a non-user-selectable tristate selected by SoC drivers; it selects SOF OF device support, core SOF, IPC3, Xtensa support, and compressed audio. `SND_SOC_SOF_MT8186` and `SND_SOC_SOF_MT8195` are user-visible tristates for MT8186 and MT8195 and both depend on `MTK_ADSP_IPC`.

Control flow and integration: Enabling a SoC option selects the shared common object and pulls the appropriate subdirectory from the Makefiles. Both SoC drivers are IPC3-only in their descriptors, so selecting IPC3 here matches runtime capability.

State and persistence: No runtime state; this is build configuration that controls which modules are compiled and which dependencies are forced into the kernel/module build.

Risks: Missing `MTK_ADSP_IPC` prevents SoC options even if device tree matches. Common selects `SND_SOC_SOF_COMPRESS`, which may expand build surface. Adding IPC4 MediaTek support would require revisiting the forced IPC3 select and SoC descriptors.

Test signals: Kconfig allmodconfig/allyesconfig coverage, ARM64 and COMPILE_TEST builds, dependency visibility when `MTK_ADSP_IPC=n`, and module link checks for common plus each SoC object.
