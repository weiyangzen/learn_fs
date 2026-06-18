<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/bundle.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/bundle.h

Purpose: This header defines Greybus bundles, the logical function units within an interface that drivers bind to.

Important APIs/types/functions: `struct gb_bundle` embeds a device, points to its interface, stores bundle id/class/version, CPort descriptors, connection list, state byte array, and interface list links. Lifecycle APIs are `gb_bundle_create()`, `gb_bundle_add()`, and `gb_bundle_destroy()`. Runtime PM wrappers include `gb_pm_runtime_get_sync()`, `gb_pm_runtime_put_autosuspend()`, `gb_pm_runtime_get_noresume()`, and `gb_pm_runtime_put_noidle()`, with no-op stubs when `CONFIG_PM` is off.

Control flow, state, and persistence: The manifest parser creates bundles from descriptors and attaches CPort descriptors. Adding a bundle publishes it to the driver core; protocol drivers create connections from its CPorts. Runtime PM wrappers increment/decrement the bundle device usage count and handle autosuspend bookkeeping.

Dependencies/integration: Bundles are children of Greybus interfaces and integrate with Linux devices, lists, PM runtime, manifest CPort descriptors, and Greybus driver matching.

Risks and test signals: Runtime PM get failures must be balanced with `pm_runtime_put_noidle()`, which the helper does. Tests should cover bundle creation from manifests, version/class matching, connection list cleanup, PM enabled/disabled builds, autosuspend behavior, and destroy after failed add.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/bundle.h -->
