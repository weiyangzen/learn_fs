# sources/distributed-fs/ceph-client/drivers/ata/pata_rz1000.c

## Purpose
Supports RZ1000/RZ1001 PCI ATA controllers while disabling their unsafe FIFO behavior and forcing PIO operation.

## Important APIs, Types, And Functions
`rz1000_set_mode()` configures enabled devices for PIO0 only. `rz1000_fifo_disable()` clears FIFO enable bits in PCI config and verifies the result. `rz1000_init_one()` disables FIFO before registering the host. `rz1000_reinit_one()` repeats FIFO disable on resume before resuming libata.

## Control Flow
PCI probe first calls `rz1000_fifo_disable()`; if FIFO cannot be disabled, probe fails. It then registers a PIO-only SFF host. Resume repeats device resume, FIFO disable, and `ata_host_resume()`.

## State And Persistence
State persists in PCI config register `0x40` FIFO bits and libata device mode flags. No driver-private allocation exists.

## Dependencies And Integration Points
Uses PCI config access, libata SFF PIO, generic PCI PM helpers, and RZ1000/RZ1001 PCI IDs.

## Risks And Edge Cases
The FIFO is the main data-corruption risk; failure to disable it must prevent use. The driver deliberately limits modes to PIO0, trading performance for safety. Resume must reapply FIFO disable because firmware or power state can restore defaults.

## Test Signals
Probe with FIFO disable success/failure, PIO-only mode assignment, RZ1000 and RZ1001 IDs, suspend/resume re-disable, and data integrity tests under repeated reads/writes.
