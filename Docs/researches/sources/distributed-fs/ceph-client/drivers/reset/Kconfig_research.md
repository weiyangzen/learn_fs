# sources/distributed-fs/ceph-client/drivers/reset/Kconfig

Purpose: top-level Kconfig menu for the Linux reset controller framework and many SoC-specific reset providers.

Important APIs/types/functions: defines `ARCH_HAS_RESET_CONTROLLER`, `RESET_CONTROLLER`, and symbols such as `RESET_A10SR`, `RESET_ASPEED`, `RESET_BRCMSTB`, `RESET_EYEQ`, `RESET_GPIO`, `RESET_IMX7`, `RESET_INTEL_GW`, `RESET_K230`, `RESET_NPCM`, `RESET_POLARFIRE_SOC`, and `RESET_QCOM_AOSS`. It also sources submenus for `amlogic`, `hisilicon`, `spacemit`, `starfive`, `sti`, and `tegra`.

Control flow: configuration-time only. If `RESET_CONTROLLER` is enabled, the file exposes individual drivers and uses `depends on`, `select`, and defaults to shape the build graph.

State and persistence: persistent state is the generated kernel `.config`; there is no runtime state.

Dependencies and integration: gates platform drivers on architecture, `COMPILE_TEST`, `HAS_IOMEM`, `MFD_SYSCON`, `REGMAP_MMIO`, `AUXILIARY_BUS`, firmware protocols, GPIO, and vendor subsystems.

Risks and test signals: dependency drift causes link/build failures or missing reset providers. Test with `allmodconfig`, `allyesconfig`, target defconfigs, and dependency-negative builds such as `GPIOLIB=n`, `AUXILIARY_BUS=n`, and `MFD_SYSCON=n`.
