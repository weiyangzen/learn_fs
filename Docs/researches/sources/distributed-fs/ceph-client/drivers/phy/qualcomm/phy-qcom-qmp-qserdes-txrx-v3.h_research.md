# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v3.h

Purpose: Defines QSERDES v3 TX/RX lane offsets. It is a compact map for TX emphasis/drive/lane controls and RX UCDR, signal-detect, equalizer, and mode-rate programming.

Important APIs/types/functions: Exports `QSERDES_V3_TX_*` and `QSERDES_V3_RX_*` macros, including TX drive/emphasis and lane mode plus RX `UCDR_*`, `RX_EQU_ADAPTOR_CNTRL*`, `SIGDET_*`, and mode registers. No functions or structures.

Control flow: No local flow. QMP init tables consume these constants and shared QMP code performs writes during lane setup.

State and persistence: No software state; hardware lane settings persist until reset or later table writes.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used by v3-generation USB/PCIe/UFS descriptors.

Risks: The v3 map resembles v2 but should not be treated as identical. Incorrect namespace selection can break signal detect or equalization while still compiling cleanly.

Test signals: Build, probe, PLL plus lane startup, signal detect, link training, and resume.
