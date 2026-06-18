<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/coalesced_io_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/coalesced_io_test.c

Purpose: this architecture-generic KVM selftest validates coalesced MMIO and, on x86, coalesced PIO. It checks that registered I/O ranges fill KVM's coalesced I/O ring up to one spare entry, that the next write exits to userspace, that ring entries contain correct payload metadata, and that unregistering ranges restores immediate exits.

Important APIs, types, and functions: `struct kvm_coalesced_io` records the ring, ring size, MMIO GPA/HVA, and x86 PIO port. `guest_code()` repeatedly writes enough MMIO/PIO entries to fill the ring and then does ucalls and non-coalesced writes. `vcpu_run_and_verify_io_exit()` checks `KVM_EXIT_MMIO` or `KVM_EXIT_IO`. `vcpu_run_and_verify_coalesced_io()` validates ring fullness and every `struct kvm_coalesced_mmio` entry. `test_coalesced_io()` wraps register/unregister and ucall checks.

Control flow: `main()` requires `KVM_CAP_COALESCED_MMIO` and, on x86, `KVM_CAP_COALESCED_PIO`, creates a one-vCPU VM, derives the ring address from the vCPU run page and capability page offset, computes ring capacity from host page size, identity maps an arbitrary high MMIO GPA, syncs the ring descriptor to the guest, and tests every possible initial ring index.

State, persistence, and dependencies: state is the KVM coalesced ring inside the vCPU run mmap and transient guest writes. Dependencies include KVM coalesced I/O capabilities, selftest VM mapping helpers, and x86 `outl()` for PIO coverage.

Risks and edge cases: KVM intentionally leaves one free ring entry, so the test relies on `ring_size - 1` writes before exit. PIO data must only be read on PIO exits because `data_offset` is invalid for MMIO exits. Ring wrap-around is tested by varying `ring_start`.

Test signals: expected ring first/last positions, exact MMIO or PIO entry contents, immediate ucall exit without ring mutation, and immediate exits after unregistering coalesced ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/coalesced_io_test.c -->
