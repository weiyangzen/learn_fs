# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v5.h

Purpose: Provides the QSERDES v5 TX/RX lane register map. It covers TX BIST, drive/emphasis, reset, band/interface, resistance, lane modes, PRBS, receiver detect, status/debug, and PWM; RX UCDR, auxiliary/JTAG, IDAC, IVCM, DFE, equalization, VGA/VTH/GM calibration, signal detect, CDR/interface, jitter/SSC, mode tables, margining, QPI/PI, data readbacks, and backup/status registers.

Important APIs/types/functions: Exports more than 200 `QSERDES_V5_TX_*` and `QSERDES_V5_RX_*` macros. There are no C functions or structures.

Control flow: None. QMP protocol tables reference the offsets and shared helpers write them during lane initialization.

State and persistence: Only numeric constants. Lane tuning and calibration state is in hardware until reset/reprogramming.

Dependencies and integration points: Included by `phy-qcom-qmp.h` and `phy-qcom-sgmii-eth.c`; paired with v5 COM/PCS maps.

Risks: Broad protocol reuse means a macro can be valid but inappropriate for a given PHY mode. Care is needed around margining and backup/status fields.

Test signals: Build, lane bring-up, link training, SGMII/USB/PCIe/UFS protocol tests where applicable, margin/error status, and resume.
