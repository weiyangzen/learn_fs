<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonet.h -->
# sources/distributed-fs/ceph-client/include/linux/sonet.h

Purpose: This header provides kernel support types for SONET/SDH physical-layer statistics while reusing the UAPI item list.

Important APIs/types/functions: `struct k_sonet_stats` expands `__SONET_ITEMS` into `atomic_t` fields using a temporary macro. `sonet_copy_stats()` copies atomic kernel counters into a UAPI `struct sonet_stats`; `sonet_subtract_stats()` subtracts a UAPI snapshot from kernel counters.

Control flow: Device drivers maintain atomic counters, then call copy/subtract helpers when serving stats requests or delta computations.

State and persistence: The persistent state is per-device statistics stored as atomics. This header does not allocate or own storage; drivers embed `k_sonet_stats`.

Dependencies/integration: Depends on `linux/atomic.h` and `uapi/linux/sonet.h`. Integrates with ATM/SONET drivers that expose stats to userspace.

Risks and test signals: Risks include UAPI item-list drift, torn non-atomic reads if helpers are bypassed, and incorrect delta handling. Test with counter increments under load, ioctl/stat readouts, and compile checks after changing `__SONET_ITEMS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonet.h -->
