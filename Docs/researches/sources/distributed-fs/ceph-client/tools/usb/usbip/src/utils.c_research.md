# sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.c

Purpose: `utils.c` provides the CLI helper for modifying the `usbip-host` driver's `match_busid` sysfs attribute.

Important API: `modify_match_busid(char *busid, int add)` builds `/sys/bus/usb/drivers/usbip-host/match_busid`, formats either `add BUSID` or `del BUSID`, and writes it with `write_sysfs_attribute()`.

Control flow and integration: `usbip bind` calls it before binding to allow the usbip-host driver to match the target device; `usbip unbind` calls it after unbinding to remove the special match.

State and dependencies: it mutates kernel driver matching state and depends on sysfs helper, root privileges, and a loaded usbip-host driver. Risks include command buffer truncation for maximum-length busids because the fixed buffer is `SYSFS_BUS_ID_SIZE + 4`, not checking `snprintf()` for truncation before writing, and no rollback logic in this helper. Test signals are visible match-list changes and successful bind/unbind workflows.
