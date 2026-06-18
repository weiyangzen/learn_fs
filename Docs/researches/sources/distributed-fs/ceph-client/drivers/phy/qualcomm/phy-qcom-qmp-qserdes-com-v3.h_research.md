# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-com-v3.h

Purpose: Provides the QSERDES v3 common block register map for PLL, SSC, clocking, reset, calibration, and common-mode controls.

Important APIs/types/functions: Exports `QSERDES_V3_COM_*` macros for mode 0/1 PLL programming, `SSC_*`, `CP_CTRL*`, `PLL_RCTRL*`, `PLL_CCTRL*`, `LOCK_CMP*`, `DEC_START*`, `DIV_FRAC_START*`, `HSCLK_SEL`, `INTEGLOOP_*`, `VCO_TUNE*`, `BG_TIMER`, `CLK_ENABLE1`, `SYS_CLK_CTRL`, `PLL_IVCO`, `RESETSM_*`, and `CMN_VREG_SEL`. It defines no functions.

Control flow: None in the header. QMP init arrays use these offsets, followed by generic PLL enable and lock polling in protocol drivers.

State and persistence: Hardware state is created only by writes to the common QSERDES block and persists until reset/powerdown.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; feeds QMP USB/PCIe/UFS and related SoC tables.

Risks: v3 register names are similar to v2/v4 but offsets differ. Table copy errors can break PLL lock or program the wrong VCO mode.

Test signals: Compile, PLL lock, link-up at expected rate, SSC enablement, and power-management recovery.
