# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v5_20.h

Purpose: Provides QMP v5.20 PCS offset overrides for signal mux, lock-detect, TX pre-gain, signal-detect, alignment, and equalization fields.

Important APIs/types/functions: Exports `QPHY_V5_20_PCS_*` macros for `INSIG_SW_CTRL7`, `INSIG_MX_CTRL7`, lock-detect config, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, `ALIGN_DETECT_CONFIG*`, and `EQ_CONFIG*`. It has no functions or structures.

Control flow: None. The macros are used by version-specific init tables and then applied by common QMP register-write flow.

State and persistence: Contains no state. Programmed values affect PCS muxing, lock detection, signal thresholds, alignment, and equalization until the PHY is reset or retuned.

Dependencies and integration points: Included from `phy-qcom-qmp.h`; paired with v5.20 SoC tables in QMP protocol drivers.

Risks: Small offset shifts are easy to miss during SoC enablement. Incorrect align/equalization offsets can pass compilation but fail only as marginal high-speed links.

Test signals: Version-specific platform probe, PCS lock, link-up at all supported rates, eye/equalization stability, and suspend/resume recovery.
