# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5_5nm.h

Purpose: Supplies a large QSERDES v5 5nm TX/RX lane map. TX covers BIST, drive/emphasis, reset, lane mode, receiver detect, PRBS, VMODE, PI/QEC, band/interface, debug and backup. RX covers rate-indexed UCDR fastlock/gain, IDAC/IVCM, DFE, adaptation, VGA/VTH/GM, equalizer, signal detect, CDR, jitter/SSC, RX modes, DCC, margining, QPI/PI, readbacks, and calibration status.

Important APIs/types/functions: Exports about 315 `QSERDES_V5_5NM_TX_*` and `QSERDES_V5_5NM_RX_*` macros. No functions or types.

Control flow: None locally. QMP tables select these offsets for 5nm PHY layouts and common helpers apply the writes.

State and persistence: The header is immutable. Runtime lane/calibration/margin state lives in hardware until reset or retuning.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v5/v5.20 common and PCS descriptors as SoC tables require.

Risks: This map has many rate-indexed and status registers. Copy/paste or base-version mixups can produce failures isolated to specific gears/generations or diagnostics.

Test signals: Build, high-speed link training at each supported rate, RX margining, DCC/calibration status, error counters, and suspend/resume.
