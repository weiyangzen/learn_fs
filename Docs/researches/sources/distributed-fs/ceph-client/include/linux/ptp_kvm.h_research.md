# sources/distributed-fs/ceph-client/include/linux/ptp_kvm.h

Purpose: declares architecture hooks for the virtual PTP clock used by KVM guests to obtain host-synchronized time.

Important APIs and types: `kvm_arch_ptp_init()` and `kvm_arch_ptp_exit()` manage arch-specific setup. `kvm_arch_ptp_get_clock()` returns a `timespec64` clock value. `kvm_arch_ptp_get_crosststamp()` returns cycle, timespec, and clocksource ID for cross timestamping.

Control flow: the KVM PTP driver initializes arch support, services guest/PHC clock reads through arch hooks, optionally obtains cross timestamps, then tears down on exit.

State and persistence: state is architecture/KVM runtime state and host timekeeping state. No persistent data is defined here.

Dependencies and integration points: depends on KVM paravirtual time, clocksource IDs, timekeeping, and architecture implementations. It integrates guest-visible PTP devices with host clocks.

Risks and test signals: risks include time discontinuities, wrong clocksource IDs, cross timestamp inconsistency, and init/exit ordering with KVM modules. Test guest PTP reads, host time steps, live migration/time sync behavior, and arch-specific failure paths.
