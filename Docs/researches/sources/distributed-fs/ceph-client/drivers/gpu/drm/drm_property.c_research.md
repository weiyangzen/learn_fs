# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_property.c

Purpose: implements DRM modeset property creation, enumeration metadata, blob properties, userspace property/blob ioctls, blob replacement helpers, and property value validation with object/blob reference handling.

Important APIs/types/functions: property constructors include `drm_property_create()`, enum, bitmask, range, signed range, object, and bool variants. `drm_property_add_enum()` and `drm_property_destroy()` manage metadata. Ioctls include `drm_mode_getproperty_ioctl()`, `drm_mode_getblob_ioctl()`, `drm_mode_createblob_ioctl()`, and `drm_mode_destroyblob_ioctl()`. Blob APIs include `drm_property_create_blob()`, `drm_property_blob_get/put()`, `drm_property_lookup_blob()`, `drm_property_destroy_user_blobs()`, `drm_property_replace_global_blob()`, `drm_property_replace_blob()`, and `drm_property_replace_blob_from_id()`. `drm_property_change_valid_get()` and `drm_property_change_valid_put()` validate and manage referenced dynamic values.

Control flow: property creation validates flags/name, allocates value storage, registers a mode object, initializes enum list and device property list membership. User property get copies fixed values first and enum metadata second. Blob creation allocates one object plus inline data, registers a refcounted mode object with `drm_property_free_blob()` release, and links it globally; user-created blobs are additionally linked to `file_priv->blobs`. Blob destroy verifies file ownership, unlinks file membership, then drops both lookup and file references.

State and persistence behavior: properties persist in `dev->mode_config.property_list` until mode config cleanup. Blobs are refcounted mode objects in a global blob list protected by `blob_lock`; user blobs also persist per DRM file until explicit destroy or file release. Blob data is immutable after creation by contract.

Dependencies and integration points: used by legacy and atomic modeset objects, connector/CRTC/plane properties, EDID/path/color metadata blobs, user ioctls, mode object ID lookup, and `uaccess` copy paths.

Risks: property flags must contain exactly one valid type class; bad flags are rejected with warnings. User blob ownership checks prevent one file from destroying another file's blob, but global lookups still expose readable blob IDs. `drm_property_replace_global_blob()` assumes caller-side locking around the pointer being replaced. Reference-returning validation requires paired `drm_property_change_valid_put()` on failure paths.

Test signals: constructor validation for all property types, duplicate enum rejection, getproperty count-only and copy paths, create/get/destroy blob ownership, file release cleanup, blob replacement with size and element constraints, immutable property rejection, object/blob value reference leak checks, and atomic property validation fuzzing.
