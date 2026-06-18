# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-haltpoll.c

Purpose: provides the haltpoll cpuidle driver for x86 KVM guests, intended to work with the haltpoll governor by polling briefly before architectural idle.

Important APIs and functions: `haltpoll_init()` refuses to load when `idle=` overrides are present, requires KVM paravirt plus `KVM_HINTS_REALTIME` unless `force=1`, initializes the poll state, registers the driver, allocates per-CPU devices, and registers CPU hotplug callbacks. `default_enter_idle()` clears polling state and calls `arch_cpu_idle()` if no reschedule is pending. Hotplug callbacks register/unregister devices and call `arch_haltpoll_enable/disable()`.

Control flow and state: state 0 is initialized as the polling state by `cpuidle_poll_state_init()`, and state 1 is architecture idle. Global state stores the percpu device allocation and dynamic hotplug state ID.

Dependencies and integration points: depends on x86 KVM guest paravirtual hints, the haltpoll governor, CPU hotplug framework, arch haltpoll hooks, and scheduler polling flags.

Risks and test signals: risks include force-loading on unsuitable guests, no driver load if boot idle override is set, per-CPU registration failures leaving module init failed, and energy/performance sensitivity to haltpoll governor tuning. Test signals include KVM hint detection, governor `haltpoll` selected, per-CPU devices registered on online, arch haltpoll enabled, and module exit removing hotplug state and freeing percpu devices.
