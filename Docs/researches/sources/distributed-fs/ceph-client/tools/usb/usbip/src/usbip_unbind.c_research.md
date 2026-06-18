# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_unbind.c

Purpose: `usbip_unbind.c` implements `usbip unbind`, reversing `usbip bind` for a device currently attached to `usbip-host`.

Important functions: `unbind_device()` validates that the busid exists and that its current driver is `usbip-host`, writes the busid to the driver's `unbind` attribute, removes it from `match_busid` with `modify_match_busid(add=0)`, then writes to the driver's `rebind` attribute to trigger normal probing. `usbip_unbind()` parses `-b`.

Control flow and integration: sysfs driver operations are sequenced as unbind, update match list, rebind. The command relies on usbip-host-specific attributes and shared sysfs writing.

State and dependencies: it mutates kernel driver binding and match-list state. It depends on root privileges, libudev, and loaded `usbip-host`. Risks include no rollback if match removal or rebind fails after unbinding, unref on potentially NULL `dev` in error paths, and no protection from concurrent daemon export. Test signals are `usbip unbind -b BUSID`, device no longer bound to usbip-host, and the original or another normal driver reprobing.
