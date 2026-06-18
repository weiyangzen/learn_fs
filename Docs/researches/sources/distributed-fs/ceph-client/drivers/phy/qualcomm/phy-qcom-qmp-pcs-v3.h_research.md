# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v3.h

Purpose: Defines the full QMP v3 PCS offset map for USB/PCIe style PHYs. It expands v2 with TX amplitude/de-emphasis groups, receiver-detect timing, LFPS timers, equalization training, BIST/PRBS, debug/status, oscillator-detect, and refgen request controls.

Important APIs/types/functions: Exports `QPHY_V3_PCS_*` macros for reset/start, TX magnitude and deemphasis levels, power states, lock detect, FLL, autonomous mode, signal detect, test/BIST, revision IDs, debug buses, wake delays, and `REFGEN_REQ_CONFIG*`. No functions or types exist.

Control flow: None locally. Static QMP init arrays write selected offsets, then the generic QMP power-on path polls PCS status and lock bits.

State and persistence: All state is hardware-resident. Writes to these offsets configure signal quality, timing, test, and low-power behavior until reset or another table write.

Dependencies and integration points: Included through `phy-qcom-qmp.h`; consumed by protocol-specific QMP PHY drivers and their SoC configuration tables.

Risks: The dense map mixes operational and diagnostic registers. Confusing status/debug offsets with writable configuration offsets can cause non-obvious link-training failures.

Test signals: Build for v3 users, PCS lock/status polling, link-up across supported rates, LFPS or electrical-idle behavior, and BIST/debug register sanity checks when available.
