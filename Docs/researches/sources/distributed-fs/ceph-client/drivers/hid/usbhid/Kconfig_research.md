# sources/distributed-fs/ceph-client/drivers/hid/usbhid/Kconfig

Purpose: build configuration for USB HID transport, optional hiddev/PID support, and legacy boot-protocol keyboard/mouse drivers.

Important symbols: `USB_HID` is the generic USB HID transport and defaults to yes when USB and HID are present. `HID_PID` enables PID force feedback support. `USB_HIDDEV` enables `/dev/usb/hiddevX`. `USB_KBD` and `USB_MOUSE` are expert boot-protocol alternatives when generic USB HID is not built in.

Control flow: Kconfig choices decide whether `usbhid`, `hiddev`, `hid-pidff`, `usbkbd`, and `usbmouse` objects are compiled.

State and persistence: no runtime state; it shapes kernel configuration.

Dependencies and integration: depends on USB, HID, and INPUT for boot-protocol input devices.

Risks: boot-protocol drivers are intentionally discouraged because they bypass generic HID functionality. `USB_HIDDEV` depends on generic USB HID.

Test signals: config matrix builds and runtime module loading for generic USB HID, hiddev, PID, usbkbd, and usbmouse.
