# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-ufs-v7.h

Purpose: Defines UFS-specific QSERDES v7 TX/RX offsets for newer UFS PHY lanes. The map covers TX drive/emphasis, band and interface selection, lane modes, UCDR gains, RX calibration, signal detection, mode-rate tables, DFE, QPI bias, PI controls, backup, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_UFS_V7_TX_*` and `QSERDES_UFS_V7_RX_*` macros. It has no functions or data types.

Control flow: No code here. `phy-qcom-qmp-ufs.c` references the macros in static register tables applied during UFS PHY initialization and power mode setup.

State and persistence: Only immutable offsets. UFS lane hardware retains written values until reset or mode switch reprogramming.

Dependencies and integration points: Included by the UFS QMP driver and paired with UFS PCS v6 headers where SoC tables require it.

Risks: UFS v7 has separate names from generic v7 TX/RX. Mixing generic and UFS-specific maps can cause subtle high-speed mode failures.

Test signals: Build, UFS link startup, HS gear changes, hibern8 enter/exit, storage stress I/O, and suspend/resume.
