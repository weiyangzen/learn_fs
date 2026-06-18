# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/access_tracking_perf_test.c

Purpose: this KVM performance selftest measures the cost of access tracking when guest memory is aged through page-idle tracking or MGLRU. It times guest reads/writes to populated memory and aged memory across configurable guest modes, memory backings, vCPU counts, and overlapped/disjoint memory regions.

Important APIs, types, and functions: `struct test_params` holds backing source, bytes per vCPU, and vCPU count. Host helpers include `lookup_pfn()`, `is_page_idle()`, `mark_page_idle()`, `pageidle_mark_vcpu_memory_idle()`, `lru_gen_mark_memory_idle()`, `assert_ucall()`, `vcpu_thread_main()`, `run_iteration()`, `access_memory()`, `mark_memory_idle()`, `run_test()`, `access_tracking_unreliable()`, and `run_test_for_each_guest_mode()`. It uses `memstress`, `guest_modes`, `cgroup_util`, and `lru_gen_util`.

Control flow: `main()` parses `-m`, `-b`, `-v`, `-o`, `-s`, and `-w`, chooses MGLRU if usable or falls back to `/sys/kernel/mm/page_idle/bitmap`, optionally creates/runs inside a memory cgroup, and iterates guest modes. `run_test()` creates a memstress VM, starts vCPU worker threads, populates memory, optionally primes MGLRU generations, measures read/write control passes, ages memory, and measures idle-memory read/write passes. Worker threads spin on a global `iteration` counter and either run the vCPU or mark their memory idle.

State and persistence: global synchronization state includes `iteration`, `iteration_work`, per-vCPU completion counters, `idle_pages_warn_only`, `use_lru_gen`, `test_pages`, and `lru_gen_last_gen`. It creates/destroys a memory cgroup for MGLRU mode and touches debugfs/sysfs/proc state. No test data is persisted beyond cgroup cleanup.

Dependencies and integration points: requires KVM, memstress helpers, guest mode support, `page_idle` or MGLRU debugfs, `/proc/self/pagemap`, and often `CAP_SYS_ADMIN` for PFNs. It integrates with NUMA balancing detection and nested-virtualization heuristics to downgrade some idle-page checks to warnings.

Risks: correctness of access tracking cannot be deterministic because page-idle/MGLRU clear young bits without guaranteed TLB flush and pagevec/LRU timing is asynchronous. Nested virtualization, NUMA balancing, missing PFN visibility, cgroup setup failures, and insufficient memory can skew results or skip/fail. Busy spin synchronization is intentional but CPU-intensive.

Test signals: printed timing lines for populate/read/write/mark-idle phases are the primary performance signal. Failures come from missing kernel facilities, too many idle/old pages when not warning-only, unexpected ucalls, missing cgroup accounting, or memstress guest asserts.
