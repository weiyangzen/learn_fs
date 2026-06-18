# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.h

## Purpose
Declares the GuC hardware configuration table API.

## Important APIs, Types, And Functions
The header exposes initialization, table size, table copy, debug dump, and 32-bit attribute lookup functions. It forward-declares `struct drm_printer` and `struct xe_guc`.

## Control Flow
The intended flow is initialize once, check size, optionally copy or dump the full table, and use lookup for individual attributes.

## State And Persistence
State is hidden in `guc->hwconfig` and owned by the implementation.

## Dependencies And Integration Points
Included by GuC init and feature-detection code that needs firmware-provided hardware attributes.

## Risks And Test Signals
The lookup API reports `-EINVAL`, `-ENOMEM`, or `-ENOENT`; callers must distinguish missing table from missing attribute. Compile coverage and platform boot with hwconfig-enabled firmware validate the interface.
