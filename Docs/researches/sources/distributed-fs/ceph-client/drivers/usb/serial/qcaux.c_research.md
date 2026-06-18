# sources/distributed-fs/ceph-client/drivers/usb/serial/qcaux.c

## Purpose

`qcaux.c` is a minimal USB serial driver for auxiliary Qualcomm DM/QCDM-capable serial ports on older CDMA and EVDO devices. These devices commonly expose a normal CDC ACM port for AT commands or PPP plus secondary vendor-specific interfaces that can be used for diagnostics, status, signal strength, NMEA, WMC, or DIAG traffic. This driver claims only the auxiliary serial-style interfaces listed in its ID table.

## Important APIs, Types, and Functions

The driver has one static `id_table[]`, one `usb_serial_driver` named `qcaux`, and the `module_usb_serial_driver(serial_drivers, id_table)` registration. It sets `.num_ports = 1` and relies on USB serial generic behavior for open, close, read, write, and TTY integration. There are no local callbacks beyond module registration.

## Control Flow

Runtime control flow is handled by the USB serial core. Matching occurs through `USB_DEVICE_AND_INTERFACE_INFO()` or `USB_VENDOR_AND_INTERFACE_INFO()` entries for UTStarcom/Pantech/Curitel, CMOTECH, LG, Sanyo, Samsung, and a small number of generic/vendor-specific interfaces. Once matched, the generic one-port USB serial path binds the interface and exposes a ttyUSB device.

## State and Persistence Behavior

There is no private driver state and no persistence. Static state is the ID table and the driver descriptor. Per-port buffers and TTY state are owned by the USB serial core.

## Dependencies and Integration Points

The file depends only on kernel, TTY, module, USB, and USB serial headers. It integrates with user space by creating serial nodes suitable for diagnostic protocols such as libqcdm while leaving primary CDC ACM modem ports to `cdc-acm`. The comments explicitly say devices without a CDC ACM AT-command port are likely better handled by `option`.

## Risks and Test Signals

Risk is almost entirely ID-table scope. Binding the wrong interface can steal a port from CDC ACM, a network driver, or another modem driver; missing an auxiliary interface prevents diagnostic access. Test signals include module autoload for listed devices, generic USB serial data transfer on QCDM/NMEA/WMC/DIAG interfaces, coexistence with CDC ACM on primary modem ports, and confirming devices without CDC ACM are not moved here from `option` without a reason.
