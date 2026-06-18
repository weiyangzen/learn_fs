<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/setup.c

## Purpose
Handles OpenRISC architecture boot setup: memory discovery/reservation, CPU feature discovery, early FDT selection, delay calibration, paging handoff, initrd handling, and `/proc/cpuinfo`.

## Important APIs, Types, And Functions
Key functions are `setup_memory()`, `setup_cpuinfo()`, `or1k_early_setup()`, `calibrate_delay()`, `setup_arch()`, and `cpuinfo_op` callbacks. Global `cpuinfo_or1k[NR_CPUS]` stores clock, core ID, and cache descriptors.

## Control Flow
`setup_arch()` reserves kernel/initrd/FDT memory, unflattens DT, records CPU info, initializes SMP CPU possible map, sets initial mm bounds, initializes jump labels before RO page lockdown, calls `paging_init()`, and exposes the command line.

## State And Persistence
Populates memblock reservations, global PFN limits, initrd state, CPU info, `loops_per_jiffy`, initial mm section bounds, and procfs CPU display state.

## Dependencies And Integration Points
Depends on OF/FDT, memblock, linker symbols, SMP setup, jump labels, paging, and OpenRISC SPR feature registers.

## Risks
Missing `clock-frequency` is warning-only in CPU info but fatal in delay calibration. `extract_value_bits()` appears unused and has a suspicious `(0 << width)` mask. Memory discovery assumes the kernel-containing DRAM range is the only main memory.

## Test Signals
Boot with/without initrd, DT CPU clock parsing, `/proc/cpuinfo`, memblock reservations, SMP CPU enumeration, and jump-label initialization before paging locks text RO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/setup.c -->
