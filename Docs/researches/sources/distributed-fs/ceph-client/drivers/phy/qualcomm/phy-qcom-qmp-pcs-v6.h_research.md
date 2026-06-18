# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcs-v6.h

Purpose: Supplies the base QMP v6 PCS offset subset for USB/PCIe PHY initialization. It mirrors the compact v5-style map with updated v6 naming.

Important APIs/types/functions: Exports `QPHY_V6_PCS_*` macros for reset, `PCS_STATUS1`, power control, start, lock-detect configs, refgen request, `G12S1_TXDEEMPH_M6DB`, `G3S2_PRE_GAIN`, `RX_SIGDET_LVL`, receiver detect, rate slew, `RX_CONFIG`, align detect, `PCS_TX_RX_CONFIG`, and equalization configs.

Control flow: No code executes. Constants are consumed by static PHY tables and written by common QMP initialization helpers.

State and persistence: No in-memory state. Register values written through these offsets configure PCS state until reset/powerdown.

Dependencies and integration points: Included from `phy-qcom-qmp.h`; used by common USB/PCIe QMP platform descriptors.

Risks: Base v6, v6.20, v6.30, and v6 N4 are close but not interchangeable. Offset mistakes are hardware-visible and often appear as link-training timeouts.

Test signals: Build, probe, PCS status polling, Gen/rate-specific link-up, equalization, receiver detect, and low-power transition tests.
