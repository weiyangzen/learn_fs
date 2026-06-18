# sources/distributed-fs/ceph-client/net/bluetooth/hci_sysfs.c

## Purpose
Provides driver-model/sysfs support for Bluetooth HCI host devices and connection child devices. It registers the global `bluetooth` class, initializes host and link `struct device` objects, exposes a write-only host `reset` attribute, and handles object release.

## APIs, Types, and Functions
`bt_class` is the shared class. `bt_link_release()` frees an `hci_conn`, and `bt_link` names connection devices as type `link`. `hci_conn_init_sysfs()`, `hci_conn_add_sysfs()`, and `hci_conn_del_sysfs()` initialize, register, and unregister per-connection devices. `bt_host_release()` frees or releases an `hci_dev` and drops the module reference taken during initialization. `reset_store()` invokes `hdev->reset` when available. `hci_init_sysfs()`, `bt_sysfs_init()`, and `bt_sysfs_cleanup()` initialize host device objects and register/unregister the class.

## Control Flow, State, and Persistence
Host devices get type `bt_host`, class `bluetooth`, and a module reference before `device_initialize()`. Their lifetime ends through `bt_host_release()`, which chooses `hci_release_dev()` for unregistering devices and `kfree()` otherwise. Connection devices are initialized under their parent HCI device, named as `<hdev-name>:<handle>`, and added only once. Deletion handles both paths: if `device_add()` never succeeded it only calls `put_device()`, otherwise it moves children off the connection device before `device_unregister()`.

The only sysfs attribute is `reset`; writing it does not parse the buffer and simply calls the transport reset callback if present. No persistent data is stored in this file beyond device model references, names, class/type metadata, and module references.

## Dependencies and Integration
Depends on the Linux device model, module reference counting, Bluetooth core `hci_dev`/`hci_conn` conversion helpers, and transport callbacks embedded in `struct hci_dev`. It integrates with the HCI connection lifecycle and the global Bluetooth subsystem init/exit sequence through `bt_sysfs_init()` and `bt_sysfs_cleanup()`.

## Risks and Test Signals
Risks include device lifetime mismatches around failed `device_add()`, use-after-free if connection children are not detached before unregister, reset callback side effects from any sysfs write content, and module reference leaks if `hci_init_sysfs()` is not paired with release. Test signals are sysfs class creation/removal, host device registration and release, failed connection `device_add()` cleanup, child-device reparenting on connection deletion, and reset attribute invocation under a fake transport callback.
