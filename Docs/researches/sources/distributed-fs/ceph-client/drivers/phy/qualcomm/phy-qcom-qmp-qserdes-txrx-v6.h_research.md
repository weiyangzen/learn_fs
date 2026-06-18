# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6.h

Purpose: Defines the QSERDES v6 TX/RX lane offset set, named in the guard as USB v6 but used as a generic v6 lane map. It covers TX clock/drive/lane mode/band/interface and RX UCDR, calibration, DFE, adaptation, VGA/GM, signal detect, RX modes, DFE timer, DCC, VTH, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_V6_TX_*` and `QSERDES_V6_RX_*` macros such as `TX_CLKBUF_ENABLE`, `TX_EMP_POST1_LVL`, `TX_DRV_LVL`, `LANE_MODE_*`, `RX_UCDR_*`, `RX_IVCM_*`, `RX_DFE_*`, `RX_MODE_00_*`, and `RX_SIGDET_CAL_TRIM`. No functions.

Control flow: None. Static QMP tables apply these offsets through common register writers.

State and persistence: Stateless constants; hardware lane settings persist until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v6 COM/PCS maps.

Risks: Include guard naming says `TXRX_USB_V6`, which can obscure generic use. Namespace clarity matters when adding protocol-specific v6 variants.

Test signals: Build, lane startup, CDR lock, signal detect, equalization, high-speed link-up, and resume.
