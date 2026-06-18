# sources/distributed-fs/ceph-client/fs/resctrl/pseudo_lock.c

## Purpose
`pseudo_lock.c` implements optional resctrl cache pseudo-locking. It converts a CAT allocation in a resource group into a cache-resident memory region exposed through a character device and debugfs measurement trigger, while preventing ordinary task/CPU assignment and conflicting cache allocations.

## Important APIs, Types, And Functions
Global device state includes `pseudo_lock_major`, the minor availability bitmap, and `pseudo_lock_class` with `pseudo_lock_devnode()`. Minor management uses `pseudo_lock_minor_get()` and `pseudo_lock_minor_release()`. `region_find_by_minor()` maps an opened device back to the owning `rdtgroup`.

Region setup functions include `pseudo_lock_init()`, `pseudo_lock_region_init()`, `pseudo_lock_region_alloc()`, `pseudo_lock_region_clear()`, and `pseudo_lock_free()`. C-state constraints use `struct pseudo_lock_pm_req`, `pseudo_lock_cstates_constrain()`, and `pseudo_lock_cstates_relax()`.

Mode transitions are handled through exported helpers `rdtgroup_locksetup_enter()`, `rdtgroup_locksetup_exit()`, `rdtgroup_pseudo_lock_create()`, and `rdtgroup_pseudo_lock_remove()`. Overlap checks are exposed as `rdtgroup_cbm_overlaps_pseudo_locked()` and `rdtgroup_pseudo_locked_in_hierarchy()`. Debug measurement uses `pseudo_lock_measure_cycles()` and `pseudo_lock_measure_trigger()`. Character device operations include `pseudo_lock_dev_open()`, `pseudo_lock_dev_release()`, `pseudo_lock_dev_mmap_prepare()`, and a rejected `mremap`.

## Control Flow
Entering locksetup rejects the default group, CDP-enabled systems, unsupported prefetch-disable platforms, existing monitor groups, assigned tasks, or assigned CPUs. It then restricts relevant kernfs files, allocates a pseudo-lock region object, and frees the group RMID because monitoring is not allowed.

When a valid cache schemata is written in locksetup mode, `rdtgroup_pseudo_lock_create()` allocates backing memory sized from the CBM, constrains C-states on CPUs in the cache domain, runs the architecture pseudo-lock thread on the selected CPU, allocates a minor, temporarily drops `rdtgroup_mutex` to create debugfs and device nodes, then rechecks deletion state. On success it marks the group pseudo-locked, frees the CLOSID, and makes CPU files read-only.

Device `mmap_prepare` requires the caller to be affined to the pseudo-locked domain CPUs, requires shared mapping, checks offset/length bounds, zeroes the mapped region slice, installs VM ops, and remaps physical pages. Removal tears down PM QoS, debugfs, device node, minor, CLOSID/RMID ownership, and region memory depending on the mode.

## State And Persistence
Pseudo-lock state is in memory and device/debugfs namespace entries. `rdtgroup::plr` points to a `pseudo_lock_region` that records schema, domain, CBM, size, line size, CPU, memory pointer, waitqueue, PM QoS requests, debugfs dir, and device minor. The pseudo-locked memory is allocated with `kzalloc()` and freed on group removal or failed setup.

## Dependencies And Integration Points
This file depends on CAT allocation state from `rdtgroup.c` and `ctrlmondata.c`, architecture pseudo-lock and measurement callbacks, PM QoS, CPU hotplug state, debugfs, char devices, NOMMU-style `mmap_prepare` APIs, kernfs permission helpers, CLOSID/RMID helpers, and cacheinfo.

## Risks
The code intentionally drops `rdtgroup_mutex` during debugfs/device creation to avoid lock inversions, so deletion races must be rechecked carefully. CPU affinity is a correctness requirement for mapped users; otherwise the user could evict the pseudo-locked cache lines. CLOSID/RMID ownership changes are asymmetric across setup, creation, exit, and removal, making leak tests important. Large regions are limited by `KMALLOC_MAX_SIZE`, and C-state QoS setup must unwind completely on partial failure.

## Test Signals
Tests should cover mode transitions into and out of locksetup, rejection with tasks/CPUs/monitor groups/CDP enabled, CBM overlap and hierarchy rejection, successful device creation/removal, mmap bounds and shared-only checks, affinity rejection, interrupted lock thread handling, debugfs measurement selectors, and CPU/domain offline behavior where `plr->d` becomes unavailable.
