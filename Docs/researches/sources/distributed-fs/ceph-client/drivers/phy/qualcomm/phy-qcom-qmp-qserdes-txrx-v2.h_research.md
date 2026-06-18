# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v2.h

Purpose: Provides the QSERDES v2 TX/RX lane offset subset used by versioned QMP PHY tables. It includes TX clock buffer, emphasis/drive, reset, lane mode, receiver detect, and RX UCDR/equalization/signal-detect/mode fields.

Important APIs/types/functions: Exports `QSERDES_V2_TX_*` and `QSERDES_V2_RX_*` macros, including `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `RESET_TSYNC_EN`, `LANE_MODE`, `RCV_DETECT_LVL*`, `RX_UCDR_*`, `RX_EQU_ADAPTOR_CNTRL*`, `RX_SIGDET_*`, and `RX_MODE_00/01`. No functions.

Control flow: No direct control flow. Static init tables write TX/RX registers through common QMP helpers after common PLL setup.

State and persistence: Stateless constants. Lane state persists in QSERDES hardware until reset/reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and used by legacy QMP protocol tables.

Risks: TX and RX offsets share one header but target different base regions. Consumers must use the right base address when applying each table.

Test signals: Compile, lane bring-up, signal detect, equalization, link-up, and suspend/resume.
