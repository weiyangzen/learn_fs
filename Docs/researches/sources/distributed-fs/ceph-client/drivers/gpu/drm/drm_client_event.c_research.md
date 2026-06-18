# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client_event.c

## Purpose
`drm_client_event.c` dispatches unregister, hotplug, restore, suspend, resume, and debugfs events to in-kernel DRM clients attached to a device.

## Important APIs, Types, And Functions
Public APIs include `drm_client_dev_unregister()`, `drm_client_dev_hotplug()`, `drm_client_dev_restore()`, `drm_client_dev_suspend()`, `drm_client_dev_resume()`, and debugfs initialization through `drm_client_debugfs_init()`. Internal `drm_client_hotplug()` centralizes hotplug gating.

## Control Flow
Hotplug skips non-modeset devices and devices with no connectors, then iterates clients under `clientlist_mutex`. Clients without callbacks, failed hotplug state, or suspended state are skipped or marked pending. Resume clears suspension and replays pending hotplug. Unregister safely removes and frees clients. Restore runs clients in order and stops at the first successful restore.

## State And Persistence
Per-client runtime flags `suspended`, `hotplug_pending`, and `hotplug_failed` drive callback behavior. The device client list is mutated on unregister. Debugfs output is transient.

## Dependencies And Integration Points
This file connects KMS hotplug helpers, `drm_dev_unregister()`, PM paths, fbdev/internal clients, debugfs, and `DRIVER_MODESET` checks.

## Risks And Edge Cases
Transient hotplug failure permanently suppresses future hotplug for that client unless reset elsewhere. Callbacks run under `clientlist_mutex`, creating lock-order constraints. Suspend marks clients suspended even if the suspend callback fails. Restore ordering determines which client wins.

## Test Signals
Test hotplug success/failure, pending hotplug replay after resume, unregister callbacks that free clients, restore first-success semantics, no-connector suppression, and debugfs client listing.
