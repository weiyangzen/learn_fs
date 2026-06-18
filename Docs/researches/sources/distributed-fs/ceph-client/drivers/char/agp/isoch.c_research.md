# sources/distributed-fs/ceph-client/drivers/char/agp/isoch.c

## Purpose

`isoch.c` implements generic AGP 3.5 node setup for isochronous transfer support. It enumerates AGP 3.x devices behind a bridge, validates that they are compatible with AGP 3.x electrical mode, and allocates isochronous bandwidth/request-queue resources or falls back to non-isochronous queue allocation.

## Important APIs, Types, And Functions

- `struct agp_3_5_dev` tracks a candidate device, its AGP capability offset, and maximum bandwidth.
- `agp_3_5_dev_list_sort()` and `agp_3_5_dev_list_insert()` order devices by `maxbw`.
- `agp_3_5_isochronous_node_enable()` computes ISOCH_N, ISOCH_Y, and request queue allocations for target and master devices.
- `agp_3_5_nonisochronous_node_enable()` divides target request queue slots across masters.
- `agp_3_5_enable()` is the exported entry from generic AGP enable logic.

## Control Flow

`agp_generic_enable()` calls `agp_3_5_enable()` for AGP bridges with major version >= 3 and minor >= 5. The function reads target status, exits if isochronous support is not present, builds a list of AGP-capable display/multimedia devices, verifies each is AGP 3.x and in AGP 3.x mode, and then attempts isochronous setup. If bandwidth, ISOCH_N, or request queue capacity cannot satisfy all devices, it logs and falls back to non-isochronous queue partitioning.

## State And Persistence Behavior

All software lists and allocation arrays are temporary. Persistent effects are PCI config writes to target/master `AGPNICMD` and `AGPCMD` fields, which set payload size, isochronous transaction count, and request queue depth until reset or reconfiguration.

## Dependencies And Integration Points

The file depends on `agp.h`, PCI enumeration/config access, list helpers, and AGP register definitions from the private backend header. It is tightly integrated with `generic.c` mode negotiation and only runs during AGP enable for AGP 3.5-capable bridges.

## Risks And Edge Cases

The code assumes at least one eligible AGP master when dividing request queue slots; a bridge with isochronous support but no collected devices would risk division by zero. Enumeration scans all PCI devices and filters by class/capability rather than strictly by bus topology, relying on comments and class filtering to avoid unrelated devices. Resource allocation is approximate: it divides target resources evenly and gives remainders to the last sorted device. Capability walking and AGP 2.x rejection are critical to avoid programming incompatible devices.

## Test Signals

Useful signals include AGP 3.5 hardware logs, successful enable with multiple AGP 3.x masters, fallback logs when isochronous constraints are exceeded, and post-enable PCI config reads showing expected `AGPNICMD`/`AGPCMD` fields. Static tests should check `ndevs` zero handling, list cleanup on allocation failure, and capability-walk bounds.
