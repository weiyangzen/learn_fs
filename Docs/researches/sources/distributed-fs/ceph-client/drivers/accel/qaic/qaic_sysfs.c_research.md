# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_sysfs.c

Purpose: exposes per-DBC state under the DRM accel device sysfs hierarchy. It creates one read-only attribute per DBC showing the numeric current `enum dbc_states` value and emits uevents when state changes.

Important APIs and types: exported functions are `qaic_sysfs_init`, `qaic_sysfs_remove`, and `set_dbc_state`. The file uses a small attribute wrapper containing a `device_attribute`, DBC id, and `qaic_drm_device` pointer.

Control flow: init allocates a DRM-managed attribute array sized to `qdev->num_dbc`, names entries `dbcN_state`, initializes sysfs attributes, and calls `sysfs_create_file`. Remove deletes each created file and frees the array. `dbc_state_show` resolves the DRM minor back to `qaic_device` and prints the numeric state. `set_dbc_state` bounds-checks the DBC and enum, skips unchanged values, updates state, and emits a `KOBJ_CHANGE` uevent with `DBC_ID` and `DBC_STATE`.

State and persistence: the authoritative state is `qdev->dbc[i].state`; sysfs attribute storage hangs from `qddev->sysfs_attrs`. State lasts for the DRM device lifetime and is reset by driver state transitions.

Dependencies and integration: uses sysfs, DRM managed allocation, DRM minor drvdata, and kobject uevents. It is used by `qaic_drv.c`, `qaic_control.c`, and `qaic_ssr.c` to surface activation, deactivation, and SSR transitions.

Risks and test signals: test partial sysfs creation unwind, removal during reads, invalid DBC ids, invalid states, and state transitions through activation, deactivation, SSR, and device removal.
