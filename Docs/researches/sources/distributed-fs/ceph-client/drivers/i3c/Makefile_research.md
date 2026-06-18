# sources/distributed-fs/ceph-client/drivers/i3c/Makefile

Purpose: Kbuild entry for the I3C core and master-driver subdirectory.

Important APIs/types/functions: `i3c-y := device.o master.o` aggregates the public device API and master/bus core into `i3c.o`. `obj-$(CONFIG_I3C) += i3c.o` and `obj-$(CONFIG_I3C) += master/` build the core and descend into master drivers.

Control flow: Kbuild includes these objects only when `CONFIG_I3C` is enabled. Runtime control flow is in `device.c` and `master.c`.

State and persistence: Build output is either built-in I3C core code or `i3c.ko`.

Dependencies/integration: Kbuild object aggregation and `drivers/i3c/master/Makefile`.

Risks: New core files must be added to `i3c-y`; missing entries cause unresolved symbols or absent APIs.

Test signals: `make drivers/i3c/` should build `device.o`, `master.o`, and selected master drivers for built-in and module configs.
