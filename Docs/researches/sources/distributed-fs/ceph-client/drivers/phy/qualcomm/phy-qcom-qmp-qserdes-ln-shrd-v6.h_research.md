# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-ln-shrd-v6.h

Purpose: Supplies QSERDES v6 lane-shared offsets for UCDR, RX mode, DFE/CTLE, PI, and summer calibration controls.

Important APIs/types/functions: Exports `QSERDES_V6_LN_SHRD_*` macros, including `UCDR_PI_CTRL1/2`, `RXCLK_DIV2_CTRL`, `RX_Q_EN_RATES`, `DFE_DAC_ENABLE1/2`, `RX_MODE_RATE*`, `RX_Q_PI_INTRINSIC_BIAS_RATE*`, `RX_MARG_VERTICAL_CODE`, `PI_CTRL*`, `QPI_CTRL*`, and `RX_SUMMER_CAL_SPD_MODE`. No code exists.

Control flow: No local flow. QMP init arrays write these shared-lane registers while per-lane TX/RX maps handle lane-specific programming.

State and persistence: Constants only; programmed lane-shared CDR/equalizer state persists in hardware until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; complements v6 TX/RX headers.

Risks: Shared-lane fields can affect multiple lanes. Wrong values or offsets may break multi-lane behavior even when each per-lane table is correct.

Test signals: Build, multi-lane link training, CDR stability, equalizer convergence, lane margin, and resume.
