<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/service.go -->
# sources/cloud-native/moby/daemon/images/service.go

Purpose: constructs and implements the legacy `ImageService` backend around image, layer, reference, distribution, content, lease, event, and container stores.

Important APIs and control flow: `ImageServiceConfig` supplies all dependencies. `NewImageService` creates download/upload managers and wraps the image store with lease deletion. Methods expose distribution services, image counts, children, layer creation from containers or images, layer lookup/status/mount IDs, cleanup, storage driver name, layer release, disk usage, layer reference accounting, and runtime concurrency config updates.

State and persistence: owns pointers to persistent stores and transient managers. It writes layer state through create/release, reads image/layer maps for disk usage, and updates manager concurrency.

Dependencies and integration: central hub for daemon image operations, distribution pull/push, builders, container lifecycle, events, and disk usage. It depends on Moby internal image/layer/refstore and containerd content/leases.

Risks: `ReleaseLayer` type-asserts to `layer.RWLayer`, so alternative RW layer implementations must satisfy that concrete internal interface. `ImageDiskUsage` counts only layers referenced by images that are tagged or childless, matching Docker semantics but not all on-disk data. `UpdateConfig` ignores zero values, so zero cannot be used to set concurrency here.

Test signals: behavior is covered broadly by image, container, and daemon tests rather than a single service test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/service.go -->
