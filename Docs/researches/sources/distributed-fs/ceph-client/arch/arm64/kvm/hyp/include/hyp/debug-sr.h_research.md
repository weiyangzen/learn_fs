# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/debug-sr.h

## Purpose

This header implements common hyp debug-register save/restore helpers for switching between host and guest debug contexts.

## Important APIs, Types, And Functions

Macros `save_debug()` and `restore_debug()` unroll breakpoint/watchpoint register transfers. Helpers include `__vcpu_debug_regs()`, `__debug_save_state()`, `__debug_restore_state()`, `__debug_switch_to_guest_common()`, and `__debug_switch_to_host_common()`.

## Control Flow

Switch helpers first check whether debug registers are in use. They select either guest-owned or external host-owned debug state based on `debug_owner`, save current host or guest debug registers, and restore the target context.

## State And Persistence Behavior

The code persists BCR/BVR/WCR/WVR arrays and `MDCCINT_EL1` in `kvm_guest_debug_arch` and `kvm_cpu_context`. It uses host per-CPU `debug_brps` and `debug_wrps` counts.

## Dependencies And Integration Points

It is shared by VHE/nVHE debug switching code and userspace debug setup in `guest.c`.

## Risks And Test Signals

Risks are wrong owner selection, register count mismatches, and leaked host debug configuration into guests. Test signals include guest hardware break/watchpoints, host single-step debugging while running guests, and debug-owner transitions.
