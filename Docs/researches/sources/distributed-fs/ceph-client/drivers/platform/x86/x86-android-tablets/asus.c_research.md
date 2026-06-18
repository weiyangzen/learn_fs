# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/asus.c

Purpose: Asus board manifests for x86 Android tablet DSDT fixups. It covers Asus ME176C and TF103C tablets, adding missing charger, fuel gauge, sensors, touchscreen, USB-ID, lid switch, and optional Bluetooth serdev data.

Important APIs and data: exports `asus_me176c_info` and `asus_tf103c_info`. Shared data defines an `intel-int3496` platform device and gpio-keys lid switch software nodes. ME176C instantiates BQ24190/BQ24297 charger, UG3105 fuel gauge, AK09911 compass, KXTJ21009 accelerometer, Goodix touchscreen, and BCM serdev. TF103C instantiates similar charger/fuel-gauge/compass/accelerometer devices plus an Atmel touchscreen with GPIO IRQ.

State and dependencies: static software nodes and `x86_i2c_client_info` arrays are consumed during init by `core.c`. Dependencies include Bay Trail GPIO nodes, shared battery software nodes, charger platform data, I2C adapter paths, PMIC/APIC/GPIO IRQ helpers, serdev helpers, and gpio-keys.

Risks and test signals: board manifests are sensitive to I2C addresses, IRQ polarity, mount matrices, and battery chemistry selection. Tests should verify ME176C and TF103C DMI routes select the right info, all clients bind on expected adapters, lid switch reports `SW_LID`, charger/fuel gauge supply links resolve, and optional serdev binding does not block other devices.
