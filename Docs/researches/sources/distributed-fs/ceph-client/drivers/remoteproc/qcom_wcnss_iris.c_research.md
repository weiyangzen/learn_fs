# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss_iris.c

Purpose: implements the IRIS RF child helper used by the WCNSS driver. It discovers an `iris` child node, creates a device for it, selects WCN3620/WCN3660/WCN3680 regulator requirements, acquires the XO clock, programs regulator voltage/load constraints, and exposes enable/disable operations to power the RF block during WCNSS boot.

Important APIs/types/functions: `struct qcom_iris` embeds a `struct device` and stores `xo_clk`, regulator bulk array, and count. `struct iris_data` supplies per-compatible regulator tables and whether the WCNSS PMU should use a 48 MHz XO. Exported helpers are `qcom_iris_probe()`, `qcom_iris_remove()`, `qcom_iris_enable()`, and `qcom_iris_disable()`. `qcom_iris_release()` drops the OF node and frees the allocation.

Control flow: `qcom_iris_probe()` finds the `iris` child, allocates and initializes a child device, adds it to the device hierarchy, matches compatible data, acquires the `xo` clock, obtains regulators in bulk, applies voltage/load constraints, and returns the helper plus `use_48mhz_xo` to the parent. Enable turns on regulators then prepares/enables XO, unwinding regulators on clock failure. Disable reverses clock and regulators. Remove deletes and puts the child device.

State and persistence: state is the child device lifetime, regulator constraints, enabled regulator/clock state during boot, and the boolean XO mode returned to WCNSS. There is no persistent storage.

Dependencies and integration: depends on OF child matching, platform device-style `struct device` lifecycle, clk, regulator bulk APIs, and the local `qcom_wcnss.h` regulator descriptor. It is not an independent platform driver; the parent WCNSS driver explicitly probes and removes it.

Risks and test signals: manual `device_initialize()`/`device_add()` ownership requires balanced `device_del()`/`put_device()` on all errors and remove. Regulator voltage/load return values are ignored after acquisition. Test missing child node, unknown compatible, clock probe deferral, regulator failures, enable clock failure unwind, repeated enable/disable through WCNSS start failures, and node reference release.
