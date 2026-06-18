# sources/distributed-fs/ceph-client/mm/damon/Makefile

Purpose: Maps DAMON Kconfig symbols to compiled objects.

Important entries: `obj-y := core.o` always builds the DAMON core when the directory is selected. `CONFIG_DAMON_VADDR` builds `ops-common.o vaddr.o`; `CONFIG_DAMON_PADDR` builds `ops-common.o paddr.o`; `CONFIG_DAMON_SYSFS` builds `sysfs-common.o sysfs-schemes.o sysfs.o`; module policies add `modules-common.o` plus `reclaim.o`, `lru_sort.o`, or `stat.o`.

Control flow: The build system includes common objects only when their consumers are enabled. Both address backends share `ops-common.o`; all policy modules share `modules-common.o`.

State and persistence: No runtime state; it is build metadata.

Dependencies and integration: Integrates with `mm/Makefile` and Kconfig. Object inclusion must match symbol dependencies to avoid unresolved symbols such as paddr helpers or module parameter macros.

Risks: If multiple enabled symbols add the same object, Kbuild de-duplicates in practice, but dependency changes should be checked. Moving shared APIs between files requires updating this map.

Test signals: Compile each Kconfig combination, especially `DAMON_PADDR` with each policy module, sysfs-only builds, and vaddr+paddr together.
