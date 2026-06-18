# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/ucall.c

## Purpose
This arm64 ucall backend maps the generic selftest "hypercall to userspace" mechanism onto an MMIO write exit.

## Important APIs, Types, and Functions
`ucall_arch_init()` allocates an unused guest virtual page, maps it to the selected MMIO GPA, records `vm->ucall_mmio_addr`, and writes the guest global `ucall_exit_mmio_addr`. `ucall_arch_get_ucall()` recognizes matching `KVM_EXIT_MMIO` writes and returns the ucall payload pointer from `run->mmio.data`.

## Control Flow
During VM creation, generic ucall setup calls `ucall_arch_init()`. At runtime, guest ucall code writes a pointer-sized value to the mapped MMIO page, causing KVM to exit; host code calls `get_ucall()`, which delegates to this backend.

## State, Dependencies, and Integration
The file stores per-VM MMIO GPA in `struct kvm_vm` and guest-visible GVA in a guest global. It depends on `virt_map()`, `vm_unused_gva_gap()`, and `write_guest_global()`.

## Risks and Test Signals
Unexpected access width or read accesses assert. If the MMIO address collides with real memory or is not mapped, guest/host synchronization through `GUEST_SYNC()` and `GUEST_ASSERT()` fails.
