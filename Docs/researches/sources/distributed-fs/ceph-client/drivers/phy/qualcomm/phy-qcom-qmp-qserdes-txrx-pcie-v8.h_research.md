# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-pcie-v8.h

Purpose: Defines PCIe-specific QSERDES v8 TX/RX offsets. It targets PCIe lane controls for resistance codes, lane modes, driver emphasis, band selection, rate-specific adaptation, UCDR gains, signal detect, RX band/termination, RX mode tables, EOM, auxiliary data, threshold calibration, and GM calibration.

Important APIs/types/functions: Exports `QSERDES_V8_PCIE_TX_*` and `QSERDES_V8_PCIE_RX_*` macros. No functions or types are defined.

Control flow: None locally. `phy-qcom-qmp-pcie.c` uses these constants in PCIe Gen-rate initialization arrays that the common QMP code writes during PHY bring-up.

State and persistence: Header constants only. Programmed TX/RX lane state persists in QSERDES hardware until reset, powerdown, or rate-specific reprogramming.

Dependencies and integration points: Directly included by `phy-qcom-qmp-pcie.c`; paired with `phy-qcom-qmp-qserdes-com-v8.h` and v8 PCIe PCS headers.

Risks: PCIe Gen4/Gen5 tuning is sensitive. Wrong rate-specific RX mode or UCDR offset may only fail at higher negotiated speeds or under marginal signal conditions.

Test signals: Build, PCIe link training across supported generations, receiver detection, equalization, EOM/margin checks, and resume.
