# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v4.h

Purpose: Supplies a full QSERDES v4 TX/RX lane register map. TX coverage includes BIST, clock buffer, common controls, drive/emphasis, reset, band/interface, resistance, lane mode, PRBS, receiver detect, PWM, VMODE, analog observation, and status. RX coverage includes UCDR gains, auxiliary/JTAG, IDAC, equalizer/adaptor, signal detect, CDR, interface, jitter/SSC, PWM, PI, data/status readbacks, and error counters.

Important APIs/types/functions: Exports roughly 220 `QSERDES_V4_TX_*` and `QSERDES_V4_RX_*` macros. No functions or C types are defined.

Control flow: None. Version-specific QMP tables program selected TX/RX offsets through common register-write helpers.

State and persistence: Header constants only; programmed lane tuning, calibration, and diagnostic state live in hardware.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v4 COM and PCS maps.

Risks: The file mixes writable controls and readback/status offsets. Accidentally writing a status offset or reading a control as status can hide bugs until hardware testing.

Test signals: Build, lane startup, BIST/PRBS if used, equalization, signal detect, error counters, link-up, and power-cycle recovery.
