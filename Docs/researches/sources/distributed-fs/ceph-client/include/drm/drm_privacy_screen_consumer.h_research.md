# sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_consumer.h

## Purpose
`drm_privacy_screen_consumer.h` declares the consumer-facing API for display drivers or connectors that use a privacy-screen provider, such as laptop display privacy filters.

## Important APIs, types, and functions
When `CONFIG_DRM_PRIVACY_SCREEN` is enabled, consumers can call `drm_privacy_screen_get`, `drm_privacy_screen_put`, `drm_privacy_screen_set_sw_state`, `drm_privacy_screen_get_state`, `drm_privacy_screen_register_notifier`, and `drm_privacy_screen_unregister_notifier`. Disabled stubs return `ERR_PTR(-ENODEV)`, `-ENODEV`, no-op, or disabled software/hardware status values.

## Control flow
A consumer resolves a provider by device and connector ID, reads current software and hardware states, requests software state changes, and optionally registers a notifier for provider state updates. Reference release uses `drm_privacy_screen_put`.

## State and persistence
The header stores no state. State lives in the provider object and includes software and hardware privacy status. Stub behavior reports privacy disabled when the subsystem is not compiled.

## Dependencies and integration points
It depends on `linux/device.h` and DRM connector privacy-screen status enums. It integrates with connector properties and provider drivers registered through the driver-facing privacy-screen API.

## Risks and test signals
Risks include treating `-ENODEV` as fatal when privacy support is optional, missing notifier unregister on connector teardown, mismatched connector IDs, and stale references after provider unregister. Test signals include config-enabled and config-disabled builds, connector property updates, notifier delivery, get/put lifetime, provider removal while a consumer exists, and locked hardware-state behavior.
