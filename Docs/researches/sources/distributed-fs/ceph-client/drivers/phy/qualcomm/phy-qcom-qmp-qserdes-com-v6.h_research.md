# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v6.h

Purpose: Defines QSERDES v6 common block offsets for PLL mode programming, SSC, clocking, lock compare, divider programming, VCO tune, reset, common config, adaptive PLL controls, and readiness status.

Important APIs/types/functions: Exports `QSERDES_V6_COM_*` macros, including `SSC_STEP_SIZE*`, `CP_CTRL_MODE*`, `PLL_RCTRL_MODE*`, `PLL_CCTRL_MODE*`, `CORECLK_DIV_MODE*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL_1`, `BG_TIMER`, `PLL_IVCO`, `LOCK_CMP_EN`, `VCO_TUNE_MAP`, `CORE_CLK_EN`, `CMN_MODE`, `PLL_CCTRL_ADAPTIVE_MODE1`, and status fields. No functions.

Control flow: None in this file. QMP PCIe/eDP/common tables program the common block, then generic code waits for PLL/common readiness.

State and persistence: Immutable offset definitions. Writes persist in QSERDES common hardware until reset/powerdown.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-edp.c`; heavily used by `phy-qcom-qmp-pcie.c`.

Risks: Adaptive PLL and mode-specific controls are rate-sensitive. Offset mistakes may only appear at higher link generations.

Test signals: Build, PLL lock, C-ready status, PCIe/eDP link training, rate switching, and resume.
