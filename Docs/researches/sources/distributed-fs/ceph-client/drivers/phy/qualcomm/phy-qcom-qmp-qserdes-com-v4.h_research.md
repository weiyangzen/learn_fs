# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v4.h

Purpose: Defines QSERDES v4 common block offsets for PLL/SSC setup, common clocks, lock comparison, VCO calibration/tuning, reset sequencing, and additional control fields.

Important APIs/types/functions: Exports `QSERDES_V4_COM_*` macros, including mode-specific `SSC_STEP_SIZE*`, `CP_CTRL*`, `PLL_RCTRL*`, `PLL_CCTRL*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `INTEGLOOP_*`, `VCO_TUNE*`, `CLK_SELECT`, `PLL_ANALOG`, `SW_RESET`, `CORE_CLK_EN`, `CMN_CONFIG_*`, and `BIN_VCOCAL_HSCLK_SEL`. No executable code.

Control flow: None. The eDP and common QMP drivers include this map and write selected constants through initialization tables.

State and persistence: Constants only. Programmed PLL and common-clock state persists in QSERDES hardware until power/reset.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-edp.c`; used by QMP protocol init tables.

Risks: Common-block PLL configuration is foundational. Wrong lock compare or VCO tune offsets can produce intermittent lock or rate-specific failures.

Test signals: Build, PLL lock polling, eDP/USB/PCIe/UFS link-up where applicable, clock-rate validation, and resume retest.
