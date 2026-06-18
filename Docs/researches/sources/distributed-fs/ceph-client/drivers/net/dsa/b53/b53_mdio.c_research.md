# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mdio.c

Purpose: B53 transport for Broadcom pseudo-PHY MDIO register access.

Important APIs/types/functions: `b53_mdio_op()` handles page selection, register opcode writes, and completion polling. Width-specific `b53_mdio_read*()`/`write*()` marshal 8/16/32/48/64-bit values through 16-bit MDIO data registers. `b53_mdio_probe()` validates address/OUI and registers the common B53 switch.

Control flow: probe leaves non-management MDIO addresses to PHY drivers, validates Broadcom OUIs, handles a BCM7445D0 bus defer quirk, allocates B53 with MDIO ops, forces page refresh, and calls `b53_switch_register()`. Each access sets page if changed, writes address/op, polls completion, and reads/writes data words.

State and persistence behavior: `current_page` caches the selected hardware page; `dev->priv`/`dev->bus` point to the MDIO bus. No persistent state.

Dependencies and integration points: MDIO/PHY APIs, `BRCM_PSEUDO_PHY_ADDR`, OF matching, and common B53 exported helpers.

Risks: short polling window can fail on slow hardware; page cache must be invalidated after reset; PHY read error propagation is weak; OUI filter may exclude future variants.

Test signals: supported/unsupported OUI probe, page switching, all access widths, timeout injection, reset page invalidation, and DSA remove/shutdown cycles.
