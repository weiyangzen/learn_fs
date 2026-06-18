<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.h

## Purpose
`id.h` defines the shared die-ID data structure used by OMAP2 CPU identification code.

## Important APIs, Types, and Functions
It defines `struct omap_die_id` with four 32-bit ID words: `id_0`, `id_1`, `id_2`, and `id_3`. There are no function declarations.

## Control Flow
There is no runtime control flow. `id.c` fills this struct from TAP die-ID registers.

## State and Persistence Behavior
The struct carries hardware identity values while in memory. It does not persist data by itself; consumers may use values for randomness, package detection, or logging.

## Dependencies and Integration Points
It integrates with `id.c` and any code needing a typed die-ID container. It relies on standard fixed-width integer typedefs being available through included kernel headers in consumers.

## Risks
Changing field order or width breaks die-ID interpretation and randomness/package detection. The header is otherwise stable and minimal.

## Test Signals
Compile `id.c`; boot logs and die-ID debug output should show four correctly read words on OMAP families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.h -->
