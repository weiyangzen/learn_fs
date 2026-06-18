# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epat.c

## Purpose
Provides Shuttle EPAT/EPEZ parallel-port IDE protocol support, including optional EP1284 c7/c8 chip initialization for newer LS-120-class devices.

## Important APIs, Types, And Functions
`epat_read_regr()`, `epat_write_regr()`, `epat_read_block()`, and `epat_write_block()` implement six transfer modes. `epat_connect()` issues CPP command sequences and optionally programs c8 registers when `epatc8` is enabled. `epat_test_proto()` performs register and block scratch tests. `epat_log_adapter()` reads and reports the chip version. `epat_init()` defaults `epatc8` from `CONFIG_PATA_PARPORT_EPATC8`.

## Control Flow
Module init registers the `epat` protocol. Probe iterates modes, connect initializes the chip and requests EPP for modes 3-5, tests taskfile and block paths, and then runtime ATA operations use the selected mode callbacks.

## State And Persistence
`epatc8` is module/config state. `pi->saved_r0/saved_r2` preserve host port state; EPAT internal registers persist while connected.

## Dependencies And Integration Points
Depends on `pata_parport` core, module parameter handling, config option `PATA_PARPORT_EPATC8`, and EPP-capable parport IO for high modes.

## Risks And Edge Cases
The comment notes CPP handling is not fixed for multiple EPATs on a chain. c8 setup changes internal registers and must match hardware. Tail handling in EPP-16/32 block reads has special byte reads for the final bytes.

## Test Signals
EPAT and EP1284/c8 devices, all six modes, version logging, scratch block test failures, EPP alignment constraints, and module parameter/config combinations.
