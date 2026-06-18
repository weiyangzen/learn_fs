# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/rtase/rtase.h

## Purpose

`rtase.h` is the private hardware contract for the Realtek Automotive Switch Ethernet PCIe driver. It defines register offsets, bit fields, descriptor layouts, queue/vector constants, ring metadata, interrupt-vector state, per-queue QoS state, software statistics, and the top-level `struct rtase_private` consumed by the driver implementation in `rtase_main.c`.

The header describes a multi-queue PCIe NIC/switch function with 8 TX queues, 4 RX queues, one active function TX/RX queue by default, MSI/MSI-X support, VLAN filter storage, interrupt mitigation fields, page-pool-backed RX buffers, DMA tally counters, and hardware-version identifiers for RTASE 906x/907x families.

## Important APIs, Types, And Data

Hardware identity and limits are represented by `RTASE_HW_VER_MASK` and version constants such as `RTASE_HW_VER_906X_7XA`, `RTASE_HW_VER_906X_7XC`, `RTASE_HW_VER_907XD_V1`, and `RTASE_HW_VER_907XD_VA`. Buffer and MTU constraints are set by `RTASE_RX_BUF_SIZE` and `RTASE_MAX_JUMBO_SIZE`, where jumbo size is derived from page-sized RX buffers minus VLAN Ethernet header and FCS.

`enum rtase_registers` is the main register map. It includes MAC address registers, multicast hash registers, tally counter command registers, TX/RX descriptor base registers, boot/clock registers, chip command bits, interrupt mask/status registers for base and queue interrupts, EPHY interrupt registers, TX/RX config registers, EEPROM/config unlock, TX poll, FIFO status, CPlus command, queue descriptor addresses, VLAN entries, TX queue credit registers, RX FIFO backpressure, and interrupt mitigation registers.

Descriptor ABI is defined by `struct rtase_tx_desc` and `union rtase_rx_desc`, both packed. TX descriptors contain options, address, and reserved words for the "new" descriptor format. TX bits include ownership/ring end from `enum rtase_desc_status_bit`, first/last fragment, GSO v4/v6, VLAN tagging, and checksum offload flags. RX descriptors have command and status views, with status bits for first/last fragment, receive errors, runt/RWT/CRC, IPv4/IPv6/TCP/UDP classification, checksum failures, VLAN tag availability, and packet-size masks.

Software data structures are:

- `struct rtase_int_vector`, binding a vector to the private state, IRQ number, name, per-vector IMR/ISR addresses, NAPI instance, ring list, and poll callback.
- `struct rtase_ring`, representing one TX or RX ring with descriptor memory, DMA address, producer/consumer indices, queue index/type, SKB and data-buffer arrays, length or data DMA tracking, list linkage, ring handler, and allocation-failure counter.
- `struct rtase_txqos`, storing credit-based shaper values.
- `struct rtase_stats`, storing software-maintained drop/error/multicast counters.
- `struct rtase_private`, the top-level device state with MMIO base, software flags, PCI/netdev pointers, RX buffer size, page pool, TX/RX rings, TX QoS, DMA tally memory, VLAN filter cache, MSI-X entries, interrupt vectors, stats, queue counts, interrupt mitigation settings, and hardware version.

## Control Flow

This header does not implement control flow, but it shapes the implementation. A typical driver path will identify hardware with `RTASE_HW_VER_MASK`, map registers from `enum rtase_registers`, allocate `RTASE_NUM_DESC` descriptors per ring, initialize `rtase_ring` structures, assign rings to `rtase_int_vector` lists, program descriptor base registers, enable RX/TX through `RTASE_CHIP_CMD`, service interrupts from `RTASE_ISR0/ISR1`, and use NAPI callbacks stored in vectors and ring handlers to process TX completions and RX packets.

