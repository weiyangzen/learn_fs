# sources/distributed-fs/ceph-client/drivers/usb/serial/option.c

## Purpose

`option.c` is the Linux USB serial driver for GSM, UMTS, LTE, and other WWAN modem USB interfaces that present vendor-specific serial ports. It exists because generic USB serial support is insufficient for modem workloads: the driver needs multiple receive URBs through the `usb-wwan` layer, modem-control quirks, reserved network-interface filtering, and product-specific endpoint behavior. The file is dominated by a large `option_ids[]` table that maps many vendors, product IDs, interface class triples, and per-interface quirks to a single one-port USB serial driver named `option1`.

## Important APIs, Types, and Functions

The main exported integration is `module_usb_serial_driver(serial_drivers, option_ids)`, registering `option_1port_device` with the USB serial core. `option_1port_device` delegates normal TTY and URB data paths to `usb_wwan_open()`, `usb_wwan_close()`, `usb_wwan_write()`, `usb_wwan_dtr_rts()`, `usb_wwan_tiocmget()`, `usb_wwan_tiocmset()`, `usb_wwan_port_probe()`, and PM callbacks when enabled. Local logic is concentrated in `option_probe()`, `option_attach()`, `option_release()`, and `option_instat_callback()`.

Device flags are encoded in `driver_info`: `RSVD(ifnum)` blocks binding to non-serial interfaces, `NCTRL(ifnum)` disables modem-control setup on interfaces that do not accept it, `NUMEP2` requires exactly two endpoints for devices whose interface numbering varies, and `ZLP` requests zero-length packet behavior in the `usb-wwan` private state. `iface_is_reserved()` and `iface_no_modem_control()` decode those flags only for interface numbers up to `FLAG_IFNUM_MAX`.

## Control Flow

Probe rejects mass-storage interfaces, rejects reserved interfaces, optionally enforces two endpoints, and stashes the matched flags in `usb_set_serial_data()` for attach. Attach allocates `struct usb_wwan_intf_private`, enables `use_send_setup` unless `NCTRL` applies to the current interface, enables `use_zlp` for `ZLP` devices, initializes the suspend spinlock, and replaces the temporary flags pointer with the real private state. Runtime open, close, write, modem-control, and suspend/resume are then handled by the shared `usb-wwan` implementation.

Interrupt-status URBs are handled locally. `option_instat_callback()` decodes CDC-style notification payloads with request type `0xA1` and request `0x20`, updates CTS, DCD, DSR, and RI in `struct usb_wwan_port_private`, and hangs up the tty when DCD drops. Nonfatal interrupt URB statuses are logged, and the URB is resubmitted unless it was stopped or shut down.

## State and Persistence Behavior

There is no file-backed persistence. Static state is the device ID table and the registered `usb_serial_driver`. Runtime state is per USB serial interface through `struct usb_wwan_intf_private` and per port through the `usb-wwan` port private object. The attach path owns the interface private allocation and `option_release()` frees it. Device-specific policy is persistent only as `driver_info` constants compiled into the module.

## Dependencies and Integration Points

The driver depends on the USB core, USB serial core, TTY core, URBs, and the local `usb-wwan` helper. It deliberately coexists with other modem drivers by refusing mass-storage, QMI, NCM, MBIM, ECM, RNDIS, audio, and other reserved interfaces where encoded by `RSVD()` or class/protocol matching. Its device table is also a policy surface for ModemManager and user space because each bound interface becomes a `/dev/ttyUSB*` modem, diagnostic, NMEA, or AT port.

## Risks and Test Signals

The primary risk is incorrect ID-table policy. A wrong `RSVD()` can bind a network or storage interface as serial, while a missing entry can hide an AT, GPS, or diagnostic port. `NCTRL()` mistakes can trigger unsupported control requests, and `NUMEP2` can reject a valid interface if firmware changes descriptors. Interrupt-status parsing assumes the control request payload is present and uses DCD drop for hangup behavior, so modem notification regressions can affect carrier handling.

Good test signals include probing representative devices from the Option, Huawei, Quectel, Telit, ZTE, Sierra, Fibocom, and Qualcomm-style entries; verifying reserved network interfaces remain handled by QMI, MBIM, NCM, ECM, or RNDIS drivers; confirming `use_send_setup` and `use_zlp` are set for flagged interfaces; checking DCD, RI, CTS, and DSR updates through interrupt notifications; and exercising suspend/resume through the `usb-wwan` callbacks.
