# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of.c

Purpose: device-tree integration for the I2C core. It converts OF child nodes into `i2c_board_info`, instantiates clients when adapters appear, performs OF and sysfs-compatible matching, and handles dynamic OF node add/remove notifications.

Important APIs: `of_i2c_get_board_info()` parses a node into client type, address, flags, fwnode, host-notify, wake, 10-bit, and own-slave settings. `of_i2c_register_devices()` walks adapter children or an `i2c-bus` subnode. `i2c_of_match_device()` combines normal `of_match_device()` with sysfs-created device-name matching. `i2c_of_notifier` handles `CONFIG_OF_DYNAMIC`.

Control flow: adapter registration calls `of_i2c_register_devices()`, which sets `OF_POPULATED`, creates each client through `i2c_new_client_device()`, and clears the flag on failure. Dynamic add finds the parent adapter, marks the new node populated, clears `FWNODE_FLAG_NOT_DEVICE` for fw_devlink, and registers the client. Dynamic remove finds the client by node and unregisters it.

State and persistence: OF node flags record population state; client devices hold fwnode references until unregister. Dynamic status is reflected in kernel device model state, not persistent storage.

Dependencies and integration: depends on OF core, `dt-bindings/i2c/i2c.h` address flags, sysfs name matching, and the core client creation/unregistration APIs.

Risks: malformed `reg` or compatible aliases prevent registration. Duplicate population flags suppress devices. Sysfs compatibility matching is looser than true OF matching and can bind by full compatible or vendor-stripped name. Dynamic remove relies on node-to-client lookup and reference balancing.

Test signals: DT client enumeration, ten-bit and own-slave address flags, `host-notify` and `wakeup-source` properties, overlays adding/removing I2C children, and sysfs-created clients matching OF tables.
