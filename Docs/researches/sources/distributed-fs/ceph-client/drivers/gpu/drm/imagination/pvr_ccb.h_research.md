# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_ccb.h

Purpose: declares the core PowerVR CCB data structure and KCCB/FWCCB public API.

Important APIs/types: `struct pvr_ccb` stores firmware objects, firmware addresses, ring sizing, a mutex, and CPU mappings for control and CCB memory. Public functions cover KCCB/FWCCB init/fini, FWCCB processing, KCCB fence allocation/freeing, slot reservation/release, command send variants, completion wait, idle check, and waiter wakeup.

Control flow and state: callers initialize device-level rings, reserve KCCB slots before queueing from scheduler paths, send commands with PM/reset assumptions satisfied, and wait for completion where required. Locking is centered on `pvr_ccb.lock`.

Dependencies and integration: includes PowerVR firmware interface definitions and Linux mutex/types. It forward declares `pvr_device` and firmware object types to avoid broader include coupling.

Risks: API naming separates powered/reserved variants; using the wrong variant can miss PM refs or corrupt reservation accounting.

Test signals: compile coverage from firmware, queue, job, and device code; runtime tests around command submission and interrupt completion.
