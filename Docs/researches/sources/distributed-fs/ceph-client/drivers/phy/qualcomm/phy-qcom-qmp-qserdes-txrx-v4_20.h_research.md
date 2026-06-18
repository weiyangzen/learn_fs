# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4_20.h

Purpose: Defines QSERDES v4.20 TX/RX lane delta offsets, mainly TX drive/lane controls and RX UCDR, calibration, adaptation, signal detect, mode, DFE, PI, and margining controls.

Important APIs/types/functions: Exports `QSERDES_V4_20_TX_*` and `QSERDES_V4_20_RX_*` macros, including `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `LANE_MODE_*`, `RX_UCDR_*`, `RX_IVCM_*`, `DFE_*`, `RX_EQ_OFFSET_ADAPTOR_CNTRL1`, `SIGDET_*`, `RX_MODE_00_*`, `Q_PI_INTRINSIC_BIAS_RATE32`, and margin coarse controls. No functions.

Control flow: None. Used by v4.20-specific init tables through the standard QMP table write path.

State and persistence: Stateless offset map; hardware lane state persists after writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; complements v4.20 PCS deltas and v4 COM maps.

Risks: Delta headers omit many base registers. Consumers must combine base and variant constants carefully.

Test signals: Build, platform probe, link training, RX margining, DFE/equalization behavior, and resume.
