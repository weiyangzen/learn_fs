# sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/tsi108_eth.h

## Purpose
This header is the hardware contract for the Tundra Tsi108 Gigabit Ethernet controller driver. It defines big-endian MMIO access helpers, register offsets, interrupt/status bits, DMA queue controls, and the on-device TX/RX descriptor layouts used by the companion Tsi108 Ethernet implementation.

## Important APIs, types, and constants
The `TSI_READ`, `TSI_WRITE`, `TSI_READ_PHY`, and `TSI_WRITE_PHY` macros assume the caller has a `data` object with `regs` and `phyregs` MMIO bases and perform big-endian `in_be32`/`out_be32` accesses. Register groups cover MAC configuration (`TSI108_MAC_CFG1`, `TSI108_MAC_CFG2`, MII management, station address), statistics counters and carry masks, Ethernet controller port control, interrupt status/mask bits, TX/RX queue configuration, queue pointer registers, hash filters, and DMA thresholds.

The public data types are `tx_desc` and `rx_desc`, each aligned to 32 bytes. `tx_desc` holds split buffer and next-descriptor addresses, VLAN metadata, length, and a 32-bit `misc` field using `TSI108_TX_*` ownership/status/control bits. `rx_desc` mirrors the split address and next fields, then exposes VLAN, received length, buffer length, and a 16-bit `misc` field using `TSI108_RX_*` bits. `TSI108_RX_SKB_SIZE` fixes normal RX buffer size at 1536 bytes.

## Control flow and integration
This file has no executable control flow. Runtime code includes it to program the MAC, configure DMA queue endianness and burst behavior, set descriptor ring base pointers with valid bits, arm RX/TX engines, process interrupts from `TSI108_EC_INTSTAT`, and interpret descriptor ownership. The descriptor comments explicitly state the layout assumes big-endian byte order, which ties the header to the Tsi108 platform's register and DMA representation.

## State and persistence behavior
State is entirely hardware-facing. MAC enable bits, link mode, RX filter bits, interrupt masks, statistics counters, queue pointers, and descriptor ownership persist in device registers and DMA memory until reset or reprogramming. The header also exposes statistic carry bits so driver code can account for counter overflow in software.

## Dependencies and integration points
The header depends on Linux integer types plus architecture/platform support for `in_be32` and `out_be32`. It integrates with Linux netdev DMA paths through descriptor memory that must remain 32-byte aligned and visible to the device. PHY management is through Tsi108 MAC MII registers and separate `phyregs` accessors.

## Risks and edge cases
The access macros rely on an implicit variable named `data`, making misuse easy outside the original driver style. Descriptor fields are split into high/low address words, so DMA address width and endian conversion must be handled exactly by callers. Incorrect ownership bit ordering can let the NIC consume partially initialized descriptors. RX buffer sizing is limited to normal Ethernet plus alignment slack, so jumbo support would require coordinated changes. Register bit definitions include several status carry and queue error bits that must be acknowledged correctly to avoid stuck interrupts.

## Test signals
Useful validation is build coverage of the Tsi108 driver on the target architecture, smoke tests for MMIO read/write byte order, TX/RX descriptor ownership transitions under traffic, PHY read/write operations, interrupt masking/acknowledgement behavior, and statistic overflow accounting with high packet rates.
