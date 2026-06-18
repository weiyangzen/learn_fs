<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_mem.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_mem.c

**Purpose:** `sclp_mem.c` implements s390 memory hotplug backed by SCLP storage assignment and storage-info commands.

**Important APIs and functions:** `arch_get_memory_phys_device()` maps PFNs to SCLP memory increment IDs. Internal SCLP operations are `sclp_assign_storage()`, `sclp_unassign_storage()`, and `sclp_attach_storage()`. Sysfs attributes per firmware memory object are `config` and `memmap_on_memory`, implemented by `sclp_config_mem_*()` and `sclp_memmap_on_memory_*()`. Boot setup uses `sclp_setup_memory()`.

**Control flow, state, and persistence:** Boot reads storage-info for each storage ID, builds sorted `memory_increment` entries for assigned and standby increments, infers unassigned standby increments, then creates `/sys/firmware/memory/memoryN` objects aligned to Linux memory block size. Writing `config=1` attaches unqueried storage IDs, assigns intersecting increments, initializes storage keys/CMMA state, and calls `__add_memory()`. Writing `config=0` requires the memory block to be offline, unassigns increments, removes memory, and releases KASAN early shadow mapping if needed.

**Dependencies and integration:** It depends on SCLP core, memory hotplug, firmware ksets, KASAN shadow helpers, page-state/CMMA operations, and early `sclp.rnmax`/`sclp.rzm` discovery.

**Risks and test signals:** Risks include incorrect region-number to address mapping, partial assignment rollback, memory-block alignment losing standby memory, races with device hotplug, and leaks on kset allocation failure paths. Tests should cover storage-info response variants, standby object creation, config on/off with online-memory rejection, memmap-on-memory gating, KASAN cleanup, and kdump mode skipping standby memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_mem.c -->
