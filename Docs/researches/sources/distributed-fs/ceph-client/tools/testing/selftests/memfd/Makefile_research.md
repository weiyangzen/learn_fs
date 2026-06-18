# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/Makefile

Purpose: builds memfd core, FUSE race, and hugetlbfs wrapper tests.

Important APIs/types/functions: builds `memfd_test`, scripts `run_fuse_test.sh` and `run_hugetlbfs_test.sh`, generated files `fuse_test` and `fuse_mnt`, and detects FUSE cflags/libs through `pkg-config` with fallback include/library flags.

Control flow: compiles common code into `memfd_test` and `fuse_test`; applies FUSE cflags to `fuse_mnt.o` and FUSE libs to the `fuse_mnt` link.

State and persistence: build metadata only.

Dependencies and integration points: FUSE development headers/libs, memfd uapi headers, kselftest `lib.mk`.

Risks: fallback FUSE flags may not match all distributions. Missing FUSE support affects only FUSE-specific generated tools.

Test signals: generated binaries and scripts are kselftest-visible.
