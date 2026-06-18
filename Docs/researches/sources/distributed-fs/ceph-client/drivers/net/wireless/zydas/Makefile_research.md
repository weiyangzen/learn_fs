# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/Makefile

Purpose: this Makefile connects the ZyDAS vendor directory to the ZD1211RW driver subdirectory in the kernel build. It is build glue only.

Important APIs, types, and functions: the single object rule `obj-$(CONFIG_ZD1211RW) += zd1211rw/` tells kbuild to descend into the `zd1211rw` subdirectory when the driver symbol is built in or as a module.

Control flow: if `CONFIG_ZD1211RW=y`, kbuild descends into `zd1211rw/` for built-in objects. If `CONFIG_ZD1211RW=m`, kbuild builds the subdirectory module. If the symbol is unset, no ZyDAS driver objects are visited from this Makefile.

State and persistence: no runtime state exists. The persistent input is the kernel `.config` value of `CONFIG_ZD1211RW`.

Dependencies and integration points: this file is reached from the parent wireless drivers Makefile. It relies on `zydas/zd1211rw/Makefile` to define the actual module object composition.

Risks: the directory rule must stay aligned with the Kconfig symbol and subdirectory name. A mismatch would produce either missing driver builds or attempts to enter a nonexistent directory.

Test signals: with `CONFIG_ZD1211RW=m`, the build should enter `drivers/net/wireless/zydas/zd1211rw` and emit `zd1211rw.ko`; with the symbol unset, the subdirectory should be skipped.
