# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.h

## Purpose
Transmit declarations for Octeon Ethernet.

## Important APIs, Types, And Functions
Declares `cvm_oct_xmit()`, `cvm_oct_xmit_pow()`, `cvm_oct_transmit_qos()`, `cvm_oct_tx_initialize()`, `cvm_oct_tx_shutdown()`, and `cvm_oct_tx_shutdown_dev()`.

## Control Flow
`ethernet.c` netdev ops call `cvm_oct_xmit()` for hardware ports and `cvm_oct_xmit_pow()` for the virtual POW device; module probe/remove call TX initialize/shutdown helpers.

## State And Persistence
No header-local state. Functions operate on per-netdev TX lists and hardware counters.

## Dependencies And Integration Points
Included by core and TX implementation files; uses kernel `netdev_tx_t`, `sk_buff`, and `net_device`.

## Risks
The declaration of `cvm_oct_transmit_qos()` must match an implementation elsewhere in the driver snapshot or trigger link failures if referenced.

## Test Signals
Build/link checks and TX path tests from `ethernet-tx.c`.
