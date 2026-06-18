# sources/distributed-fs/ceph-client/scripts/gdb/linux/genpd.py

## Purpose
`genpd.py` registers `lx-genpd-summary`, a GDB view that mirrors `/sys/kernel/debug/pm_genpd/pm_genpd_summary` for generic PM domains. It is intended for live kernel or vmcore debugging where sysfs/debugfs is unavailable.

## Important APIs, Types, and Functions
The script caches `struct generic_pm_domain`, `struct pm_domain_data`, and `struct device_link`. `kobject_get_path()` recursively reconstructs a device kobject path. `rtpm_status_str()` formats runtime PM state from `struct dev_pm_info`. `LxGenPDSummary.summary_one()` prints domain status, child domains from `parent_links`, and devices from `dev_list`.

## Control Flow
`invoke()` checks for `gpd_list`, prints headers, walks the global genpd list through `lists.list_for_each_entry()`, and calls `summary_one()` for each domain. Each domain walk nests a device-link list traversal and a PM-domain device list traversal.

## State and Persistence Behavior
The command is read-only. Its only persistent state is cached GDB type lookup state in `CachedType`; all PM state is read from kernel data structures at invocation time.

## Dependencies and Integration Points
It depends on `linux.utils` and `linux.lists`, plus kernel symbols `gpd_list` and the PM domain structure layout. It integrates into the loader through `vmlinux-gdb.py`.

## Risks and Test Signals
Recursive kobject path reconstruction can fail or recurse deeply if kobject parents are corrupt. Runtime status indexing assumes the kernel enum values match the local string table. Test with a kernel built with genpd users and compare output against debugfs `pm_genpd_summary`.
