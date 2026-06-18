# sources/distributed-fs/ceph-client/mm/damon/Kconfig

Purpose: Declares build-time configuration for DAMON, its operation backends, user interfaces, optional modules, and KUnit tests.

Important symbols: `DAMON` enables the framework. `DAMON_DEBUG_SANITY` adds runtime sanity checks. `DAMON_KUNIT_TEST`, `DAMON_VADDR_KUNIT_TEST`, and `DAMON_SYSFS_KUNIT_TEST` gate test inclusion. `DAMON_VADDR` and `DAMON_PADDR` select virtual and physical address monitoring operations and select `PAGE_IDLE_FLAG`. `DAMON_SYSFS` enables sysfs control. `DAMON_RECLAIM`, `DAMON_LRU_SORT`, and `DAMON_STAT` enable policy modules. `DAMON_STAT_ENABLED_DEFAULT` controls default stat startup.

Control flow: Kconfig dependencies shape which objects the Makefile builds and which runtime module parameters become available. Core DAMON can exist alone; paddr/vaddr ops depend on `DAMON && MMU`; sysfs depends on `SYSFS`; policy modules depend on paddr ops.

State and persistence: No runtime state. It persists selected build capabilities into the kernel configuration and therefore constrains the runtime API surface.

Dependencies and integration: Feeds `mm/damon/Makefile`, module initialization, and tests. The selected symbols govern whether `core.c`, ops backends, sysfs files, and modules such as reclaim/lru_sort/stat are compiled.

Risks: Build combinations need to preserve object dependencies, especially shared `ops-common.o` for vaddr/paddr and `modules-common.o` for modules. Enabling debug sanity checks may add overhead. Default-enabling `DAMON_STAT` changes boot-time monitoring behavior.

Test signals: Build matrices should cover minimal `DAMON`, paddr/vaddr, sysfs, KUnit, and each module. Kconfig dependency checks should reject modules without required ops and ensure `PAGE_IDLE_FLAG` is selected for monitoring backends.
