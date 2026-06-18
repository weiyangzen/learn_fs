# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_zswap.c

## Purpose

`test_zswap.c` validates cgroup memory/zswap integration: zswap usage accounting, disabling zswap per cgroup, zswap-in stats, writeback enable/disable behavior, per-memcg shrink isolation, kswapd charging, and incompressible page stats. The complete 772-line file was read.

## Important APIs, Types, and Functions

Helpers include `read_int()`, `set_min_free_kb()`, `read_min_free_kb()`, `get_zswap_stored_pages()`, `get_cg_wb_count()`, `get_zswpout()`, `allocate_and_read_bytes()`, `allocate_bytes()`, `setup_test_group_1M()`, `attempt_writeback()`, `test_zswap_writeback_one()`, `no_kmem_bypass_child()`, `allocate_random_and_wait()`, and `get_zswap_incomp()`. Tests include `test_zswap_usage`, `test_swapin_nozswap`, `test_zswapin`, writeback enabled/disabled, `test_no_kmem_bypass`, `test_no_invasive_cgroup_shrink`, and `test_zswap_incompressible`.

## Control Flow

`main()` finds cgroup v2, requires zswap module presence and memory controller, enables memory, then runs the table. Tests create limited cgroups, allocate more than `memory.max` to force swap/zswap, read `memory.stat` fields, manipulate `memory.zswap.max` and `memory.zswap.writeback`, trigger `memory.reclaim`, temporarily raises `min_free_kbytes` to wake kswapd, and uses `MADV_PAGEOUT` on random data for incompressible tracking.

## State and Persistence Behavior

The file mutates cgroup memory and zswap files, allocates memory in children, writes `/proc/sys/vm/min_free_kbytes` with restoration, reads debugfs zswap global stats, and creates shared memory/pipe synchronization for child tests.

## Dependencies and Integration Points

It depends on cgroup v2 memory/zswap files, zswap kernel support, debugfs `/sys/kernel/debug/zswap/stored_pages`, swap/reclaim behavior, `MADV_PAGEOUT`, sysinfo, sysctl `min_free_kbytes`, and `cgroup_util`.

## Risks and Edge Cases

Many tests require swap/zswap configuration and enough memory pressure without destabilizing the host. `test_no_kmem_bypass` skips systems above about 5GB RAM and temporarily changes a global VM sysctl. Some stats are gauges and can fall when children exit, so synchronization is important. Debugfs may be unavailable.

## Test Signals

Signals include increasing `zswpout`, zero `zswpout` when `memory.zswap.max=0`, sufficient `zswpin`, `zswpwb` changing only when writeback is enabled, control cgroup writeback count staying zero during another memcg's shrink, zswapped bytes matching global stored pages during kswapd pressure, and positive `zswap_incomp` for random pages.
