# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_attach.c

Purpose: `usbip_attach.c` implements `usbip attach`, connecting to a remote `usbipd`, requesting a device import, and attaching the returned connection to a local VHCI port.

Important functions: `record_connection()` creates `/var/run/vhci_hcd` and writes `host port busid` into `portN`. `import_device()` opens the local VHCI driver, finds a compatible free port, and writes the socket/devid/speed to VHCI attach, retrying on `EBUSY`. `query_import_device()` sends `OP_REQ_IMPORT`, sends the busid request, validates the `OP_REP_IMPORT` reply, and passes device metadata to `import_device()`. `attach_device()` performs TCP connect, import query, socket close, and state-file recording. `usbip_attach()` parses `-r`, `-b`, and `-d`.

Control flow and integration: the remote server takes ownership of the connection by receiving the socket fd in its kernel driver, while the local client passes the connected socket to `vhci_hcd`. `-d` is treated like `-b` for vUDC busids.

State and dependencies: persistent state is `/var/run/vhci_hcd/portN`; kernel state changes through VHCI sysfs. Dependencies are `vhci_hcd`, remote `usbipd`, TCP, and protocol helpers. Risks include leaking the socket on some failure paths, closing the fd after attach assuming the kernel duplicated/owns it, no validation of host/port string length beyond fixed buffer, and no rollback if `record_connection()` fails after kernel attach. Test signals are `usbip attach -r HOST -b BUSID`, new imported device under `usbip port`, and matching state file.
