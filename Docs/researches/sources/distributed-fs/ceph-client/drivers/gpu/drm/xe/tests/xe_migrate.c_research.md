# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_migrate.c

## Purpose

`xe_migrate.c` is a live KUnit suite for migration engine behavior. It validates page-table update jobs, buffer clear/copy operations across system/VRAM regions, and flat-CCS preservation/clear semantics on Xe2 discrete devices.

## Important APIs, Types, and Functions

- Sanity helpers: `sanity_fence_failed`, `run_sanity_job`, `test_copy`, `test_copy_sysmem`, `test_copy_vram`, and `xe_migrate_sanity_test`.
- Device runner: `migrate_test_run_device` and `xe_migrate_sanity_kunit`.
- BLT/CCS helpers: `blt_copy`, `test_migrate`, `test_clear`, `validate_ccs_test_run_tile`, `validate_ccs_test_run_device`, and `xe_validate_ccs_kunit`.
- Suite: exported `xe_migrate_test_suite`.

## Control Flow

The sanity test maps migration page tables, creates big/tiny BOs, emits PTE updates into a batch buffer, submits migration jobs, verifies PTE writes, clears mapped memory, and then clears/copies small and big BOs to system memory or other VRAM. The CCS validation path creates pinned system, VRAM, and CCS BOs, uses custom BLT copy jobs to compress/decompress or copy CCS only, evicts/restores VRAM BOs, and checks first/last values and CCS zeroing.

## State and Persistence Behavior

The tests mutate live migration queues, batch buffers, page-table BOs, BO vmap contents, TTM resources, migration fences, `m->fence`, job mutex state, and runtime PM. They expect data and CCS metadata to persist or clear according to migration operations.

## Dependencies and Integration Points

It depends on Xe migration internals, batch-buffer helpers, scheduler jobs, VM/page-table encoding, BO creation/validation/vmap, resource cursors, BLT emit helpers, flat-CCS helpers, runtime PM, and live device enumeration.

## Risks and Edge Cases

- The test reaches into internal migration emit helpers and job sequencing, so refactors can require synchronized test updates.
- Fence timeout failures may reflect hardware hangs, scheduling delays, or test bugs.
- CCS validation is platform-gated; non-flat-CCS or non-Xe2 discrete systems skip important paths.
- `blt_copy` updates `m->fence` and must maintain synchronization on error paths.

## Test Signals

Passing tests indicate migration PTE updates execute, clear/copy jobs complete, first/last data values are correct, cross-memory transfers work, compressed VRAM data decompresses correctly, CCS-only copies report expected zeroes, and BO eviction/restore preserves data.
