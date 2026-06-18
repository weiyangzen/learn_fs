# sources/distributed-fs/ceph-client/drivers/misc/sram-exec.c

## Purpose
`sram-exec.c` adds protected executable SRAM support to the generic SRAM driver. It lets SRAM partitions marked `protect-exec` be copied into safely while preserving a write-xor-execute policy.

## Important APIs, Types, and Functions
`sram_check_protect_exec()` validates that a protected executable partition is page-aligned. `sram_add_protect_exec()` records a partition in the global executable-pool list. The exported `sram_exec_copy()` finds the matching partition for a `gen_pool`, verifies the target range, temporarily switches memory attributes with `set_memory_nx()` and `set_memory_rw()`, performs architecture-specific `fncpy()`, and restores `set_memory_rox()`.

## Control Flow
During SRAM probe, `sram.c` calls the check/add helpers for `protect-exec` reserved blocks. A later client calls `sram_exec_copy()` with a pool and destination inside that pool. The helper locates the partition under `exec_pool_list_mutex`, validates the destination using `gen_pool_has_addr()`, locks the partition, flips the entire relevant page range non-executable and writable, copies the function body with `fncpy()`, restores read-only executable attributes, and returns the callable copied address.

## State and Persistence
The file maintains a global list of executable SRAM partitions protected by a mutex. Per-partition serialization uses `part->lock`. There is no durable state; memory permissions and copied code live only for the current boot and depend on page-attribute state.

## Dependencies and Integration Points
It depends on `CONFIG_SRAM_EXEC`, genalloc pools, `set_memory_*()` page attribute APIs, `asm/fncpy.h`, and the structures declared in `sram.h`. It integrates with the main SRAM driver through `sram_check_protect_exec()` and `sram_add_protect_exec()`, and exports `sram_exec_copy()` to other kernel clients.

## Risks and Edge Cases
The page count is based on `PAGE_ALIGN(size)` from the partition base, not the destination offset, so callers copying near the end of a page range need careful review. If `set_memory_rox()` fails after making memory writable, the function returns `NULL` but may leave weaker permissions. The helper requires architecture support for `fncpy()` and rejects non-page-aligned partitions.

## Test Signals
Validate DT `protect-exec` partitions with aligned and unaligned ranges, `sram_exec_copy()` range rejection, permission transitions through architecture page tables, callable returned addresses, concurrent copy serialization, and error handling for failed `set_memory_*()` calls.
