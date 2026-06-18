# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx.h

Purpose: Provides the original/base QSERDES TX and RX lane register maps for QMP v2-era PHYs. TX covers BIST, clock/common controls, drive/emphasis, reset, band/interface, resistance, debug, lane mode, receiver detect, PRBS, PWM, VMODE, and status. RX covers UCDR, auxiliary/JTAG, termination, IDAC, equalizer, signal detect, CDR, interface, jitter/SSC, PWM, PI, data/readback, calibration status, and error counters.

Important APIs/types/functions: Exports `QSERDES_TX_*` and `QSERDES_RX_*` macros, roughly 193 offsets total. It defines no functions or C types.

Control flow: No direct flow. The umbrella QMP header includes it and static init tables use these constants with TX/RX base addresses.

State and persistence: Stateless constants. Runtime lane state exists only in hardware after writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by legacy QMP protocol drivers and tables.

Risks: This unversioned namespace is easy to misuse for later QSERDES revisions. TX and RX sections also require correct base selection by the caller.

Test signals: Compile, lane initialization, signal detect, equalizer convergence, BIST/error counters where used, link-up, and resume.
