
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_reg.h

## Purpose

This header defines the HIBMCGE hardware register map, bitfields, interrupt masks, port modes, and TX/RX descriptor layouts/error-code constants used by all driver modules.

## Important APIs, Types, and Functions

- Register groups cover device specs/events/messages, MDIO, SGMII/GMAC, PCU/FIFO/interrupts, TX/RX buffer channels, stats counters, and descriptor/error fields.
- Interrupt masks include hardware bits such as `WE_ERR`, `RBREQ_ERR`, MAC FIFO errors, AHB errors, drops, buffer availability, TX packet completion, plus driver-only pseudo bits `HBG_INT_MSK_TX_B` and `HBG_INT_MSK_RX_B`.
- Port modes define SGMII 10/100/1000 values.
- `struct hbg_tx_desc` and `struct hbg_rx_desc` represent the hardware descriptor words used by TX/RX and tracepoints.
- RX descriptor field masks and L3/L4 error enums drive receive validation and stats classification.

## Control Flow

There is no runtime control flow. The constants are consumed by register access and descriptor parsing code.

## State and Persistence

No state is stored here. The definitions describe persistent hardware registers and DMA descriptor formats.

## Dependencies and Integration Points

The header is included by hardware, MDIO, IRQ, TX/RX, ethtool, diagnostics, and tracepoint code. It depends on Linux bit macros through transitive includes in consumers.

## Risks and Edge Cases

Register offset or bitfield errors would corrupt device programming or stats interpretation. Driver-only TX/RX pseudo interrupt bits must not be confused with hardware `CF_INTRPT_MSK` bits. Descriptor format definitions must match hardware DMA writes exactly, especially field widths for packet length, port number, checksum errors, and valid size.

## Test Signals

Signals include correct hardware initialization, valid ethtool register dumps, IRQ handling for all masks, RX descriptor trace output matching packets, checksum/stat classification, and successful TX descriptor submission.
