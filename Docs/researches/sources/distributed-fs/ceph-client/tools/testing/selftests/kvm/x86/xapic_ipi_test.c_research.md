<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_ipi_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_ipi_test.c

## Purpose
This stress test validates xAPIC IPI delivery to a halted vCPU, optionally while userspace pages are migrated across NUMA nodes. It targets APIC access page relocation and wake-from-HLT behavior.

## Important APIs, Types, and Functions
Important data is `struct test_data_page` and `struct thread_params`. Key functions are `halter_guest_code()`, `sender_guest_code()`, `guest_ipi_handler()`, `vcpu_thread()`, `do_migrations()`, `cancel_join_vcpu_thread()`, and `get_cmdline_args()`. It uses xAPIC register helpers, `migrate_pages()`, `kvm_get_mempolicy()`, pthread cancellation, `virt_pg_map(APIC_DEFAULT_GPA)`, and vCPU stats such as `halt_exits`.

## Control Flow, State, and Persistence
The host starts a halter vCPU that enables xAPIC, records APIC diagnostics, then repeatedly disables interrupts, increments `hlt_count`, executes safe HLT, and increments `wake_count`. After the first halt, a sender vCPU repeatedly writes ICR2/ICR to send fixed IPIs and waits for IPI, wake, and re-halt counters to advance. The host either sleeps for the configured runtime or repeatedly migrates process pages between NUMA nodes, then cancels both vCPU threads and validates HLT exit accounting. State is shared guest data page counters, global `ipis_rcvd`, APIC ICR state, migration counters, and KVM vCPU stats.

## Dependencies and Integration Points
It integrates with xAPIC MMIO/APIC access page mapping, HLT wakeup, APIC interrupt delivery, optional NUMA page migration, pthreads, and KVM statistics.

## Risks and Test Signals
Risks include hangs if IPIs are lost, false failures on single-node NUMA when migration is requested, APIC access backing page relocation bugs, and idle-HLT stat differences. Signals are continuously increasing IPI/HLT/wake counters, no guest abort, and halt-exit count matching or not exceeding HLT count under idle-HLT rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_ipi_test.c -->
