# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v7.h

Purpose: Provides QSERDES v7 TX/RX lane offsets. It covers TX clock/reset/pre-stall, band/interface, resistance, lane modes, receiver detect, driver emphasis, VMODE and PI QEC; RX UCDR, auxiliary data, adaptation thresholds, VGA/GM, equalizer, IDAC timing, signal detect, RX mode tables, DFE, DCC, VTH, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_V7_TX_*` and `QSERDES_V7_RX_*` macros. No functions or C types.

Control flow: None. QMP tables program selected v7 lane offsets after common PLL setup.

State and persistence: No software state; lane configuration and calibration state persist in hardware until reset or retuning.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v7 COM/PCS maps.

Risks: v7 and v8 maps are similar but not identical. Using v8 macros or assumptions in v7 tables can corrupt lane tuning.

Test signals: Build, lane startup, signal-detect, CDR lock, equalization, rate-specific link training, and suspend/resume.
