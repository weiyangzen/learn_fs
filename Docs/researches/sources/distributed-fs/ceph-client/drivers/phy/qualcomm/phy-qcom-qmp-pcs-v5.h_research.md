# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5.h

Purpose: Defines the reduced QMP v5 PCS offset set needed by USB/PCIe PHY tables. It keeps common reset/start, status, lock detect, refgen request, signal detect, receiver detect, rate slew, alignment, TX/RX config, and equalization registers.

Important APIs/types/functions: Exports `QPHY_V5_PCS_*` macros such as `SW_RESET`, `PCS_STATUS1`, `POWER_DOWN_CONTROL`, `START_CONTROL`, `LOCK_DETECT_CONFIG*`, `REFGEN_REQ_CONFIG1`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `RX_CONFIG`, `PCS_TX_RX_CONFIG`, and `EQ_CONFIG*`. No code is defined.

Control flow: No local control flow. QMP init arrays write these offsets during PHY initialization before common start and status polling.

State and persistence: Hardware-only state; the header contains immutable numeric constants.

Dependencies and integration points: Included by `phy-qcom-qmp.h`, and used with USB/PCIe QMP configuration tables.

Risks: `CDR_RESET_TIME` and `RX_CONFIG` share offset `0x1b0` under different semantic names, so table authors must choose the name matching the protocol block meaning.

Test signals: Build, probe, PCS lock, RX detect, alignment, equalization, and link-up on v5 PHY platforms.
