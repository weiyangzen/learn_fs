# sources/distributed-fs/ceph-client/drivers/firmware/memmap.c

Purpose: Maintains the firmware memory map exposed under `/sys/firmware/memmap`, including early boot entries and hotplug-added/removed entries.

Important APIs/types/functions: `firmware_map_entry` stores start/end/type, list node, and kobject. Public APIs are `firmware_map_add_early()`, `firmware_map_add_hotplug()`, and `firmware_map_remove()`. Sysfs attributes expose `start`, `end`, and `type`. `firmware_memmap_init()` publishes early entries at late init.

Control flow: Early callers allocate entries from memblock and add them to `map_entries`. Late init creates the memmap kset and sysfs kobjects for existing entries. Hotplug add reuses bootmem-backed entries from `map_entries_bootmem` when possible or allocates a new entry, then creates sysfs immediately. Remove deletes from the active list and drops the kobject reference, with bootmem-backed storage saved for reuse by the release method.

State and persistence behavior: Persistent kernel state includes active and reusable firmware map entry lists protected by spinlocks. The driver mirrors firmware/platform memory ranges but does not change actual firmware memory.

Dependencies and integration points: Depends on firmware-map API, memblock, kobjects/ksets under `firmware_kobj`, memory hotplug hooks, and sysfs.

Risks and test signals: Callers must use exclusive end addresses; internally entries store inclusive end. Locking around find/add/remove and kobject release/reuse is subtle. Test early entries appearing after late init, hot-add/hot-remove/re-add reuse, duplicate add behavior, sysfs attribute formatting, and removal of missing entries.
