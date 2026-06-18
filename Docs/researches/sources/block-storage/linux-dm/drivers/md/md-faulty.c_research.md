# File Research: sources/block-storage/linux-dm/drivers/md/md-faulty.c

## Purpose
Implements the deprecated MD `faulty` personality, a fault-injection array mode that intentionally fails selected read or write requests for testing.

## Main Interfaces
- Request handling: `faulty_make_request()`, `faulty_fail()`.
- Fault control: `faulty_reshape()` via layout/new_layout.
- Status and sizing: `faulty_status()`, `faulty_size()`.
- Lifecycle: `faulty_run()`, `faulty_free()`.
- Registered personality: `faulty_personality`.

## Control Flow
`faulty_run()` rejects bitmaps, allocates `faulty_conf`, initializes counters and periods, records the underlying rdev, stacks limits, sets array size, then applies the initial layout through `faulty_reshape()`.

`faulty_make_request()` checks write or read modes. Transient modes fail every Nth request or once. Persistent modes add the current sector to the fault table and then fail matching future I/O. `WriteAll` fails writes immediately without submitting them. Other failures clone the original bio, send the clone to the underlying device, and install `faulty_fail()` as completion so the original bio receives an error after the lower device completes.

## State And Synchronization
`faulty_conf` stores per-mode periods, atomic counters, up to 50 persistent fault sectors, per-sector modes, and the single backing rdev. Mode counters are atomic, but persistent fault array updates are simple in-memory mutations intended for this testing personality.

## Integration Points
Registers as an MD personality at `LEVEL_FAULTY` with aliases for faulty MD levels. Uses MD core helpers for bitmap rejection, disk limit stacking, array sizing, and personality registration.

## Notable Behaviors
- Supported modes include write transient, read transient, write persistent, read persistent, write all, and read fixable.
- `ReadFixable` read failures are cleared by a write to the same sector.
- `ClearErrors` clears mode counters and periods; `ClearFaults` drops persistent sector faults.
- Multiple persistent modes on one sector can combine into internal `AllPersist`.
- The module description marks the personality deprecated.

## Risks And Review Focus
- Fault table capacity is fixed at 50 sectors; excess persistent faults are ignored.
- The request is still sent to the backing device for most failure modes, so this is failure simulation rather than media write suppression except for `WriteAll`.
- Persistent-fault mutation has minimal synchronization and should remain test-only.
