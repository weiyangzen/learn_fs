# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_devlink.c

Purpose: exposes Kvaser USB device metadata and per-channel physical ports through devlink.

Important APIs/types/functions: `kvaser_usb_devlink_info_get` publishes serial number, running firmware version, fixed board revision, and fixed board ID/EAN when present. `kvaser_usb_devlink_ops` installs `.info_get`. `kvaser_usb_devlink_port_register` sets physical port attributes and links a netdev to its `devlink_port`; `kvaser_usb_devlink_port_unregister` removes it.

Control flow: the core allocates devlink before probe initialization and registers it after all CAN channels are created. During each channel init, this file registers a devlink physical port with `phys.port_number = channel` and calls `SET_NETDEV_DEVLINK_PORT`. `devlink info` calls read metadata previously filled by Leaf/Hydra card and software-info discovery.

State and persistence behavior: no independent state is allocated here beyond `devlink_port` embedded in `kvaser_usb_net_priv`. Reported values come from in-memory probe-time fields (`serial_number`, `fw_version`, `hw_revision`, `ean`). No persistent data is written.

Dependencies/integration points: depends on netdev and devlink APIs and the shared Kvaser structs. It is integrated by `kvaser_usb_core.c` during channel registration/removal and by the module-level `devlink_alloc` call.

Risks: metadata is omitted when probe did not fill a value or the EAN MSB does not match the expected Kvaser prefix. Buffer formatting must remain large enough for decimal serials and concatenated EAN strings. Port unregister must mirror successful register to avoid devlink resource leaks.

Test signals: `devlink info` should show serial, firmware, board revision, and board ID for devices that report them; `devlink port` should show one physical port per CAN channel and removal should clean ports on unplug.
