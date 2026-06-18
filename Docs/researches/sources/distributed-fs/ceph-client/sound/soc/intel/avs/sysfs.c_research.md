# sources/distributed-fs/ceph-client/sound/soc/intel/avs/sysfs.c

Purpose: Exposes AVS firmware version through a device sysfs attribute group.

Important APIs/functions: `fw_version_show()` formats `adev->fw_cfg.fw_version`; `DEVICE_ATTR_RO(fw_version)` declares the read-only attribute; `avs_attr_groups` exports the `avs/fw_version` group.

Control flow: Sysfs read converts the device to `avs_dev`, reads cached firmware version fields, and emits `major.minor.hotfix.build`.

State and persistence: Reads cached firmware config populated elsewhere through IPC. Does not allocate or mutate state.

Dependencies and integration: Depends on `avs.h`, Linux sysfs helpers, and parent device registration using `avs_attr_groups`.

Risks: If firmware config was not populated before sysfs exposure, users may see zeros or stale data. No locking is used around the cached config read; values are expected stable after firmware init.

Test signals: Sysfs presence under the AVS device, expected version after firmware boot, behavior before/after runtime suspend, and read formatting.
