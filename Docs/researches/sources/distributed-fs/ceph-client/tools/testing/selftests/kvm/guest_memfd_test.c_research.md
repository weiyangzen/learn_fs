<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_memfd_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_memfd_test.c

Purpose: this test validates the `KVM_CAP_GUEST_MEMFD` file API, optional mmap/shared initialization flags, fallocate semantics, NUMA policy interactions, SIGBUS behavior for inaccessible ranges, and actual guest access through a `KVM_MEM_GUEST_MEMFD` memslot.

Important APIs, types, and functions: file API checks include `test_file_read_write()`, `test_file_size()`, `test_fallocate()`, and `test_invalid_punch_hole()`. Mapping checks include `test_mmap_supported()`, `test_mmap_not_supported()`, `test_mmap_cow()`, `test_fault_private()`, `test_fault_overflow()`, and `test_collapse()`. NUMA checks use `test_mbind()` and `test_numa_allocation()`. Creation checks use `test_create_guest_memfd_invalid_sizes()`, `test_create_guest_memfd_multiple()`, and `test_guest_memfd_flags()`. `test_guest_memfd_guest()` installs a guest_memfd-backed memslot and runs guest code that reads `0xaa` and writes back `0xff`.

Control flow: `main()` requires `KVM_CAP_GUEST_MEMFD`, gets host page size, enumerates VM types from `KVM_CAP_VM_TYPES` or defaults to the default type, and runs `test_guest_memfd()` for each. That function validates supported flags, always tests flags zero, conditionally tests `GUEST_MEMFD_FLAG_MMAP`, and tests `GUEST_MEMFD_FLAG_MMAP | GUEST_MEMFD_FLAG_INIT_SHARED` when available. The final guest-backed test runs only when guest_memfd flags are queryable and asserts default VM type supports mmap and init-shared flags.

State, persistence, and dependencies: state is guest_memfd file contents, host mappings, NUMA policies, and VM memslot state; files are anonymous KVM guest_memfd descriptors and are closed after each subtest. Dependencies include `KVM_CAP_GUEST_MEMFD`, `KVM_CAP_GUEST_MEMFD_FLAGS`, `KVM_MEM_GUEST_MEMFD`, `mmap`, `fallocate`, `madvise`, `mbind`, `move_pages`, SIGBUS test helpers, hugepage size discovery, and selftest NUMA wrappers.

Risks and edge cases: guest_memfd intentionally rejects normal read/write/pread/pwrite and private COW mappings. Page-size alignment is mandatory for creation and punch-hole operations. Mmap support depends on flags; private mappings SIGBUS on access when not shared-initialized. `MADV_COLLAPSE` must fail to prevent huge folios from exposing data outside shared ranges. NUMA tests skip on single-node systems.

Test signals: expected failures for unsupported flags and invalid sizes, expected mmap/SIGBUS/fallocate behavior, NUMA placement checks when applicable, and guest round-trip verification that host-initialized `0xaa` bytes become `0xff` after guest execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_memfd_test.c -->
