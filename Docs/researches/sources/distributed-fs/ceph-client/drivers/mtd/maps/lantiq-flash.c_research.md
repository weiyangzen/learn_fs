<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/lantiq-flash.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/lantiq-flash.c

Purpose: OF platform map driver for Lantiq SoC NOR flash attached to the External Bus Unit, working around address endianness behavior shared with PCI.

Important APIs, types, and functions: `struct ltq_mtd` stores resource, MTD, and map pointers. Custom map hooks are `ltq_read16()`, `ltq_write16()`, `ltq_copy_from()`, and `ltq_copy_to()`. Probe/remove are `ltq_mtd_probe()` and `ltq_mtd_remove()`.

Control flow: intended probe flow allocates driver state and `map_info`, maps the memory resource, installs 16-bit map hooks, probes with address XOR active in `LTQ_NOR_PROBING`, switches to normal mode, swizzles CFI unlock addresses, and registers the MTD with OF node association. Remove unregisters and destroys the map.

State and persistence: persistent state is NOR contents. Runtime state includes the map mode flag `map_priv_1`, EBU spinlock protection, CFI unlock addresses, and MTD registration.

Dependencies and integration points: depends on Lantiq `ebu_lock`, OF compatible `lantiq,nor`, CFI probing, MTD registration, and platform resources.

Risks: in this snapshot `ltq_mtd_probe()` assigns `ltq_mtd->map->virt` before allocating `ltq_mtd->map`, a clear null-pointer dereference/order bug if compiled as shown. The address-swizzle workaround is fragile and tied to 16-bit CFI. Test signals are probe ordering under KASAN, successful PF/OF resource mapping, correct unlock address swizzle, and read/write behavior while PCI EBU swapping is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/lantiq-flash.c -->
