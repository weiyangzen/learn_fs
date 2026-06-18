# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_helper_internal.h

## Purpose
`drm_dp_helper_internal.h` is the private internal header that connects the generic DP helper implementation and MST topology code to the optional DP AUX character-device implementation. It keeps the chardev-specific functions out of the public DRM DP helper header while still allowing `drm_dp_helper.c`, `drm_dp_mst_topology.c`, and the display-helper module init/exit path to call into `drm_dp_aux_dev.c` when `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV` is enabled.

## Important APIs, Types, And Functions
The header forward-declares `struct drm_dp_aux` and conditionally exposes four functions:

- `drm_dp_aux_dev_init()` initializes the AUX chardev subsystem.
- `drm_dp_aux_dev_exit()` tears down the AUX chardev subsystem.
- `drm_dp_aux_register_devnode(struct drm_dp_aux *aux)` creates/registers the devnode associated with one AUX channel.
- `drm_dp_aux_unregister_devnode(struct drm_dp_aux *aux)` unregisters the devnode for one AUX channel.

When `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV` is disabled, the same names are defined as static inline stubs. The init and register stubs return `0`; the exit and unregister stubs are no-ops. This lets call sites remain unconditional and avoids spreading preprocessor checks across helper and MST code.

## Control Flow
With chardev support enabled, `drm_display_helper_mod.c` calls `drm_dp_aux_dev_init()` and `drm_dp_aux_dev_exit()` during module lifecycle, while `drm_dp_aux_register()` and `drm_dp_aux_unregister()` call the per-AUX devnode helpers as part of AUX adapter registration. MST topology code also registers and unregisters remote port AUX devnodes using the same declarations.

With chardev support disabled, those call sites compile to simple success/no-op paths. `drm_dp_aux_register()` proceeds directly to I2C adapter registration after the stub register call returns `0`; unregister paths can call the stub without checking configuration state.

## State And Persistence Behavior
The header itself owns no state. When chardev support is enabled, the corresponding implementation in `drm_dp_aux_dev.c` owns any class/minor/device-node state and stores per-AUX devnode references reachable through `struct drm_dp_aux`. When disabled, no devnodes are created and no extra persistent state exists.

The compile-time configuration is the main state selector. The stubs intentionally preserve successful control flow so that AUX channels still work for kernel and I2C users even when userspace raw AUX access is unavailable.

## Dependencies
The file depends only on include guards, the `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV` Kconfig symbol, and the existence of `struct drm_dp_aux` as an opaque type. Enabled builds require matching definitions in `drm_dp_aux_dev.c`; disabled builds require no additional source file linkage for these functions.

## Integration Points
This header is included by `drm_dp_helper.c` for local AUX registration and by MST/display-helper code that needs optional raw AUX devnode management. It is part of the internal display helper module boundary, not a public driver API. The public API remains `drm_dp_aux_register()`/`drm_dp_aux_unregister()` plus MST topology helpers; those functions hide whether devnodes exist.

## Risks
The important risk is configuration skew. If enabled prototypes stop matching `drm_dp_aux_dev.c`, chardev builds fail or mis-handle AUX lifetime. If disabled stubs return errors, all AUX registration would fail in configurations without raw AUX userspace support. If callers start depending on devnode side effects while the stubs remain no-ops, behavior will differ between Kconfig variants.

Because devnodes expose raw AUX access to userspace, lifetime ordering matters in enabled builds: unregister must run before the AUX backing object is destroyed, and registration failures must be unwound. The header's unconditional API shape makes that easier, but it also means call sites must continue to call the unregister helper on every registered AUX object.

## Test Signals
Build-test both `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV=y/m` and disabled configurations. In enabled builds, module init should create the AUX chardev infrastructure, AUX registration should create devnodes for local and MST remote AUX channels, and unregister should remove them without use-after-free warnings. In disabled builds, DP connector detection, AUX DPCD reads, I2C-over-AUX EDID reads, and MST operation should still work, with no unresolved references to `drm_dp_aux_dev_*` symbols.
