# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/ioas.c

## Purpose
`ioas.c` implements the userspace IO address-space ioctl surface for iommufd IOAS objects. An IOAS is the software IOVA-to-PFN address space backed by `struct io_pagetable`; this file allocates and destroys IOAS objects, exposes allowed IOVA ranges, maps user/file pages, copies mappings between IOAS objects, unmaps mappings, changes page-accounting ownership after process handoff, and handles IOAS-specific options.

## Important APIs, Types, And Functions
The public entry points are `iommufd_ioas_alloc_ioctl()`, `iommufd_ioas_iova_ranges()`, `iommufd_ioas_allow_iovas()`, `iommufd_ioas_map()`, `iommufd_ioas_map_file()`, `iommufd_ioas_copy()`, `iommufd_ioas_unmap()`, `iommufd_ioas_change_process()`, `iommufd_ioas_option()`, and `iommufd_option_rlimit_mode()`. `iommufd_ioas_alloc()` initializes the `io_pagetable`, HWPT list, and mutex, while `iommufd_ioas_destroy()` unmaps everything and destroys table state. `conv_iommu_prot()` translates IOAS map flags to `IOMMU_READ`, `IOMMU_WRITE`, and mandatory `IOMMU_CACHE`.

## Control Flow
Map ioctls validate flags, integer ranges, and read/write permission, then acquire the IOAS object and delegate to `iopt_map_user_pages()` or `iopt_map_file_pages()`. Unmap either removes all mappings on `(iova=0,length=U64_MAX)` or calls `iopt_unmap_iova()` and reports the actual length. Copy reads source pages with `iopt_get_pages()`, then maps them into the destination with `iopt_map_pages()`. Allowed IOVA replacement builds a temporary interval tree from userspace, then atomically swaps it through `iopt_set_allow_iova()`.

## State And Persistence
The persistent state is in the iommufd object xarray and the IOAS `io_pagetable`: area interval trees, reserved ranges, allowed ranges, attached domains, access list, and large-page state. `iommufd_ioas_change_process()` globally takes every IOAS `iova_rwsem` under `ioas_creation_lock`, verifies only file-backed mappings exist, charges the current process/user, uncharges old owners, then updates `source_mm`, `source_task`, and `source_user`.

## Dependencies And Integration Points
This file depends on `io_pagetable` primitives, interval-tree iteration, object lifetime helpers from `main.c`, and test-only syzkaller IOVA conversion. HWPT attachment behavior is indirect through `ioas->hwpt_list` and the table domain list.

## Risks And Test Signals
Key risks are lock ordering in `iommufd_take_all_iova_rwsem()`, overflow around user-provided IOVAs and lengths, atomic replacement of allowed IOVA ranges, and accounting correctness during `IOMMU_IOAS_CHANGE_PROCESS`. Tests should cover fixed and allocated IOVA mapping, map-file accounting migration, all-vs-range unmap, overlapping allowed ranges, invalid flags/reserved fields, IOAS copy failure cleanup, large-page option toggles, and VFIO compatibility paths that reuse the same table primitives.
