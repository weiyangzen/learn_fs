
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/core.h

## Purpose
`core.h` is the private contract for the IBM EMAC core driver. It gathers local EMAC/MAL/PHY/bridge headers, defines descriptor-ring sizing and MTU helpers, declares the central `struct emac_instance`, and documents feature bits and ethtool register-dump layout shared by `core.c` and helper modules.

## Important APIs, Types, and Functions
Inline helpers `emac_rx_size()`, `emac_rx_skb_size()`, and `emac_rx_sync_size()` derive hardware RX buffer sizes from MTU and MAL limits. `struct emac_stats` and `struct emac_error_stats` define the ethtool statistics layout that must stay in lockstep with `emac_stats_keys` in `core.c`. `struct emac_instance` is the driver’s full per-netdev state: EMAC register base, OF devices, MAL linkage, PHY/MDIO state, optional ZMII/RGMII/TAH state, FIFO sizes, descriptor rings, skb arrays, counters, locks, work, and open/reset flags. `emac_has_feature()` gates implementation-specific behavior against compile-time possible features and runtime device-tree/compatible detection. Address hash-table helpers compute XAHT slots/registers/masks and locate IAHT/GAHT register blocks. `struct emac_ethtool_regs_hdr` and `struct emac_ethtool_regs_subhdr` define the composite register dump framing.

## Control Flow
The header does not run control flow itself, but it shapes all control flow in `core.c`: probe fills `struct emac_instance`, open/close mutate descriptor and PHY fields, TX/RX poll paths use descriptor and skb arrays, and ethtool register dumping uses the register-dump header constants. Feature macros such as `EMAC_FTR_EMAC4`, `EMAC_FTR_HAS_TAH`, and clock-workaround flags are tested before reset, link, checksum, bridge, and register-layout decisions.

## State and Persistence
All state is in-memory kernel state or MMIO/DMA references. Ring sizes are compile-time `CONFIG_IBM_EMAC_TXB` and `CONFIG_IBM_EMAC_RXB`, hard-limited to 256 descriptors each. MTU calculations include VLAN-capable L2 overhead and MAL’s 4080-byte RX ceiling. No persistent storage is used.

## Dependencies and Integration Points
The file depends on Linux netdevice, DMA, locking, interrupt, and PowerPC DCR headers, plus local register and helper headers. Its feature masks depend on Kconfig symbols such as `CONFIG_IBM_EMAC_EMAC4`, `CONFIG_IBM_EMAC_TAH`, `CONFIG_IBM_EMAC_ZMII`, `CONFIG_IBM_EMAC_RGMII`, and `CONFIG_IBM_EMAC_NO_FLOW_CTRL`.

## Risks
Statistics layout drift is a concrete risk because `EMAC_ETHTOOL_STATS_COUNT` assumes the concatenated `u64` structures match string keys. Ring-size macros derive from config and are used for descriptor allocation and wrap control, so invalid config or changed descriptor assumptions can corrupt rings. Feature masks combine compile-time and runtime bits; unsupported runtime device-tree properties can produce disabled stubs or `-ENXIO` paths.

## Test Signals
Builds under multiple Kconfig combinations are important: with/without EMAC4, TAH, RGMII, ZMII, and no-flow-control. Runtime test signals are correct ethtool stat counts, valid register dump component framing, successful jumbo MTU RX buffer sizing, and no descriptor wrap/accounting warnings.
