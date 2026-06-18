# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6_30.h

Purpose: Defines the small QMP v6.30 PCS delta used where selected de-emphasis, signal-detect, electrical-idle, TX/RX config, and equalization registers shifted from base v6.

Important APIs/types/functions: Exports `QPHY_V6_30_PCS_G12S1_TXDEEMPH_M6DB`, `RX_SIGDET_LVL`, `COM_ELECIDLE_DLY_SEL`, `TX_RX_CONFIG1`, `TX_RX_CONFIG2`, `EQ_CONFIG1`, `EQ_CONFIG4`, and `EQ_CONFIG5`. It defines no code.

Control flow: No local control flow. PCIe and common QMP tables refer to these offsets and the shared init path writes them.

State and persistence: No state in the header. Values written to these offsets persist in PCS link-training hardware until reset or reprogramming.

Dependencies and integration points: Included by `phy-qcom-qmp-pcie.c`; used with v6.30 PCIe PCS tables and common QMP helpers.

Risks: The naming overlaps with PCIe-specific v6.30 PCS headers, so developers must keep common PCS and protocol-specific PCS offsets distinct.

Test signals: Build for v6.30 users, PCIe link training, equalization across supported generations, electrical-idle transitions, and resume.
