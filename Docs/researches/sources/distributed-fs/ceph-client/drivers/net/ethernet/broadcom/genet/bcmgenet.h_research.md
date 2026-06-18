# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/bcmgenet.h

## Purpose

`bcmgenet.h` is the shared private header for the Broadcom GENET driver files. It defines descriptor formats, register offsets, interrupt bits, hardware-version flags, queue/ring/private-state structures, accessor macros, and cross-file function prototypes used by `bcmgenet.c`, `bcmmii.c`, and `bcmgenet_wol.c`.

## Important APIs, Types, and Definitions

Global geometry constants include `GENET_MAX_MQ_CNT`, `TOTAL_DESC`, `DESC_INDEX`, `ENET_MAX_MTU_SIZE`, `DMA_MAX_BURST_LENGTH`, `MAX_NUM_OF_FS_RULES`, and DMA flow-control thresholds. `struct status_64` models the 64-byte RX/TX status block used by checksum offload paths. Descriptor register offsets and bit definitions include `DMA_DESC_LENGTH_STATUS`, `DMA_DESC_ADDRESS_LO`, optional `DMA_DESC_ADDRESS_HI`, `DMA_OWN`, `DMA_SOP`, `DMA_EOP`, `DMA_WRAP`, TX flags such as `DMA_TX_APPEND_CRC` and `DMA_TX_DO_CSUM`, and RX error/classification flags such as `DMA_RX_CRC_ERROR`, `DMA_RX_OV`, `DMA_RX_MULT`, and `DMA_RX_BRDCAST`.

The counter structs (`bcmgenet_pkt_counters`, `bcmgenet_rx_counters`, `bcmgenet_tx_counters`, `bcmgenet_mib_counters`, `bcmgenet_tx_stats64`, `bcmgenet_rx_stats64`) define both hardware MIB layout and software per-ring stats. Register definitions cover UniMAC MIB/MDIO/Magic Packet Detection registers, RBUF/TBUF/HFB blocks, interrupt controller instances, system and external power/RGMII blocks, and DMA control/status/ring fields.

Driver state types are central. `struct enet_cb` binds an SKB, descriptor address, and DMA unmap metadata. `enum bcmgenet_power_mode`, `enum bcmgenet_version`, and `GENET_HAS_*` flags describe power and hardware capabilities. `struct bcmgenet_hw_params` captures version-specific queue counts, filter sizes, register offsets, descriptor width, and queue tag masks. `struct bcmgenet_tx_ring` and `struct bcmgenet_rx_ring` store per-ring software pointers, NAPI objects, stats, and RX DIM state. `struct bcmgenet_rxnfc_rule` holds ethtool flow classifier state. `struct bcmgenet_priv` is the device-wide private state shared by all source files.

The `GENET_IO_MACRO` generates endian-aware inline accessors for named register blocks: `ext`, `umac`, `sys`, `intrl2_0`, `intrl2_1`, `hfb`, `hfb_reg`, and `rbuf`. Capability helpers such as `bcmgenet_has_40bits`, `bcmgenet_has_ext`, `bcmgenet_has_mdio_intr`, `bcmgenet_has_moca_link_det`, and `bcmgenet_has_ephy_16nm` centralize flag checks.

## Control Flow and Integration

This header has no executable top-level control flow. Its role is to make the rest of the driver agree on register layout, bit semantics, and state ownership. `bcmgenet.c` consumes almost every register definition and private field for probe/open/DMA/NAPI/PM. `bcmmii.c` uses PHY, MDIO, RGMII, power, and pause definitions. `bcmgenet_wol.c` uses WOL, HFB, RBUF status, MPD, clock, IRQ, and PHY-state fields.

The cross-file prototypes at the end form the internal module boundary: MII init/probe/config/exit and PHY pause/power/setup functions, WOL get/set and power transition functions, plus `bcmgenet_eee_enable_set`.

## State and Persistence Behavior

The header defines in-memory state only. `struct bcmgenet_priv` persists for the lifetime of the registered netdev and tracks clocks, platform devices, descriptor pools, RX/TX rings, PHY/MDIO objects, IRQ numbers/status, feature settings, WOL options, and counters. Per-ring structures persist across an open instance after DMA initialization, then are torn down and rebuilt during close or reset-style resume. RX NFC rules are stored in the private struct and can be replayed after resume.

## Dependencies

The header depends on kernel networking, spinlock, clock, MII/PHY, VLAN, DIM, and ethtool headers, plus Broadcom UniMAC definitions from `../unimac.h`. Many numeric definitions are hardware-contract values and must stay synchronized with the GENET programming manual and with hardware-version choices in `bcmgenet.c`.

## Risks and Edge Cases

The main risk is layout drift: MIB counter structs are expected to match hardware counter order, descriptor constants must match hardware descriptor word layouts, and register offsets differ across GENET revisions. `struct bcmgenet_hw_params` is explicitly used in hot paths and is expected to remain compact/aligned. The `GENET_IO_MACRO` uses `priv->hw_params` in generated HFB accessor offsets; callers must ensure hardware params are initialized before using those accessors. The file also encodes special cases such as v4 40-bit address support, v5/E PHY flags, and MIPS big-endian raw MMIO behavior.

## Test Signals

Compile coverage is an important signal because this header controls cross-file ABI. Runtime signals include successful register access on big-endian MIPS and little-endian platforms, correct descriptor programming on 32-bit and 40-bit DMA systems, stable ethtool stat ordering, RX/TX queue setup matching hardware params, and successful WOL/MDIO/HFB paths that depend on shared offsets and flags.
