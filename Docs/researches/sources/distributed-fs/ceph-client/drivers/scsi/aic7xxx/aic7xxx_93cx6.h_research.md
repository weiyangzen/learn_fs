# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.h

## Purpose

`aic7xxx_93cx6.h` declares the descriptor, chip-type enum, register access macros, and public functions for AIC7xxx 93Cx6 serial EEPROM access. It isolates board-specific control/status/data offsets and bit masks from the generic bit-banging implementation.

## Important APIs, Types, and Functions

- `enum seeprom_chip_t` uses `C46 = 6` and `C56_66 = 8`, representing the number of address bits.
- `struct seeprom_descriptor` carries the owning `ahc_softc`, control/status/dataout register offsets, chip type, and masks for memory-select, ready, chip-select, clock, data-out, and data-in lines.
- Macros `SEEPROM_INB()`, `SEEPROM_OUTB()`, `SEEPROM_STATUS_INB()`, and `SEEPROM_DATA_INB()` route descriptor-relative access through AHC register I/O and flush posted writes.
- Public functions are `ahc_read_seeprom()`, `ahc_write_seeprom()`, and `ahc_verify_cksum()`.

## Control Flow and State

The header has no standalone flow. It defines how implementation code toggles board lines and reads status. A caller fills `struct seeprom_descriptor` for a specific adapter, acquires the SEEPROM using bus/core code, then passes it to read/write helpers.

## State and Persistence Behavior

The descriptor is transient runtime state. `SEEPROM_OUTB()` mutates adapter control registers and flushes writes; `ahc_write_seeprom()` persists changes to serial EEPROM hardware. `ahc_verify_cksum()` validates in-memory persistent configuration images.

## Dependencies and Integration Points

The header depends on `struct ahc_softc`, `struct seeprom_config`, and AHC register access helpers from the OS/core headers. It is used by AIC7xxx bus attach/config code and `aic7xxx_93cx6.c`.

## Risks

- The enum values double as address-bit counts; changing them would break command/address shifting.
- Register offsets and masks are not validated by the helper, so incorrect descriptors can hang or corrupt EEPROM operations.
- The write macro relies on `ahc_flush_device_writes()` semantics for hardware ordering.

## Test Signals

- Compile with all AHC bus front ends that construct `seeprom_descriptor`.
- Confirm descriptor settings can read expected EEPROM contents and checksum on supported C46 and C56/C66 parts.
- Verify write-protect enable/disable sequencing with hardware documentation or a bus analyzer when changing macros.
