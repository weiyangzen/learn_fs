# Research: sources/distributed-fs/ceph-client/drivers/usb/common/Makefile

Purpose: maps common USB Kconfig symbols to kernel objects. It builds `usb-common.o` from `common.o` plus optional `debug.o` and `led.o`, and builds separate objects for GPIO connector detection, OTG FSM, and ULPI bus.

Important build rules: `obj-$(CONFIG_USB_COMMON) += usb-common.o`; `usb-common-y += common.o`; `usb-common-$(CONFIG_TRACING) += debug.o`; `usb-common-$(CONFIG_USB_LED_TRIG) += led.o`; `obj-$(CONFIG_USB_CONN_GPIO) += usb-conn-gpio.o`; `obj-$(CONFIG_USB_OTG_FSM) += usb-otg-fsm.o`; `obj-$(CONFIG_USB_ULPI_BUS) += ulpi.o`.

Control flow and state: build-only file. The main state is the object composition of `usb-common.o`: tracing controls whether `usb_decode_ctrl` is linked, and LED trigger support controls whether `ledtrig_usb_init/exit` do real registration.

Dependencies and integration points: ties Kconfig to objects consumed by host, gadget, PHY, and OTG code. `debug.o` is compiled into usb-common for trace formatting, not as an independent module. `usb-otg-fsm.o` is built from a core Kconfig symbol even though the source lives in common.

Risks: moving objects between `usb-common-y` and separate `obj-*` lines changes symbol export/module loading behavior. Missing `debug.o` under tracing would break tracepoints that call `usb_decode_ctrl`. Missing `led.o` when `USB_LED_TRIG` is enabled would leave declared hooks unresolved.

Test signals: run kernel builds with `CONFIG_TRACING=y/n`, `CONFIG_USB_LED_TRIG=y`, `CONFIG_USB_COMMON=m/y`, and module builds for `ulpi`, `usb-conn-gpio`, and `usb-otg-fsm`.
