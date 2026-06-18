# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6-n4.h

Purpose: Defines the QMP v6 N4 PCS register subset for USB/PCIe-style PHYs. The map covers reset, status, power/start, power-state config, lock detect, refgen request, signal detect, receiver detect, rate slew, RX config, alignment, TX/RX config, and equalization.

Important APIs/types/functions: Exports `QPHY_V6_N4_PCS_*` constants, including `POWER_STATE_CONFIG1`, `LOCK_DETECT_CONFIG1..6`, `RX_SIGDET_LVL`, `RCVR_DTCT_DLY_P1U2_*`, `RX_CONFIG`, `ALIGN_DETECT_CONFIG*`, and `EQ_CONFIG*`. No functions or types.

Control flow: No executable logic. SoC tables reference these constants and the shared QMP driver writes them during initialization.

State and persistence: Immutable offsets only. Hardware state persists after register writes until reset or reconfiguration.

Dependencies and integration points: Included by `phy-qcom-qmp.h` for common QMP SoC configuration code.

Risks: N4 has its own namespace despite similarity to v6. Mixing `QPHY_V6_N4_*` and base `QPHY_V6_*` constants can target wrong offsets on newer nodes.

Test signals: Build for N4 users, probe, power-state behavior, PCS lock, signal detect, and stable USB/PCIe link training.
