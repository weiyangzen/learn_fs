<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_conversions_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_conversions_test.c

## Purpose
This test stresses software-protected VM private-memory conversion flows backed by `guest_memfd`. It verifies explicit shared/private transitions through `KVM_HC_MAP_GPA_RANGE`, host visibility of shared memory, host invisibility of private memory, `PUNCH_HOLE` behavior, page/2 MiB range handling, multiple memslots, and multiple vCPUs.

## Important APIs, Types, and Functions
Key guest helpers are `guest_test_explicit_conversion()`, `guest_test_punch_hole()`, `guest_map_shared()`, `guest_map_private()`, `guest_sync_shared()`, and `guest_sync_private()`. Host-side control is in `handle_exit_hypercall()`, `__test_mem_conversions()`, and `test_mem_conversions()`. The test uses `KVM_X86_SW_PROTECTED_VM`, `vm_create_guest_memfd()`, `vm_mem_add(... KVM_MEM_GUEST_MEMFD ...)`, `vm_guest_mem_fallocate()`, `vm_set_memory_attributes()`, `vm_enable_cap(KVM_CAP_EXIT_HYPERCALL)`, and selftests backing-source parsing.

## Control Flow, State, and Persistence
`main()` parses optional backing source, vCPU count, and memslot count, then creates a protected VM. Each vCPU receives a private GPA window above 4 GiB. Guest code first initializes shared memory, asks the host to verify and rewrite shared bytes, converts selected ranges private, verifies private data from the guest while the host still sees shared backing, then converts holes and whole ranges back to shared. It also punches holes without full conversion and expects refaulted private memory to read as zero. Per-vCPU host threads run `KVM_RUN`, service hypercall exits, and handle `UCALL_SYNC` content checks. After VM destruction the test fallocates and punches the guest_memfd to verify lifetime/reference handling.

## Dependencies and Integration Points
This file depends on `KVM_CAP_VM_TYPES` advertising `KVM_X86_SW_PROTECTED_VM`, guest_memfd, memory attributes, hypercall exits, pthreads, and fallocate semantics. It integrates with KVM memory-slot registration, selftests address translation, and backing source helpers.

## Risks and Test Signals
Risks include races between vCPU threads and host memory checks, misaligned memslot sizing, incorrect folio/page granularity for 2 MiB ranges, stale SPTEs after punching holes, and broken guest_memfd lifetime after VM close. Test signals are guest assertions on byte patterns, host assertions on shared visibility, successful hypercall handling, zero reads after hole punching, and no failure across different vCPU/memslot configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_conversions_test.c -->
