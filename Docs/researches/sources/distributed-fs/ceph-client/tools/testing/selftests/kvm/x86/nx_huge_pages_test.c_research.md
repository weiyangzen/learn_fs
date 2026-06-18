# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.c

Purpose: Tests NX huge page splitting and recovery behavior. It verifies that executing from hugepage-backed guest memory splits mappings when NX huge pages are enabled, that the recovery thread reclaims split mappings, and that per-VM disabling of NX huge pages requires reboot permission.

Important APIs/types/functions: Constants define a three-2MB-page slot at 4GB; `guest_code()` performs reads and calls into hugepage memory; `check_2m_page_count()` and `check_split_count()` read KVM VM stats; `wait_for_reclaim()` sleeps for recovery; `run_test()` creates the VM, maps HugeTLB memory, optionally calls `__vm_disable_nx_huge_pages()`, and validates page counts.

Control flow: The program requires a magic token from the shell wrapper. It runs once with NX huge pages enabled and once with them disabled. Guest reads create 2MB mappings; guest execution from those mappings causes split counts to rise unless disabled; later recovery should reset split counts and allow huge mappings to return.

State and persistence behavior: VM page-stat counters and KVM NX hugepage state are transient. HugeTLB backing is supplied by the wrapper. Per-VM disablement is VM-local but permission-gated by process capabilities.

Dependencies and integration points: Requires `KVM_CAP_VM_DISABLE_NX_HUGE_PAGES`, HugeTLB pages, KVM `nx_huge_pages` module parameters, VM stats, and the wrapper script for environment setup.

Risks and maintenance notes: The test is not intended to be run directly; without wrapper setup, hugepage availability and reclaim period may be wrong. Timing of recovery is based on sleeping five periods, which assumes the recovery thread runs.

Test signals: Passing means read/execute transitions produce expected 2MB mapping and split counts, reclaim clears split accounting, and disabling NX huge pages succeeds only with permissions. Failures implicate NX hugepage splitting, reclaim, stats, or permission checks.
