# sources/distributed-fs/ceph-client/drivers/greybus/Makefile

Purpose: Kbuild manifest for Greybus core and host-controller modules.

Important targets: `greybus-y` aggregates core, debugfs, host device, manifest, module, interface, bundle, connection, control, SVC, watchdog, and operation objects. `obj-$(CONFIG_GREYBUS)` builds `greybus.o`; `obj-$(CONFIG_GREYBUS_BEAGLEPLAY)` builds `gb-beagleplay.o`; `gb-es2-y := es2.o` and `obj-$(CONFIG_GREYBUS_ES2)` builds the ES2 module. `ccflags-y += -I$(src)` supports local trace event includes.

Control flow: no runtime flow; build composition only.

State and persistence: no state.

Dependencies and integration: maps Greybus Kconfig symbols to core and transport objects.

Risks: object ordering matters for built-in initialization dependencies. New Greybus core files must be added to `greybus-y` or they will not link.

Test signals: successful module builds and trace include resolution.
