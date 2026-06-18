# sources/distributed-fs/ceph-client/drivers/net/ethernet/moxa/moxart_ether.h

## Purpose
`moxart_ether.h` defines the MOXA ART Ethernet register map, descriptor layouts, bit masks, ring sizes, buffer sizing limits, and private driver state used by `moxart_ether.c`.

## Important APIs, Types, And Functions
The header has no functions. It defines TX/RX descriptor offsets and flags such as `TX_DESC0_DMA_OWN`, `TX_DESC1_LTS`, `RX_DESC0_DMA_OWN`, and RX error bits; ring constants such as `TX_DESC_NUM`, `RX_DESC_NUM`, `TX_NEXT`, `RX_NEXT`, `TX_WAKE_THRESHOLD`; MMIO register offsets from interrupt status through counters; MAC/PHY/flow-control/test-mode bit fields; and `struct moxart_mac_priv_t`.

## Control Flow
The macros shape runtime control in the C file. Ring wrap macros implement power-of-two descriptor cycling. Descriptor ownership bits coordinate DMA versus CPU ownership. Register bit masks drive reset, interrupt masking, MAC enable, DMA enable, RX filtering, multicast hashing, and PHY access.

## State And Persistence
`struct moxart_mac_priv_t` contains all persistent in-memory state for a device instance: platform device, MMIO base, cached MAC control and interrupt-mask registers, NAPI, netdev pointer, coherent RX/TX descriptor bases and DMA addresses, RX/TX buffer arrays and mappings, ring head/tail indices, TX lock, TX lengths, and pending TX SKBs.

## Dependencies And Integration Points
The header is consumed by the MOXART platform driver and assumes Linux kernel types such as `struct platform_device`, `struct napi_struct`, `struct net_device`, `dma_addr_t`, `spinlock_t`, and `struct sk_buff`. Register definitions are specific to the MOXART MAC block.

## Risks
The header encodes fixed 64-entry rings and 1600-byte buffers, so jumbo frames are unsupported. Compile-time checks reject buffers that exceed the descriptor size mask. There is a likely typo in `tx_buf[RX_DESC_NUM]`, which happens to be harmless only because RX and TX descriptor counts are both 64. Any hardware revision with different register layout, descriptor format, or buffer-size limits would require coordinated changes.

## Test Signals
Compile coverage should catch buffer-size mask violations. Runtime tests should validate ring wrap at 64 descriptors, descriptor `END` handling, RX/TX buffer size limits, register writes for promiscuous and multicast modes, and DMA ownership transitions.
