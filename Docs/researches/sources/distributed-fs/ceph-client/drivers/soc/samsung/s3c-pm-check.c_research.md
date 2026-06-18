# sources/distributed-fs/ceph-client/drivers/soc/samsung/s3c-pm-check.c

## Purpose

`s3c-pm-check.c` implements an optional suspend/resume memory corruption checker for Samsung S3C-style platforms. It computes CRC32 checksums over system RAM chunks before suspend and compares them after resume to detect memory retention or restore failures.

## Important APIs, Types, and Functions

Public functions are `s3c_pm_check_prepare()`, `s3c_pm_check_store()`, `s3c_pm_check_restore()`, and `s3c_pm_check_cleanup()`. Internal traversal uses `s3c_pm_run_res()` and `s3c_pm_run_sysram()` over `iomem_resource`. Callback type `run_fn_t` returns the next CRC pointer. `s3c_pm_countram()` sizes the CRC buffer, `s3c_pm_makecheck()` stores CRCs, `s3c_pm_runcheck()` validates them, and `in_region()` skips volatile memory areas. Global state is `crc_size` and `crcs`.

## Control Flow

Prepare counts all `IORESOURCE_SYSTEM_RAM` resources in `CHECK_CHUNKSIZE` blocks and allocates the CRC array before late suspend. Store traverses the same RAM resources and writes one CRC per chunk using `crc32_le(~0, phys_to_virt(addr), left)`. Restore traverses again, skips chunks containing the current stack page or CRC buffer, recalculates CRCs, and logs mismatches. Cleanup frees the allocated CRC buffer separately because restore may run in a context that cannot sleep.

## State and Persistence Behavior

`crcs` persists only across one suspend/resume cycle in kernel heap memory. The checker intentionally avoids persistent storage. It reads physical RAM through direct mappings and reports errors to the kernel log; it does not repair memory.

## Dependencies and Integration Points

It depends on kernel resource trees, suspend hooks from Samsung PM code, CRC32, direct `phys_to_virt` mappings, `CONFIG_SAMSUNG_PM_CHECK_CHUNKSIZE`, and `S3C_PMDBG` logging. It integrates with platform suspend sequencing.

## Risks and Edge Cases

The code casts stack addresses through `u32`, which is only safe for legacy 32-bit platforms. `in_region()` performs arithmetic on `void *`, relying on compiler extensions. The chunk loop uses `addr < res->end` and `left = res->end - addr`, while resource ends are inclusive, so boundary coverage deserves scrutiny. Allocating `crc_size + 4` has no explicit overflow check. Memory modified legitimately during resume, beyond stack and CRC buffer, can trigger false positives.

## Test Signals

Run suspend/resume with PM debug enabled on supported 32-bit Samsung systems, verify no CRC mismatches on healthy hardware, inject controlled RAM corruption if possible, and test small/large chunk sizes. Static analysis should flag pointer-width assumptions if this code is built outside its intended architecture.