TX flow is implied by the descriptor fields: map SKB data into `struct rtase_tx_desc`, set checksum/GSO/VLAN/fragment bits, set `RTASE_DESC_OWN`, advance `cur_idx`, and notify via `RTASE_TPPOLL`. Completion reads ownership back, frees SKBs, advances `dirty_idx`, and updates `rtase_stats`. RX flow uses the RX descriptor status view to classify packets, validate error bits, extract VLAN/checksum metadata, and recycle or refill buffers through `page_pool` and `data_phy_addr`.

Interrupt moderation control is implied by the `RTASE_INT_MITI_TX/RX` registers and masks/count constants. Queueing/QoS control is implied by `RTASE_TXQCRDT_0`, `struct rtase_txqos`, and idle/slope constants.

## State And Persistence

Persistent runtime state lives in `struct rtase_private`. It caches hardware version, queue counts, interrupt mitigation values, VLAN filter state, ring indices, DMA addresses, SKB/data buffer ownership, page-pool state, and software stats. Hardware-visible persistent state lives in MMIO registers, descriptor rings, DMA tally memory, and VLAN filter entries. Descriptor ownership bits are the main synchronization contract between CPU and NIC.

The union in `struct rtase_ring::mis` is type-dependent: TX rings use packet lengths for unmapping/accounting, while RX rings use data DMA addresses. Callers must respect `ring->type` or equivalent ownership conventions to avoid interpreting the wrong member.

## Dependencies And Integration Points

The header assumes inclusion from a Linux network driver context where `PAGE_SIZE`, `SKB_DATA_ALIGN`, `struct skb_shared_info`, `VLAN_ETH_HLEN`, `ETH_FCS_LEN`, `GENMASK`, `BIT`, `MAX_SKB_FRAGS`, `IFNAMSIZ`, `struct pci_dev`, `struct net_device`, `struct page_pool`, `struct msix_entry`, `struct list_head`, `struct napi_struct`, `dma_addr_t`, `__le32`, and `__le64` are available through implementation includes. It integrates with PCI MSI/MSI-X, Linux NAPI, page_pool RX allocation, DMA mapping, VLAN filtering, netdev queue management, checksum/GSO offload, and Kbuild via the adjacent Makefile.

The header references `struct rtase_counters` without defining it, so the implementation must define that tally-counter layout before use or through another included header/source-local declaration.

## Risks And Edge Cases

The highest risk is hardware ABI mismatch. Packed descriptor layouts and bit positions must match silicon exactly; any alignment, endian, or reserved-field misuse can break DMA. `RTASE_RX_BUF_SIZE` is page-size derived, so architectures with unusual page sizes alter jumbo limits and RX allocation behavior. `RTASE_NUM_DESC` at 1024 creates large fixed arrays in every ring for SKB and data tracking; memory pressure and cache footprint matter.

The header defines more hardware queues than the function defaults use. Bugs can arise if code assumes `RTASE_FUNC_TXQ_NUM` or `RTASE_FUNC_RXQ_NUM` equals the array size. Interrupt-vector lists and ring handlers also require careful initialization because callbacks are function pointers in mutable state. VLAN filter arrays must stay synchronized with hardware `RTASE_VLAN_ENTRY_0` programming or software cache and hardware filtering will diverge.

The `RSVD_MASK`, descriptor reserved fields, and "new descriptor format" bits imply that the implementation must clear reserved fields consistently. Interrupt mitigation masks encode count/unit fields; out-of-range settings can silently wrap unless validated against the max constants.

## Test Signals

Validation should include compile coverage for `CONFIG_RTASE=m/y`, sparse/endian checks for descriptor fields, structure size/layout assertions against hardware documentation, probe on each supported hardware version, MSI and MSI-X interrupt modes, TX/RX traffic on every enabled queue, GSO/checksum/VLAN offload tests, jumbo MTU boundary tests using `RTASE_MAX_JUMBO_SIZE`, page-pool recycle stress, interrupt mitigation configuration limits, VLAN filter programming, and error-path tests for RX allocation failures and DMA mapping failures.
