# sources/distributed-fs/ceph-client/security/landlock/errata.h

## Purpose

`errata.h` builds the list of Landlock ABI errata known to this kernel. Errata let userspace detect semantic fixes that may affect compatibility or feature decisions.

## Important APIs, Types, and Functions

`struct landlock_erratum` stores the ABI number and erratum number. `LANDLOCK_ERRATUM(NUMBER)` emits entries using the currently defined `LANDLOCK_ERRATA_ABI`. `landlock_errata_init[]` conditionally includes `errata/abi-*.h` files using `__has_include` for ABIs 1 through 6 and terminates with an empty entry.

## Control Flow

At compile time, each included ABI errata file expands one or more `LANDLOCK_ERRATUM()` entries. At boot, `setup.c` iterates this table in `compute_errata()` and sets bits in `landlock_errata` for entries whose ABI is not newer than the runtime ABI version.

## State and Persistence Behavior

The table is `__initconst` and only feeds the boot-time bitmask. Runtime state is the integer bitmask in `setup.c`.

## Dependencies and Integration Points

It depends on compiler `__has_include` support and ABI-specific errata headers. The bitmask is visible through Landlock ABI/syscall surfaces outside this file.

## Risks and Test Signals

Missing include lines can hide errata from userspace. New errata must preserve backport rules documented in the header. Test boot warnings for compilers without `__has_include`, verify errata bits through Landlock selftests, and add documentation with each erratum.
