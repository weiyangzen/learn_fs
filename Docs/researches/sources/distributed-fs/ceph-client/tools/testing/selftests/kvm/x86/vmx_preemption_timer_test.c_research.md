<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_preemption_timer_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_preemption_timer_test.c

## Purpose
This nested VMX migration-style test verifies that VMX preemption timer state is saved and restored with the decayed timer value, not restarted from the original value after restore.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code()`, and `guest_code()`. The test uses `VMX_PREEMPTION_TIMER_VALUE`, `PIN_BASED_VMX_PREEMPTION_TIMER`, `VM_EXIT_SAVE_VMX_PREEMPTION_TIMER`, `MSR_IA32_VMX_MISC` timer rate, `vcpu_save_state()`, and `vcpu_load_state()`.

## Control Flow, State, and Persistence
L1 verifies preemption timer controls are supported, runs L2 once to a VMCALL, enables the preemption timer with a large value, records TSC-derived deadlines, and resumes L2. L2 waits until a threshold has elapsed, syncs to host to force save/release/recreate/load, then spins until the preemption timer exits to L1. L1 reports observed finish times and deadlines to host; host validates the timer did not expire too early from L1's perspective and did not restart too late from L2's perspective. State is nested VMCS preemption-timer value, saved x86 nested state, and timing globals.

## Dependencies and Integration Points
It requires VMX and `KVM_CAP_NESTED_STATE`, and integrates with VMX timer controls, nested-state migration, TSC timing, and KVM x86 state serialization.

## Risks and Test Signals
Risks include restoring the original timer instead of decayed value, losing timer-save control state, or timing flakiness. Signals are L2 reaching save/restore before expiry, `EXIT_REASON_PREEMPTION_TIMER`, and deadline comparisons passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_preemption_timer_test.c -->
