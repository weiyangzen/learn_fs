# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_encoder.c

## Purpose

`drm_encoder.c` implements DRM core encoder object lifecycle, managed allocation helpers, debugfs registration hooks, and the legacy `GETENCODER` ioctl response. Encoders model the link between CRTCs and connectors, but the file's documentation emphasizes that encoder UAPI restrictions are historically unreliable and that modern userspace should use atomic test-only commits to discover valid routing.

## Important APIs and Data

`drm_encoder_enum_list[]` maps UAPI encoder type constants to names used for default object names. Internal `__drm_encoder_init()` adds a mode object, assigns device/type/function/name fields, initializes the bridge chain, appends the encoder to `dev->mode_config.encoder_list`, and assigns an index. The index is used in 32-bit masks, so initialization fails if `num_encoder >= 32`.

Exported lifecycle APIs are `drm_encoder_init()` for caller-owned encoder storage and `drm_encoder_cleanup()` for teardown. Managed APIs are `__drmm_encoder_alloc()` and `drmm_encoder_init()`, both backed by `__drmm_encoder_init()` and `drmm_add_action_or_reset()`. Managed encoders must not provide a `destroy` hook because cleanup is driven by DRM managed resources; unmanaged `drm_encoder_init()` warns if the destroy hook is missing.

`drm_encoder_register_all()` and `drm_encoder_unregister_all()` walk all encoders, add/remove debugfs entries, and invoke optional driver `late_register` and `early_unregister` callbacks.

The UAPI handler `drm_mode_getencoder()` looks up an encoder by id, determines the current CRTC, filters CRTC masks by leases, and fills `struct drm_mode_get_encoder`.

## Control Flow

Initialization first registers a DRM mode object. If name formatting fails, it unregisters the mode object and returns `-ENOMEM`. Once named, the encoder is inserted into the device list and counted. Cleanup detaches every bridge in `encoder->bridge_chain`, unregisters the mode object, frees the name, removes the list node, decrements `num_encoder`, and zeroes the structure.

Managed initialization wraps the same core init but registers `drmm_encoder_alloc_release()` as a device-managed action. If later managed registration fails, `drmm_add_action_or_reset()` immediately runs cleanup. `__drmm_encoder_alloc()` allocates a container with `drmm_kzalloc()`, finds the embedded encoder by offset, initializes it, and returns either the container pointer or `ERR_PTR()`.

`drm_encoder_get_crtc()` handles atomic and legacy drivers differently. It scans connectors under the connection mutex. If connector states exist, it treats the device as atomic and returns the CRTC whose connector state has this encoder as `best_encoder`. If any atomic state was observed but no match was found, it returns NULL to avoid stale `encoder->crtc`. Legacy drivers fall back to `encoder->crtc`.

## State and Persistence Behavior

The file mutates persistent DRM device mode configuration: encoder list membership, encoder count, mode object id, encoder index, name allocation, bridge chain ownership, and debugfs registration. UAPI queries are transient but protected by `connection_mutex` while resolving the current CRTC. Cleanup zeroes the entire encoder, so callers must not use fields after cleanup.

## Dependencies and Integration Points

The file integrates with DRM bridge detach, mode object registration, managed resource cleanup, debugfs, DRM leases, connector iteration, and the modeset ioctl layer. Driver callbacks in `struct drm_encoder_funcs` provide device-specific registration and destruction behavior. Bridge-heavy drivers may keep most hardware-specific logic outside encoders, but encoder bridge chains still need correct detach ordering.

## Risks and Edge Cases

The 32-encoder limit is structural because masks are 32-bit. Runtime encoder removal is discouraged by an in-code note: removing from the static list would require reindexing later encoders. Managed and unmanaged lifetime rules differ, especially around `destroy`; mixing them can double-clean or leak. `drm_encoder_get_crtc()` must avoid stale legacy state for atomic drivers, hence the atomic-state detection. `drm_mode_getencoder()` must filter leased CRTCs or userspace could observe objects outside its lease.

## Test Signals

Tests should cover unmanaged init/cleanup error paths, managed init cleanup on action registration failure, bridge-chain detach on cleanup, default and formatted names, index/count behavior at the 32-encoder boundary, debugfs add/remove callback ordering, late/early register error propagation, GETENCODER for leased and unleased CRTCs, and atomic versus legacy CRTC reporting. Driver unload tests should confirm no encoder mode objects, debugfs entries, names, or bridge attachments remain.
