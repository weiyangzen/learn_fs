# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_hmi.c

## Purpose

`book3s_hv_hmi.c` provides small synchronization helpers used by Hypervisor Maintenance Interrupt handling when KVM-HV guests may be running on POWER8 subcores. It waits for guest subcores to leave guest mode and waits for timebase resynchronization to complete before host HMI handling proceeds.

## Important APIs, Types, And Functions

`wait_for_subcore_guest_exit()` loops over `MAX_SUBCORE_PER_CORE` entries in the local PACA's `sibling_subcore_state->in_guest[]` array and waits until no sibling subcore is marked in guest mode. `wait_for_tb_resync()` waits until `CORE_TB_RESYNC_REQ_BIT` is clear in the sibling subcore state flags.

## Control Flow

Both functions first check `local_paca->sibling_subcore_state`. A NULL pointer means KVM has not initialized subcore tracking, no relevant guests are running, or the CPU is POWER9 or newer where this synchronization is not needed. In that case they return immediately. Otherwise they spin with `cpu_relax()` until the relevant guest-exit or timebase-resync condition clears.

## State And Persistence Behavior

The file does not own state. It observes per-core `sibling_subcore_state` installed in PACA by KVM-HV initialization and shared with HMI/timebase code. It does not persist data.

## Dependencies And Integration Points

It depends on PACA, HMI definitions, processor relaxation primitives, `MAX_SUBCORE_PER_CORE`, and the bit layout of `sibling_subcore_state`. It integrates with HMI paths that need all subcores in host context before OPAL or host code modifies timebase-related state.

## Risks

These are busy-wait loops in a high-priority maintenance path. If `in_guest[]` or the resync flag is not cleared because a guest thread is stuck or state ownership is broken, HMI handling can spin indefinitely. Conversely, returning too early can allow host timebase changes while a guest subcore still observes old state. The NULL-pointer fast path must stay aligned with POWER9+ and unloaded-KVM assumptions.

## Test Signals

Signals include HMI recovery on POWER8 with KVM guests in split-core mode, no hangs waiting for `in_guest[]`, successful timebase resync completion, and no unnecessary waiting on POWER9 or systems where KVM-HV subcore tracking was never initialized.
