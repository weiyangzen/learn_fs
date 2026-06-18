# sources/distributed-fs/ceph-client/include/linux/armada-37xx-rwtm-mailbox.h

## Purpose
Defines message payload structures for the Armada 37xx rWTM BIU mailbox.

## Important APIs, Types, And Functions
`struct armada_37xx_rwtm_tx_msg` contains a 16-bit command and sixteen 32-bit arguments. `struct armada_37xx_rwtm_rx_msg` contains a 32-bit return value and sixteen 32-bit status words.

## Control Flow, State, And Persistence
The header stores no state. Mailbox client/provider code fills a TX message, sends it through the mailbox channel, and interprets the RX status returned by firmware.

## Dependencies And Integration Points
Depends on `linux/types.h`. Integrated by Armada 37xx firmware mailbox drivers and clients issuing commands to the rWTM.

## Risks And Test Signals
Struct layout and argument count must match firmware. Tests should validate command serialization, response status parsing, endian assumptions, oversized command rejection in implementation code, and timeout/error propagation from the mailbox framework.
