# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atlx/atl1.h

## Purpose
Defines the ATL1 driver-specific hardware constants, descriptor formats, statistics blocks, ring structures, hardware state, adapter state, and macro aliases that let the shared `atlx.c` helpers compile against ATL1 types. It is the primary data-model header for `atl1.c`.

## Important APIs, Types, and Functions
The macro aliases map common-helper names to ATL1 symbols, for example `atlx_adapter` to `atl1_adapter`, `atlx_hw` to `atl1_hw`, `atlx_check_link` to `atl1_check_link`, and `atlx_set_mac` to `atl1_set_mac`. Static prototypes declare common helper targets: `atl1_hash_mc_addr`, `atl1_hash_set`, `atl1_set_mac_addr`, `atl1_mii_ioctl`, and `atl1_check_link`.

Important register definitions cover idle status, MDIO timing, MAC control, WOL, SRAM partitioning, descriptor base/ring-size registers, TXQ/RXQ controls, flow-control thresholds, DMA control, CMB/SMB controls, mailbox layout, and ATL1 interrupt masks. Important descriptor and state types are `struct stats_msg_block`, `struct coals_msg_block`, `struct rx_return_desc`, `struct rx_free_desc`, `struct tx_packet_desc`, `struct atl1_ring_header`, `struct atl1_buffer`, `struct atl1_tpd_ring`, `struct atl1_rfd_ring`, `struct atl1_rrd_ring`, `struct atl1_cmb`, `struct atl1_smb`, `struct atl1_sft_stats`, `struct atl1_hw`, and `struct atl1_adapter`.

## Control Flow and State
There is no runtime control flow, but the header defines the state transitions that `atl1.c` implements. RX state moves through RFD buffers, RRD completion descriptors, `next_to_use`/`next_to_clean` indices, `alloced` flags, and mailbox producer/consumer fields. TX state moves through TPD descriptors, `buffer_info` DMA/skb ownership, and CMB-consumer indices. Statistics state is split between hardware-written `stats_msg_block`, driver-accumulated `atl1_sft_stats`, and netdev stats. Link/power state is represented by `atl1_hw` fields such as media type, advertisement registers, PHY configured flag, WOL flags, and MAC address storage.

## Dependencies and Integration Points
Includes Linux ethtool, VLAN, MII, module, skb, spinlock, timer, workqueue, and type headers plus `atlx.h`. It integrates with `atl1.c`, the textually included `atlx.c`, Kbuild through `atl1.o`, ethtool register/stat code, and the Linux netdev/PCI/DMA APIs.

## Risks
This header encodes hardware ABI and in-memory DMA layout. Incorrect descriptor field masks or structure packing can break offloads, VLAN tags, DMA addresses, or RX completion parsing. `struct rx_free_desc` is explicitly packed; removing that would change hardware-visible layout. Ring index types and masks must match hardware register widths. The macro alias layer is risky because common helpers compile as if ATL1 were the `atlx` generic type; renaming struct fields or functions can break helpers in non-obvious ways. Interrupt mask definitions separate normal RX/TX CMB events from fatal/base events; wrong masks can lose interrupts or keep NAPI from reenabling RX/TX.

## Test Signals
Compile `atl1.c` with common `atlx.c` helpers, run sparse/struct layout checks where available, verify descriptor sizes and register masks against hardware expectations, exercise checksum/TSO/VLAN descriptors, validate CMB/SMB DMA updates, run ethtool stat/register dumps, and test interrupt masking under RX/TX load and fatal-error conditions. Build coverage with `CONFIG_ATL1=m/y` is especially important because many declarations are static and only validated through the single translation unit.
