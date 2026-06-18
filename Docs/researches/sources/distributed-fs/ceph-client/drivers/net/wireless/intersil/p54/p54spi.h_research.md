# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.h

## Purpose
This header defines SPI register addresses, control/status bits, interrupt bits, DMA limits, target timing constants, small SPI DMA/TX metadata structs, and the SPI-private p54 driver state.

## Important APIs, Types, and Functions
- Register constants define ARM interrupt, host interrupt, general-purpose, device control/status, DMA data, DMA write, and DMA read addresses.
- Control bits include host override, start halted, RAM boot, host reset, CPU enable, and DMA enable.
- Interrupt constants distinguish target wake/sleep/read-done/CTS/DR and host ready/write-ready/update/SW-update bits.
- `struct p54s_dma_regs` models DMA command/length/address triples.
- `struct p54s_tx_info` embeds a list node used in SKB TX metadata.
- `struct p54s_priv` embeds `p54_common`, SPI device, work item, mutex, firmware completion, TX lock/list, firmware state, and firmware pointer.

## Control Flow
No executable logic exists. `p54spi.c` uses the constants and state structs for register transactions, firmware boot, RX/TX, and lifecycle management.

## State and Persistence Behavior
`p54s_priv` persists as the SPI device private data and mac80211 private state. The TX list is protected by `tx_lock`; bus/device state is protected by `mutex`; `fw_state` tracks off/booting/ready/reset phases.

## Dependencies and Integration Points
It depends on Linux mutex/list, mac80211, SPI driver code, and shared p54 definitions. It must remain compatible with `P54_TX_INFO_DATA_SIZE` because `p54s_tx_info` is stored inside p54 TX metadata.

## Risks and Edge Cases
Register constants are firmware/hardware ABI. `SPI_MAX_PACKET_SIZE` and interrupt masks shape transfer behavior. Any growth in `p54s_tx_info` can violate the TX metadata size assumption checked in `p54spi.c`.

## Test Signals
Successful SPI build, firmware boot, interrupt handling, and TX list operation validate the definitions.
