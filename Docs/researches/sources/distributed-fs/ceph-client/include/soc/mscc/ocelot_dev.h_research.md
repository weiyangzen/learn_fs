# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_dev.h

Purpose: defines bitfields for Ocelot per-port DEV blocks, including port reset and link speed, MAC enable/mode/tag/IFG/half-duplex/debug/sticky status, Energy Efficient Ethernet, PTP prediction, MAC Merge preemption status, 1G PCS/SGMII/auto-negotiation/LPI/test-pattern controls, and 100FX PCS controls.

Important APIs/types/functions: macro-only API. Key groups are `DEV_CLOCK_CFG_*`, `DEV_MAC_*`, `DEV_EEE_CFG_*`, `DEV_MM_*`, `PCS1G_*`, and `DEV_PCS_FX100_*`. Encoder and extractor macros provide the values consumed by `ocelot_port` setup, phylink, MAC Merge, and link-state paths.

Control flow: none in the header. Consumers sequence reset, PCS/MAC mode setup, link speed encoding, enabling RX/TX, then status or sticky-bit inspection. Auto-negotiation and LPI behavior is driven by hardware once the fields are programmed.

State and persistence: persistent state is in port device registers. Sticky status bits persist until cleared by the driver. MAC Merge verification and PCS auto-negotiation status represent hardware progress rather than software-owned state.

Dependencies and integration: uses `BIT()`/`GENMASK()` and is included by the MSCC Ethernet stack, DSA Ocelot/Felix code, and MAC Merge support. It integrates with phylink, ethtool link mode reporting, frame preemption, and PTP timing support.

Risks: wrong reset ordering or speed encodings can leave the MAC/PCS unusable. Sticky-bit handling can lose diagnostics if cleared too eagerly. MAC Merge fields affect express/preemptible traffic behavior, so regressions can break TSN/preemption tests. Test signals include link-up/down across speeds, SGMII auto-negotiation, EEE, 100FX, frame preemption, and register readback.
