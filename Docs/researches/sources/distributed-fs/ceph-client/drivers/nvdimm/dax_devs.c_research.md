# sources/distributed-fs/ceph-client/drivers/nvdimm/dax_devs.c

## Purpose
`dax_devs.c` implements the `nd_dax` device wrapper for NVDIMM namespaces configured for device-DAX mode. It reuses `struct nd_pfn` infrastructure for DAX metadata, creates DAX seed devices, and probes existing DAX info blocks on namespaces.

## Important APIs, Types, And Functions
Public functions are `to_nd_dax()`, `is_nd_dax()`, `nd_dax_create()`, and `nd_dax_probe()`. Internal allocation is handled by `nd_dax_alloc()`, while release uses `nd_dax_release()`.

The `nd_dax` device type is named `nd_dax` and uses `nd_pfn_attribute_groups`, reflecting that DAX and PFN devices share sysfs attributes around namespace, UUID, alignment, and mode.

## Control Flow
`nd_dax_create()` creates a seed DAX device only for memory regions, allocates an ID from the region's `dax_ida`, initializes the embedded PFN device through `nd_pfn_devinit()`, and registers it. `nd_dax_probe()` ignores forced-raw namespaces, accepts only none/DAX claim classes, allocates and attaches a DAX device under the bus lock, allocates a PFN superblock buffer, validates it with `nd_pfn_validate(nd_pfn, DAX_SIG)`, and registers or tears down the device based on validation.

## State And Persistence Behavior
Volatile state is held in `struct nd_dax`, whose first member is `struct nd_pfn`; this lets PFN helpers operate on DAX devices. Persistent state is the namespace's PFN/DAX info block validated by `nd_pfn_validate()` with `DAX_SIG`. Release detaches the namespace, frees the DAX ID, UUID, and device object.

## Dependencies And Integration Points
The file depends on `pfn.h` for DAX signatures and PFN helpers, `claim.c` for namespace attach/detach, `namespace_devs.c` for claim class and forced raw behavior, and `bus.c` for device registration. The actual device-DAX runtime is outside this file; this wrapper prepares libnvdimm device state.

## Risks And Edge Cases
The shared PFN/DAX representation requires correct `to_nd_pfn_safe()` behavior elsewhere; treating a DAX device as a standalone PFN container incorrectly would corrupt offsets. Probe failure after attachment must detach and drop the device to avoid stale claims. Forced raw bypass and claim-class filtering are essential to avoid auto-creating DAX wrappers for raw or BTT/PFN namespaces.

## Test Signals
Tests should cover seed creation only for memory regions, ID allocation failure cleanup, forced raw skip, claim-class rejection, valid DAX info-block registration, invalid signature detach/put behavior, sysfs attribute reuse from PFN, and release freeing the region `dax_ida` ID.
