# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/epia.c

## Purpose
Implements the older Shuttle EPIA parallel-to-IDE adapter protocol, now superseded by EPAT but still supported for legacy devices.

## Important APIs, Types, And Functions
`epia_read_regr()` and `epia_write_regr()` encode command/control accesses with EPIA-specific cont maps. `epia_read_block()` and `epia_write_block()` provide nibble, 5/3, 8-bit, and EPP-style transfer modes. `epia_connect()`, `epia_disconnect()`, `epia_test_proto()`, and `epia_log_adapter()` initialize, validate, and report the adapter.

## Control Flow
The core probes supported modes using the protocol's test hook. Connect enters the adapter command state, test writes and reads taskfile registers and may validate block transfer behavior, then libata operations run through the selected callbacks.

## State And Persistence
Saved port registers and selected mode live in `pi_adapter`; EPIA adapter state persists only during connect.

## Dependencies And Integration Points
Uses the common `pata_parport` protocol ABI, direct port IO macros, and module-driver registration.

## Risks And Edge Cases
Obsolete hardware and overlapping Shuttle protocol families make false-positive tests a concern. EPP modes require correct base alignment and byte-count assumptions. Connect/disconnect must restore the parallel port for system stability.

## Test Signals
Legacy EPIA adapter probe, each mode's register echo path, block transfer tests, EPP mode constraints, and clean detach after ATA host removal.
