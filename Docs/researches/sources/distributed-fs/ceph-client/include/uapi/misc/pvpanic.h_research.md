<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/pvpanic.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/pvpanic.h

Purpose: defines bit flags written to a paravirtual panic device to notify the host of guest panic, crash-kernel load, or shutdown.

Important APIs and types: `PVPANIC_PANICKED`, `PVPANIC_CRASH_LOADED`, and `PVPANIC_SHUTDOWN` are bit values built with `_BITUL`.

Control flow, state, and persistence: guest kernel or userspace writes event bits to a pvpanic IO/MMIO device; the hypervisor consumes them for logging, management actions, or crash handling. No persistent state is defined by the header.

Dependencies and integration points: integrates with pvpanic platform/PCI devices, QEMU/libvirt management, crash dump workflows, and guest shutdown paths.

Risks and test signals: risks include bit assignment drift, host ignoring combined flags, and event ordering around panic/crash-kernel boot. Test panic notification, kdump loaded notification, clean shutdown notification, and hypervisor event logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/pvpanic.h -->
