# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v2.h

Purpose: Defines the QSERDES v2 common/PLL register offsets used by QMP PHY PLL programming. It covers SSC, clock dividers, charge pump, PLL R/C controls, lock compare, divider fractional values, VCO tune, bias/clock enables, reset state machine, and mode-specific PLL fields.

Important APIs/types/functions: Exports `QSERDES_V2_COM_*` macros such as `SSC_*`, `CLK_EP_DIV*`, `CP_CTRL*`, `PLL_RCTRL*`, `PLL_CCTRL*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL`, `VCO_TUNE*`, `PLL_IVCO`, and `CORECLK_DIV_MODE1`. No functions or types.

Control flow: None. Static QMP init tables write these offsets before the common driver enables PLLs and waits for lock.

State and persistence: No software state. PLL configuration persists in common QSERDES hardware while the PHY remains powered.

Dependencies and integration points: Included by `phy-qcom-qmp.h` for legacy QMP USB/PCIe/UFS users.

Risks: PLL offsets directly affect frequency synthesis. A wrong mode or fractional divider offset can create clock lock failures or unstable links.

Test signals: Build, PLL lock, generated reference rate correctness, link-up, SSC behavior, and resume after power collapse.
