<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sync_regs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sync_regs_test.c

## Purpose
This test validates the x86 `KVM_CAP_SYNC_REGS` shared `kvm_run.s.regs` ABI. It covers valid/invalid register masks, synchronization direction controlled by `kvm_valid_regs` and `kvm_dirty_regs`, and races while KVM processes events or special registers.

## Important APIs, Types, and Functions
Important functions are `guest_code()`, `compare_regs()`, `race_sync_regs()`, `race_events_inj_pen()`, `race_events_exc()`, and `race_sregs_cr4()`. The harness tests include `read_invalid`, `set_invalid`, `req_and_verify_all_valid`, `set_and_verify_various`, `clear_kvm_dirty_regs_bits`, `clear_kvm_valid_and_dirty_regs`, `clear_kvm_valid_regs_bits`, and three race tests. It uses `KVM_SYNC_X86_REGS`, `KVM_SYNC_X86_SREGS`, `KVM_SYNC_X86_EVENTS`, `KVM_TRANSLATE`, and `vcpu_save_state()`.

## Control Flow, State, and Persistence
The guest loops on port I/O and increments RBX after each exit. Tests set valid/dirty masks before `KVM_RUN`, compare shared-page register data with ioctl-returned state, and mutate RBX/APIC base to check copy-in/copy-out behavior. Race tests save a known-good state, spawn a pthread that continuously dirties event or sregs fields in `struct kvm_run`, run for a timeout, and reload state after shutdowns caused by injected bad events. State is the shared `kvm_run` page, vCPU register/event/sreg state, and a temporary saved x86 state snapshot.

## Dependencies and Integration Points
It integrates with KVM_RUN register synchronization, exception injection validation, CR4/EFER long-mode validity, KVM translation, shutdown behavior, and the one-vCPU test harness.

## Risks and Test Signals
Risks include accepting invalid sync masks, stale shared-page fields, applying dirty values when not requested, ignoring dirty values when requested, or racing into invalid MMU state. Signals are expected `EINVAL`, exact RBX/APIC-base behavior, matching ioctl/shared regs, and no kernel failure during race loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sync_regs_test.c -->
