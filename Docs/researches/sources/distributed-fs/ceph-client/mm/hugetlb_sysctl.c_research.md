# `sources/distributed-fs/ceph-client/mm/hugetlb_sysctl.c`

## Purpose
`hugetlb_sysctl.c` registers HugeTLB controls under `/proc/sys/vm` when `CONFIG_SYSCTL` is enabled. It provides sysctl handlers for the default hstate's persistent hugepage count, mempolicy-aware count, shared-memory group, overcommit count, and optional movable gigantic page behavior.

## Important APIs, Types, And Functions
- Global setting: `int movable_gigantic_pages`, exposed when `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION` is enabled.
- `proc_hugetlb_doulongvec_minmax()` safely duplicates a `ctl_table` and redirects `.data` to a stack temporary before calling `proc_doulongvec_minmax()`.
- `hugetlb_sysctl_handler_common()` reads/writes `default_hstate.max_huge_pages` through `__nr_hugepages_store_common()`, optionally honoring task mempolicy.
- `hugetlb_sysctl_handler()` implements `nr_hugepages`.
- `hugetlb_mempolicy_sysctl_handler()` implements `nr_hugepages_mempolicy` under `CONFIG_NUMA`.
- `hugetlb_overcommit_handler()` reads/writes `default_hstate.nr_overcommit_huge_pages` and rejects writes to gigantic hstates without runtime support.
- `hugetlb_table[]` defines the `/proc/sys/vm` entries.
- `hugetlb_sysctl_init()` registers the table under `vm`.

## Control Flow
For `nr_hugepages` and `nr_hugepages_mempolicy`, the handler snapshots the default hstate max count into `tmp`, lets the generic sysctl parser read or update `tmp`, and on write calls `__nr_hugepages_store_common()` with `NUMA_NO_NODE`. The mempolicy variant passes `obey_mempolicy=true`.

For `nr_overcommit_hugepages`, the handler rejects writes when the default hstate is gigantic and runtime allocation/free is unsupported, parses into a temporary, and commits `h->nr_overcommit_huge_pages` under `hugetlb_lock`.

## State And Persistence Behavior
Sysctl writes mutate in-kernel HugeTLB state only. `nr_hugepages` changes persistent pool size through the same core resize path used by sysfs. `nr_overcommit_hugepages` changes the default hstate's surplus allocation ceiling. `hugetlb_shm_group` writes to `sysctl_hugetlb_shm_group`. These settings persist until changed or rebooted; the file does not itself store state on disk.

## Dependencies And Integration Points
The file depends on sysctl core, `default_hstate`, `hugepages_supported()`, `hugetlb_lock`, `hstate_is_gigantic_no_runtime()`, `__nr_hugepages_store_common()`, and `sysctl_hugetlb_shm_group`. It is initialized from `hugetlb_init()` through `hugetlb_sysctl_init()` declared in `hugetlb_internal.h`.

## Risks
- The temporary-table wrapper avoids races with generic sysctl parsing; bypassing it and pointing directly at live counters would expose partially parsed writes or races with HugeTLB resize.
- Only the default hstate is exposed through these sysctls; multi-size HugeTLB management belongs in sysfs.
- Overcommit writes are protected by `hugetlb_lock` but no resize mutex; this is acceptable for a scalar limit but must stay consistent with surplus allocation checks.
- Gigantic hstates without runtime support must reject overcommit and resize writes to avoid impossible allocations.

## Test Signals
- Read and write `/proc/sys/vm/nr_hugepages` and compare with `/proc/meminfo` and sysfs default hstate counts.
- On NUMA systems, write `nr_hugepages_mempolicy` under an mbind/cpuset policy and verify node placement constraints.
- Write `nr_overcommit_hugepages` while faulting `MAP_NORESERVE` mappings to verify surplus allocation caps.
- Build with `CONFIG_SYSCTL=n` and verify the inline no-op path from the internal header.
- Build with `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION=y` and verify `movable_gigantic_pages` registration.
