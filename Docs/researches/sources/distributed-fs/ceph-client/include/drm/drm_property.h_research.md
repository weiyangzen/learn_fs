# sources/distributed-fs/ceph-client/include/drm/drm_property.h

## Purpose
`drm_property.h` defines KMS object properties and blob properties. Properties are the generic metadata and atomic state transport used by connectors, CRTCs, planes, framebuffers, and userspace IOCTLs.

## Important APIs, types, and functions
Important types are `struct drm_property_enum`, `struct drm_property`, `struct drm_property_blob`, and `struct drm_prop_enum_list`. `drm_property_type_is()` handles legacy and extended type encodings. Creation APIs include `drm_property_create`, `_enum`, `_bitmask`, `_range`, `_signed_range`, `_object`, and `_bool`, plus `drm_property_add_enum` and `drm_property_destroy`. Blob APIs include `drm_property_create_blob`, `drm_property_lookup_blob`, `drm_property_replace_blob_from_id`, `drm_property_replace_global_blob`, `drm_property_replace_blob`, `drm_property_blob_get`, and `drm_property_blob_put`. `drm_property_find()` wraps mode-object lookup.

## Control flow
Drivers create property definitions, populate enum/bitmask values, attach properties to mode objects, and let the core validate user-provided values against ranges, object types, or blob IDs. Atomic IOCTL state is expressed by setting properties, while immutable properties can still be updated by the kernel.

## State and persistence
Property definitions live on the DRM device property list. Blobs are refcounted mode objects on global and per-file lists, with immutable data length and embedded data. State is runtime-only and tied to device/file/object lifetimes.

## Dependencies and integration points
The header depends on mode object lookup, UAPI property flags, DRM file leasing checks, and KMS object property attachment. It underpins standard and driver-private KMS properties such as EDID blobs, rotation, zpos, CRTC links, framebuffer links, and damage clips.

## Risks and test signals
Risks include incorrect property type flags, signed/unsigned range confusion, enum value drift with UAPI, blob refcount leaks, accepting blobs with wrong size, exposing duplicate property names with incompatible ranges, and lease visibility mistakes. Test signals include atomic property set/get, blob create/replace/free, enum/bitmask validation, immutable property updates, lease-filtered lookup, and KMS property IOCTL fuzzing.
