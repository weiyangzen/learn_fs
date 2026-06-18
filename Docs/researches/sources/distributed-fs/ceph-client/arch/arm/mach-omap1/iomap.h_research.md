<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/iomap.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/iomap.h

## Purpose
Defines the common physical, virtual, and size constants for the OMAP1 IO window used by early static mappings and direct physical-address helpers.

## Important APIs, Types, and Functions
Provides `OMAP1_IO_PHYS`, `OMAP1_IO_SIZE`, and `OMAP1_IO_VIRT`. It is a constants-only header.

## Control Flow
No runtime flow. `io.c` consumes these constants to populate `map_desc`, while low-level address macros use the same window for register access.

## State and Persistence Behavior
No software state. The constants describe the persistent static mapping contract for the OMAP1 IO region.

## Dependencies and Integration Points
Requires `OMAP1_IO_OFFSET` from the broader OMAP hardware headers. It integrates with ARM MMU setup and `OMAP1_IO_ADDRESS()` translations.

## Risks
A wrong offset or size corrupts all OMAP1 register access. Because many files use absolute register addresses, this header is a central boot-critical dependency.

## Test Signals
Build-time coverage is inclusion in OMAP1 configs. Runtime validation is early boot through revision detection, timer init, and serial init without data aborts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/iomap.h -->
