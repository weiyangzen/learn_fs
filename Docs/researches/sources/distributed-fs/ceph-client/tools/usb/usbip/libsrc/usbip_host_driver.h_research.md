# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/usbip_host_driver.h

Purpose: this header exports the physical-host usbip backend.

Important API: `extern struct usbip_host_driver host_driver;` exposes the backend instance consumed by `usbipd`.

Control flow and integration: `usbipd.c` initializes its global `driver` to `&host_driver` unless `--device` is selected. The backend plugs into generic devlist/import logic through `usbip_host_common.h`.

State, dependencies, risks, and tests: the header has no state. It depends on common USB metadata, list support, and the backend abstraction. Risks are minimal, mostly coupling all users to the concrete global backend instance. Test signals are successful daemon build/link and default daemon enumeration of `usbip-host` devices.
