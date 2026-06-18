# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/debug-sr.c

## Purpose
This file provides VHE wrappers for switching debug register state between host and guest.

## Important APIs, Types, and Functions
- `__debug_switch_to_guest(struct kvm_vcpu *vcpu)` delegates to `__debug_switch_to_guest_common()`.
- `__debug_switch_to_host(struct kvm_vcpu *vcpu)` delegates to `__debug_switch_to_host_common()`.

## Control Flow
The VHE world-switch code calls the guest wrapper after restoring guest system registers and calls the host wrapper after restoring host system registers. The wrappers contain no VHE-specific policy beyond selecting the common implementation.

## State and Persistence
Debug state is held in vCPU and host CPU contexts managed by the common debug-switch helpers. This file does not allocate or persist independent state.

## Dependencies and Integration Points
It depends on `hyp/debug-sr.h`, `linux/kvm_host.h`, and `asm/kvm_hyp.h`. It is called from `hyp/vhe/switch.c` around `__guest_enter()`.

## Risks and Edge Cases
The file is small, but its placement in the world switch matters. Calling the wrappers in the wrong order could expose host breakpoints/watchpoints to the guest or lose guest debug state.

## Test Signals
Run guest debug-register selftests, breakpoint/watchpoint tests, single-step tests, and VHE guest entry/exit stress. Failures usually appear as unexpected debug exceptions, lost breakpoints, or host debug state corruption.
