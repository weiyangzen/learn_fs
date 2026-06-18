# sources/distributed-fs/ceph-client/include/drm/drm_client_event.h

## Purpose
This header declares event fan-out helpers that notify registered DRM clients about device unregister, hotplug, restore, suspend, and resume. It also provides no-op stubs when `CONFIG_DRM_CLIENT` is disabled.

## Important APIs, types, and functions
The API surface is `drm_client_dev_unregister`, `drm_client_dev_hotplug`, `drm_client_dev_restore`, `drm_client_dev_suspend`, and `drm_client_dev_resume`.

## Control Flow
Core DRM and helper paths call these functions at lifecycle and display events. With client support enabled, implementations iterate registered clients and invoke relevant callbacks; with support disabled, static inline stubs discard the event.

## State and Persistence
This header owns no state. It operates on the device's registered client list and client suspend/hotplug bookkeeping declared in `drm_client.h`.

## Dependencies and Integration Points
It depends on `CONFIG_DRM_CLIENT` and `struct drm_device`. It integrates DRM device lifecycle, hotplug helpers, fbdev/client restore, and power management paths.

## Risks and Test Signals
Risks include missing events when the config is disabled, callbacks after unregister, restore semantics when multiple clients exist, and hotplug deferral across suspend. Tests should cover enabled and disabled builds, unregister followed by hotplug, forced restore, suspend/resume ordering, and clients that return errors from hotplug.
