# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/charge_reserved_hugetlb.sh

Purpose: validates hugetlb cgroup reservation and fault accounting under cgroup v1 or v2.

Important APIs/types/functions: mounts/finds hugetlb cgroup, writes hugetlb `limit/max`, `rsvd.limit/max`, reads `usage/current` and `rsvd.usage/current`, mounts hugetlbfs at `/mnt/huge`, adjusts `/proc/sys/vm/nr_hugepages`, invokes `write_hugetlb_memory.sh`, and uses `killall write_to_hugetlbfs` for cleanup.

Control flow: requires root and `killall`, stores original huge page count, configures cgroup file names for v1/v2, defines cleanup and wait helpers, then iterates over populate/write methods/private/reserve modes. `run_test()` sets huge pages, creates one cgroup, mounts hugetlbfs, runs writer, measures usage deltas, and asserts final usage zero. `run_multiple_cgroup_test()` does the same for two cgroups and checks isolation. In this snapshot, a `continue` after the normal write case makes the later reservation-limit, cgroup-limit, and multi-cgroup cases unreachable inside the loop.

State and persistence: mutates cgroups, hugetlbfs mount, huge page pool, and files under `/mnt/huge`; cleanup restores many but not all paths on interruption.

Dependencies and integration points: root, hugetlb cgroup controller, hugetlbfs, `write_hugetlb_memory.sh`, huge page availability.

Risks: destructive cleanup writes `0` to `nr_hugepages` repeatedly and only restores original count at the end. The unreachable section reduces actual coverage versus script text.

Test signals: explicit `expect_equal` failures exit `1`; skips on root/tool prerequisites; `PASS` text per reachable case.
