# sources/distributed-fs/ceph-client/drivers/hid/usbhid/Makefile

Purpose: object composition for USB HID support.

Important entries: `usbhid-y := hid-core.o`; optional `hiddev.o` and `hid-pidff.o` are appended based on `CONFIG_USB_HIDDEV` and `CONFIG_HID_PID`; standalone `usbkbd.o` and `usbmouse.o` follow their boot-protocol configs.

Control flow: kernel build system links selected objects into modules or built-in code according to Kconfig.

State and persistence: no runtime state.

Dependencies and integration: ties the USB HID Kconfig symbols to compiled transport objects.

Risks: optional object ordering is simple, but missing Kconfig dependencies would surface as unresolved symbols.

Test signals: build with optional hiddev/PID enabled and disabled.
