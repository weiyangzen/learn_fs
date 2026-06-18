# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunbmac.h

## Purpose
`sunbmac.h` defines the hardware register offsets, bit masks, descriptor layouts, ring sizing, helper macros, enums, and private state for the Sun BigMAC 100baseT driver. It is the static ABI layer used by `sunbmac.c` to program QEC global/channel resources, BigMAC MAC registers, the transceiver PAL/MDIO interface, and RX/TX descriptor rings.

## Important APIs, Types, And Functions
Register groups include QEC global registers (`GLOB_*`), QEC BigMAC channel registers (`CREG_*`), BigMAC core registers (`BMAC_*`), XIF/TX/RX config and status masks (`BIGMAC_*`), and transceiver PAL/MGMT registers (`TCVR_*`, `MGMT_PAL_*`). Descriptor types are `struct be_rxd` and `struct be_txd` with `RXD_*` and `TXD_*` ownership, update, SOP/EOP, and length bits. Ring constants fix both RX and TX rings at 256 entries, with `NEXT_RX()`, `NEXT_TX()`, `PREV_RX()`, `PREV_TX()`, and `TX_BUFFS_AVAIL()` providing wrap and flow-control arithmetic.

`struct bmac_init_block` stores the coherent RX and TX descriptor arrays. `bib_offset()` computes descriptor offsets inside that block for QEC descriptor base registers. `enum bigmac_transceiver` selects external, internal, or unknown transceiver mode; `enum bigmac_timer_state` defines the link timer state machine. `struct bigmac` is the driver's private state. The inline `big_mac_alloc_skb()` allocates 64-byte-aligned receive skbs using `ALIGNED_RX_SKB_ADDR()`.

## Control Flow
The header shapes `sunbmac.c` control flow: probe maps register ranges sized by `*_REG_SIZE`, initialization writes QEC burst/memory controls, TX/RX reset loops poll `BIGMAC_*CFG` bits, descriptor setup fills `be_rxd`/`be_txd` entries, open starts the timer in `ltrywait`, RX/TX paths advance ring indexes with the macros, and multicast setup writes BMAC hash-table registers. Transceiver MDIO operations use the PAL bit definitions to drive internal or external MDIO pins.

## State, Persistence, And Dependencies
`struct bigmac` stores volatile per-device state: MMIO pointers, coherent descriptor block and DVMA address, lock, skb arrays, ring indexes, board revision, transceiver selection, burst capabilities, PHY software registers, timer, platform device links, and the netdev pointer. There is no filesystem persistence. Hardware state persists only while the device is powered and is reprogrammed on initialization or reset. The header depends on Linux kernel types (`u32`, `dma_addr_t`, `spinlock_t`, `sk_buff`, `timer_list`, `platform_device`, `net_device`) and Ethernet constants.

## Integration Points
This header is included directly by `sunbmac.c` and forms the interface between the Linux netdev driver and the QEC/BigMAC hardware. Descriptor structs are shared with DMA hardware. The `TX_BUFFS_AVAIL()` macro controls when the netdev TX queue is stopped or woken. `big_mac_alloc_skb()` provides the alignment assumptions used by RX DMA setup. The register masks align driver error handling with QEC and BigMAC interrupt status bits.

## Risks
The descriptor length masks are 11 bits, so callers must keep RX/TX buffer sizes within the hardware's encoded limits. Ring macros assume 256-entry power-of-two rings. `TX_BUFFS_AVAIL()` relies on `tx_old` and `tx_new` being updated under the same synchronization expected by the driver. `big_mac_alloc_skb()` assumes the extra 64 bytes are sufficient for DMA alignment and that callers reserve subsequent protocol offsets correctly. Incorrect QEC memory sizes or FIFO pointer programming can cause RX/TX overlap in local memory. Status registers such as `BMAC_STATUS` are clear-on-read, so consumers must avoid accidental reads.

## Test Signals
Good signals are successful compilation against current kernel type definitions, correct descriptor block offsets, RX skb data alignment, ring wrap behavior under 256-entry pressure, queue stop/wake thresholds, and multicast hash register programming. Hardware tests should watch QEC `CREG_STAT_ERRORS`, BigMAC status bits, and collision/error counters while sending traffic, changing multicast modes, opening/closing the interface, and triggering link fallback.
