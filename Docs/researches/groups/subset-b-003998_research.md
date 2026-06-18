# Research Report: subset-b-003998

Work item `subset-b-003998` covers the iommufd IOAS, object, PFN movement, VFIO compatibility, vIOMMU, and selftest support files under `sources/distributed-fs/ceph-client/drivers/iommu/iommufd/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/ioas.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/ioas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_private.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_private.h

## Purpose
`iommufd_private.h` is the internal contract for the iommufd driver. It defines the context object, IO page-table abstraction, user command carrier, object lifetime helpers, and the object families used by IOAS, hardware page tables, devices, access objects, fault queues, vIOMMU objects, virtual devices, vevent queues, and hardware queues.

## Important APIs, Types, And Functions
`struct iommufd_ctx` owns the file, object xarray, group xarray, destroy waitqueue, IOAS creation lock, mmap maple tree, software MSI state, accounting mode, VFIO no-IOMMU mode, and compat IOAS pointer. `struct io_pagetable` owns domain/access xarrays and interval trees for mapped areas, allowed IOVAs, and reserved IOVAs. `struct iommufd_ucmd` carries ioctl context and automatic object creation state. Inline helpers wrap object lookup and put semantics, including `iommufd_get_ioas()`, `iommufd_get_device()`, `iommufd_get_hwpt_paging()`, `iommufd_get_viommu()`, and similar typed accessors.

## Control Flow
The header establishes the object allocation/finalization protocol: `_iommufd_object_alloc()` reserves an xarray slot, callers initialize privately, and `iommufd_object_finalize()` publishes the pointer. Ucmd allocators defer finalization or abort to the ioctl dispatcher. Destruction helpers either remove an object, tombstone an ID, or attempt auto-destroy for auto-domain HWPTs.

## State And Persistence
All persistent kernel state is rooted in `iommufd_ctx::objects`. Object refcounting uses `users` for live users and `wait_cnt` for deterministic destruction. IOAS state persists through `struct iommufd_ioas` and `struct io_pagetable`; vIOMMU state persists through `struct iommufd_viommu` relationships to HWPTs, vdevices, and event queues.

## Dependencies And Integration Points
The header binds together Linux IOMMU core types, uapi structures, xarrays, maple trees, interval trees, access APIs exported to in-kernel users, fault/event queue dispatch, and optional `CONFIG_IOMMUFD_TEST` hooks. It also declares VFIO compatibility and software MSI support.

## Risks And Test Signals
The main risks are API contract drift between object types, refcount imbalance, lock-order mismatch with `domains_rwsem -> iova_rwsem -> pages::mutex`, and incorrect inline helper type assumptions. Tests should exercise object creation abort/finalize paths, auto-domain lifetime, access detach/destroy, vIOMMU event queue lookup, selftest-disabled stubs, and all ioctl handlers declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_test.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_test.h

## Purpose
`iommufd_test.h` defines the UAPI-only selftest command ABI used by `selftest.c` and tools under kernel selftests. It exposes mock operation IDs, mock hardware constants, synthetic data structures, and special type IDs for testing IOAS mapping, mock domains, access pinning, dirty tracking, IOPF, vIOMMU, PASID, hardware queues, and dma-buf revocation.

## Important APIs, Types, And Functions
The central ABI is `struct iommu_test_cmd`, selected by `op` and carrying per-operation payloads in a union. Operation IDs include `IOMMU_TEST_OP_MOCK_DOMAIN`, `IOMMU_TEST_OP_MD_CHECK_MAP`, `IOMMU_TEST_OP_CREATE_ACCESS`, `IOMMU_TEST_OP_DIRTY`, `IOMMU_TEST_OP_TRIGGER_IOPF`, `IOMMU_TEST_OP_TRIGGER_VEVENT`, PASID attach/replace/detach/check commands, and dma-buf get/revoke commands. Mock constants define aperture bounds, page sizes, huge-page size, access flags, PASID width, nested IOTLB slots, device cache slots, and selftest-only type discriminators.

## Control Flow
Userspace submits `IOMMU_TEST_CMD`; the main ioctl dispatcher copies the structure and `selftest.c` switches on `op`. Each union member mirrors one command handler and uses `id` as the primary object ID, with `last` providing the minimum-size marker for ioctl validation.

## State And Persistence
The header itself has no runtime state, but its fields name persistent kernel-side state: mock devices and HWPT IDs, access item IDs, nested IOTLB entries, vdevice cache entries, dma-buf file descriptors, and returned vIOMMU mmap offsets.

## Dependencies And Integration Points
It includes public `linux/iommufd.h` and is consumed by the module's `CONFIG_IOMMUFD_TEST` implementation and userspace selftests. The selftest type constants deliberately avoid normal enum values so the generic user-data parsing paths can reject or accept them explicitly.

## Risks And Test Signals
ABI risks include structure-size drift, wrong `last` marker coverage, conflicting selftest type constants, and command union fields being misinterpreted by old userspace. Test signals are broad: every enum value should map to exactly one `selftest.c` handler, invalid flags should return the documented errno, and returned IDs/fds/offsets should remain stable across object lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iova_bitmap.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iova_bitmap.c

## Purpose
`iova_bitmap.c` implements a helper for setting bits in a userspace bitmap that represents an IOVA range. It is used by dirty tracking and similar report paths that need to mark arbitrary IOVA subranges without permanently pinning an entire large bitmap.

## Important APIs, Types, And Functions
The exported namespace APIs are `iova_bitmap_alloc()`, `iova_bitmap_free()`, `iova_bitmap_for_each()`, and `iova_bitmap_set()`. Internal `struct iova_bitmap` tracks the full IOVA range, userspace bitmap pointer, mapped word indices, and current `struct iova_bitmap_map`. The map stores the currently pinned user pages, base IOVA, length, page granularity shift, page offset, and page count.

## Control Flow
Allocation records the base IOVA, length, bit granularity, total u64 word count, and allocates one page for `struct page *` pointers. `iova_bitmap_for_each()` currently invokes the callback once for the full range, while `iova_bitmap_set()` lazily pins the bitmap window containing the requested IOVA range. If the set spans outside the pinned window, it advances, unpins old pages, pins the next pages, and continues setting bits through `kmap_local_page()` and `bitmap_set()`.

## State And Persistence
Only the bitmap object and transient pinned user pages persist across calls. The user-visible persistent result is the modified userspace bitmap. `iova_bitmap_put()` releases pinned pages, and `iova_bitmap_free()` unpins, frees the pointer page, and frees the object.

## Dependencies And Integration Points
The helper depends on GUP (`pin_user_pages_fast()`), highmem local mappings, and kernel bitmap operations. It exports symbols in the `IOMMUFD` namespace for use by dirty tracking code.

## Risks And Test Signals
Risks concentrate around arithmetic: bitmap byte-vs-u64 indexing, unaligned userspace bitmap addresses, page-window rollover, range-end overflow, and silently returning from `iova_bitmap_set()` if advancing fails. Tests should include unaligned bitmap pointers, multi-window dirty ranges, end-of-range ranges, different page sizes, partial final words, GUP failure injection, and verification that all pinned pages are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iova_bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/main.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/main.c

## Purpose
`main.c` is the iommufd module core. It registers `/dev/iommu` and, when enabled, `/dev/vfio/vfio`, owns per-file context creation/destruction, dispatches ioctls, implements object allocation/finalization/removal, supports mmap of driver-provided MMIO windows, and exports context reference helpers.

## Important APIs, Types, And Functions
Core object APIs are `_iommufd_object_alloc()`, `_iommufd_object_alloc_ucmd()`, `iommufd_object_finalize()`, `iommufd_object_abort()`, `iommufd_object_abort_and_destroy()`, `iommufd_get_object()`, and `iommufd_object_remove()`. File operations are `iommufd_fops_open()`, `iommufd_fops_release()`, `iommufd_fops_ioctl()`, and `iommufd_fops_mmap()`. Exported helpers are `iommufd_ctx_get()`, `iommufd_ctx_from_file()`, `iommufd_ctx_from_fd()`, `iommufd_ctx_put()`, and `iommufd_global_device()`.

## Control Flow
Open allocates an `iommufd_ctx`, initializes xarrays, locks, maple tree, waitqueue, MSI state, and optional VFIO accounting mode. Ioctl dispatch reads the user size, validates command number and minimum size, copies the extensible structure, calls the command handler, then finalizes or aborts any object allocated through `ucmd->new_obj`. Unknown iommufd command numbers fall through to VFIO compatibility. Release repeatedly removes leaf objects whose `users` refcount reaches one until the object graph is gone.

## State And Persistence
Persistent state is per file descriptor in `iommufd_ctx`. Objects start as reserved xarray slots and become visible only after finalization. `wait_cnt` allows destroy paths to wait for transient users before freeing. Mmap state is stored in `ictx->mt_mmap`, keyed by page-shifted offsets handed to userspace.

## Dependencies And Integration Points
The dispatch table wires the uapi command set to IOAS, HWPT, dirty tracking, fault queue, vIOMMU, vdevice, vevent queue, hardware queue, VFIO IOAS, and selftest handlers. Module init/exit register misc devices and selftest support.

## Risks And Test Signals
Important risks are refcount ordering, destroy wait timeouts, ucmd auto-finalization mismatch, object ops missing destroy/abort callbacks, mmap offset validation, and VFIO misc-device compatibility. Tests should cover short and extended ioctl sizes, abort after partial object creation, concurrent destroy/get, file release with interior object graphs, mmap exact-offset/length checks, and module init error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/pages.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/pages.c

## Purpose
`pages.c` is the PFN storage and movement engine for iommufd. It backs `struct iopt_pages`, which represents a linear PFN array sourced from userspace memory, a memfd/file, or a dma-buf, and moves PFNs between three storage tiers: the `pinned_pfns` xarray for in-kernel access, IOMMU domains, and the original source.

## Important APIs, Types, And Functions
Key exported/internal APIs include `iopt_alloc_user_pages()`, `iopt_alloc_file_pages()`, `iopt_alloc_dmabuf_pages()`, `iopt_release_pages()`, `iopt_pages_update_pinned()`, `iopt_area_fill_domain()`, `iopt_area_fill_domains()`, `iopt_area_unfill_domain()`, `iopt_area_unfill_domains()`, `iopt_pages_fill_xarray()`, `iopt_pages_fill_from_xarray()`, `iopt_pages_rw_access()`, `iopt_area_add_access()`, and `iopt_area_remove_access()`. Internal helpers include the double-span interval iterator, `struct pfn_batch`, user/file/dma-buf PFN readers, and xarray/domain transfer helpers.

## Control Flow
Mapping a new area into domains locks the pages, builds a `pfn_reader`, reads PFNs from the best available tier, batches contiguous PFNs, and maps each batch into every domain. On failure it unmaps already-installed ranges and releases newly pinned pages. Removing a domain or area unmaps IOVA first, then unpins pages only if neither another domain nor access interval still covers them. In-kernel access fills the xarray from existing domains or the source, inserts an access interval, and removes/unpins on release. Read/write access either uses direct userspace copy fast paths or the full PFN reader slow path.

## State And Persistence
`iopt_pages` persists source ownership (`source_mm`, `source_task`, `source_user`), type-specific source data, `npages`, `npinned`, `last_npinned`, `account_mode`, `pinned_pfns`, `access_itree`, and `domains_itree`. Dma-buf pages also keep an attachment, physical vector, revoke status, and per-domain trackers. Destruction asserts all interval trees and xarrays are empty and no pins remain.

## Dependencies And Integration Points
This file integrates Linux GUP, memfd folio pinning, dma-buf dynamic attachments and revoke callbacks, VFIO PCI dma-buf mapping by symbol lookup, IOMMU map/unmap/iova-to-phys APIs, generic page-table dirty support, and iommufd access/domain code.

## Risks And Test Signals
High-risk areas are unmap-before-unpin security, accounting mode transitions, remote-mm locking, fault-injection cleanup, dma-buf revocation while mapped, contiguous-batch carry logic, large-page-disabled VFIO behavior, and xarray rollback. Tests should use selftest memory-limit/failure injection, map/unmap with overlapping access intervals, domain attach/detach under active pins, memfd and user mappings, dma-buf revoke, read/write slow paths, and dirty-page interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/selftest.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/selftest.c

## Purpose
`selftest.c` provides kernel-side infrastructure for iommufd selftests. It creates a mock IOMMU bus/device/domain implementation, test-only ioctls, fault injection hooks, access-object tests, dirty tracking tests, vIOMMU and hardware queue mocks, PASID attach/replace/detach tests, and dma-buf mapping/revocation tests.

## Important APIs, Types, And Functions
The main ioctl entry is `iommufd_test()`. Mock objects include `struct mock_iommu_domain`, `struct mock_iommu_domain_nested`, `struct mock_viommu`, `struct mock_hw_queue`, `struct mock_dev`, `struct selftest_obj`, `struct selftest_access`, and `struct iommufd_test_dma_buf`. Setup/teardown are `iommufd_test_init()` and `iommufd_test_exit()`. Public hooks for production code include `iommufd_should_fail()`, `iommufd_test_syz_conv_iova_id()`, `iommufd_selftest_is_mock_dev()`, and `iommufd_test_dma_buf_iommufd_map()`.

## Control Flow
Initialization registers debugfs fault injection, a platform IOMMU device, a mock bus, IOMMU ops, and an IOPF queue. `IOMMU_TEST_CMD` switches to handlers for adding reserved IOVAs, creating mock domains/devices, replacing HWPTs, checking mappings/refcounts/IOTLB/cache entries, creating and using access FDs, setting temporary allocation limits, marking dirty pages, triggering IOPF and vIOMMU events, PASID operations, and dma-buf get/revoke. Mock attach ops update vIOMMU/vdevice state and IOPF registration.

## State And Persistence
Persistent test state includes mock devices, bound iommufd devices, selftest objects, mock IOTLB arrays, mock device cache arrays, vIOMMU queue arrays, access item lists, exported dma-buf backing memory, and global fault-injection/memory-limit settings. Object lifetime is tied into normal iommufd object destruction.

## Dependencies And Integration Points
The file depends on iommufd core APIs, IOMMU core mock hooks, generic page-table helpers, dma-buf APIs, debugfs fault injection, platform devices, and userspace selftests consuming `iommufd_test.h`.

## Risks And Test Signals
Risks include selftest code masking production lifetime bugs, PASID rollback simulation accuracy, vIOMMU mmap cleanup, queue dependency cleanup, dma-buf revocation races, and access unmap locking. Strong test signals include successful fault-injection cleanup, page-ref checks after map/unmap, dirty bitmap round trips, nested invalidation processed counts, vevent delivery, PASID attach/replace rollback at reserved PASID 1024, and module unload waiting for mock IOMMU users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/vfio_compat.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/vfio_compat.c

## Purpose
`vfio_compat.c` emulates the legacy VFIO type1 container ioctl ABI on top of iommufd. It provides a compatibility IOAS for ABI calls that do not carry an IOAS ID and translates VFIO map/unmap/info/extension operations to iommufd IOAS and `io_pagetable` primitives.

## Important APIs, Types, And Functions
Exported compatibility helpers are `iommufd_vfio_compat_ioas_get_id()`, `iommufd_vfio_compat_set_no_iommu()`, and `iommufd_vfio_compat_ioas_create()`. The iommufd ioctl handler is `iommufd_vfio_ioas()`, and the fallback VFIO dispatcher is `iommufd_vfio_ioctl()`. Internal handlers implement DMA map/unmap, cache-coherency extension checks, `VFIO_SET_IOMMU`, page-size reporting, IOVA capability construction, and DMA availability capability construction.

## Control Flow
Group attach paths create or retrieve a compat IOAS. `IOMMU_VFIO_IOAS_GET/SET/CLEAR` exposes or changes the compat IOAS pointer. `VFIO_IOMMU_MAP_DMA` validates legacy flags, converts them to IOMMU protections, and maps user pages into the compat IOAS. `VFIO_IOMMU_UNMAP_DMA` handles full unmap or range unmap, with extra IOVA cuts when large pages are disabled. `VFIO_IOMMU_GET_INFO` reports page sizes and chained capabilities.

## State And Persistence
The persistent state is `ictx->vfio_ioas` and `ictx->no_iommu_mode`, guarded by the context object xarray lock. The compat IOAS is a normal user-visible IOAS object and is destroyed by regular object release if userspace does not destroy it.

## Dependencies And Integration Points
This file integrates Linux VFIO uapi structures, iommufd IOAS lookup/allocation, `io_pagetable` mapping, reserved IOVA interval traversal, and attached domain page-size discovery. It is called from `main.c` for unknown iommufd ioctls and from VFIO-facing attach paths.

## Risks And Test Signals
Risks include imperfect no-IOMMU emulation, legacy TYPE1 large-page splitting behavior, divergence from VFIO capability sizing, stale compat IOAS pointers, and unsupported dirty-page legacy ABI. Tests should cover VFIO API version, set/check extension combinations, map/unmap all, TYPE1 disabling of large pages, cap buffer truncation/resizing, no-IOMMU exclusion from normal IOAS, and cache-coherency reporting across HWPTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/vfio_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/viommu.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/viommu.c

## Purpose
`viommu.c` implements user-visible virtual IOMMU objects, virtual devices attached to a vIOMMU, and hardware queue objects backed by guest memory. It is the core glue between generic iommufd objects and IOMMU-driver-specific vIOMMU callbacks.

## Important APIs, Types, And Functions
Main entry points are `iommufd_viommu_alloc_ioctl()`, `iommufd_viommu_destroy()`, `iommufd_vdevice_alloc_ioctl()`, `iommufd_vdevice_abort()`, `iommufd_vdevice_destroy()`, `iommufd_hw_queue_alloc_ioctl()`, and `iommufd_hw_queue_destroy()`. Internal helpers include `iommufd_hw_queue_alloc_phys()` for pinning guest queue memory and verifying physical contiguity, and `iommufd_hw_queue_destroy_access()` for access cleanup.

## Control Flow
vIOMMU allocation validates type/flags, gets the physical device and paging HWPT, requires the HWPT to be a nesting parent, allocates a driver-sized object, initializes vdevice and veventq containers, records the IOMMU device, and calls `ops->viommu_init()`. Vdevice allocation validates the device belongs to the same physical IOMMU, serializes under the IOMMU group lock, inserts by virtual ID into the vIOMMU xarray, and calls optional driver init. Hardware queue allocation validates type/length, pins a physically contiguous range from the nesting parent IOAS through an internal access object, then calls the driver physical-queue init callback.

## State And Persistence
`struct iommufd_viommu` persists a reference to the parent paging HWPT, a vdevice xarray, veventq list, IOMMU device pointer, type, and driver ops. `struct iommufd_vdevice` links a physical iommufd device to a virtual ID. `struct iommufd_hw_queue` persists vIOMMU reference, internal access, base IOVA, length, type, and driver destroy callback.

## Dependencies And Integration Points
This file depends on IOMMU driver ops (`get_viommu_size`, `viommu_init`, optional vdevice and queue ops), iommufd access APIs, HWPT nesting state, IOMMU group locking, and object lifetime handling in `main.c`.

## Risks And Test Signals
High-risk areas are object-finalization error paths, group-lock lifetime of `idev->vdev`, stale vdevice xarray entries, hardware queue physical-contiguity assumptions, pinned queue cleanup on driver init failure, and driver-provided size/callback mismatches. Tests should cover unsupported/default types, non-nesting HWPT rejection, mismatched IOMMU devices, duplicate virtual IDs, vdevice destroy while device is pre-destroying, non-contiguous queue memory, queue dependency teardown, and vIOMMU driver init failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommufd/viommu.c -->
