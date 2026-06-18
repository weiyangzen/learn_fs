# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_migrate.h

Purpose: declares the SVM migration interface for KFD code when `CONFIG_HSA_AMD_SVM` is enabled.

Important APIs/types/functions: defines `enum MIGRATION_COPY_DIR` with `FROM_RAM_TO_VRAM` and `FROM_VRAM_TO_RAM`. Declares `svm_migrate_to_vram`, `svm_migrate_vram_to_ram`, and `svm_migrate_addr_to_pfn`.

Control flow: SVM policy code calls `svm_migrate_to_vram` to move a range or subrange to a selected GPU node and calls `svm_migrate_vram_to_ram` to evict/fault pages back to system memory. Address translation helpers convert VRAM offsets into device-page PFNs using the amdgpu KFD pgmap.

State and persistence: the header owns no state. It exposes functions that mutate `svm_range`, process-device counters, and HMM page state in the implementation.

Dependencies/integration: guarded by `IS_ENABLED(CONFIG_HSA_AMD_SVM)` and includes KFD SVM/private headers plus Linux MM locking definitions. It is the compile-time bridge between SVM range management and migration implementation.

Risks: callers must hold the locks documented in the implementation: mmap read lock, SVM/prange locks, and `prange->migrate_mutex` as applicable. Test signals are compile coverage with SVM enabled/disabled and migration callers honoring lock/context requirements.
