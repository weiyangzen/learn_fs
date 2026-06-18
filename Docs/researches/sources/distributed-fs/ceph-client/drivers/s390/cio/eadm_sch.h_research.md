# sources/distributed-fs/ceph-client/drivers/s390/cio/eadm_sch.h

Purpose: declares the private per-subchannel state used by the EADM subchannel driver.

Important APIs/types/functions: `struct eadm_private` contains the cached `union orb`, state enum `EADM_IDLE/EADM_BUSY/EADM_NOT_OPER`, optional quiesce completion, owning `struct subchannel *`, timeout timer, and list node. `get_eadm_private()` and `set_eadm_private()` wrap subchannel device driver data.

Control flow: the header itself has no runtime flow, but its accessors are used by probe, start, timeout, IRQ, remove, shutdown, and event paths in `eadm_sch.c`.

State and persistence behavior: state is per-subchannel, in memory, aligned to 8 bytes, and bound to `sch->dev` through driver data. It is allocated at probe and freed at remove.

Dependencies and integration points: includes completion, device, timer, list, and ORB definitions. It is private to CIO EADM/SCM plumbing and should remain synchronized with the EADM driver's locking and lifecycle.

Risks and test signals: misuse risk is mostly lifetime-related: callers must not read private data after remove or without the expected subchannel lock/list lock. Tests are indirect through EADM probe/remove/start/quiesce coverage.
