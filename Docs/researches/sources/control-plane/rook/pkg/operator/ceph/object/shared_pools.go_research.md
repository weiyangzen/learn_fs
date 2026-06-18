# sources/control-plane/rook/pkg/operator/ceph/object/shared_pools.go

Purpose: transforms `ObjectSharedPoolsSpec` and placement specs into Ceph RGW zone and zonegroup JSON updates that allow object stores to share data/metadata pools with namespaced RADOS layouts.

Important APIs/types: `IsNeedToCreateObjectStorePools`, `validatePoolPlacements`, `validatePoolPlacementStorageClasses`, `adjustZonePlacementPools`, `getDefaultPlacementName`, `getDefaultMetadataPool`, `toZonePlacementPools`, `toZonePlacementPool`, `adjustZoneGroupPlacementTargets`, `createPlacementTargetsFromZonePoolPlacements`, `getZoneJSON`, `getZoneGroupJSON`, `updateZoneJSON`, `updateZoneGroupJSON`, and structs `ZonegroupPlacementTarget`, `ZonePlacementPool`, `ZonePlacementPoolVal`, `ZonePlacementStorageClass`.

Control flow: validation enforces one default placement, unique placement names, reserved `default-placement` semantics, and unique non-reserved storage class names. Zone placement adjustment deep-copies zone JSON, converts desired spec placements to RGW JSON, updates existing placements, preserves or mirrors `default-placement` for Ceph workarounds, removes placements not in spec, adds missing placements, sorts them for stable comparison with `radosgw-admin`, and writes them back. Zonegroup adjustment sets the default placement, derives placement targets/storage classes from zone placements, updates/removes/adds targets, and writes back. Get/update helpers call `radosgw-admin zone/zonegroup get/set`, writing JSON to temporary files under `ConfigDir`.

State and persistence: reads and writes Ceph zone and zonegroup JSON; temporary config files are created with mode 0600 and removed after command execution. It does not directly create pools; it assumes `objectstore.go` has verified referenced pools exist.

Dependencies and integration points: called by `ConfigureSharedPoolsForZone` in `objectstore.go`; depends on JSON helper functions such as `getObjProperty`, `updateObjProperty`, `deepCopyJson`, `toObj`, and `castJson` elsewhere in the package; integrates with Ceph `radosgw-admin` command semantics and known tracker workarounds for `inline_data` and default placement handling.

Risks: this code is sensitive to Ceph JSON schema changes and type assertions from generic `map[string]interface{}`. It deliberately preserves `default-placement` for a Ceph issue, which can surprise users expecting removal. Storage class data pool namespace for extra classes is based on storage class name rather than placement name. Update helpers require non-empty realm/zone/zonegroup context and writable config dir.

Test signals: shared-pool behavior is covered indirectly in `objectstore_test.go` for no-op, default shared pools, new default placement, already-set pools, extra placement, validation errors, and missing referenced pools. Direct tests for malformed zone JSON and helper type failures are limited.
