# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-mtk-lynxi.c

Purpose: Implements a MediaTek LynxI SGMII/BASE-X PCS phylink helper using regmap-backed SGMII subsystem registers.

Important APIs, types, and functions: `struct mtk_pcs_lynxi` stores regmap, ANA_RGC3 offset, current interface, phylink PCS, flags, and fwnode. `mtk_pcs_lynxi_ops` implements in-band caps, state read, config, autoneg restart, link-up, and disable. Exported APIs are `mtk_pcs_lynxi_create()` and `mtk_pcs_lynxi_destroy()`.

Control flow: Creation verifies device ID and version, allocates a PCS object, stores fwnode/regmap, and advertises SGMII/1000BASE-X/2500BASE-X. Config encodes advertisement, selects SGMII versus BASE-X mode, powers down and resets QPHY on interface change, applies RX/TX polarity from properties, programs analog speed and link timer, updates advertisement/BMCR/mode bits, then powers QPHY back up after a short sleep. Link-up forces speed/duplex when not using in-band negotiation.

State and persistence behavior: `mpcs->interface` caches the active interface to avoid disruptive analog reprogramming. Register programming persists in the PCS hardware until reconfigured or reset. Fwnode reference is held for polarity parsing.

Dependencies and integration points: It depends on regmap, phylink C22 encode/decode helpers, PHY common polarity properties, firmware child node `"pcs"`, and MediaTek consumer headers.

Risks and edge cases: Interface changes intentionally reset/power-cycle QPHY and can interrupt traffic. Polarity defaults can be inverted by legacy `mediatek,pnswap` or per-direction properties. QPHY power-up has a race-sensitive sleep and full-register write to clear problematic states. Creation returns NULL rather than ERR_PTR on ID/version/read failures, so consumers must handle that convention.

Test signals: Verify ID/version rejection, SGMII and BASE-X config, 2500BASE-X analog speed, polarity properties, forced speed/duplex, disable/reconfigure, link timer values, regmap failure injection, and traffic after QPHY power-cycle.
