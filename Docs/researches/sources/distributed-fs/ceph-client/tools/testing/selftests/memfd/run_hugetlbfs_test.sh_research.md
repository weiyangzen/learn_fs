# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/run_hugetlbfs_test.sh

Purpose: prepares enough huge pages and runs memfd tests in hugetlbfs mode.

Important APIs/types/functions: reads `HugePages_Free` from `/proc/meminfo`, adjusts `/proc/sys/vm/nr_hugepages`, drops caches, runs `./memfd_test hugetlbfs` and `./run_fuse_test.sh hugetlbfs`, and restores original huge page count if changed.

Control flow: requires eight free huge pages, attempts to allocate more if root, skips if insufficient, runs both tests, then restores count.

State and persistence: mutates global huge page pool and drops caches. Restoration is at the end, without a shell trap.

Dependencies and integration points: root for allocation, hugetlbfs-capable kernel, memfd/FUSE tests.

Risks: on early failure, huge page count may not be restored. Error message references `$needpgs`, which is undefined in this snapshot.

Test signals: skip on insufficient huge pages/non-root allocation need; success is inherited from child tests.
