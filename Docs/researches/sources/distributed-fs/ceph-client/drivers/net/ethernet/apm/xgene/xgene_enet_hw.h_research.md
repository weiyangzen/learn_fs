## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_hw.h

Purpose: declares X-Gene1 hardware register constants, descriptor encodings, bit helpers, ring layout helpers, error codes, and GMAC/ring exported symbols.

Important APIs, types, and functions: inline `xgene_set_bits` and `xgene_get_bits`, resource-manager enum, ring CSR offsets, ring type/mode constants, descriptor field positions, buffer pool helpers, MAC/stat register offsets, MDIO fields, clock/reset bits, error enums, and helper prototypes such as `xgene_enet_parse_error`, `xgene_enet_wr_mac`, `xgene_enet_rd_mac`, `xgene_enet_rd_stat`, MDIO/PHY functions, and extern operation tables.

Control flow, state, and dependencies: included by most original X-Gene C files and paired with `xgene_enet_hw.c`. It has no live state, but its macros define how software interprets descriptor and register state.

Integration points: ring creation in `xgene_enet_main.c`, ring setup in `xgene_enet_hw.c`, X-Gene2 ring code, ethtool stats, and MAC variants all depend on these definitions.

Risks: any bitfield change affects DMA descriptor ownership, buffer length decoding, ring IDs, interrupt mode, and MAC/MDIO access. Header-level helper semantics must remain consistent with existing `SET_VAL`/`GET_VAL` call sites.

Test signals: compile all original driver objects; runtime validation should include descriptor ownership transitions, ring length, MDIO reads/writes, stats reads, and all supported PHY modes.
