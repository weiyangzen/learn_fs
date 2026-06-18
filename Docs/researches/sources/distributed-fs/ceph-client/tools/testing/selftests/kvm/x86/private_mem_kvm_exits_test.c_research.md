<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_kvm_exits_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_kvm_exits_test.c

## Purpose
This protected-VM test verifies that impossible private accesses exit to userspace as `KVM_EXIT_MEMORY_FAULT` with accurate private-fault metadata. It covers private access after deleting a guest_memfd memslot and private access to a memslot that was not created as private-capable.

## Important APIs, Types, and Functions
Important pieces are `protected_vm_shape`, `guest_repeatedly_read()`, `run_vcpu_get_exit_reason()`, `test_private_access_memslot_deleted()`, and `test_private_access_memslot_not_private()`. The test uses `KVM_X86_SW_PROTECTED_VM`, `vm_userspace_mem_region_add()`, `vm_mem_set_private()`, `vm_mem_region_delete()`, `virt_map()`, `_vcpu_run()`, and `struct kvm_run.memory_fault`.

## Control Flow, State, and Persistence
The guest loops reading a fixed virtual address mapped to a single GPA. In the deletion case, the host marks the page private and starts `KVM_RUN` on a pthread while deleting the memslot, expecting the run to fail with `EFAULT` and `KVM_EXIT_MEMORY_FAULT`. In the non-private-slot case, the VM maps ordinary anonymous memory, marks the GPA private, runs the vCPU, and expects the same exit. State exists only in the protected VM, one memslot, one page mapping, and the run-page fault fields.

## Dependencies and Integration Points
The file integrates with KVM's software-protected VM type, guest memory attributes, guest_memfd slot flags, memslot deletion, and userspace memory-fault exit ABI.

## Risks and Test Signals
Risks are race sensitivity in the memslot-deleted case and regressions in private-fault size/GPA reporting. Passing signals are `KVM_EXIT_MEMORY_FAULT`, `KVM_MEMORY_EXIT_FLAG_PRIVATE`, GPA equal to `EXITS_TEST_GPA`, and size equal to one page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_kvm_exits_test.c -->
