# sources/distributed-fs/ceph-client/sound/soc/mxs/Kconfig

Purpose: defines Kconfig options for Freescale MXS ASoC support and the MXS SGTL5000 machine driver.

Important APIs/types/functions: `SND_MXS_SOC` is the menuconfig root, depending on `ARCH_MXS || COMPILE_TEST` and `COMMON_CLK`, and selecting `SND_SOC_GENERIC_DMAENGINE_PCM`. `SND_SOC_MXS_SGTL5000` depends on `I2C` and selects `SND_SOC_SGTL5000`.

Control flow: Kconfig selection enables compilation of SAIF/PCM support and, optionally, the SGTL5000 board driver.

State and persistence: no runtime state; it persists build-time feature relationships.

Dependencies and integration: feeds `sound/soc/mxs/Makefile` object selection and ensures DMAEngine PCM and codec dependencies are available.

Risks: board audio will not build unless the parent menu is enabled; SGTL5000 selection assumes I2C. `COMPILE_TEST` allows non-MXS builds but runtime hardware dependencies still apply.

Test signals: `allyesconfig`, `allmodconfig`, MXS defconfig, and dependency resolution for SGTL5000 with I2C enabled/disabled.
