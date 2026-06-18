# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/dirty_log_page_splitting_test.c

Purpose: Verifies eager page splitting and hugepage restoration behavior when dirty logging is enabled, cleared, and disabled under the TDP MMU. It ensures dirty logging splits huge mappings to 4K pages and that disabling dirty logging allows huge mappings to repopulate.

Important APIs/types/functions: `struct kvm_page_stats` captures `pages_4k`, `pages_2m`, `pages_1g`, and total hugepages; `get_page_stats()`, `run_vcpu_iteration()`, `vcpu_worker()`, and `run_test()` drive the workload. It uses `memstress_create_vm()`, `memstress_enable_dirty_logging()`, `memstress_get_dirty_log()`, `memstress_clear_dirty_log()`, `KVM_CAP_MANUAL_DIRTY_LOG_PROTECT2`, and KVM VM stats.

Control flow: For each guest mode, the test creates a two-vCPU/two-slot memstress VM backed by HugeTLB by default. Worker threads dirty all memory by iteration. The host records page stats after population, after dirty logging enablement, after each dirtying pass, after optional manual clear, after disabling dirty logging, and after repopulation. It runs once without manual dirty-log protection and, if supported, once with manual protection.

State and persistence behavior: Global `iteration`, `host_quit`, and per-vCPU completion counters coordinate threads. Dirty bitmaps are host memory. KVM page stats and memslot dirty logging state are transient VM state. No disk persistence exists.

Dependencies and integration points: Requires `eager_page_split` and `tdp_mmu` KVM parameters, HugeTLB or best-effort THP backing, memstress helpers, guest mode enumeration, and KVM dirty-log ioctls/statistics.

Risks and maintenance notes: The test is strongest with HugeTLB; THP can be nondeterministic. Busy-wait coordination assumes worker vCPUs progress. Page-stat expectations are tightly coupled to TDP MMU hugepage accounting and manual dirty-log semantics.

Test signals: Passing means hugepages are initially populated, split at dirty-log enablement or first manual clear as appropriate, and restored after dirty logging is disabled and memory is touched again. Failures indicate eager-splitting, dirty-log clear, or hugepage repopulation regressions.
