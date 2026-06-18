
# sources/distributed-fs/ceph-client/lib/test_hmm.c

## Purpose

This module is a character-device HMM test driver that mirrors a process address space and simulates device private or coherent memory. It lets userspace read, write, snapshot, migrate, make exclusive, and release mirrored pages through ioctls.

## Important APIs, Types, And Functions

Major types include `struct dmirror` for per-open mirror state, `struct dmirror_device` for each simulated device, `struct dmirror_chunk` for `dev_pagemap` backed device memory, and `struct dmirror_bounce` for temporary user-copy buffers. It uses an XArray as a device page table with pointer tags for write and atomic/exclusive mappings. Important functions cover open/release, MMU interval invalidation, range faulting with `hmm_range_fault()`, read/write bounce copies, migration to device/system through `migrate_vma`, snapshot generation, device-memory fault handling, chunk allocation/removal, and ioctl dispatch.

## Control Flow And State

Module init allocates a chrdev region and creates two device-private devices, plus two coherent devices if both SPM address parameters are supplied. Opening a device allocates a `dmirror`, initializes an XArray, and registers a full-range `mmu_interval_notifier` against the caller's `mm`. Reads and writes consult the XArray, fault missing pages into the mirror, and copy data through a vmalloc bounce buffer. Migration to device allocates simulated device pages, copies system page contents, finalizes migration, and maps backing pages into the XArray. Migration back to system uses `migrate_vma_setup()`, allocates normal pages, copies data back, and erases device mappings. Release removes the interval notifier, evicts chunks back to system pages, destroys the XArray, and frees per-open state.

## State And Persistence

Persistent kernel state includes global `dmirror_devices`, per-device devmem chunk arrays, free-page/free-folio lists protected by spinlock, allocation counters, and per-open XArray mappings protected by `dmirror->mutex`. Device private pages use `zone_device_data` to point to backing system pages; coherent pages use the actual mapped page. The state persists across ioctls until file release or explicit `HMM_DMIRROR_RELEASE`.

## Dependencies And Integration Points

The file depends on HMM, MMU interval notifiers, migrate_vma, ZONE_DEVICE/dev_pagemap, memremap_pages, char devices, device model, xarray, mmap insertion, uaccess, swap/rmap, and the local UAPI header. Userspace integrates through `/dev/hmm_dmirror*`, mmap, and the ioctls defined in `test_hmm_uapi.h`.

## Risks And Test Signals

Risks include page lifetime bugs in fake device memory, missing invalidation of stale XArray entries, large-folio split/fallback corner cases, allocation-failure injection with `HMM_DMIRROR_FLAG_FAIL_ALLOC`, and cleanup ordering around chunk removal. Test signals include ioctl return codes, `cpages` and `faults`, snapshot permission bytes, successful round-trip data after migration, SIGBUS/OOM behavior on device faults, and kernel warnings from migration or page-type assertions.
