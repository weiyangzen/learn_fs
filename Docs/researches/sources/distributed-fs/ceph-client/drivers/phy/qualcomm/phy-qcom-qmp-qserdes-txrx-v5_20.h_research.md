# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_20.h

Purpose: Defines QSERDES v5.20 TX/RX lane offsets for a trimmed newer layout. It includes TX drive/lane controls and RX CDR, IVCM, DFE, adaptation, VGA/GM, signal detect, post-calibration, QPI bias, mode-rate, and backup controls.

Important APIs/types/functions: Exports `QSERDES_V5_20_TX_*` and `QSERDES_V5_20_RX_*` macros. Key groups include `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `LANE_MODE_*`, `RX_UCDR_*`, `RX_IVCM_*`, `DFE_*`, `RX_TX_ADPT_CTRL`, `VGA_CAL_*`, `SIGDET_ENABLES`, `RX_MODE_RATE*`, `Q_PI_INTRINSIC_BIAS_RATE32`, and `RX_BKUP_CTRL1`. No functions.

Control flow: None. Consumers use the constants in static init tables applied by QMP helpers.

State and persistence: Stateless address map; hardware state persists after writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used with v5.20 PCS and v5 COM-family tables.

Risks: Versioned RX mode offsets are dense and rate-specific; a single wrong offset can break one speed while lower speeds still pass.

Test signals: Build, link training across rates, equalization, CDR lock, signal-detect, backup behavior, and resume.
