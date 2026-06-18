# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-pll.h

Purpose: Defines a QSERDES PLL-specific register map used where PLL offsets are separated from the broader COM namespace. It covers SSC, clock dividers, charge pump, PLL controls, lock compare, divider fractional starts, VCO tune, bias/clock, reset, and core clock fields.

Important APIs/types/functions: Exports `QSERDES_PLL_*` macros such as `SSC_STEP_SIZE*`, `CLK_EP_DIV`, `CP_CTRL`, `PLL_RCTRL`, `PLL_CCTRL`, `LOCK_CMP*`, `DEC_START`, `DIV_FRAC_START*`, `HSCLK_SEL`, `VCO_TUNE*`, `PLL_IVCO`, `RESETSM_CNTRL*`, `LOCK_CMP_EN`, and `CORECLK_DIV_MODE1`. No functions or types.

Control flow: None. Included by the QMP umbrella header for tables that address PLL fields through a PLL block rather than COM.

State and persistence: Stateless constants; runtime PLL state is hardware-resident.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by QMP configuration tables and common PHY register helpers.

Risks: It overlaps semantically with COM headers. Selecting PLL-vs-COM namespaces incorrectly can write valid-looking values to invalid offsets.

Test signals: Build, PLL lock, rate generation, link-up, and suspend/resume re-lock.
