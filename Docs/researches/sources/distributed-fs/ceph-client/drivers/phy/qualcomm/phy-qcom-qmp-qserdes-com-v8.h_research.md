# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v8.h

Purpose: Defines QSERDES v8 common/PLL offsets for newest QMP PCIe/common PHY initialization. It covers mode 0/1 PLL parameters, SSC, clocking, VCO tuning, common config, miscellaneous PLL ECO fields, and ready status.

Important APIs/types/functions: Exports `QSERDES_V8_COM_*` macros such as `SSC_STEP_SIZE*`, `CP_CTRL_MODE*`, `PLL_RCTRL_MODE*`, `PLL_CCTRL_MODE*`, `CORECLK_DIV_MODE*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL_1`, `BG_TIMER`, `PLL_IVCO`, `LOCK_CMP_EN`, `VCO_TUNE_MAP`, `CMN_MISC_1`, `PLL_SPARE_FOR_ECO`, and `C_READY_STATUS`. No code.

Control flow: None locally. `phy-qcom-qmp-pcie.c` and common QMP tables write these offsets during PLL setup.

State and persistence: No software state; programmed PLL/common hardware settings persist while powered.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and directly by `phy-qcom-qmp-pcie.c`.

Risks: v8 introduces ECO/misc fields and high-generation PCIe rate programming. Wrong offsets can cause PLL lock failures or marginal Gen4/Gen5 behavior.

Test signals: Build, PLL lock and C-ready status, PCIe link generation negotiation, clock stability, and power-management retest.
