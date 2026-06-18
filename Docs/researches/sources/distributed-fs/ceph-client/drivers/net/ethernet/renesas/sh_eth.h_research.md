# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/sh_eth.h

## Purpose
`sh_eth.h` is the private hardware and state header for the SuperH/R-Car Ethernet driver. It defines register IDs, ring limits, packet buffer sizing, descriptor layouts, register bit masks, TSU constants, SoC capability flags, and the private per-device state consumed by `sh_eth.c`.

## Important APIs, Types, And Constants
The first enum is the canonical register index list used by offset tables and ethtool dumps; new register indices must be inserted before `SH_ETH_MAX_REGISTER_OFFSET`. Register-family IDs are `SH_ETH_REG_GIGABIT`, `SH_ETH_REG_FAST_RCAR`, `SH_ETH_REG_FAST_SH4`, and `SH_ETH_REG_FAST_SH3_SH2`. Descriptor definitions are `struct sh_eth_txdesc` and `struct sh_eth_rxdesc`, with status, length, address, and padding fields. `struct sh_eth_cpu_data` captures per-SoC reset hooks, speed/duplex hooks, initial register values, interrupt masks, and feature booleans. `struct sh_eth_private` stores platform device, capability table, register offsets, MMIO/TSU mappings, rings, SKB arrays, locks, ring indices, NAPI, PHY/MDIO, link state, TSU port/VLAN state, and WoL/open flags.

## Control Flow Role
This header drives conditional control flow in `sh_eth.c`. Capability bits choose register programming, interrupt masks, ethtool dump contents, TSU/VLAN operations, checksum support, link handling, byte swapping, and WoL support. Descriptor bit definitions define ownership transfer between CPU and E-DMAC. Register enum ordering also controls the ABI of ethtool register dumps.

## State And Persistence
The descriptor structs are DMA-shared state for rings allocated at open or ring resize. `sh_eth_private` is netdev-private runtime state and is not persistent across driver remove. `sh_eth_cpu_data` instances are static module data; they become effectively shared immutable configuration after default fields are filled, although the defaulting helper mutates them.

## Dependencies And Integration Points
The header is private to the Renesas driver and expects Linux kernel networking, platform, DMA, NAPI, phylib, ethtool, and MDIO APIs included by the C file. It is indirectly tied to public platform data in `<linux/sh_eth.h>`, hardware manuals for all supported SoCs, and ethtool register-dump consumers that depend on stable register indices.

## Risks
Changing register enum order can break ethtool dump interpretation. Incorrect descriptor alignment or bit definitions can break DMA ownership. Capability flags are densely packed and easy to misuse across SoCs. Ring size constants gate ethtool validation and memory allocation behavior. `SH_ETH_RX_ALIGN` varies by architecture config, so buffer alignment assumptions differ by build target. Static `sh_eth_cpu_data` mutability should be considered before adding per-instance dynamic defaults.

## Test Signals
Build tests should cover OF and non-OF configurations, CPU/architecture variants affecting `SH_ETH_RX_ALIGN`, and all platform ID tables. Runtime signals include successful descriptor DMA, ethtool register dumps with valid maps, SoC-specific feature paths, TSU CAM/VLAN behavior, RX checksum support, and ring parameter boundary validation.
