# sources/distributed-fs/ceph-client/include/linux/wwan.h

## Purpose
Defines the kernel WWAN core interface for modem control ports and data-link netdevices. The header lets transport drivers expose modem protocols as character devices, feed received control data into the core, control TX flow, and register network link operations for WWAN data devices.

## Important APIs, Types, and Functions
`enum wwan_port_type` classifies control protocols such as AT, MBIM, QMI, QCDM, Firehose, XMMRPC, Fastboot, ADB, MIPC, and NMEA. `struct wwan_port_ops` supplies mandatory `start`, `stop`, and nonblocking `tx` callbacks plus optional `tx_blocking` and `tx_poll`. `struct wwan_port_caps` describes TX fragment sizing and headroom. Port lifecycle and data APIs are `wwan_create_port()`, `wwan_remove_port()`, `wwan_port_rx()`, `wwan_port_txoff()`, `wwan_port_txon()`, and `wwan_port_get_drvdata()`. Network data-plane integration uses `struct wwan_netdev_priv`, `wwan_netdev_drvpriv()`, `WWAN_NO_DEFAULT_LINK`, `struct wwan_ops`, `wwan_register_ops()`, and `wwan_unregister_ops()`. Debugfs hooks are present when `CONFIG_WWAN_DEBUGFS` is enabled.

## Control Flow
A modem transport driver creates one or more ports under a shared parent device; the WWAN core exposes them as character devices associated with a virtual WWAN device. Userspace opens a port, which triggers `start`, writes data through `tx` or `tx_blocking`, and receives inbound `sk_buff` payloads passed to `wwan_port_rx()`. Flow-control transitions use `wwan_port_txoff()` and `wwan_port_txon()` to affect write/poll readiness. Data netdevices are installed by registering `wwan_ops`, after which rtnetlink-driven link creation calls `newlink` and deletion calls `dellink`.

## State and Persistence
Persistent state lives in opaque `struct wwan_port` instances, character devices, netdevices, and driver-private data stored by the core. `struct wwan_netdev_priv` persists the WWAN link id and embeds driver-private bytes at the end of netdev private storage. Debugfs directory references persist until released with `wwan_put_debugfs_dir()`.

## Dependencies and Integration Points
Depends on poll, skbuff, netdevice, device model, rtnetlink extack, debugfs, and driver data helpers. Integrates with USB, PCIe, MHI, and other modem transports, userspace modem managers, MBIM/QMI/AT protocol stacks, and Linux netdevice link management.

## Risks
Drivers must balance create/remove and register/unregister calls, honor nonblocking TX semantics, preserve SKB ownership expectations, and keep parent-device identity stable so ports are grouped correctly. Flow-control bugs can wedge userspace writers or lose wakeups. `WWAN_NO_DEFAULT_LINK` changes netdevice creation behavior and must match device expectations. Debugfs stubs return `ERR_PTR(-ENODEV)`, so consumers must not blindly dereference.

## Test Signals
Signals include WWAN core build tests, modem-manager port discovery, character device open/read/write/poll tests, TX flow-control tests, netlink newlink/dellink coverage, driver unbind cleanup, and debugfs enabled/disabled build coverage.
