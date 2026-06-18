# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-txrx-v8.h

Purpose: Defines the base QSERDES v8 TX/RX lane offsets for non-PCIe-specialized v8 tables. It includes TX drive/emphasis, resistance, bias, high-Z, polarity, lane modes, receiver-detect level, and PI QEC; RX UCDR, auxiliary data, VGA/GM/equalizer, signal detect, RX mode tables, DFE, DCC, VTH, and signal-detect calibration.

Important APIs/types/functions: Exports `QSERDES_V8_TX_*` and `QSERDES_V8_RX_*` macros. No functions, structs, or global data.

Control flow: None locally. The umbrella QMP header exposes these constants to SoC tables, and common QMP code writes them during lane initialization.

State and persistence: Stateless offsets; hardware lane state persists until reset/rewrite.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; paired with v8 COM, PCS, USB, PCIe, and LALB maps depending on platform.

Risks: PCIe v8 has its own TXRX header with extra rate fields. Using this base map for PCIe-specific tables can omit or misaddress required tuning.

Test signals: Build, lane bring-up, CDR/signal detect, equalization, high-speed link-up, and resume.
