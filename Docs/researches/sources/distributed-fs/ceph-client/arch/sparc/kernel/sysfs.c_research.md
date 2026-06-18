# sources/distributed-fs/ceph-client/arch/sparc/kernel/sysfs.c

Purpose: registers sparc64 CPU topology/sysfs devices, cache/clock attributes, and optional sun4v MMU statistics controls.

Important APIs/types/functions: per-CPU `mmu_stats` and `cpu_devices`; generated `show_*` handlers for MMU and CPU data; `show_mmustat_enable()`, `store_mmustat_enable()`, `register_mmu_stats()`, `unregister_mmu_stats()`, `register_cpu_online()`, `unregister_cpu_online()`, `check_mmu_stats()`, and `topology_init()`.

Control flow: init probes sun4v `sun4v_mmustat_info()` support, registers every possible CPU device, then installs a CPU hotplug online state. Online registration creates per-CPU files for clock tick and cache sizes; when supported, it also creates `mmu_stats/` and `mmustat_enable`. Reads/writes of `mmustat_enable` execute on the target CPU through `work_on_cpu()`, because the hypervisor MMU stats configuration is CPU-local.

State and persistence: per-CPU `hv_mmu_statistics` buffers are hypervisor-filled when enabled. CPU device sysfs files reflect runtime CPU/cache data; no disk persistence.

Dependencies and integration points: depends on `cpu_data`, Linux CPU devices/hotplug, sun4v hypervisor MMU stats APIs, per-CPU storage, and sysfs device attributes.

Risks: MMU stat buffers must be aligned and configured with physical addresses on the correct CPU. File creation errors are not deeply propagated. Hotplug removal must mirror created attributes.

Test signals: `/sys/devices/system/cpu/cpu*/clock_tick` and cache attributes, optional `mmu_stats` group on sun4v, enabling/disabling stats per CPU, CPU online/offline with attribute cleanup, and non-hypervisor systems without MMU stats.
