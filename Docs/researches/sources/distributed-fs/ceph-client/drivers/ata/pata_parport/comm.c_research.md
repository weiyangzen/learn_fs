# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/comm.c

## Purpose
Implements the DataStor Commuter parallel-port IDE adapter protocol for `pata_parport`.

## Important APIs, Types, And Functions
`comm_read_regr()` and `comm_write_regr()` encode ATA register access using Commuter control maps and strobe macros. `comm_read_block()` and `comm_write_block()` implement nibble and byte transfer modes. `comm_connect()`, `comm_disconnect()`, and `comm_log_adapter()` manage port state and diagnostics. The `comm` `pi_protocol` exposes two non-EPP modes.

## Control Flow
During probe the core connects, performs default register echo testing, and records the best working mode. At runtime, ATA taskfile accesses go through the register callbacks; data phases call the block callbacks that reconstruct or emit bytes using the Commuter handshake.

## State And Persistence
The protocol stores only saved parallel-port registers in `pi->saved_r0/saved_r2` and uses `pi->mode` for transfer selection.

## Dependencies And Integration Points
Depends on `pata_parport` core registration and SPP-style parallel port IO macros.

## Risks And Edge Cases
Low-speed nibble mode is timing-sensitive and susceptible to wrong delay settings. The protocol has no custom test hook, so default register tests must distinguish it from similar adapters.

## Test Signals
Default protocol testing, both modes, ATA identify/read/write paths, delay override through `new_device`, and disconnect restoring saved registers.
