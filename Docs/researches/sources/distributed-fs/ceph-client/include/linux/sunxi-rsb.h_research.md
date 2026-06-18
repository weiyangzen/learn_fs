# sources/distributed-fs/ceph-client/include/linux/sunxi-rsb.h

Purpose: declares the Allwinner Reduced Serial Bus client device/driver model and managed regmap creation helper.

Important APIs and types: `struct sunxi_rsb_device` embeds `struct device`, points to the controller, stores IRQ, runtime address, and hardware address. `to_sunxi_rsb_device()`, `sunxi_rsb_device_get_drvdata()`, and `sunxi_rsb_device_set_drvdata()` bridge to driver core data. `struct sunxi_rsb_driver` wraps `device_driver` with probe/remove callbacks. APIs/macros include `sunxi_rsb_driver_register()`, `sunxi_rsb_driver_unregister()`, `module_sunxi_rsb_driver()`, `__devm_regmap_init_sunxi_rsb()`, and `devm_regmap_init_sunxi_rsb()`.

Control flow: an RSB client driver registers a `sunxi_rsb_driver`; matching devices call probe with a `sunxi_rsb_device`; drivers usually create a devm-managed regmap to access the slave registers and unregister through driver core on module exit.

State and persistence: device and driver binding state is managed by driver core; regmap state is devm-managed per device.

Dependencies and integration points: depends on device core, regmap, lockdep wrappers, module driver helpers, and Allwinner RSB controller code.

Risks and test signals: risks include wrong runtime/hardware address mapping, regmap lock class misuse, remove/probe lifetime issues, and IRQ ownership confusion. Test with Allwinner PMIC/peripheral RSB clients, deferred probe, module unload, regmap read/write, and lockdep.
