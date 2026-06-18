# sources/distributed-fs/ceph-client/kernel/crash_reserve.c

## Purpose
`crash_reserve.c` parses `crashkernel=` command-line forms and reserves physical memory for a crash kernel. It supports simple, range-based, high/low split, and optional CMA crashkernel reservations, then publishes reserved crash resources into the kernel I/O memory resource tree.

## Important APIs, types, and functions
Global resources are `crashk_res` and `crashk_low_res`, both named "Crash kernel" with system RAM and crash-kernel descriptors. Parsing helpers include `parse_crashkernel_mem()`, `parse_crashkernel_simple()`, `parse_crashkernel_suffix()`, `get_last_crashkernel()`, `__parse_crashkernel()`, and exported/arch-called `parse_crashkernel()`.

Reservation helpers include dummy early parameter handler `parse_crashkernel_dummy()`, `reserve_crashkernel_low()`, `reserve_crashkernel_generic()`, `reserve_crashkernel_cma()`, and `insert_crashkernel_resources()`. CMA state includes `crashk_cma_ranges` and `crashk_cma_cnt` when supported.

## Control flow
`parse_crashkernel()` first parses the last plain `crashkernel=` that is not a known suffix. It chooses range syntax if the selected token contains a colon before the next space, otherwise simple `size[@offset]`. On architectures with generic reservation, if no plain value is present it parses `,high`, optionally parses `,low` or defaults low memory, and separately parses optional `,cma`.

`reserve_crashkernel_generic()` reserves the requested size with `memblock_phys_alloc_range()`. It honors a fixed base if supplied, otherwise tries low memory first for plain reservations, can fall back to high memory with a default low allocation, and for explicit high reservations can fall back to low memory. If the selected base is high and low memory is needed, it calls `reserve_crashkernel_low()`. Successful reservations update `crashk_res` and possibly `crashk_low_res`, mark the physical ranges ignored by kmemleak, and may insert resources immediately depending on architecture support.

`reserve_crashkernel_cma()` attempts to reserve the requested CMA amount in one or more contiguous regions, halving the request block size on allocation failure until a page-sized lower bound or maximum range count is reached.

## State and persistence behavior
The file mutates early-boot global reservation state: `crashk_res`, `crashk_low_res`, `crashk_cma_ranges`, and `crashk_cma_cnt`. It reserves memory with memblock/CMA so normal allocators cannot use it and later inserts resources into `iomem_resource`. These reservations persist for the running kernel lifetime and across crash-kernel load operations, but are not written to disk.

## Dependencies and integration points
Dependencies include memblock, CMA, kmemleak, I/O resource management, architecture constants such as `CRASH_ALIGN`, `CRASH_ADDR_LOW_MAX`, `CRASH_ADDR_HIGH_MAX`, optional `HAVE_ARCH_ADD_CRASH_RES_TO_IOMEM_EARLY`, command-line early parameters, and arch code that calls `parse_crashkernel()` and `reserve_crashkernel_generic()`.

## Risks and edge cases
Parsing uses the last matching `crashkernel=` token and filters known suffixes, so duplicate or malformed command lines can be surprising. Range syntax rounds total RAM up to 128M to tolerate firmware reservations. The parser rejects zero or system-RAM-sized reservations but suffix and CMA values have separate handling. Fixed-base reservations fail if the region is busy; fallback behavior differs between plain and high reservations. CMA reservation may reserve less than requested and only warn. Resource insertion is conditional on architecture timing, so early/late I/O resource visibility differs by platform.

## Test signals
Useful tests include command lines for simple size, size with offset, range lists, malformed ranges, duplicate crashkernel entries, `,high`, `,low`, `,cma`, missing low default, fixed-base busy failure, low-to-high and high-to-low fallback, resource-tree insertion, kmemleak ignore behavior, and CMA partial-reservation warnings with range count limits.
