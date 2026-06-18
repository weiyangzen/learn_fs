<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_01.sh

## Purpose
Tests ublk --shmem_zc using null target shared hugetlbfs zero-copy writes.

## Important APIs, Types, and Functions
_prep_test, hugetlbfs mount, /proc/sys/vm/nr_hugepages, fallocate, _add_ublk_dev, fio or _run_fio_verify_io/_mkfs_mount_test.

## Control Flow
Checks fio and hugetlbfs support, temporarily raises nr_hugepages, mounts hugetlbfs under UBLK_TEST_DIR, allocates a shared buffer file, creates the ublk device with --shmem_zc and mode-specific flags, runs I/O, deletes the device before unmount, and restores hugepage count.

## State and Persistence
Mutates global nr_hugepages during the run and creates a temporary hugetlbfs mount/file; cleanup restores the old count on the normal path.

## Dependencies and Integration Points
Depends on root privileges, hugetlbfs, fio io_uring/mmaphuge, kublk shmem_zc/htlb support, and test_common.sh.

## Risks and Edge Cases
Global hugepage count changes are risky if interrupted; mount cleanup must run after device deletion so daemon releases mmap.

## Test Signals
Pass is successful device add and fio/verify workload completion; unavailable hugepages or mount support produce skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_shmemzc_01.sh -->
