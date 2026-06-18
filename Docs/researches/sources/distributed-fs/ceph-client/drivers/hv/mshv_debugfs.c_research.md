# sources/distributed-fs/ceph-client/drivers/hv/mshv_debugfs.c

## Purpose

`mshv_debugfs.c` builds `/sys/kernel/debug/mshv` and exposes Hyper-V statistics pages for the hypervisor, logical processors, the parent partition, child partitions, and VPs. It also maps/unmaps the backing Hyper-V stats pages.

## Important APIs, Types, and Functions

- `mshv_debugfs_init()` creates the top-level tree, root-only hypervisor/LP stats, and parent partition stats.
- `mshv_debugfs_exit()` removes debugfs dentries and unmaps all stats pages.
- `mshv_debugfs_partition_create/remove()` create/remove per-partition directories and partition stats.
- `mshv_debugfs_vp_create/remove()` create/remove VP `stats` files under a partition's `vp` directory.
- `lp_stats_show`, `hv_stats_show`, `partition_stats_show`, and `vp_stats_show` print named counters from `hv_stats_page`.
- Mapping helpers call `hv_map_stats_page()` and `hv_unmap_stats_page()` for `HV_STATS_OBJECT_*` identities.

## Control Flow

Initialization creates `mshv`, optionally maps hypervisor stats and uses the logical processor count counter to size LP mappings, creates `lp/<index>/stats`, then creates `partition/self` for the current partition and per-online-CPU VP stats. Dynamic child partitions and VPs call the exported create/remove helpers during their own lifecycle.

Stats reads are simple seq-file show callbacks. Partition and VP stats can have both SELF and PARENT areas; display prefers PARENT values and falls back to SELF when the PARENT value is zero. L1VH parent partitions cannot access PARENT stats and alias PARENT to SELF.

## State and Persistence Behavior

Global dentries track the debugfs tree. `mshv_lps_stats`, `parent_vp_stats`, and partition/VP object fields hold mapped stats-page pointers until removal. Stats page mappings are persistent Hyper-V mappings and must be explicitly unmapped.

## Dependencies and Integration Points

The file includes `mshv_debugfs_counters.c` directly for counter names, depends on debugfs and Hyper-V stats hypercalls from `mshv_root_hv_call.c`, and is invoked by module init/exit plus partition/VP creation and destruction in `mshv_root_main.c`.

## Risks and Edge Cases

Debugfs creation is optional at runtime but mapping failures abort module init for parent stats. CPU hotplug after init is not reflected in `parent_vp_stats` because it iterates online CPUs during creation/removal. The direct include of counter data is guarded by `MSHV_DEBUGFS_C` to prevent accidental separate use. Removal paths assume dentries/private pointers were successfully initialized.

## Test Signals

Test by mounting debugfs and checking `mshv/stats`, `mshv/lp/*/stats`, `mshv/partition/self/stats`, child partition directories, VP directories, and clean teardown. Fault-injection should cover map failures at each stage, PARENT stats unsupported fallback, L1VH aliasing, and module exit without leaks or stale mappings.
