# sources/distributed-fs/ceph-client/arch/s390/kvm/pv.c

## Purpose
Implements s390 KVM protected virtualization host support. It creates/destroys secure VM and secure CPU objects with Ultravisor calls, imports/unpacks/destroys secure pages, supports asynchronous protected-VM teardown, tracks mm lifetime, and provides dump operations for protected guests.

## Important APIs, Types, And Functions
Exports include `kvm_s390_pv_is_protected()` and `kvm_s390_pv_cpu_is_protected()`. Core entry points declared in `kvm-s390.h` include `kvm_s390_pv_init_vm()`, `kvm_s390_pv_deinit_vm()`, `kvm_s390_pv_set_aside()`, `kvm_s390_pv_deinit_aside_vm()`, `kvm_s390_pv_deinit_cleanup_all()`, `kvm_s390_pv_create_cpu()`, `kvm_s390_pv_destroy_cpu()`, `kvm_s390_pv_make_secure()`, `kvm_s390_pv_convert_to_secure()`, `kvm_s390_pv_destroy_page()`, `kvm_s390_pv_unpack()`, `kvm_s390_pv_set_sec_parms()`, `kvm_s390_pv_set_cpu_state()`, and protected dump helpers.

## Control Flow And State
VM initialization registers an mmu notifier once, allocates base and variable UV storage sized from memslots, disables huge pages, splits existing huge mappings, calls `UVC_CMD_CREATE_SEC_CONF`, stores the returned handle, and increments `mm->context.protected_count`. CPU creation allocates per-CPU UV storage plus SIDA, calls `CREATE_SEC_CPU`, and programs SIE PV handles. Page import uses a fault-in callback under `kvm->arch.pv.import_lock`, exports first when required by shared-page ownership rules, rejects large/hugetlb folios, and may request folio splitting. Teardown supports normal destroy, destroy-fast, set-aside async cleanup, and cleanup of pending leftovers on signals or mm release.

## Dependencies And Integration
Depends on Ultravisor UVC ABI, gmap, guest fault-in helpers, Linux MM/MMU notifier, KVM memslots, SIE block PV fields, mm protected-count tracking, usercopy, and KVM lock/SRCU rules.

## Risks And Test Signals
Risks include intentional leaks on impossible UV failures, protected-count imbalance, mm teardown races, set-aside cleanup after fatal signals, folio splitting/retry loops, secure-page ownership transfer, and usercopy length/alignment in dump paths. Signals include protected VM boot/reboot, UV return-code logging, migration/dump tests, mm teardown under process exit, huge-page rejection, and lockdep for documented lock contexts.
