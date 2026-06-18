# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v7.h

Purpose: Supplies the QMP v7 PCS common offset subset. It covers reset/start, status, power control, lock detect, refgen, TX de-emphasis/pre-gain, signal detect, receiver detect, RX config, align detect, TX/RX config, and equalization.

Important APIs/types/functions: Exports `QPHY_V7_PCS_*` macros such as `SW_RESET`, `PCS_STATUS1`, `LOCK_DETECT_CONFIG*`, `REFGEN_REQ_CONFIG1`, `G12S1_TXDEEMPH_M6DB`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `RX_CONFIG`, `PCS_TX_RX_CONFIG`, and `EQ_CONFIG*`. No functions or structs.

Control flow: None directly. QMP init tables consume these offsets, and common QMP PHY code performs writes and later status polling.

State and persistence: The header is stateless; hardware retains programmed PCS settings until reset/reinitialization.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and used by newer protocol-specific QMP tables.

Risks: v7 continues the compact map trend but has version-specific offsets. Copying v6 or v8 table entries without checking the namespace can misprogram the PCS.

Test signals: Compile, platform probe, lock/status polling, high-speed link training, equalization stability, and power-management cycles.
