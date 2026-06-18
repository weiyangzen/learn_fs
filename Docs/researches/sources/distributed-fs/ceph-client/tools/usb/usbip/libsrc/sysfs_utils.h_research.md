# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/sysfs_utils.h

Purpose: `sysfs_utils.h` declares the shared sysfs attribute write helper used by usbip library and command code.

Important API: `write_sysfs_attribute()` takes an attribute path, buffer pointer, and byte length, returning `0` on accepted write and `-1` on open/write failure.

Control flow and integration: the header is included by host common code, VHCI code, `usbip_bind`, `usbip_unbind`, and `utils.c` to modify kernel driver state through sysfs.

State, dependencies, risks, and tests: the header has no state. It relies on including files to provide `size_t` through other headers, which can be fragile if included standalone. Test signals are clean compilation in all current include contexts and successful sysfs operations through callers.
