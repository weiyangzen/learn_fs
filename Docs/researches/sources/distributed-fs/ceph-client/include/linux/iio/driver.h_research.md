# `sources/distributed-fs/ceph-client/include/linux/iio/driver.h`

Purpose: provider-side in-kernel IIO mapping registration API that connects IIO channels to named in-kernel consumers.

Important APIs/types/functions: `iio_map_array_register`, `iio_map_array_unregister`, and `devm_iio_map_array_register`.

Control flow and state: providers register arrays of `iio_map` entries against an `iio_dev`; consumers later resolve channels through the mapping. Devm variant registers an automatic unregister callback tied to the provider device lifetime.

Dependencies/integration: depends on IIO provider devices, `struct iio_map`, and device-managed resource cleanup.

Risks: map arrays must remain valid for the registration lifetime; unregister must match successful register; duplicate or stale consumer names break channel lookup; devm cleanup order matters during provider removal.

Test signals: provider register/unregister, consumer `iio_channel_get` resolution, duplicate/missing map behavior, devm cleanup on probe failure/remove, and use-after-free checks for map storage.
