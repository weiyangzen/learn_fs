# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_common.h

Purpose: `usbip_common.h` defines usbip-wide constants, logging macros, wire-visible USB metadata structs, and shared helper prototypes.

Important types and constants: it defines default `USBIDS_FILE`, `VHCI_STATE_PATH`, module names (`usbip-core`, `usbip-host`, `usbip-vudc`, `vhci_hcd`), sysfs constants, protocol status codes, and `struct usbip_usb_device`/`struct usbip_usb_interface` with packed layout. Logging macros `err`, `info`, and `dbg` route to syslog and/or stderr.

Control flow and integration: the packed structs are used both for sysfs discovery and network PDUs, so layout compatibility matters. The macros are included by library, CLI, and daemon code, making global logging flags the process-wide output control.

State, dependencies, risks, and tests: it depends on libudev and Linux USB/UAPI headers. Risks include packed structs crossing ABI/protocol boundaries, fixed path/busid sizes, variadic GNU-style macros, and `PROGNAME` redefinition by individual C files. Test signals are compile compatibility, correct byte packing in network code, and readable diagnostics under `--debug` and `--log`.
