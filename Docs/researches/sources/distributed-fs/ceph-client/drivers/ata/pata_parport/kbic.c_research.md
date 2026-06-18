# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/kbic.c

## Purpose
Supports KingByte KBIC-951A and KBIC-971A parallel-to-IDE adapter chips, registering separate protocols because the 971A wakeup sequence can break 951A behavior.

## Important APIs, Types, And Functions
Shared helpers `kbic_read_regr()`, `kbic_write_regr()`, `kbic_read_block()`, and `kbic_write_block()` implement register and data transfers across multiple modes. Protocol-specific connect/test/log routines distinguish 951A and 971A behavior, including the 971A wakeup handling. Two `pi_protocol` instances expose the related adapters.

## Control Flow
Each protocol registers separately. The core probes both as configured, runs protocol tests, and selects a working transfer mode. Runtime callbacks branch on `pi->mode` and use SPP/EPP port sequences as needed.

## State And Persistence
Saved port state lives in `pi_adapter`; protocol-specific detection or wake state may use `pi->private`. Hardware remains selected only while connected.

## Dependencies And Integration Points
Depends on `pata_parport` registration/exported callbacks and raw IO helpers, including word reads from `pi->port + 1` for 5/3 style mode.

## Risks And Edge Cases
Registering related protocols increases false-positive risk. The 971A wakeup code must not run against 951A hardware. Wider transfer modes depend on port resource alignment.

## Test Signals
Separate 951A and 971A detection, wakeup path, all transfer modes, register echo, sector reads/writes, and loading both protocols together.
