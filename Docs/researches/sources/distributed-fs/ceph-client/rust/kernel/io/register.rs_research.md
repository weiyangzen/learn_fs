# sources/distributed-fs/ceph-client/rust/kernel/io/register.rs

## Purpose
`io/register.rs` implements the `register!` macro and supporting traits for type-safe hardware register definitions. It lets drivers model fixed, relative, array, and relative-array registers with generated bitfield accessors and integration with `Io`.

## Important APIs, Types, and Functions
Core traits include `Register`, `FixedRegister`, `RegisterBase`, `WithBase`, `RelativeRegister`, `RegisterArray`, `Array`, `RelativeRegisterArray`, and `LocatedRegister`. Location types include `FixedRegisterLoc`, `RelativeRegisterLoc`, `RegisterArrayLoc`, and `RelativeRegisterArrayLoc`. The `register!` macro generates transparent register value structs, raw conversions, `Zeroable`, `IoLoc` implementations, array metadata, field masks/ranges/shifts, getters, setters, `try_with_*`, const setters, and `Debug`.

## Control Flow
Macro input is dispatched by declaration shape: fixed address, alias, relative base plus offset, fixed array, relative array, and aliases into arrays. Generated location builders compute offsets by fixed offset, base plus offset, or index times stride; compile-time builders use `build_assert`, while `try_at` returns `None` for runtime out-of-range indexes. Field getters use bounded shifts; setters clear the field mask and OR shifted bounded values.

## State and Persistence
Generated register values are plain copyable snapshots of raw storage. Locations are zero-sized or index-carrying values. Hardware state is read/written by `Io`, not stored in this module.

## Dependencies and Integration Points
The module integrates tightly with `IoLoc` and `Io::read/write/update`, `kernel::num::Bounded`, `TryIntoBounded`, `pin_init::Zeroable`, `build_assert`, and macro paste support. It is a key driver ergonomics layer for MMIO register maps.

## Risks
Bit ranges must fit the storage type and not overlap unintentionally; the macro does not enforce all semantic register constraints. Compile-time index validation requires constant inputs. Aliases share offsets but can expose different fields, so incorrect aliasing can make code write incompatible layouts. `Debug` reads generated field getters and may include fallible conversion results.

## Test Signals
Macro tests should cover all declaration forms, aliases, stride validation, fixed and relative arrays, runtime and compile-time index checks, field get/set for full-width and sub-width fields, fallible conversion accessors, debug output, and integration with `Io` read/write.
