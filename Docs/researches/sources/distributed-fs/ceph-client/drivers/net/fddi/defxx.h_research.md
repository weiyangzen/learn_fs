# sources/distributed-fs/ceph-client/drivers/net/fddi/defxx.h

## Purpose
Defines the PDQ/DEC FDDIcontroller hardware and firmware interface consumed by `defxx.c`. It provides fixed-width aliases, port-interface command IDs, response layouts, SMT/FDDI MIB layouts, descriptor and consumer block formats, producer register views for little- and big-endian hosts, bus register offsets for TC/EISA/PCI variants, packet request header constants, driver return codes, and the driver's private board structure.

## Important APIs, Types, And Definitions
Core wire types include `PI_UINT8`, `PI_UINT16`, `PI_UINT32`, `PI_CNTR`, `PI_LAN_ADDR`, and `PI_STATION_ID`. Firmware command ABI is represented by per-command request/response structures such as `PI_CMD_FILTERS_SET_REQ`, `PI_CMD_CHARS_SET_REQ`, `PI_CMD_SMT_MIB_GET_RSP`, `PI_CMD_ADDR_FILTER_SET_REQ`, `PI_CMD_STATUS_CHARS_GET_RSP`, `PI_CMD_FDDI_MIB_GET_RSP`, `PI_CMD_DEC_EXT_MIB_GET_RSP`, and counter/error-log structures. `PI_DMA_CMD_REQ`, `PI_DMA_CMD_RSP`, and `PI_DMA_CMD_BUFFER` unify 512-byte command buffers.

DMA ring ABI definitions include `PI_CONSUMER_BLOCK`, `PI_RCV_DESCR`, `PI_XMT_DESCR`, and `PI_DESCR_BLOCK`, with fixed queue sizes for receive, transmit, SMT host, unsolicited, command response, and command request rings. `PI_TYPE_1_PROD_REG`, `PI_TYPE_2_PROD_REG`, `PI_TYPE_1_CONSUMER`, and `PI_TYPE_2_CONSUMER` are endian-sensitive views of producer/consumer longwords.

Hardware constants cover PDQ port registers, port-control commands, adapter states, halt IDs, host interrupt masks, Type 0 interrupt bits, TC CSR placement, EISA ESIC register layout, DEC EISA product IDs, PCI PFI register layout, DMA burst sizes, byte-swap initialization flags, and FDDI PRH bytes. `DFX_board_t` is the main software state container used by `defxx.c`.

## Control Flow Semantics
This header is declarative, but it encodes the state machine that `defxx.c` follows: reset and DMA unavailable states are reached through port reset/control commands; consumer and descriptor block addresses are provided through port-control commands; firmware DMA commands are posted via command request/response rings; RX/TX progress is synchronized through producer register shadows and the consumer block; Type 0 status bits trigger reset, flush, or link-state handling.

The endian-specific producer/consumer unions determine how byte-sized indices are read from and written to a 32-bit hardware register. The descriptor bit fields define how the driver marks SOP/EOP, segment sizes, physical buffer high bits, frame status, and packet lengths.

## State And Persistence Behavior
The file defines only in-memory and hardware-visible state; no persistent storage is involved. Structures in `DFX_board_t` persist for the netdev lifetime, while descriptor blocks, command buffers, consumer blocks, CAM tables, filter flags, receive skb pointers, transmit skb pointers, and statistics counters are reset or rebuilt by `defxx.c` at probe, open, close, or adapter reset boundaries.

## Dependencies And Integration Points
The header assumes Linux kernel definitions from files included by `defxx.c`, including `u8/u16/u32`, `dma_addr_t`, `struct sk_buff`, `spinlock_t`, `struct net_device`, `struct device`, `struct fddi_statistics`, and FDDI constants. It is tightly coupled to the DEC PDQ port specification, DEC EISA ESIC, DEC PCI PFI, and TURBOchannel CSR layout. Because the structures mirror firmware-visible buffers, field order and sizes are integration contracts.

## Risks
ABI drift is the primary risk: changing structure layout, field width, queue size, alignment, or endian mapping can break DMA with firmware. Several descriptor physical address fields are `PI_UINT32`, so users must ensure DMA addresses fit hardware expectations. Constants such as receive buffer alignment, descriptor block 8 KiB alignment, and command buffer 512-byte size are not optional. Some command response structures are very large and mirror SMT/FDDI specifications; incorrect copying or casting can corrupt statistics. The header also encodes legacy bus assumptions that may not hold on newer architectures.

## Test Signals
Compile coverage on little-endian and big-endian configurations is important because the producer/consumer unions differ. Runtime validation comes from successful adapter initialization, firmware command completion, stable RX/TX ring advancement, correct FDDI statistics, multicast CAM updates, and clean reset/close. Static checks should watch structure sizes, descriptor block alignment, and absence of unintended padding changes in firmware-visible structures.
