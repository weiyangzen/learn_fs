# sources/distributed-fs/ceph-client/drivers/dibs/dibs_loopback.h

Purpose: declares the loopback DIBS provider's private state and init/exit hooks, with no-op stubs when loopback support is disabled.

Important APIs/types/functions: defines `DIBS_LO_DMBS_HASH_BITS`, `DIBS_LO_MAX_DMBS`, `struct dibs_lo_dmb_node`, and `struct dibs_lo_dev`. The node tracks token, buffer length, SBA index, CPU/DMA addresses, and refcount. The device tracks the public `struct dibs_dev`, atomic DMB count, hash lock/table, SBA bitmap, and release waitqueue.

Control flow: no direct runtime flow beyond conditional declarations. With `CONFIG_DIBS_LO`, real `dibs_loopback_init()` and `dibs_loopback_exit()` are provided by `dibs_loopback.c`; otherwise inline stubs return success/do nothing so `dibs_main.c` can call them unconditionally.

State and persistence behavior: describes in-memory loopback state only. The hash table and bitmap persist for the lifetime of the singleton loopback device.

Dependencies and integration points: includes DIBS public definitions, hashtable, spinlock, waitqueue, and Linux type headers. It forms the private interface between `dibs_main.c` and the loopback provider.

Risks and test signals: the hard-coded `DIBS_LO_MAX_DMBS` limit defines memory and bitmap sizing; raising it affects allocation and lookup behavior. Test signals are clean builds with and without `CONFIG_DIBS_LO`, and correct no-op behavior in non-loopback builds.
