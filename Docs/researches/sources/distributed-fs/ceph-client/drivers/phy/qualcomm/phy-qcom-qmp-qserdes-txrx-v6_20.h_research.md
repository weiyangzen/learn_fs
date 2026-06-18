# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v6_20.h

Purpose: Provides QSERDES v6.20 PCIe TX/RX lane offsets. It covers TX drive/emphasis, lane modes, and RX UCDR rate gains, IVCM, DFE, adaptation, VGA/GM, signal detect, phpre, post-calibration, QPI bias, rate2/rate3 mode tables, and backup control.

Important APIs/types/functions: Exports `QSERDES_V6_20_TX_*` and `QSERDES_V6_20_RX_*` macros. No functions or types are defined.

Control flow: None. PCIe-oriented QMP init arrays write these offsets as part of lane setup after common PLL programming.

State and persistence: Constants only; hardware lane configuration persists until reset or rate reprogramming.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; used with v6.20 PCS/PCIe tables.

Risks: The include guard identifies it as PCIe v6.20, so using it for non-PCIe modes should be deliberate and backed by hardware documentation.

Test signals: Build, PCIe link training by generation, CDR/equalization stability, receiver detection, and resume.
