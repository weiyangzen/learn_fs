# sources/distributed-fs/ceph-client/drivers/memory/of_memory.h

## Purpose
`of_memory.h` declares the device-tree DDR parsing helper API and supplies NULL-returning stubs when `CONFIG_OF` or `CONFIG_DDR` is disabled.

## Important APIs, Types, And Functions
The header declares LPDDR2 APIs `of_get_min_tck()`, `of_get_ddr_timings()`, and `of_lpddr2_get_info()`, plus LPDDR3 APIs `of_lpddr3_get_min_tck()` and `of_lpddr3_get_ddr_timings()`. The disabled-configuration stubs preserve buildability for callers but return NULL for all helper calls.

## Control Flow
There is no runtime control flow in enabled builds beyond external function calls. In disabled builds, inline stubs immediately return NULL.

## State And Persistence
The header defines no state. Returned object ownership and persistence are controlled by `of_memory.c` through devm allocations or global const fallbacks.

## Dependencies And Integration Points
It is used by memory-controller drivers such as TI EMIF and depends on type visibility for `struct device_node`, `struct device`, LPDDR2/LPDDR3 timing structures, and `u32` from included kernel headers in consumers.

## Risks
Callers must handle NULL stubs when OF or DDR support is disabled. The include guard closing comment has a typo, but the guard macro itself is correct. Because the header does not include `jedec_ddr.h`, consumers must include required type definitions before or alongside it.

## Test Signals
Build both enabled and disabled `CONFIG_OF`/`CONFIG_DDR` combinations. Static analysis should verify all callers handle NULL timing/info pointers from stubs or parsing failures.
