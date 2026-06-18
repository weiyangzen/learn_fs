<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake_types.h

## Purpose
`xe_force_wake_types.h` defines forcewake domain identifiers, bitmasks, and persistent state structures for GT power-domain wake management.

## Important APIs, types, and functions
`enum xe_force_wake_domain_id` enumerates GT, render, generic media, VDBOX0-7, VEBOX0-3, GSC, and count. `enum xe_force_wake_domains` maps these IDs to bitmasks and defines `XE_FORCEWAKE_ALL` as a sentinel bit. `struct xe_force_wake_domain` stores domain id, control and ack registers, wake value, mask, and refcount. `struct xe_force_wake` stores the owning GT, spinlock, awake mask, initialized mask, and domain array.

## Control flow and integration points
The header has no executable code. `xe_force_wake.c` fills domains during GT/engine init and mutates refs/awake masks during get/put. Other subsystems rely on these masks to keep render/media/GSC registers accessible.

## State and persistence behavior
Per-domain register metadata is immutable after initialization. Refcounts and awake masks are mutable under `fw->lock` and persist across nested callers until all references are released.

## Dependencies, risks, and test signals
Dependencies include Linux types, register definitions, and GT ownership. Risks include enum order mismatches with bitmask macros, adding domains without increasing arrays, and using `XE_FORCEWAKE_ALL` as a real domain id. Test signals include domain initialization on GT/media/GSC engine masks, nested forcewake reference tests, and compile-time coverage of domain-to-string mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake_types.h -->
