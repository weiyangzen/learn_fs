<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_test.c

Purpose: this KVM correctness test verifies dirty page tracking for three modes: legacy `KVM_GET_DIRTY_LOG`, manual get+clear logging, and dirty-ring logging. It checks that dirty bitmaps/rings match guest writes across iterations and that clean pages contain only older iteration values.

Important APIs, types, and functions: shared guest/host globals include page sizes, guest page count, iteration, write count, stop flag, guest physical/virtual test addresses, and dirty-ring bookkeeping. `guest_code()` randomly writes iteration values to test pages until stopped. `enum log_mode_t` and `struct log_mode` abstract mode-specific support, VM setup, collection, and post-run handling. Dirty-ring helpers include `dirty_ring_create_vm_done()`, `dirty_ring_collect_one()`, `dirty_ring_collect_dirty_pages()`, and `dirty_ring_after_vcpu_run()`. `vm_dirty_log_verify()` compares collected bitmaps against host memory contents.

Control flow: `main()` initializes semaphores, parses iteration interval, guest mode, log mode, physical offset, and dirty-ring size, then runs all selected guest modes and log modes. `run_test()` creates a VM with extra memory for page tables, creates a logged test memslot near the top of guest physical memory unless overridden, maps it at a fixed guest virtual address, syncs globals to the guest, and starts one vCPU thread. Each iteration syncs the iteration number, releases the vCPU, periodically collects dirty state while the guest runs when needed, stops the vCPU, performs a final collection, verifies memory, and repeats.

State, persistence, and dependencies: state is transient VM memory, KVM dirty logs/rings, two host bitmaps, semaphores, and the vCPU thread. Dependencies include `guest_modes`, `processor.h`, `ucall_common`, Linux bitmap/bitops helpers, `KVM_CAP_MANUAL_DIRTY_LOG_PROTECT2`, `KVM_CAP_DIRTY_LOG_RING` or `KVM_CAP_DIRTY_LOG_RING_ACQ_REL`, and architecture-specific guest stores.

Risks and edge cases: dirty-ring full exits can record the last GFN before the guest write retires, so verification permits special last-page and previous-last-page cases. s390x segment dirtying requires an initial touch-all-pages workaround and excludes dirty-ring mode. Bitmap modes are destructive on collection, so collection while guest runs is limited. The test enforces a minimum write count per iteration to avoid false coverage.

Test signals: each iteration prints dirty/clean/write counts and asserts dirty pages hold the current iteration except documented exceptions, clean pages hold older values, dirty-ring reset count matches harvested entries, vCPU exits are either sync or dirty-ring-full, and total checked bits are reported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_test.c -->
