# sources/distributed-fs/ceph-client/include/linux/fsl_hypervisor.h

Purpose: exposes the Freescale hypervisor management driver interface and includes the corresponding UAPI ioctl definitions. Kernel users can register for failover notifications.

Important APIs and types: `fsl_hv_failover_register()` and `fsl_hv_failover_unregister()` manage notifier blocks for hypervisor failover events. UAPI structures and ioctl numbers come from `<uapi/linux/fsl_hypervisor.h>`.

Control flow: a driver initializes a `notifier_block`, registers it, receives failover callbacks from the hypervisor management driver, and unregisters before teardown. Userspace communicates with the management device through the included UAPI ioctls.

State and persistence: notifier registration is runtime state. Hypervisor partition/device state is external to this header.

Dependencies and integration points: integrates with the Freescale hypervisor management driver, notifier chains, and userspace management tools using the ioctl ABI.

Risks and test signals: risks include failing to unregister notifiers, callback ordering/priority mistakes, and ABI drift with UAPI definitions. Tests should cover notifier registration/unregistration, simulated failover events, module unload with registered callbacks, and ioctl compatibility.
