# sources/distributed-fs/ceph-client/include/drm/drm_privacy_screen_driver.h

## Purpose
`drm_privacy_screen_driver.h` declares the provider-side privacy-screen class interface. It lets hardware-specific drivers register privacy-screen devices, expose state through sysfs/DRM connector integration, and notify consumers of changes.

## Important APIs, types, and functions
`struct drm_privacy_screen_ops` provides `set_sw_state` and `get_hw_state`. `struct drm_privacy_screen` embeds a `struct device`, mutex, global list link, blocking notifier head, ops pointer, software and hardware state, and provider `drvdata`. APIs are `drm_privacy_screen_register`, `drm_privacy_screen_unregister`, `drm_privacy_screen_call_notifier_chain`, and `drm_privacy_screen_get_drvdata`.

## Control flow
A provider registers with parent device, ops, and private data. The core calls `get_hw_state` before sysfs registration and calls `set_sw_state` under the privacy-screen mutex when a consumer requests a change and the hardware state is not locked. Providers update both sw and hw state and invoke the notifier chain when state changes.

## State and persistence
Runtime state is in the privacy-screen object: device registration, locking, list membership, notifier subscribers, ops validity, software/hardware status, and private data. `ops` becomes NULL after unregister to prevent calls into a removed driver. Hardware privacy state may persist outside the kernel, but this header only models the runtime view.

## Dependencies and integration points
It depends on the Linux device model, mutex/list/notifier infrastructure, and DRM connector privacy status enums. It integrates with sysfs, machine lookup tables, and consumer APIs used by DRM connectors.

## Risks and test signals
Risks include provider unregister racing with consumer calls, failing to update both state fields, notifier callbacks under locks causing deadlocks, incorrect handling of locked hardware state, and sysfs lifetime mistakes. Test signals include provider register/unregister, sysfs state read/write, locked-state refusal, notifier ordering, consumer get during unregister, and driver-private data access.
