# sources/distributed-fs/ceph-client/drivers/rtc/Makefile

Purpose: build mapping for the RTC subsystem. It maps Kconfig symbols to core objects, optional interface objects, test objects, and ordered per-driver modules.

Important APIs, types, and functions: `ccflags-$(CONFIG_RTC_DEBUG) := -DDEBUG` enables debug builds. `obj-$(CONFIG_RTC_LIB) += lib.o`, `obj-$(CONFIG_RTC_CLASS) += rtc-core.o`, and `obj-$(CONFIG_RTC_MC146818_LIB) += rtc-mc146818-lib.o` build core libraries. `rtc-core-y := class.o interface.o` is extended by `rtc-core-$(CONFIG_RTC_NVMEM) += nvmem.o`, `rtc-core-$(CONFIG_RTC_INTF_DEV) += dev.o`, `rtc-core-$(CONFIG_RTC_INTF_PROC) += proc.o`, and `rtc-core-$(CONFIG_RTC_INTF_SYSFS) += sysfs.o`. `obj-$(CONFIG_RTC_LIB_KUNIT_TEST) += test_rtc_lib.o` adds tests.

Control flow: Kbuild evaluates each `CONFIG_RTC_*` symbol and links built-in or module objects accordingly. The file keeps the driver list ordered and maps each `RTC_DRV_*` symbol to its `rtc-*.o` object, including I2C, SPI, platform, SoC, MFD, firmware, and EC-backed drivers. `rtc-core.o` is a composite object whose contents change with interface and NVMEM config.

State and persistence: no runtime state. Build artifacts and module availability are determined by this mapping.

Dependencies and integration points: integrates Kconfig symbols with the kernel build system and all source files in `drivers/rtc`. It must stay synchronized with `Kconfig` names and actual `rtc-*.c` filenames.

Risks: a typo in an object mapping silently drops or misbuilds a driver for that config. Composite `rtc-core` contents must match exported symbols expected by drivers and userspace interfaces. The list is ordered, so new entries should preserve maintainability and avoid duplicate object inclusion.

Test signals: build `RTC_CLASS=y`, interface permutations, allmodconfig, randconfig, `RTC_DEBUG=y`, `RTC_LIB_KUNIT_TEST=m/y`, and representative drivers from each bus group. Use `make drivers/rtc/` or full kernel builds to catch missing files and symbol mismatches.
