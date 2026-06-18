<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/demand_paging_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/demand_paging_test.c

Purpose: this test measures and validates KVM guest memory demand paging behavior using optional userfaultfd missing or minor fault handling across one or more vCPUs and memory backing types.

Important APIs, types, and functions: `struct test_params` captures UFFD mode, single versus per-vCPU uffd, artificial delay, reader count, backing source, and overlapping versus partitioned memory access. `vcpu_worker()` runs a memstress vCPU until a sync. `handle_uffd_page_request()` services missing faults with `UFFDIO_COPY` and minor faults with `UFFDIO_CONTINUE`, tolerating `EEXIST` races. `prefault_mem()` populates shared backing for minor faults. `run_test()` creates the memstress VM, registers UFFD ranges with `uffd_setup_demand_paging()`, starts vCPU threads, stops UFFD workers, and reports rates.

Control flow: `main()` is compiled only when `__NR_userfaultfd` is present; otherwise it prints a skip. It parses guest modes, UFFD mode, memory size, backing type, vCPU count, CPU pinning, overlap mode, and reader count. Minor-fault mode requires shared backing. For each guest mode, `run_test()` creates the VM, optionally prefaults aliases for minor faults, partitions or shares UFFD registrations, runs all vCPUs, and prints per-vCPU and aggregate paging rates.

State, persistence, and dependencies: state is transient VM memory, UFFD registrations, handler threads, and a `guest_data_prototype` page used for copies. Dependencies include `memstress`, `guest_modes`, `userfaultfd_util`, `ucall_common`, Linux userfaultfd ioctls, pthreads, and selected backing sources.

Risks and edge cases: multiple vCPUs/readers can fault the same page, so duplicate `UFFDIO_COPY` or `UFFDIO_CONTINUE` may return `EEXIST` and is intentionally ignored. Minor faults require shared memory backing and prefaulted aliases. Overlap mode forces a single UFFD. Artificial delays and pinning affect performance output but not correctness.

Test signals: guest reaches `UCALL_SYNC` for each vCPU, UFFD handlers service faults without unexpected errors, all vCPU threads join, and the test prints execution time plus demand paging rates. Missing syscall support or unsupported minor-fault backing skips/fails early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/demand_paging_test.c -->
