# sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_common.c

Purpose: registers a read-only PTP hardware clock backed by KVM host wall-clock pairing. Architecture-specific files provide init, plain clock reads, and crosstimestamp reads; this common file exposes them through the kernel PTP class.

Important APIs/types/functions: `struct kvm_ptp_clock` stores the registered `ptp_clock` and its copied `ptp_clock_info`. `ptp_kvm_caps` names the PHC `"KVM virtual PTP"` and implements `gettime64` plus `getcrosststamp`; adjustment, setting, and event enable operations return `-EOPNOTSUPP`. `ptp_kvm_get_time_fn()` wraps `kvm_arch_ptp_get_crosststamp()` for `get_device_system_crosststamp()`. `ptp_kvm_init()` calls `kvm_arch_ptp_init()` and `ptp_clock_register()`, while `ptp_kvm_exit()` unregisters and calls architecture cleanup.

Control flow: init probes architecture support first. If unsupported, the module returns `-EOPNOTSUPP` without registering a PHC. `gettime64` serializes with `kvm_ptp_lock`, calls `kvm_arch_ptp_get_clock()`, and copies the returned `timespec64`. `getcrosststamp` uses a callback that disables preemption around architecture pairing so the returned cycle value and clocksource ID remain CPU-consistent.

State and persistence: the only persistent module state is the single global `kvm_ptp_clock` plus `kvm_ptp_lock`. There is no adjustable offset, no event queue, and no persistence beyond module lifetime.

Dependencies and integration: integrates with `linux/ptp_clock_kernel.h`, KVM paravirtual interfaces, architecture `ptp_kvm.h` hooks, `get_device_system_crosststamp()`, and system counter IDs. Userspace sees a normal `/dev/ptpN` device but cannot discipline or set it.

Risks and test signals: lock ordering around preemption is important; early error paths must re-enable preemption and release the spinlock. Since adjustment APIs are unsupported, time-sync daemons must treat this as a reference source, not a steerable clock. Test signals include module load on KVM and non-KVM guests, `PTP_SYS_OFFSET_PRECISE`, repeated `gettime64`, architecture hypercall failures, and unload cleanup.
