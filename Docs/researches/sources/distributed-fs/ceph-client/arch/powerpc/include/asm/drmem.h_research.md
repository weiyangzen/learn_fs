## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/drmem.h

Purpose: defines PowerPC dynamic reconfiguration memory logical memory block representation and iteration helpers.

Important APIs/types/functions: `struct drmem_lmb`, `struct drmem_lmb_info`, `drmem_info`, `drmem_lmb_next()`, `for_each_drmem_lmb*`, device-tree layout structs `of_drconf_cell_v1` and `of_drconf_cell_v2`, memory flags, reservation helpers, `drmem_lmb_memory_max()`, `walk_drmem_lmbs()`, `drmem_update_dt()`, pseries early walkers, and `invalidate_lmb_associativity_index()`.

Control flow: iterators walk LMB arrays and call `cond_resched()` every 16 entries to avoid monopolizing CPU during firmware-heavy DLPAR operations. Walk/update functions parse or rewrite dynamic-memory properties elsewhere.

State and persistence: `drmem_info` holds the runtime LMB table, LMB size, and flags. Reservation and associativity helpers mutate LMB flags/indices that drive memory hotplug and firmware/device-tree updates.

Dependencies and integration: depends on scheduler rescheduling, OF device-tree properties, and pseries DLPAR memory hotplug. Integrates with memory add/remove, NUMA associativity, and firmware dynamic memory properties.

Risks and test signals: device-tree v1/v2 layout handling and reservation flags are memory hotplug sensitive. Missing reschedules can stall large partitions. Test signals include pseries memory hotplug add/remove, dynamic-memory property updates, NUMA associativity changes, and large-LMB iteration latency.
