# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.h

## Purpose
Internal interface and hardware contract for the QE UCC Gigabit Ethernet driver. It defines the UCC register layout, bit fields, QE parameter RAM structures, buffer descriptor flags, defaults, and the main driver-private state shared by `ucc_geth.c` and `ucc_geth_ethtool.c`.

## Important APIs, Types, And Functions
Key types are `struct ucc_geth` for memory-mapped MAC registers, `struct ucc_geth_info` for configuration/defaults, and `struct ucc_geth_private` for live netdevice state. Hardware-facing PRAM structs include Tx/Rx thread data, send queue descriptors, scheduler state, firmware statistics, interrupt coalescing tables, Rx BD queue entries, global Tx/Rx PRAM, InitEnet command parameters, 82xx address filtering, and statistics snapshots. Exported declarations are `uec_set_ethtool_ops()` and `init_flow_control_params()`.

## Control Flow
The header itself has no executable flow, but its layout drives driver sequencing: defaults are copied into `ucc_geth_info`, validated by `ucc_struct_init()`, encoded into registers and PRAM by `ucc_geth_startup()`, and consumed by Tx/Rx fast paths. Ring lengths, queue counts, alignment constants, SNUM entry limits, and event masks define the legal transitions for startup, interrupt handling, and teardown.

## State And Persistence
Defines volatile hardware state, not persisted data. `struct ucc_geth_private` records register mappings, MURAM pointers/offsets, skb arrays, BD cursors, multicast hash bookkeeping, phylink state, WoL state, and debug level. The register/PRAM structs are packed to match hardware layout and are accessed through endian-aware MMIO helpers.

## Dependencies And Integration Points
Includes Linux list/phylink/Ethernet headers and Freescale QE/UCC headers. The constants mirror QE firmware expectations: InitEnet entries, RISC allocation masks, BD status bits, UCC event bits, TBI PHY registers, and UPSMR/MACCFG fields.

## Risks
Packed hardware layout and manual offsets are brittle across hardware revisions. Several masks/shift values assume big-endian register interpretation. Ring modulo macros require power-of-two lengths although validation only enforces minimum/alignment for Rx and minimum for Tx. `struct ucc_geth_private` contains fields no longer heavily used (`mii_info`, `conf_skbs`, address register arrays), increasing maintenance risk.

## Test Signals
Compile coverage should catch layout symbol drift against QE headers. Runtime signals include successful InitEnet, correct ethtool register/stat sizes, valid phylink mode changes using the MACCFG/UPSMR definitions, and clean allocation/free of every MURAM-backed pointer in `struct ucc_geth_private`.
