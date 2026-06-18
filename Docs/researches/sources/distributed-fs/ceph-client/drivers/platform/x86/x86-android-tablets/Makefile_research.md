# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Makefile

Purpose: Kbuild composition for x86 Android tablet support. It builds `vexia_atla10_ec.o` and a composite `x86-android-tablets.o` when `CONFIG_X86_ANDROID_TABLETS` is enabled.

Important APIs and control flow: the composite object includes `core.o`, `dmi.o`, `shared-psy-info.o`, and board files `acer.o`, `asus.o`, `lenovo.o`, and `other.o`.

State and dependencies: no runtime state. Object composition binds the central DMI/core machinery with per-vendor `x86_dev_info` records and shared power-supply software-node data.

Risks and test signals: missing a board object would leave extern declarations unresolved or DMI entries without data. Build tests should verify both built-in and module configurations and confirm `MODULE_DEVICE_TABLE(dmi, x86_android_tablet_ids)` is present in the composite.
