# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_svm.h

## Purpose
Defines the public and internal SVM data structures and function declarations used by KFD process, migration, fault, eviction, and CRIU code.

## Important APIs, Types, And Functions
`SVM_RANGE_VRAM_DOMAIN` tags DMA address entries that represent VRAM-domain addresses. `SVM_ADEV_PGMAP_OWNER` groups HMM ownership by XGMI hive or device. `struct svm_range_bo` owns an amdgpu BO, KRef, range list, eviction fence/work, and associated KFD node. `enum svm_work_list_ops` and `struct svm_work_list_item` describe deferred range-list operations. `struct svm_range` carries the interval, notifier, DMA mappings, VRAM BO state, attributes, access bitmaps, deferred/child lists, migration lock, and mapped/invalid bookkeeping. The header declares range initialization/finalization, ioctl dispatch, fault restore, VRAM node management, deferred work scheduling, DMA unmap helpers, CRIU helpers, SVM support checks, and XNACK reserve transitions.

## Control Flow
When SVM is enabled, callers use the full implementation. When `CONFIG_HSA_AMD_SVM` is disabled, inline stubs make initialization/finalization mostly no-op, report no SVM ranges, reject restore/restore-from-CRIU paths, and make `KFD_IS_SVM_API_SUPPORTED` false.

## State And Persistence
The header defines in-memory per-range state only. CRIU functions declared here serialize selected state through KFD private checkpoint data; no direct persistent storage exists in the header.

## Dependencies And Integration Points
Includes Linux list/mutex/rwsem/mm headers plus amdgpu and KFD private headers. It is a shared contract between `kfd_svm.c`, KFD process lifecycle code, KFD migration code, amdgpu eviction fences, and CRIU integration.

## Risks
`svm_range_lock` also enters `memalloc_noreclaim_save`, so callers must pair unlocks exactly. The stub and enabled APIs must stay signature-compatible. The VRAM-domain tag consumes a low address bit and depends on page-aligned DMA/VRAM representations. Any struct layout change affects a broad set of lock, migration, and notifier assumptions.

## Test Signals
Build both enabled and disabled SVM configurations. Exercise eviction, migration, CRIU, and process teardown paths that compile through this header, and run lockdep to catch unpaired `svm_range_lock`/`svm_range_unlock` behavior.
