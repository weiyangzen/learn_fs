# sources/distributed-fs/ceph-client/tools/usb/usbip/vudc/vudc_server_example.sh

Purpose: this example script demonstrates creating a ConfigFS USB gadget, binding it to `usbip-vudc`, and exporting it with `usbipd --device`.

Important commands and variables: `CONFIGFS_MOUNT_POINT`, `GADGET_NAME`, `ID_VENDOR`, and `ID_PRODUCT` define gadget placement and identity. The script creates `functions/acm.ser0`, `configs/c.1`, symlinks the ACM function into the configuration, writes vendor/product IDs, loads `usbip-vudc` if needed, binds by writing `usbip-vudc.0` to `UDC`, and starts `usbipd --device` in the background.

Control flow and integration: `set -e` stops on errors. The comments document client-side `modprobe usbip-vhci`, remote list, and attach commands. It exercises the same device backend implemented by `usbip_device_driver.c`.

State and dependencies: it creates persistent ConfigFS gadget directories and starts a background daemon. It depends on root privileges, mounted configfs, ACM gadget support, `usbip-vudc`, and installed usbip tools. Risks include leaving gadget/daemon state behind, hard-coded gadget name and UDC instance, no cleanup trap, and a typo in comments. Test signals are `usbip list -r SERVER` showing `usbip-vudc.0` and `usbip attach -r SERVER -d usbip-vudc.0` creating a client-side serial device.
