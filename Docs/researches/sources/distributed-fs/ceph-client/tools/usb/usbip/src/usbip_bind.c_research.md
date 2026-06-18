# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_bind.c

Purpose: `usbip_bind.c` implements `usbip bind`, preparing a local physical USB device for export by rebinding it to the `usbip-host` kernel driver.

Important functions: `bind_usbip()` writes the busid to `/sys/bus/usb/drivers/usbip-host/bind`. `unbind_other()` uses libudev to locate the device, skips hubs, detects if already bound to `usbip-host`, and writes to the current driver's `unbind` attribute when needed. `bind_device()` validates existence, rejects devices already under `vhci_hcd` to avoid loops, updates `match_busid` with `modify_match_busid(add=1)`, and binds to usbip-host. `usbip_bind()` parses `-b`.

Control flow and integration: binding is a two-step kernel-driver protocol: first add the busid to usbip-host's match table, then bind the driver. If bind fails after match update, it removes the busid again.

State and dependencies: it mutates sysfs driver binding state and the usbip-host match list. It depends on root privileges, libudev, `usbip-host.ko`, and writable sysfs attributes. Risks include unbinding active class drivers unexpectedly, hub detection relying on `bDeviceClass == "09"`, not unrefing some libudev objects on early returns, and races with hotplug. Test signals are `usbip bind -b BUSID`, driver showing as `usbip-host`, and remote `usbip list -r` exposing the device after daemon start.
