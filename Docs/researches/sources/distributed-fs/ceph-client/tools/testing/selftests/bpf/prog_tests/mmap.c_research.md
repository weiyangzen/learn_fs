<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mmap.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mmap.c

Purpose: validates mmap-able BPF map behavior, including shared userspace/kernel visibility, map sizing, page alignment, and access protections.

Important APIs and functions: the test creates/loads the companion skeleton, obtains mmap-able map fds, uses `mmap()`/`munmap()`, reads and writes mapped values, and triggers BPF programs to update map data for cross-checks.

Control flow: subtests map BPF arrays into userspace, verify initial contents, mutate via userspace and BPF paths, check synchronization, and exercise expected failure/protection cases.

State and persistence: mmap regions and map contents are transient; mappings are unmapped and skeletons/fds closed after testing.

Dependencies and integration: depends on `BPF_F_MMAPABLE` map support, page-size alignment, generated fixture, and memory mapping syscalls.

Risks and test signals: matching values seen through syscall lookup, mmap memory, and BPF-side updates are signals. Risks are architecture page-size differences and protection semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/mmap.c -->
