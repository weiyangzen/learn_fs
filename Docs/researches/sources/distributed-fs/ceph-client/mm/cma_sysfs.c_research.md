# sources/distributed-fs/ceph-client/mm/cma_sysfs.c

Purpose: Provides the sysfs interface for CMA statistics under `mm_kobj/cma/<area>/`. It exposes stable read-only counters for successful allocations, failed allocations, successful releases, total pages, and currently available pages.

Important APIs, types, and functions: `cma_sysfs_account_success_pages()`, `cma_sysfs_account_fail_pages()`, and `cma_sysfs_account_release_pages()` are accounting hooks used by CMA allocation/release paths. `cma_from_kobj()` maps each kobject back to its `struct cma`. The `*_show()` functions format atomic64 counters and page counts via `sysfs_emit()`. `cma_kobj_release()` releases `struct cma_kobject`. `cma_sysfs_init()` creates the root `cma` kobject and per-area kobjects at `subsys_initcall`.

Control flow: initialization creates `mm/cma`, allocates a `cma_kobject` for each global CMA area, links it back to `struct cma`, and calls `kobject_init_and_add()` with `cma_ktype`. Read handlers dereference the owning CMA area and emit current values. On setup failure, already-added kobjects and the root are put.

State and persistence: Statistics are in atomic64 fields inside `struct cma`, while `available_pages` and `total_pages` read live CMA state. The kobject pointer is stored in `cma->cma_kobj` and cleared on release. Values reset on boot and are not persisted.

Dependencies and integration: Integrates with the core CMA allocator through exported accounting functions and `struct cma` fields declared in `cma.h`; integrates with global mm sysfs through `mm_kobj`.

Risks: `available_pages_show()` reads `cma->available_count` without the explicit spinlock used by debugfs; this is acceptable for sysfs statistics but can be momentarily stale. Initialization failure handling assumes previous areas have valid `cma_kobj`. Counter correctness depends on all CMA paths calling the accounting helpers consistently.

Test signals: Boot with CMA enabled, inspect `/sys/kernel/mm/cma/*`, force successful and failed CMA allocations, verify atomic counters advance, and test hot error paths with allocation failures in kobject creation if fault injection is available.
