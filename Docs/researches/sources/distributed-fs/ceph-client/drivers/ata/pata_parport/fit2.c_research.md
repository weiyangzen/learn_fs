# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/fit2.c

## Purpose
Supports the Fidelity International Technology TD-2000 simple parallel-port IDE adapter.

## Important APIs, Types, And Functions
`fit2_read_regr()` and `fit2_write_regr()` implement ATA taskfile access using a small strobe sequence. `fit2_read_block()` and `fit2_write_block()` transfer data in nibble-style form. `fit2_connect()`, `fit2_disconnect()`, and `fit2_log_adapter()` save/restore port state and describe the adapter. The `fit2` protocol exposes a low mode count and no EPP modes.

## Control Flow
Core probing uses the default register echo test. Runtime control flow is direct: taskfile operations call register callbacks, and PIO data phases call the block callbacks.

## State And Persistence
Only saved parallel-port register values and selected mode are stored in `pi_adapter`.

## Dependencies And Integration Points
Uses `pata_parport` core registration and low-level SPP port IO helpers.

## Risks And Edge Cases
This is intentionally low-speed and timing-sensitive. Lack of a custom probe hook means it relies on generic echo testing to avoid matching the wrong adapter.

## Test Signals
TD-2000 probe, mode selection, register echo, single-sector reads/writes, delay tuning, and detach state restoration.
