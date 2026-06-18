# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/ucall.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/ucall.h

Purpose: x86 adapter for common ucall notifications. It uses port I/O exits rather than MMIO.

Important APIs/types/functions: `UCALL_EXIT_REASON` is `KVM_EXIT_IO`; `ucall_arch_init(struct kvm_vm *vm, gpa_t mmio_gpa)` is a no-op for x86 because port I/O does not need the MMIO setup used by other architectures.

Control flow and state: common guest ucall code triggers an I/O exit carrying the ucall payload convention expected by host-side decoding. There is no per-VM MMIO address state in this adapter.

Dependencies and integration: includes `kvm_util.h` and is included by `ucall_common.h`. It integrates with every x86 selftest using guest sync, done, abort, assertions, or printf.

Risks: the x86 transport depends on KVM I/O exit decoding and common ucall register/port conventions. Unlike MMIO adapters, initialization cannot repair a mismatched host decoder.

Test signals: almost every x86 guest-running selftest validates this path through `GUEST_SYNC` or `GUEST_DONE`.
