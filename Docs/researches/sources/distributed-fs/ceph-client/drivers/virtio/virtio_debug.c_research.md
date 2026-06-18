# sources/distributed-fs/ceph-client/drivers/virtio/virtio_debug.c

## Purpose
`virtio_debug.c` exposes debugfs controls for observing device-advertised virtio features and filtering negotiated features before driver probe finalizes them.

## Important APIs, types, and functions
Exports are `virtio_debug_init`, `virtio_debug_exit`, `virtio_debug_device_init`, `virtio_debug_device_exit`, and `virtio_debug_device_filter_features`. Debugfs files per device are `device_features`, `filter_features`, `filter_features_clear`, `filter_feature_add`, and `filter_feature_del`.

## Control flow
Virtio core creates the root debugfs directory at bus init. Device registration creates a per-device directory and files. Before feature finalization in probe, `virtio_debug_device_filter_features` removes any bits present in `dev->debugfs_filter_features` from the negotiated feature array. Removing a device recursively removes its debugfs directory.

## State and persistence
The root `dentry` is global runtime state. Each device stores debugfs directory and filter feature bitmap in `struct virtio_device`. Debugfs state is not persistent and only matters before or during probe/reprobe.

## Dependencies and integration points
It depends on debugfs, seq_file helpers, virtio feature bitmap helpers, and virtio core. It is compiled only with `CONFIG_VIRTIO_DEBUG`.

## Risks and test signals
Risks include filtering mandatory transport/device features into invalid combinations, concurrent writes while probing, debugfs lifetime during unregister, and invalid feature numbers. Test signals include reading advertised features, adding/deleting/clearing filters, reprobe with a filtered feature, invalid large bit writes returning `-EINVAL`, and debugfs cleanup after device removal.
