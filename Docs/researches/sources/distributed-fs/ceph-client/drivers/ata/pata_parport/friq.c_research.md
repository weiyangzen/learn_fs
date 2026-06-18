# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/friq.c

## Purpose
Supports Freecom IQ ASIC-2 parallel-port IDE adapters, including power-management commands for battery-powered external drives.

## Important APIs, Types, And Functions
`friq_read_regr()` and `friq_write_regr()` send encoded `CMD()` sequences for taskfile access. `friq_read_block_int()`, `friq_read_block()`, and `friq_write_block()` implement modes 0-4. `friq_test_proto()` powers the drive on and validates registers plus scratch data. `friq_log_adapter()` disables the sleep timer and marks power state in `pi->private`; `friq_release_proto()` powers the drive off.

## Control Flow
Probe turns power on, waits, tests register and block paths, and selects a working mode. Runtime connect/disconnect save/restore port state; release-time cleanup sends power-off commands if this protocol enabled power.

## State And Persistence
`pi->private` tracks whether the protocol powered the device and should power it down. Saved port state persists across connect/disconnect.

## Dependencies And Integration Points
Integrates with `pata_parport` release hooks and raw parport IO; the core calls `release_proto()` from device teardown.

## Risks And Edge Cases
Built-in use may keep devices powered indefinitely, as noted in the file header. Power sequencing delays are hardware-sensitive. Final-byte handling differs by mode and must avoid over-reading.

## Test Signals
Power-on probe, sleep-timer disable, release power-off, register echo, block scratch test, all modes, and module built-in versus module unload behavior.
