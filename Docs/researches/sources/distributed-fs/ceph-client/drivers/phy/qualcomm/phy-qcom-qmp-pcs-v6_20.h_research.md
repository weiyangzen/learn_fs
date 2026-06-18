# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_20.h

Purpose: Provides QMP v6.20 PCS offset overrides for selected TX de-emphasis, pre-gain, signal-detect, electrical-idle delay, TX/RX config, and equalization registers.

Important APIs/types/functions: Exports `QPHY_V6_20_PCS_G12S1_TXDEEMPH_M6DB`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `COM_ELECIDLE_DLY_SEL`, `TX_RX_CONFIG1`, `TX_RX_CONFIG2`, `EQ_CONFIG4`, and `EQ_CONFIG5`. No functions or types.

Control flow: None. These constants are chosen by v6.20-specific init tables and applied by the common QMP register writer.

State and persistence: Immutable address definitions only; programmed values persist in PCS hardware until reset/rewrite.

Dependencies and integration points: Included in `phy-qcom-qmp.h` and directly included by `phy-qcom-qmp-pcie.c` for v6.20 PCIe tables.

Risks: This delta header does not restate base v6 offsets, so SoC table authors must combine the right base and variant constants deliberately.

Test signals: v6.20 platform build/probe, PCIe or USB link training, electrical-idle behavior, de-emphasis tuning, and equalization margin.
