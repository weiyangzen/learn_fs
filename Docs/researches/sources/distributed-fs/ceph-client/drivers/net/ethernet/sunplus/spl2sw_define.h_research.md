# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_define.h

Purpose: Central private ABI for the Sunplus SP7021 dual 10/100 L2 switch Ethernet driver. It defines the two-port model, interrupt bit groups, switch table/VLAN/PHY/register field masks, descriptor ring sizing, DMA descriptor wire format, SKB bookkeeping, and the common/netdev-private state shared by all Sunplus implementation files.

Important APIs/types: `MAX_NETDEV_NUM` fixes the driver at two net devices. `MAC_INT_RX`, `MAC_INT_TX`, and `MAC_INT_MASK_DEF` define interrupt policy used by open, interrupt, and NAPI paths. `struct spl2sw_mac_desc` is the four-word hardware descriptor for TX/RX rings. `struct spl2sw_skb_info` tracks one SKB DMA mapping. `struct spl2sw_common` owns MMIO base, platform resources, coherent descriptor memory, RX/TX rings, NAPI contexts, MDIO bus, locks, netdev array, and the enabled-port bitmask. `struct spl2sw_mac` is per-netdev state with MAC address, PHY node/mode, LAN port bit, and VLAN identifiers.

Control flow and state: This header does not execute code, but its constants encode the runtime topology. TX has one 16-entry ring plus two guard descriptors, RX has two 16-entry queues, and all hardware ownership is coordinated through `TXD_OWN`/`RXD_OWN` plus memory barriers in implementation files. Persistent driver state is in memory only; hardware-visible persistence is descriptor DMA memory and switch registers programmed from these masks.

Dependencies and integration points: Consumers depend on Linux `BIT`, `GENMASK`, descriptor DMA APIs, phylib, NAPI, platform resources, clocks/resets, and register offsets from `spl2sw_register.h`. The `lan_port` bit values are reused as VLAN, forwarding, and forced-RMII bit selectors, so all files must treat them consistently.

Risks and test signals: Ring sizes and bit masks are hard-coded, so off-by-one or wrong queue priority assumptions break data path behavior. Validate two-port open/close combinations, TX ring full/wake behavior, RX high/low queue handling, VLAN isolation between ports, MDIO/PHY link transitions, and reset recovery after descriptor errors.
