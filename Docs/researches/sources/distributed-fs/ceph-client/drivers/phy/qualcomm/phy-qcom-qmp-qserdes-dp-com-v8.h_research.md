# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-dp-com-v8.h

Purpose: Defines DisplayPort-specific QSERDES v8 common block offsets for eDP/DP PHY initialization. It contains PLL/SSC/clock fields specialized for the DP common block.

Important APIs/types/functions: Exports `DP_QSERDES_V8_COM_*` macros for mode-specific SSC step size, clock divider, charge pump, PLL R/C, lock compare, dec/div-frac starts, high-speed clock selection, integration loop, VCO tune, common clock enables, reset, config/mode, VCO DC control, additional misc, and `C_READY_STATUS`. No functions.

Control flow: No direct flow. `phy-qcom-edp.c` uses these constants in DP/eDP initialization arrays before common DP PHY enable and status checks.

State and persistence: No in-memory state. DP QSERDES common hardware retains programmed PLL values until reset or reinitialization.

Dependencies and integration points: Included by `phy-qcom-edp.c`; complements shared QMP/eDP PHY code and DP link-rate programming.

Risks: DP common offsets are namespaced separately from generic v8 COM. Mixing them can break DisplayPort PLL programming even if macro shapes look similar.

Test signals: Build, eDP/DP PHY probe, PLL C-ready, link training at supported DP rates, display enable/disable, and suspend/resume.
