# sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.h

Purpose: shared ABI and data model for OCC hwmon common code, status sysfs, and P8/P9 transport frontends.

Important APIs/types: `struct occ_response`, poll response headers, sensor block headers, `struct occ_sensor`, `struct occ_sensors`, dynamic `struct occ_attribute`, and central `struct occ`. Public functions are `occ_active()`, `occ_setup()`, `occ_setup_sysfs()`, `occ_shutdown()`, `occ_shutdown_sysfs()`, `occ_sysfs_poll_done()`, and `occ_update_response()`.

Control flow: frontends embed `struct occ`, fill `bus_dev`, `powr_sample_time_us`, `poll_cmd_data`, and `send_cmd`, then call `occ_setup()`. Common code and sysfs callbacks use the response and parsed sensor pointers stored here.

State and persistence: `struct occ` persists the response buffer, parsed sensor metadata, command callback, update cadence, lock, hwmon/sysfs attribute storage, active/error state, last safe-state time, and previous status fields for notifications.

Dependencies and integration: includes hwmon-sysfs, mutex, and sysfs definitions and forward-declares `struct device`. Transport code depends on this header as the common contract.

Risks: `OCC_RESP_DATA_BYTES` fixes the maximum response buffer; all packed structs must match OCC firmware. `void *data` points into mutable response storage, so consumers must hold or refresh through common locking.

Test signals: compile coverage across common/sysfs/P8/P9 modules, packed layout compatibility with firmware responses, and lifecycle of embedded `struct occ` in both transports.
