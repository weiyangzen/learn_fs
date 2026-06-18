# sources/distributed-fs/ceph-client/include/drm/drm_mode_object.h

Purpose: declares the base object and property storage used by KMS objects visible to userspace, such as CRTCs, planes, connectors, framebuffers, property blobs, and properties.

Important APIs and types: `struct drm_mode_object` carries userspace ID, object type, attached properties, optional kref, and free callback for dynamic objects. `DRM_OBJECT_MAX_PROPERTY` caps attached properties at 64. `struct drm_object_properties` stores property pointers and parallel default/current values. `DRM_ENUM_NAME_FN()` generates enum-name lookup helpers. Public APIs find mode objects with lease filtering, get/put dynamic objects, set/get property values, get default or immutable values, attach properties, and ask whether a mode object type requires lease checks.

Control flow: drivers initialize KMS objects and attach immutable/default properties before exposing them. Ioctl paths look up objects by ID/type through `drm_mode_object_find()`, optionally constrained by file lease state. Legacy property paths read/write the stored value array, while atomic drivers normally decode mutable properties into object state through atomic get/set hooks instead of mutating this array.

State and persistence behavior: object IDs live in the device mode-config IDR. Static objects usually have no free callback; dynamic objects use the embedded kref and callback. Property pointer/value arrays persist with the object and are valid until mode-config cleanup.

Dependencies and integration points: includes kref and DRM lease support. It integrates with property creation, atomic property hooks, KMS ioctl object lookup, and lease-required object type checks.

Risks: property array overflow is bounded by `DRM_OBJECT_MAX_PROPERTY` and must be respected by attach paths. Mutable atomic properties should not be treated as authoritative in `values[]`. Dynamic object refcount callbacks must match container layout. Lease filtering must be used for user-visible lookups.

Test signals: object lookup by ID/type, lease-denied lookup, property attach/get/set/default retrieval, immutable property access, dynamic object refcount release, and objects with maximum property counts.
