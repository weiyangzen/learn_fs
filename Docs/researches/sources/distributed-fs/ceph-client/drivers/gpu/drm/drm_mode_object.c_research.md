# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_object.c

## Purpose
This file implements DRM modeset object ID management, lookup, optional object reference counting, property storage, property query ioctls, and property set ioctls for legacy and atomic drivers. It is the bridge between userspace object IDs/properties and in-kernel KMS objects such as connectors, CRTCs, planes, framebuffers, and blobs.

## Important APIs, Types, and Functions
Object ID APIs include `__drm_mode_object_add()`, `drm_mode_object_add()`, `drm_mode_object_register()`, `drm_mode_object_unregister()`, `drm_mode_object_find()`, `drm_mode_object_get()`, and `drm_mode_object_put()`. Leasing rules are centralized in `drm_mode_object_lease_required()`.

Property APIs include `drm_object_attach_property()`, `drm_object_property_set_value()`, `drm_object_property_get_value()`, `drm_object_property_get_default_value()`, `drm_object_immutable_property_get_value()`, `drm_mode_object_get_properties()`, `drm_mode_obj_get_properties_ioctl()`, `drm_mode_obj_find_prop_id()`, and `drm_mode_obj_set_property_ioctl()`. Set paths split into `set_property_legacy()` and `set_property_atomic()`.

## Control Flow
Object add allocates an ID from `dev->mode_config.object_idr` under `idr_mutex`, optionally places the object in the IDR immediately, sets object type/id, and initializes a kref when a free callback is supplied. Lookup locks the IDR, verifies type and ID consistency, enforces leases for CRTCs/connectors/planes, and takes a kref for refcounted objects if possible.

Properties are attached by appending to the object's fixed-size property array before userspace registration. Direct set/get functions update or read the stored software values, with atomic drivers routed to `drm_atomic_get_property()` for mutable properties. Property query ioctls take all modeset locks, find the object, filter atomic-only properties for non-atomic clients and plane color-pipeline compatibility properties based on file capability, and copy property IDs/values to userspace. Property set ioctls find the object and property, validate references, then either call legacy object-specific setters under all modeset locks or allocate an atomic state, set the property, and commit with deadlock backoff retry.

## State and Persistence Behavior
Persistent state is the mode_config IDR mapping IDs to objects, per-object ID/type/free callback/refcount, and per-object property/value arrays. Immutable/default values remain in the arrays; atomic mutable state lives in the atomic state objects and is queried through atomic callbacks. Reference counted objects can outlive lookup callers until `drm_mode_object_put()`. Non-refcounted static KMS objects rely on driver lifetime and registration ordering.

## Dependencies and Integration Points
This code depends on Linux IDR, kref, uaccess, DRM leasing, DRM atomic state/commit helpers, property validation, connector/CRTC/plane legacy setters, and modeset locks. It is exercised by `GETPROPERTIES` and `SETPROPERTY` ioctls and by all KMS object initialization paths that attach standard or driver-specific properties.

## Risks
The fixed `DRM_OBJECT_MAX_PROPERTY` array can overflow if drivers attach too many properties; the code warns and drops the attachment. Properties must be attached before userspace can see the object, otherwise userspace-visible state can change unsafely. Lease checks apply only to CRTC/connector/plane types; adding new lease-required object types requires updating `drm_mode_object_lease_required()`. Atomic and legacy property state differ; using direct stored-value getters for atomic mutable properties is wrong. Error paths in `drm_mode_obj_get_properties_ioctl()` rely on dropping references correctly when partially complete.

## Test Signals
Signals include unique ID allocation/removal under concurrent registration tests, lookup denying wrong types and unleased objects, refcounted lookup surviving object release races, property attach warnings at the max-property limit, `GETPROPERTIES` count-only and copy-out behavior, atomic-client filtering of atomic properties, plane color pipeline property filtering, legacy property setters reaching the right object callbacks, atomic set retries on `-EDEADLK`, and reference cleanup after ioctl failures.
