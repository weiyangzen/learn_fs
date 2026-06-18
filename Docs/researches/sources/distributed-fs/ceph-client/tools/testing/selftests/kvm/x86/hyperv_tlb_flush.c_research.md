# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_tlb_flush.c

Purpose: Tests Hyper-V TLB flush hypercalls across slow and fast forms: `HvFlushVirtualAddressSpace`, `HvFlushVirtualAddressList`, and their `Ex` variants. It verifies that targeted vCPUs observe updated page mappings only after the correct flush.

Important APIs/types/functions: `struct hv_tlb_flush`, `struct hv_tlb_flush_ex`, `struct hv_vpset`, and `struct test_data` model hypercall inputs and shared test pages. `worker_guest_code()` continuously checks mapped page contents; `prepare_to_test()` disables checks and swaps guest PTEs; `post_test()` sets per-vCPU expected values; `sender_guest_code()` runs a large flush matrix; pthread helpers manage worker vCPUs.

Control flow: The host maps test pages and guest-visible PTEs, creates one sender and two worker vCPUs with VP IDs 2 and 65, then runs workers in threads. For each case, sender swaps two PTEs, issues a Hyper-V flush targeting one worker, both workers, or all processors, and then publishes expected values. Workers assert their TLB view matches whether they were flushed. The matrix covers address-space/list calls, Ex VP sets, all processors, slow memory inputs, and fast XMM inputs.

State and persistence behavior: Shared guest memory stores hypercall pages, test pages, PTE pointers, and per-vCPU expected values. Worker vCPU state persists in running threads until host cancellation.

Dependencies and integration points: Requires `KVM_CAP_HYPERV_TLBFLUSH`, guest page-table manipulation helpers, Hyper-V CPUID, x86 memory barriers, XMM input helper support, and multi-vCPU scheduling.

Risks and maintenance notes: The test uses delay loops rather than precise synchronization, so very slow systems can affect timing. It intentionally maps PTE pages into the guest, which is powerful but fragile if selftest page-table helpers change. Banked VP set indexing is a key coverage point.

Test signals: Passing means KVM parses all tested Hyper-V TLB flush formats and invalidates remote vCPU TLBs with correct targeting. Failures indicate TLB shootdown, VP-set parsing, fast input, or page-table synchronization bugs.
