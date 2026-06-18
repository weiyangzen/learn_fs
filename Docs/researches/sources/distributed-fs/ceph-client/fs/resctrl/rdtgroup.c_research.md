# sources/distributed-fs/ceph-client/fs/resctrl/rdtgroup.c

## Purpose
`rdtgroup.c` is the resctrl filesystem integration hub. It registers and mounts the kernfs-based `resctrl` filesystem, creates all control/info/monitor files, manages resource and monitor groups, assigns tasks and CPUs to CLOSID/RMID pairs, handles mount options, domain hotplug, teardown, and delegates schemata, monitoring, assignable counter, I/O allocation, and pseudo-lock work to peer files.

## Important APIs, Types, And Functions
Global state includes `rdtgroup_mutex`, `rdt_root`, `rdtgroup_default`, `rdt_all_groups`, `resctrl_schema_all`, `mon_data_kn_priv_list`, mount flag `resctrl_mounted`, root kernfs nodes, `max_name_width`, `last_cmd_status`, `debugfs_resctrl`, `mba_mbps_default_event`, and `resctrl_debug`.

CLOSID management uses `closid_init()`, `closid_alloc()`, `closid_free()`, `closid_allocated()`, `closid_alloc_fixed()`, and `rdtgroup_mode_by_closid()`. Kernfs file dispatch is described by `struct rftype res_common_files[]`, `rdtgroup_add_files()`, `rdtgroup_file_write()`, and `rdtgroup_seqfile_show()`.

User operations include `rdtgroup_cpus_show/write()`, `rdtgroup_tasks_show/write()`, `rdtgroup_mode_show/write()`, `rdtgroup_size_show()`, info file show methods, MBM config show/write, and mount option parsing through `rdt_parse_param()`. Group lifecycle is handled by `rdtgroup_mkdir()`, `rdtgroup_mkdir_ctrl_mon()`, `rdtgroup_mkdir_mon()`, `rdtgroup_rmdir()`, `rdtgroup_rename()`, and helpers for mon_data directory creation/removal.

Filesystem lifecycle includes `rdt_init_fs_context()`, `rdt_get_tree()`, `rdt_kill_sb()`, `resctrl_init()`, and `resctrl_exit()`. Hotplug hooks include `resctrl_online_cpu()`, `resctrl_offline_cpu()`, `resctrl_online_ctrl_domain()`, `resctrl_offline_ctrl_domain()`, `resctrl_online_mon_domain()`, and `resctrl_offline_mon_domain()`.

## Control Flow
Mounting (`rdt_get_tree()`) serializes CPU hotplug and `rdtgroup_mutex`, rejects multiple mounts, prepares RMID LRU state, creates the root, enables mount context features such as CDP/MBA-SC/debug, builds schema entries, initializes CLOSID allocation, adds root files, creates `info`, `mon_groups`, and `mon_data`, initializes pseudo-lock device support, obtains the kernfs tree, enables architecture allocation/monitoring, sets `resctrl_mounted`, and starts MBM overflow work.

Creating a control group allocates a kernfs directory, a CLOSID, optionally an RMID and monitor files, initializes default CAT/MBA allocations across domains, adds it to `rdt_all_groups`, and creates its `mon_groups` directory. Creating a monitor group under `mon_groups` inherits the parent CLOSID, allocates its own RMID, creates monitor files, and links into the parent's child list.

CPU writes move CPUs between groups while updating per-CPU defaults and hardware state. Task writes validate permissions, set task CLOSID/RMID, issue memory barriers, and update the running CPU if needed. Removing groups moves tasks and CPUs back to parent/default groups, unassigns counters, frees RMIDs/CLOSIDs, removes kernfs nodes, and uses `RDT_DELETED` plus `waitcount` to defer freeing if files are still active.

## State And Persistence
State is in-memory and tied to the mounted filesystem. `rdtgroup` objects persist while their kernfs nodes or active references exist. `resctrl_schema` entries represent current exposed control resources and CDP split state. `mon_data` private structures are shared across event files until unmount. Hardware state is persisted only in architecture registers and reset during unmount or `resctrl_exit()`.

## Dependencies And Integration Points
The file depends on kernfs, fs context, sysfs mount points, debugfs, task iteration, CPU hotplug locks, resctrl architecture hooks, `ctrlmondata.c` schemata and monitor callbacks, `monitor.c` RMID/MBM helpers, and optional pseudo-lock helpers. It is the file that wires those helpers into the visible resctrl file tree through `res_common_files`.

## Risks
The highest-risk areas are lifetime and locking: kernfs active protection is deliberately broken while holding references, group deletion can race open files, and CPU/domain hotplug can change masks and monitor directories. Incorrect CLOSID/RMID cleanup leaks scarce hardware IDs. Mount option rollback must undo CDP/MBA-SC/root/schema/CLOSID state in the correct order. Mode transitions must preserve exclusivity, pseudo-lock restrictions, and monitor assignment invariants. Task movement relies on barriers pairing with scheduler resctrl updates.

## Test Signals
Test signals include mount/unmount with all option combinations, duplicate mount rejection, CLOSID/RMID exhaustion, creation/removal/rename of ctrl and mon groups, task and CPU migration including permission failures, default group CPU retention, pseudo-lock mode transitions, mon_data directory updates on domain hotplug, MBM config file visibility changes, `last_cmd_status` text for invalid commands, and teardown after simulated architecture fatal exit.
