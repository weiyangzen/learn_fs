<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/pre_fault_memory_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/pre_fault_memory_test.c

## Purpose
`pre_fault_memory_test.c` validates the `KVM_PRE_FAULT_MEMORY` vCPU ioctl. It checks successful prefaulting, partial failure at unmapped tails, racing memslot deletion/recreation, and private-memory behavior for supported x86 protected VM types.

## Important APIs, Types, and Functions
Key functions are `guest_code()`, `delete_slot_worker()`, `pre_fault_memory()`, `__test_pre_fault_memory()`, `test_pre_fault_memory()`, and `main()`. The race state is held in `struct slot_worker_data`. The ioctl payload is `struct kvm_pre_fault_memory`.

## Control Flow
The test creates a VM, places a test slot near the top of GPA space, maps it into guest VA space, optionally marks it private, and calls `pre_fault_memory()` for three ranges. Each prefault attempt starts a worker that deletes the slot once prefaulting begins, then recreates it when requested. The host retries after `EINTR` or after slot recreation, asserts expected remaining size, and checks success or `ENOENT`. Finally, the guest reads all mapped pages and exits with `GUEST_DONE()`.

## State and Persistence
State includes the test memslot, optional guest_memfd/private memory attribute, the racing worker flags, and the mutable `range.size` field returned by KVM. All state is freed with the VM.

## Dependencies and Integration Points
The file depends on `KVM_CAP_PRE_FAULT_MEMORY`, KVM VM type caps, pthreads, `kvm_util.h`, `processor.h`, and protected memory helpers. It integrates with x86 software-protected VM tests and generic KVM vCPU ioctl wrappers.

## Risks and Test Signals
Risks include misinterpreting partial progress, treating racing deletion `EAGAIN` as stable, accepting size-zero retries, and failing private-memory prefaults. Test signals are `range.size` decreasing only on success, expected zero or `PAGE_SIZE` bytes left, success for complete ranges, `ENOENT` for unmapped portions, and final guest read completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/pre_fault_memory_test.c -->
