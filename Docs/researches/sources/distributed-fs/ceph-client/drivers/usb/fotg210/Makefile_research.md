# sources/distributed-fs/ceph-client/drivers/usb/fotg210/Makefile

Purpose: defines the object composition for the Faraday FOTG210 dual-role driver.

Important APIs/functions: no runtime API. `obj-$(CONFIG_USB_FOTG210) += fotg210.o`; `fotg210-y` always includes `fotg210-core.o`; optional objects are `fotg210-hcd.o` for host support and `fotg210-udc.o` for peripheral support.

Control flow: kbuild links one composite object whose contents depend on selected role subconfigs.

State and persistence: build-time state only. The selected objects determine which probe/remove calls in `fotg210-core.c` can resolve and execute.

Dependencies and integration: depends on the local Kconfig symbols and the top-level USB driver build system. It integrates core, HCD, and UDC sources into one driver/module.

Risks: if Kconfig permits a role symbol without the matching source object, core references to `fotg210_hcd_*` or `fotg210_udc_*` would fail at link time. If neither role is selected, the core object may build but have limited practical use.

Test signals: build matrix with host only, UDC only, both, built-in, and module configurations.
