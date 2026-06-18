# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.c

## Purpose
`hclgevf_devlink.c` provides devlink support for the HNS3 VF driver. It registers a devlink instance, reports running firmware version, and implements devlink reload with `DEVLINK_RELOAD_ACTION_DRIVER_REINIT` by driving the VF NIC client down/uninit and init/up notification sequence.

## Important APIs And Functions
- `hclgevf_devlink_info_get()` formats `hdev->fw_version` as four dotted bytes using HNAE3 firmware version masks and publishes it as `DEVLINK_INFO_VERSION_GENERIC_FW`.
- `hclgevf_devlink_reload_down()` rejects reload during reset handling, supports only `DRIVER_REINIT`, takes `rtnl_lock()`, sends `HNAE3_DOWN_CLIENT` then `HNAE3_UNINIT_CLIENT` reset notifications, and unwinds the lock on errors.
- `hclgevf_devlink_reload_up()` sets `*actions_performed = BIT(action)`, supports only `DRIVER_REINIT`, takes `rtnl_lock()`, sends `HNAE3_INIT_CLIENT` then `HNAE3_UP_CLIENT`, and returns unsupported for other actions.
- `hclgevf_devlink_ops` wires info and reload callbacks and advertises the reload action bit.
- `hclgevf_devlink_init()` allocates a devlink with private storage, stores `hdev`, saves the devlink pointer on the VF device, and registers it.
- `hclgevf_devlink_uninit()` unregisters and frees the devlink.

## Control Flow
VF probe calls `hclgevf_devlink_init()` after the VF device object and PCI device exist. Userspace `devlink dev info` calls `info_get`. Userspace reload calls first enter `reload_down`; if no reset is in progress and the action is driver reinit, the VF client is quiesced and uninitialized under RTNL. `reload_up` then initializes and brings the client up, also under RTNL. Remove calls `hclgevf_devlink_uninit()`.

## State And Persistence Behavior
The file stores the devlink pointer in `hdev->devlink` and stores a back pointer to `hdev` in `struct hclgevf_devlink_priv`. It does not persist config; reload operates through client reset-notify callbacks that tear down and rebuild VF NIC runtime state. Firmware version is read from cached `hdev->fw_version`.

## Dependencies And Integration Points
It depends on Linux devlink and RTNL APIs, `hclgevf_main.h` through the header, HNAE3 firmware version masks, VF reset state bit `HCLGEVF_STATE_RST_HANDLING`, `hdev->nic_client->ops->reset_notify`, and the VF probe/remove lifecycle in `hclgevf_main.c`.

## Risks And Edge Cases
- `reload_up()` sets `actions_performed` before action validation, so unsupported actions still briefly receive a bit assignment before returning `-EOPNOTSUPP`.
- Reload sequencing depends on NIC client callbacks being valid and correctly idempotent under RTNL.
- Reload during asynchronous reset is rejected, but races around reset state changes require broader VF reset synchronization.
- `devlink_register()` return value is not checked in this kernel API form; behavior depends on the API version used by the source tree.

## Test Signals
Run `devlink dev info` for VF firmware string formatting, `devlink dev reload action driver_reinit`, reload while reset is active, unsupported reload actions, VF traffic before/after reload, probe failure injection for `devlink_alloc`, and remove/unregister with devlink userspace watchers active.
