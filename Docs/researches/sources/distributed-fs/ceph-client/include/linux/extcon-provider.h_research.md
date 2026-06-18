# sources/distributed-fs/ceph-client/include/linux/extcon-provider.h

Purpose: provider-side API for registering external connector devices and publishing connector state/property changes.

Important APIs/types/functions: `extcon_dev_register/unregister`, devm registration, allocation/free helpers, `extcon_sync()`, `extcon_set_state()`, `extcon_set_state_sync()`, `extcon_set_property()`, `extcon_set_property_sync()`, and `extcon_set_property_capability()` plus disabled stubs.

Control flow: provider drivers allocate an `extcon_dev`, register it, declare property capabilities, update connector state/properties, and sync notifications to consumers. Managed variants tie lifetime to a device.

State/persistence: runtime extcon state/properties and notifier state in `extcon_dev`; physical connector state is hardware-derived and may persist electrically but is re-detected.

Dependencies/integration: extcon core, device model/devres, notifier chains, consumer API in `extcon.h`, charger/USB/display/jack drivers.

Risks/test signals: risks are setting unsupported properties, missed sync notifications, managed/unmanaged lifetime mixups, and config-off stubs returning success for state updates. Test provider probe/remove, state/property notifications, devm cleanup, unsupported ID/property errors, and disabled config builds.
