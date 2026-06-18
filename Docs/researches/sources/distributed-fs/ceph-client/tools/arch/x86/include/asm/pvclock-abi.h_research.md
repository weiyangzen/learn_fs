# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/pvclock-abi.h

## Purpose
Defines the shared paravirtual clock ABI between hypervisors and x86 guests. The layouts are used by Xen and KVM and are explicitly immutable.

## APIs, Types, and Functions
Exports packed `struct pvclock_vcpu_time_info` with version, TSC timestamp, system time, multiplier, shift, and flags; packed `struct pvclock_wall_clock`; and flag bits `PVCLOCK_TSC_STABLE_BIT`, `PVCLOCK_GUEST_STOPPED`, and legacy `PVCLOCK_COUNTS_FROM_ZERO`.

## Control Flow, State, and Persistence
The structs are shared-memory state updated by a hypervisor and sampled by a guest. The `version` field is a seqlock-style protocol: odd while updating and even when stable.

## Dependencies and Integration
Included by `pvclock.h` and hypervisor/guest code consuming KVM or Xen pvclock data. It relies on fixed integer typedefs being available in the including environment.

## Risks and Test Signals
Risks are ABI-breaking field edits, missing packing, and readers ignoring the version protocol. Test signals include structure size checks, KVM/Xen clocksource tests, stable TSC flag behavior, and version retry tests under concurrent updates.
