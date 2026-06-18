# sources/distributed-fs/ceph-client/drivers/nvdimm/claim.c

## Purpose
`claim.c` implements shared claim and namespace byte-access helpers for libnvdimm namespace personality devices. It attaches/detaches namespaces to BTT/PFN/DAX devices, resets idle claim devices, parses the common `namespace` sysfs store operation, computes generic 4 KiB info-block checksums, and enables raw namespace I/O mappings.

## Important APIs, Types, And Functions
Exported or shared functions include `__nd_detach_ndns()`, `nd_detach_ndns()`, `__nd_attach_ndns()`, `nd_namespace_store()`, `nd_sb_checksum()`, `devm_nsio_enable()`, and `devm_nsio_disable()`. `to_nd_pfn_safe()` supports PFN attributes reused by DAX devices.

Internal helpers include `is_idle()`, `nd_detach_and_reset()`, and `nsio_rw_bytes()`.

## Control Flow
Attach requires the caller to hold the bus reconfiguration mutex. `__nd_attach_ndns()` rejects already claimed namespaces, sets `ndns->claim`, stores the namespace pointer in the personality device, and takes a namespace device reference. Detach clears the namespace's claim, nulls the caller's pointer, and drops the reference. The public detach wrapper takes a temporary namespace reference and grabs the bus lock before calling the internal detach.

`nd_namespace_store()` is the common sysfs handler for BTT/PFN/DAX `namespace` attributes. It rejects active claim devices, accepts either an empty string for detach or a `namespace*` child name, finds the namespace under the region, checks claim-class compatibility, enforces a minimum namespace size, and attaches if unclaimed. Empty string detaches and either unregisters idle non-seed claim devices or resets BTT/PFN/DAX configuration fields.

`devm_nsio_enable()` reserves the physical resource, installs `nsio_rw_bytes()` as the namespace byte accessor, initializes badblocks, populates them from the region, and memremaps the namespace. The disable path unmaps, exits badblocks, and releases the region.

## State And Persistence Behavior
Claim state is volatile kernel device state: `nd_namespace_common.claim` and each personality's `ndns` pointer. The helper deliberately ties references to claims to prevent namespace device teardown while claimed. BTT/PFN/DAX UUIDs and modes are reset on detach if the device remains as a seed.

`nsio_rw_bytes()` performs direct persistent-memory reads and writes. Reads check badblocks and use `copy_mc_to_kernel()` so machine-check recoverable faults become `-EIO`. Writes optionally clear poison for sector-aligned non-atomic writes, then use `memcpy_flushcache()` and `nvdimm_flush()` to make data durable. The generic info-block checksum uses `nd_fletcher64()` with the final checksum field zeroed.

## Dependencies And Integration Points
The file depends on device type helpers from BTT/PFN/DAX code, namespace and region types from `nd.h`, badblocks, provider poison clearing from `bus.c`, and persistent memory mapping/flushing primitives. It is used by BTT, PFN, DAX, and namespace probe code to share claim semantics.

## Risks And Edge Cases
Locking discipline is critical: internal attach/detach asserts the bus reconfiguration mutex, while sysfs handlers must hold device and bus locks. `nd_namespace_store()` only accepts names beginning with `namespace` or empty strings, preventing arbitrary child claims. Minimum capacity is hard-coded to 16 MiB for claim hosting. `nsio_rw_bytes()` has distinct behavior for atomic writes: it refuses to clear poison for atomic or unaligned writes, returning `-EIO` instead.

## Test Signals
Tests should cover claim attach/detach, claim-class mismatch rejection, attaching already claimed namespaces, detaching seed and non-seed claim devices, namespace capacity checks, checksum compatibility with BTT/PFN superblocks, badblock read errors, poison clear on aligned writes, no poison clear on atomic writes, namespace resource reservation failure, and device-reference lifetime around detach.
