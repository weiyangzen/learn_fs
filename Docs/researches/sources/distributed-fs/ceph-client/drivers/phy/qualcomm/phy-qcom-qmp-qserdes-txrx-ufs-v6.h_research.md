# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v6.h

Purpose: Provides UFS-specific QSERDES v6 TX/RX offsets for MPHY/UFS lane initialization. It includes TX driver/emphasis, lane mode, interface select, UCDR/PI, RX mode, signal detect, calibration, DFE, GM, QPI, and DLL tuning fields.

Important APIs/types/functions: Exports `QSERDES_UFS_V6_TX_*` and `QSERDES_UFS_V6_RX_*` macros. Notable groups are `TX_LANE_MODE_*`, `TX_INTERFACE_SELECT`, `RX_UCDR_*`, `RX_MODE_RATE_*`, `RX_SIGDET_*`, `RX_DFE_*`, `RX_Q_PI_INTRINSIC_BIAS_RATE32`, and `RX_DLL0_FTUNE_CTRL`. No functions.

Control flow: No local flow. `phy-qcom-qmp-ufs.c` uses these constants in UFS PHY init sequences before link startup.

State and persistence: Stateless offsets; hardware settings persist until UFS PHY reset/power mode change.

Dependencies and integration points: Included by `phy-qcom-qmp-ufs.c`; paired with UFS PCS headers and common QMP helpers.

Risks: UFS power modes and gears depend on precise RX/TX tuning. Wrong offsets can cause boot storage link failures.

Test signals: Build, UFS host probe, gear negotiation, HS mode entry, link startup, hibern8/resume, and storage I/O.
