# sources/distributed-fs/ceph-client/arch/s390/kvm/sigp.c

## Purpose
Handles s390 SIGP interprocessor communication instructions for KVM guests. It emulates common SIGP orders in-kernel, injects KVM local interrupts to target VCPUs, returns architecture condition codes/status words, and delegates reset/start-like orders or configured userspace SIGP handling to userspace.

## Important APIs, Types, And Functions
Public entry points are `kvm_s390_handle_sigp()` and `kvm_s390_handle_sigp_pei()`. Static handlers implement SENSE, external call, emergency and conditional emergency signals, STOP, STOP AND STORE STATUS, SET ARCHITECTURE rejection, SET PREFIX, STORE STATUS AT ADDRESS, SENSE RUNNING, and preparation for START/RESTART/CPU RESET. `handle_sigp_dst()` validates the destination VCPU and dispatches target orders. `handle_sigp_order_in_user_space()` honors `kvm->arch.user_sigp`.

## Control Flow And State
`kvm_s390_handle_sigp()` rejects problem-state execution, decodes source/destination registers and order code, optionally exits to userspace, reads the order parameter, traces the request, then either handles SET ARCHITECTURE locally or routes through `handle_sigp_dst()`. Destination handling refuses most orders while stop/restart IRQs are pending to avoid reporting stale state. Success and status paths set the guest PSW condition code; negative returns propagate kernel or userspace-exit handling. Partial-execution interception only handles external call by waking the target VCPU and accepting the order.

## Dependencies And Integration
Depends on s390 SIGP constants, KVM VCPU lookup, KVM local interrupt injection, stop/restart IRQ state, prefix helpers, guest memory validity checks, tracepoints, and userspace KVM run exits.

## Risks And Test Signals
Risks include incorrect busy/status ordering around asynchronous STOP/RESTART, wrong register half used for parameters, prefix validation/alignment errors, and mismatched userspace delegation counters. Test signals include multi-VCPU guest CPU hotplug/start/stop, external call delivery, SIGP status polling after STOP, userspace SIGP mode, and `kvm_s390_handle_sigp_pei()` wakeup behavior.
