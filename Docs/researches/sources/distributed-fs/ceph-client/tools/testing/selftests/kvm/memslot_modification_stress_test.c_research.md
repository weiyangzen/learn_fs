<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_modification_stress_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_modification_stress_test.c

## Purpose
`memslot_modification_stress_test.c` stresses KVM behavior while memslots are repeatedly added and removed as guest vCPUs actively access memory. It targets memslot update/zap races and the x86 slot-zap-all quirk.

## Important APIs, Types, and Functions
Key functions are `vcpu_worker()`, `add_remove_memslot()`, `run_test()`, `help()`, and `main()`. Parameters are carried in `struct test_params`, including delay, iteration count, memory partitioning, and optional x86 quirk disabling.

## Control Flow
The test creates a memstress VM for each selected guest mode, optionally disables `KVM_X86_QUIRK_SLOT_ZAP_ALL`, starts memstress vCPU threads, repeatedly adds and deletes a dummy memslot just below the memstress GPA range, then joins vCPUs and destroys the VM. Guest workers run until `memstress_args.stop_vcpus` is set and only accept expected `UCALL_SYNC` exits.

## State and Persistence
State includes global vCPU count, per-vCPU memory size, memstress global arguments, and transient dummy memslot state at slot 7. No state persists after VM destruction.

## Dependencies and Integration Points
The file depends on generic `memstress.h`, `guest_modes.h`, KVM memory region helpers, `ucall_common.h`, and optional x86 `KVM_CAP_DISABLE_QUIRKS2`. It integrates with the memstress framework's vCPU thread lifecycle.

## Risks and Test Signals
Risks include memslot invalidation races, incorrect GPA placement for the dummy slot, unsupported vCPU counts, and quirk-capability mismatches. Test signals are absence of unexpected exits, successful memslot add/delete loops, worker joins, and explicit assertions on invalid guest sync status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_modification_stress_test.c -->
