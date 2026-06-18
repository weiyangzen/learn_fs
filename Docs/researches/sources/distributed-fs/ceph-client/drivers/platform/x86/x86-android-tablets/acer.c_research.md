# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/acer.c

Purpose: Acer board manifests for the x86 Android tablet fixup driver. It describes missing devices and software properties for Acer Iconia One 8 A1-840 and Acer Iconia One 7 B1-750.

Important APIs and data: exports `acer_a1_840_info` and `acer_b1_750_info` as `struct x86_dev_info`. A1-840 instantiates a BQ24297 charger, MPU6515 sensor, FT5416 touchscreen, an `intel-int3496` USB ID platform device, generic LiPo battery software nodes, and a custom init hook that attaches fuel-gauge properties to the existing `chtdc_ti_battery` device. B1-750 instantiates Novatek touchscreen and BMA250E accelerometer with mount matrix and reset/IRQ GPIO properties.

State and dependencies: board data is mostly `__initconst`; A1-840 has global pointers for the fuel-gauge device and software node until exit. Integration depends on Bay Trail GPIO software nodes, shared power-supply metadata, I2C client instantiation, GPIO IRQ helpers, and platform device registration in `core.c`.

Risks and test signals: A1-840 intentionally leaks the software node on exit to avoid dangling `supplied-from` string references in another driver. Tests should verify deferred probing until `chtdc_ti_battery` exists, charger module preloading, GPIO polarity, I2C addresses/adapters, touchscreen reset, and cleanup of device references.
