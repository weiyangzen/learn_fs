<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/tc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/tc.h

## Purpose
Defines OMAP1 Traffic Controller register addresses, external memory chip-select ranges, and EMIFS helper bit macros.

## Important APIs, Types, and Functions
Provides `TCMIF_BASE`, priority/config registers, `EMIFS_CCS(n)`, `EMIFS_ACS(n)`, chip-select physical/size constants, and EMIFS config bits.

## Control Flow
No runtime flow. DMA priority, suspend assembly, PM save/restore, and board memory setup consume the constants to program memory/interconnect behavior.

## State and Persistence Behavior
No state. Describes memory-controller and traffic-controller hardware layout.

## Dependencies and Integration Points
Used by `pm.c`, `sleep.S`, `omap-dma.c`, `io.c`, and memory/flash board code. Requires size macros such as `SZ_64M` from kernel headers when used.

## Risks
Wrong addresses or chip-select sizes can corrupt memory timing, flash mappings, or DMA bus priority. Assembly users rely on constants remaining integer-literal friendly.

## Test Signals
Compile C and assembly consumers; on hardware, validate flash/SDRAM access, suspend self-refresh, and DMA priority changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/tc.h -->
