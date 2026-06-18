# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/page_fault_test.c

Purpose: this arm64 KVM selftest exercises stage-2 fault handling across guest access types, backing sources, userfaultfd, dirty logging, read-only memslots, holes in backing storage, access-flag updates, and no-syndrome instructions.

Important APIs, types, and functions: `struct test_desc` describes each generated scenario: guest prepare functions, guest access function, post-checks, userfaultfd handlers, abort handlers, MMIO/fail handlers, memslot flags, and expected event counts. Guest accessors include `guest_read64()`, `guest_write64()`, `guest_cas()`, `guest_at()`, `guest_dc_zva()`, `guest_ld_preidx()`, `guest_st_preidx()`, and `guest_exec()`. Host helpers include `setup_uffd()`, `punch_hole_in_backing_store()`, `mmio_on_test_gpa_handler()`, `check_write_in_dirty_log()`, `handle_cmd()`, `setup_memslots()`, `vcpu_run_loop()`, and `run_test()`.

Control flow: `main()` parses guest mode/backing source options, then iterates the static `tests[]` matrix across enabled guest modes. `run_test()` manually creates VM memory slots for code/data, page tables, and test data; maps `TEST_GVA` and a guest-visible PTE address; loads tiny executable code into the data memslot; configures userfaultfd and abort handlers; then runs the vCPU loop. Guest `guest_code()` performs optional preparation, syncs requested host memory mutations, executes the selected access, performs post-checks, and exits.

State and persistence: global `events` counts MMIO exits, failed vCPU runs, and userfaultfd faults. `pt_args` and `data_args` hold demand-paging copies and HVA metadata. Test descriptors can be marked `skip` when feature preparation is unavailable. No durable files are written.

Dependencies and integration points: depends on KVM memory-slot flags, dirty-log UAPI, userfaultfd demand paging helpers, guest mode helpers, backing source helpers, page-table introspection, AArch64 access-flag support, LSE atomics, DC ZVA, and MMIO exit behavior.

Risks: the matrix is broad and architecture-sensitive. No-syndrome operations should fail KVM_RUN with `ENOSYS` in read-only cases, while syndrome writes should become MMIO. Userfaultfd behavior depends on host kernel support and backing source semantics. Dirty-log page granularity uses host page size, not guest page size.

Test signals: expected counts for UFFD faults, MMIO exits, and failed KVM_RUNs must match. Dirty-log checks, PTE_AF checks, guest access assertions, unexpected abort handlers, and failed memory-hole operations all signal regressions.
