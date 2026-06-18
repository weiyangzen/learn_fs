# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.c

Purpose: `usbip_common.c` provides shared logging controls, USB speed/status formatting, libudev sysfs readers, and usb.ids name formatting for usbip tools.

Important APIs and functions: global `usbip_use_syslog`, `usbip_use_stderr`, and `usbip_use_debug` drive logging macros from the header. `usbip_status_string()`, `usbip_speed_string()`, and `usbip_op_common_status_string()` format kernel/protocol statuses. `read_attr_value()` and `read_attr_speed()` read sysfs attributes through libudev. `read_usb_device()` fills `struct usbip_usb_device`; `read_usb_interface()` fills `struct usbip_usb_interface`. `usbip_names_*()` wrap `names.c` and format product/class strings.

Control flow and integration: host and vHCI driver discovery calls `read_usb_device()` on udev devices; listing and daemon replies use the packed device/interface structs over the network. Debug dump helpers format the same structs for trace output.

State and dependencies: it depends on the global `udev_context` defined in `vhci_driver.c` and reused by host common code, libudev sysattrs, Linux USB speed constants, and usb.ids parser globals. Risks include a global udev context shared across independent subsystems, benign missing attributes being folded into zero values, unchecked `sscanf(name, "%u-%u")` assumptions, and names parser lifecycle issues. Test signals are accurate list/port output, successful remote devlist serialization, and stable behavior when devices are unconfigured after binding to `usbip-host`.
