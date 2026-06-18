# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/aten.c

## Purpose
Implements the ATEN EH-100 parallel-port IDE protocol for the `pata_parport` core, supporting 4-bit and 8-bit transfer modes.

## Important APIs, Types, And Functions
`aten_write_regr()` and `aten_read_regr()` translate ATA register accesses through ATEN command/control strobes. `aten_read_block()` and `aten_write_block()` transfer PIO data in the selected mode. `aten_connect()`, `aten_disconnect()`, and `aten_log_adapter()` save/restore parallel-port state and report mode details. The `aten` `pi_protocol` advertises `max_mode = 2` and one unit.

## Control Flow
The core probes modes through the protocol table, calls connect before register tests, and then uses the protocol callbacks for libata taskfile and data operations. Mode 0 reconstructs bytes from nibbles with `j44()`, while mode 1 uses direct 8-bit reads.

## State And Persistence
`pi->saved_r0` and `pi->saved_r2` preserve port register state across connect/disconnect. No protocol-private allocation exists.

## Dependencies And Integration Points
Depends on `pata_parport.h` port IO macros and `module_pata_parport_driver()` registration.

## Risks And Edge Cases
The EH-132 EPP variant is explicitly unsupported. Byte-pair loops assume even transfer counts from libata PIO block operations. Incorrect restore of parallel-port state can affect other devices after detach.

## Test Signals
Mode 0 and mode 1 probe, register echo tests, read/write sectors, disconnect state restoration, and failure to select unsupported EPP modes.
