<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/mmu_stress_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/mmu_stress_test.c

## Purpose
`mmu_stress_test.c` stresses KVM MMU and mmu-notifier behavior across large numbers of memslots and vCPUs. It exercises guest writes/reads, MMU context reset, host `mprotect(PROT_READ)` faults, writable restoration, slot deletion, and backing unmap cleanup.

## Important APIs, Types, and Functions
Important functions are `guest_code()`, `rendezvous_with_boss()`, `assert_sync_stage()`, `run_vcpu()`, `vcpu_worker()`, `spawn_workers()`, `rendezvous_with_vcpus()`, `calc_default_nr_vcpus()`, and `main()`. Host state uses `struct vcpu_info`, atomic rendezvous counters, `mprotect_ro_done`, `all_vcpus_hit_ro_fault`, and `nr_ro_faults`.

## Control Flow
The host creates a large VM, maps many memslots backed by one mmap, identity maps guest memory, partitions GPA ranges across worker threads, and synchronizes phases. Guests write all pages, sync, optionally have CR0.WP toggled on x86 to reset MMU context, rewrite, read read-only memory, then repeatedly write while the host changes the backing VMA to read-only. Workers expect `-EFAULT` on writes, optionally advance PC on x86/arm64 to validate all writes fault, then resume after writable protection is restored. The host later deletes even slots and unmaps half the backing to test cleanup.

## State and Persistence
State spans many KVM memslots, one shared backing mapping, per-vCPU KVM state, atomic phase counters, and guest-visible booleans synchronized into the VM. The test intentionally exits without fully deleting all memslots or closing KVM fd to exercise cleanup paths.

## Dependencies and Integration Points
The file depends on `kvm_util.h`, `guest_modes.h`, `processor.h`, `ucall_common.h`, pthreads, atomics, Linux sizes, and architecture-specific guest store instruction handling. It integrates with KVM MMU invalidation, dirty/write fault handling, memslot deletion, and mmu_notifier release.

## Risks and Test Signals
Risks include deadlocked rendezvous, failure to convert host faults to `-EFAULT`, incorrect PC advancement for fixed instruction sizes, slot limits below test size, and untested cleanup if vCPUs never run. Test signals are staged `UCALL_SYNC` values, expected `EFAULT`, all-vCPU fault accounting, timing output for run/reset/RO/RW phases, and successful worker joins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/mmu_stress_test.c -->
