# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.c

## Purpose

`hclge_devlink.c` registers minimal devlink support for the HNS3 PF driver. It exposes running firmware version information and supports `DEVLINK_RELOAD_ACTION_DRIVER_REINIT`, mapping devlink reload to the driver's NIC client down/uninit and init/up notification sequence.

## Important APIs And Functions

`hclge_devlink_init()` allocates a devlink instance with `hclge_devlink_ops`, stores `hdev` in private devlink data, assigns `hdev->devlink`, and registers the instance. `hclge_devlink_uninit()` unregisters and frees it.

`hclge_devlink_info_get()` formats `hdev->fw_version` into a four-component string and publishes it as `DEVLINK_INFO_VERSION_GENERIC_FW`. For device revisions newer than V2, it calls `hclge_devlink_scc_info_get()`, which queries SCC firmware version with `hclge_query_scc_version()` and publishes it as `"fw.scc"`.

Reload callbacks are `hclge_devlink_reload_down()` and `hclge_devlink_reload_up()`. Both support only `DEVLINK_RELOAD_ACTION_DRIVER_REINIT`; unsupported actions return `-EOPNOTSUPP`.

## Control Flow

Reload down first rejects operation while `HCLGE_STATE_RST_HANDLING` is set. For driver reinit it takes `rtnl_lock()`, calls the NIC client's `reset_notify()` with `HNAE3_DOWN_CLIENT`, then `HNAE3_UNINIT_CLIENT`, and releases RTNL. Reload up sets `*actions_performed = BIT(action)`, takes RTNL, sends `HNAE3_INIT_CLIENT`, then `HNAE3_UP_CLIENT`, and releases RTNL. Errors short-circuit after unlocking.

## State And Persistence Behavior

Devlink private state is just `struct hclge_devlink_priv { struct hclge_dev *hdev; }`. Runtime effects are on the NIC client and netdev lifecycle through reset notifications. Firmware version strings are read-only snapshots. The devlink pointer persists in `hdev->devlink` until uninit.

## Dependencies And Integration Points

The file depends on Linux devlink, `hclge_devlink.h`, `hclge_main.h` through that header, firmware version macros, `hclge_query_scc_version()`, PCI device revision, `hdev->nic_client`, and HNAE3 reset notification enums. Probe and remove in `hclge_main.c` call the init/uninit functions.

## Risks

`hclge_devlink_uninit()` assumes `hdev->devlink` is valid. Reload paths assume `hdev->nic_client` and its reset callbacks are present and safe under RTNL. The reload implementation handles only client notifications; it does not re-run full hardware probe, so expectations must match devlink's driver-reinit semantics. Formatting uses `%lu` for extracted fields from a `u32`, relying on macro return typing.

## Test Signals

Use `devlink dev info` to verify generic firmware and SCC version fields. Use `devlink dev reload ... action driver_reinit` and confirm down/uninit/init/up notifications, no reload during reset handling, correct `actions_performed`, and no RTNL lock imbalance on callback failure.
