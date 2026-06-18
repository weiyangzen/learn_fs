<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_exception_with_invalid_guest_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_exception_with_invalid_guest_state.c

## Purpose
This Intel-only test verifies KVM behavior when exceptions are pending while guest state is invalid and unrestricted guest mode is disabled. It checks repeated internal emulation-failure exits and signal-timed races.

## Important APIs, Types, and Functions
Important functions are `guest_ud_handler()`, `guest_code()`, `run_vcpu_with_invalid_state()`, `set_invalid_guest_state()`, `clear_invalid_guest_state()`, `sigalrm_handler()`, and `set_timer()`. It uses `struct kvm_sregs.tr.unusable`, `vcpu_events_get()`, `KVM_EXIT_INTERNAL_ERROR`, and `KVM_INTERNAL_ERROR_EMULATION`.

## Control Flow, State, and Persistence
The guest loops on `ud2` under a #UD handler. The host first marks TR unusable and runs the vCPU twice, expecting internal emulation failures both times. It then restores valid state, arms a frequent SIGALRM, and the signal handler waits until an exception is pending, marks state invalid, and runs the vCPU from the handler to exercise the pending-exception plus invalid-state path. State is vCPU TR usability, exception pending state, and timer-driven host control.

## Dependencies and Integration Points
It depends on Intel VMX behavior, unrestricted guest being disabled, KVM invalid guest-state emulation limits, POSIX interval timers, and vCPU event ioctls.

## Risks and Test Signals
Risks include KVM crashing or losing pending exceptions when userspace re-enters with invalid state. Signals are repeated `KVM_EXIT_INTERNAL_ERROR` exits with emulation suberror and no assertion from the signal race.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_exception_with_invalid_guest_state.c -->
