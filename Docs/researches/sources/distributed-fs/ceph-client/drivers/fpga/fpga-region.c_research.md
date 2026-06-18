# sources/distributed-fs/ceph-client/drivers/fpga/fpga-region.c

Purpose: generic FPGA region class. A region ties an FPGA manager, optional compatibility ID, private data, and optional bridge acquisition callback into a programmable unit that can safely load an image while bridge traffic is disabled.

Important APIs and functions: exported APIs are `fpga_region_class_find`, `fpga_region_program_fpga`, `__fpga_region_register_full`, `__fpga_region_register`, and `fpga_region_unregister`. `fpga_region_get` and `fpga_region_put` are internal exclusive-reference helpers that lock the region mutex and hold the owner module. Sysfs `compat_id` exposes a 128-bit compatibility identifier if provided.

Control flow: registration allocates an IDA ID, initializes the bridge list and mutex, sets class/parent/OF node, and registers `regionN`. Programming gets the region exclusively, locks the FPGA manager, optionally invokes `get_bridges`, disables collected bridges, calls `fpga_mgr_load(region->mgr, region->info)`, enables bridges, unlocks the manager, and puts the region. On error after bridge collection, dynamic bridge lists are put and manager/region locks are released.

State and persistence: global state is the `fpga_region` class and IDA. Per-region state includes manager pointer, compat ID, private pointer, bridge list, `get_bridges` callback, module owner, current image info pointer owned by callers such as OF overlay code, and a mutex. Bridge references can remain held after successful programming when the region-specific callback collected them, so the overlay lifecycle can prevent unsafe reprogramming.

Dependencies and integration points: depends on FPGA manager and bridge frameworks, device classes, lists, IDA, module refs, and `<linux/fpga/fpga-region.h>`. Used directly by DFL core for container regions and by OF support for device-tree controlled programming.

Risks and test signals: risks include successful programming intentionally retaining bridge references until caller cleanup, caller-owned `region->info` lifetime, exclusive mutex causing `-EBUSY`, and error paths that differ depending on whether bridges were pre-provided or dynamically collected. Test signals are `/sys/class/fpga_region/region*/compat_id`, KUnit region tests, manager lock contention behavior, correct bridge disable/load/enable ordering, and cleanup during failed loads.
