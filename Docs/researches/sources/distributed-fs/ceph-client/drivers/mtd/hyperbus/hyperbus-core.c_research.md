# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hyperbus-core.c

Purpose: common HyperBus-to-MTD framework. It adapts controller-specific HyperBus operations to the MTD map/CFI layer and registers HyperFlash devices.

Important APIs/types/functions: map callbacks `hyperbus_read16()`, `hyperbus_write16()`, `hyperbus_copy_from()`, and `hyperbus_copy_to()` dispatch through `hyperbus_ctlr.ops`. Public exports are `hyperbus_register_device()` and `hyperbus_unregister_device()`.

Control flow: registration validates `hbdev`, child node, controller, and controller device; requires compatible `cypress,hyperflash`; initializes `map_info` with bankwidth 2 and OF node; installs map callbacks for provided controller ops; optionally calibrates once per controller; probes CFI with `do_map_probe("cfi_probe")`; sets parent/OF node; and registers the resulting MTD. Unregister removes MTD and destroys the map.

State and persistence: core runtime state lives in caller-owned `hyperbus_device` and `hyperbus_ctlr`, including `ctlr->calibrated` and `hbdev->mtd`. Persistent data remains in HyperFlash.

Dependencies/integration: MTD map API, CFI probe stack selected by Kconfig, OF compatible validation, and exported symbols for controller modules.

Risks: the calibration condition logs "Calibration failed" when `ops->calibrate()` returns zero, implying controller calibrate callbacks must return nonzero on success; this inverted convention is easy to misuse. Missing controller ops can leave default simple-map accessors, so map fields must be valid.

Test signals: invalid argument rejection, missing compatible, controller with each subset of ops, calibration success/failure, CFI probe failure, MTD register failure cleanup, and unregister idempotence for absent `mtd`.
