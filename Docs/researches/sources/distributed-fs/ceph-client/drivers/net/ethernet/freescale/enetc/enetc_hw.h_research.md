# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_hw.h

## Purpose
Defines the core ENETC hardware ABI: PCI IDs, SI/port/global register offsets, descriptor formats, command descriptor formats, TSN/PSFP structures, mailbox definitions, stats register names, and register accessors with the LS1028A MDIO erratum workaround.

## Important APIs, Types, and Functions
Important types are `struct enetc_hw`, `union enetc_tx_bd`, `union enetc_rx_bd`, `struct enetc_cbd`, `struct enetc_cmd_rfse`, TSN command data structures such as `tgs_gcl_data`, `streamid_conf`, `sfi_conf`, `sgi_table`, `sgcl_conf`, and `fmi_conf`, plus mailbox structures and enums. Important inline helpers include `enetc_rd`, `enetc_wr`, `enetc_port_rd`, `enetc_port_wr`, `enetc_port_rd_mdio`, `enetc_get_primary_mac_addr`, `enetc_load_primary_mac_addr`, VLAN BDR enable helpers, `enetc_set_bdr_prio`, and time conversion helpers.

## Control Flow
This header has mostly declarative control flow. Its active logic wraps MMIO accesses. Normal register reads take a read side of `enetc_mdio_lock` only when static key `enetc_has_err050089` is enabled; MDIO register accessors take a write lock to exclude concurrent non-MDIO access. 64-bit stat reads use native `ioread64` or a high/low/high retry sequence on 32-bit systems.

## State and Persistence
The file defines persistent hardware state layout: SI mode/capability registers, BDR registers, CBDR registers, VF/PF mailbox registers, port MAC/VLAN/filter/QBU/QBV/PSFP registers, global revision registers, TX/RX descriptor bit fields, and CBDR command classes. `struct enetc_hw` stores MMIO base pointers for SI, port, and global blocks.

## Dependencies and Integration Points
Included throughout the ENETC driver and indirectly by PF, VF, MDIO, ethtool, QoS, CBDR, and PTP paths. It exposes erratum symbols defined by `enetc_mdio.c` and `enetc_pci_mdio.c`, and it shares command descriptor definitions with QoS and ethtool classification code.

## Risks
This is hardware ABI. Any offset, mask, endian type, or descriptor field mistake can silently corrupt packet DMA, command execution, timestamping, TSN scheduling, or filtering. Erratum locking misuse can reintroduce dropped MDIO transactions or cause lockdep failures when hot accessors are called without `enetc_lock_mdio`.

## Test Signals
Compile coverage across PF/VF/rev1/rev4/QoS/PTP configs, register dumps matching datasheets, traffic with TX/RX descriptors on 32-bit and 64-bit builds, MDIO stress with ERR050089 enabled, RSS/RFS/CBDR command tests, Qbv/Qbu/PSFP offloads, and endian-sensitive packet offload validation are the main signals.
