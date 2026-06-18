# sources/distributed-fs/ceph-client/drivers/net/can/usb/Makefile

Purpose: Maps USB CAN Kconfig symbols to object files or subdirectories built by Kbuild.

Important APIs, types, and functions: Uses `obj-$(CONFIG_...) += ...` assignments for `usb_8dev.o`, `ems_usb.o`, `esd_usb.o`, `etas_es58x/`, `f81604.o`, `gs_usb.o`, `kvaser_usb/`, `mcba_usb.o`, `nct6694_canfd.o`, `peak_usb/`, and `ucan.o`.

Control flow: Kbuild evaluates each symbol and includes the corresponding object or subdirectory as built-in or module.

State and persistence behavior: No runtime state; build outputs are controlled by kernel configuration.

Dependencies and integration points: Paired with `usb/Kconfig`; subdirectory entries rely on nested Kbuild files. Parent CAN build includes this directory when USB CAN support is in scope.

Risks: Symbol/object mismatches break builds or omit selected drivers. Subdirectory entries require valid nested Makefiles.

Test signals: Build each USB CAN symbol as module and built-in, run `make M=drivers/net/can/usb`, and compare generated modules with Kconfig help text.
