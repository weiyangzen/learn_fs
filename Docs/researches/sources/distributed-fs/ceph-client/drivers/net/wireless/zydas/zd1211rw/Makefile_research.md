# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/Makefile

Purpose: this Makefile defines the kbuild objects that compose the ZD1211RW driver module and attaches optional debug compiler flags. It is the concrete build recipe for the ZyDAS USB wireless driver.

Important APIs, types, and functions: `obj-$(CONFIG_ZD1211RW) += zd1211rw.o` declares the final driver object/module. `zd1211rw-objs` lists the component objects: `zd_chip.o`, `zd_mac.o`, RF frontend implementations `zd_rf_al2230.o`, `zd_rf_rf2959.o`, `zd_rf_al7230b.o`, `zd_rf_uw2453.o`, the common `zd_rf.o`, and USB transport `zd_usb.o`. `ccflags-$(CONFIG_ZD1211RW_DEBUG) := -DDEBUG` enables debug code paths when the debug Kconfig symbol is selected.

Control flow: kbuild combines the listed component objects into `zd1211rw.o` when `CONFIG_ZD1211RW` is `y` or `m`. The top-level ZyDAS Makefile controls whether this directory is entered. Debug flag evaluation happens at compile time and affects all source files compiled under this Makefile.

State and persistence: no runtime state is stored here. Build output depends on `.config` and source object composition. The resulting module/built-in driver owns runtime chip, MAC, RF, firmware, and USB state.

Dependencies and integration points: this file links separate driver responsibilities into one module: chip control, mac80211 integration, RF calibration/frontends, common RF code, and USB transport. It consumes `CONFIG_ZD1211RW` and `CONFIG_ZD1211RW_DEBUG` from the sibling Kconfig.

Risks: omitting one RF object would remove support for devices using that frontend; omitting `zd_usb.o` would break transport; object order can matter if init/exit sections or symbol resolution assumptions change. `ccflags-... :=` applies the debug define within this directory, so accidental broadening or removal changes logging and diagnostics.

Test signals: `CONFIG_ZD1211RW=m` should produce a `zd1211rw.ko` containing all listed component objects. Enabling `CONFIG_ZD1211RW_DEBUG` should show compiler invocations with `-DDEBUG` and produce additional runtime debug messages from the driver.
