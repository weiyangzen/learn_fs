<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_perf_test.c

Purpose: this benchmark-style KVM selftest measures dirty logging overhead while one or more memstress vCPUs dirty guest memory. It times memory population, enabling/disabling dirty logging, guest dirtying iterations, `KVM_GET_DIRTY_LOG`, and optional manual clear-log operations.

Important APIs, types, and functions: global controls include `nr_vcpus`, `guest_percpu_mem_size`, `dirty_log_manual_caps`, `iteration`, and `vcpu_last_completed_iteration`. `vcpu_worker()` loops running guest memstress code and synchronizing on the host iteration counter. `struct test_params` covers iteration count, physical offset, memory partitioning, backing source, slot count, write percentage, and random access. `run_test()` creates the VM through `memstress_create_vm()`, allocates bitmaps, enables manual dirty-log protection when available, coordinates iterations, and reports timings. `main()` parses benchmark options including nested mode and CPU pinning.

Control flow: the test first populates memory with 100 percent sequential writes to avoid later copy-on-write noise. It enables dirty logging over the configured slots, restores requested write percentage and access pattern, then for each iteration releases vCPUs, waits for them to finish, collects dirty logs, and optionally clears dirty bits. At the end it may keep vCPUs running during dirty-log disable to stress SPTE zapping, disables logging, stops vCPU threads, and prints aggregate averages.

State, persistence, and dependencies: state is transient VM memory, KVM dirty bitmap state, host bitmaps, and memstress thread coordination. Dependencies include `memstress`, `guest_modes`, manual dirty-log cap `KVM_CAP_MANUAL_DIRTY_LOG_PROTECT2`, backing source helpers, nested-mode support when requested, and pthreads.

Risks and edge cases: benchmark values are sensitive to backing source, CPU pinning, random seed, write percentage, memslot count, and whether vCPUs run while disabling dirty logging. Manual dirty-log capabilities are masked to `KVM_DIRTY_LOG_MANUAL_PROTECT_ENABLE` and `KVM_DIRTY_LOG_INITIALLY_SET`; `-g` disables them to compare legacy behavior. Iteration count must be at least two.

Test signals: the program prints timing for population, enable, each dirtying/get/clear iteration, disable, and averages. Assertions cover vCPU sync exits, vCPU count limits, write percentage range, and bitmap allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_perf_test.c -->
