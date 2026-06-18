# sources/distributed-fs/ceph-client/drivers/rapidio/rio-scan.c

## Purpose
Implements the basic RapidIO fabric enumeration and discovery method. In enumeration mode it claims the host lock, assigns destination IDs and component tags, creates `rio_dev`/`rio_net` objects, programs switch route tables, initializes error management, and enables port-write handling. In discovery mode it waits for a remote enumerator to set the discovered bit, reads already-assigned IDs/routes, and reconstructs the kernel device topology.

## Important APIs, types, and functions
`struct rio_id_table` is per-network enumeration state: a spinlocked bitmap plus a logical start ID. `rio_destid_alloc/reserve/free/first/next()` manage destination IDs. `rio_setup_device()` reads RapidIO config space, allocates `struct rio_dev` plus embedded switch storage, assigns component tags and destIDs, initializes route-table cache state, sets device names, attaches sysfs/device model state, and calls `rio_add_device()`. `rio_enum_peer()` and `rio_disc_peer()` are the recursive topology walkers. `rio_scan_alloc_net()` creates `struct rio_net` and optional enumeration state. `rio_enum_mport()` and `rio_disc_mport()` are exported through the local `struct rio_scan` registered by `rio_basic_attach()`.

## Control flow
Enumeration begins from `rio_enum_mport()`: reject repeated scans, set the local host lock and device ID, verify link activity, allocate a net, reserve the host destID, enable the local port, write the host component tag, allocate the next destID, then call `rio_enum_peer()`. Each peer access checks config-read reachability, arbitrates host locks against other enumerators, creates a device, and if it is a switch, programs routes back to the host and all previously allocated endpoints, walks active switch ports, recurses through them, and patches routes for newly found destIDs. After recursion it frees the last unused destID, updates missing routes across switches, releases locks, marks devices discovered/master, and enables port-write handling. Discovery begins from `rio_disc_mport()`, optionally waits up to `CONFIG_RAPIDIO_DISC_TIMEOUT`, allocates a net, reads the host destID, recursively follows switch route entries, and builds in-memory route caches.

## State and persistence
State is volatile kernel/device-model state. Persistent hardware-visible state is in RapidIO config CSRs: destination IDs, host locks, component tags, switch route tables, port lockout bits, port discovered/master bits, and port-write target CSRs. The file uses static counters `next_destid` and `next_comptag`; they are process/module global and assume one scan sequence at a time. `net->enum_data` owns the ID bitmap until `rio_scan_release_net()`.

## Dependencies and integration
Depends on RapidIO core helpers from `rio.c`/`rio.h`, Linux device model, config-space accessors from mport drivers, route ops supplied by switch drivers, and standard RapidIO register definitions. It is registered with `rio_register_scan(RIO_MPORT_ANY, &rio_scan_ops)` at `late_initcall`; the `scan` module parameter can trigger `rio_init_mports()`.

## Risks
Recursive enumeration has little recovery granularity: failed recursion returns `-1` and can leave partially discovered devices/routes until higher-level cleanup. Global counters are not protected by a top-level scan lock. Route discovery assumes route-table contents identify the next device and may silently skip ports with no matching route. Several config reads ignore return values. Switch `port_ok` is bitmask-based and would be fragile if port counts exceed the bit width.

## Test signals
Exercise enumerator and discoverer roles, multi-host lock contention, inactive links, empty switches, redundant paths, mixed endpoint/switch fabrics, 8-bit versus 16-bit destID system sizes, route-table cache contents, port-write target programming, and sysfs/device-model registration/teardown after failed mid-scan paths.
