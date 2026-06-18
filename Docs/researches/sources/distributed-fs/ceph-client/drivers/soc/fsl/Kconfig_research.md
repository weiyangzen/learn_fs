# sources/distributed-fs/ceph-client/drivers/soc/fsl/Kconfig

Purpose: top-level Kconfig menu for NXP/Freescale QorIQ SoC drivers.

Important configuration: includes submenus for DPAA1 QBMan and QUICC Engine. `FSL_GUTS` selects `SOC_BUS` and supports global utility block SoC identification. `FSL_MC_DPIO` is a tristate depending on `FSL_MC_BUS` and `NET`, selecting `SOC_BUS`, `FSL_GUTS`, and `DIMLIB`. `DPAA2_CONSOLE` exposes MC/AIOP firmware logs. `FSL_RCPM` gates ARM/ARM64 sleep wakeup control.

Control flow and integration: these options determine whether SoC identity, DPAA1 BMan/QMan, DPAA2 DPIO service, firmware console, and RCPM code are compiled.

State and persistence: build-time selection only.

Risks and test signals: risks are dependency gaps between DPAA2 service APIs and networking/MC bus requirements. Test signals are config coverage for Layerscape, COMPILE_TEST, and absence of missing symbols for DIMLIB or FSL_GUTS consumers.
