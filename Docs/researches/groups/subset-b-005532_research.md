# subset-b-005532 Research

Grouped source research for USB serial drivers under `sources/distributed-fs/ceph-client/drivers/usb/serial`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/option.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/option.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/oti6858.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/oti6858.c

## Purpose

`oti6858.c` implements a one-port USB serial driver for the Ours Technology Inc. OTi-6858 USB-to-serial adapter. It provides TTY serial behavior using a vendor-specific control packet protocol discovered from device observation. Unlike simpler generic adapters, this device reports line status, receive availability, transmit buffer availability, and serial format through interrupt and control transfers, so the driver coordinates bulk reads and writes with interrupt-driven status packets and delayed work.

## Important APIs, Types, and Functions

The module registers `oti6858_device` with one bulk-in, one bulk-out, and one interrupt-in endpoint. `struct oti6858_control_pkt` describes the device status and setup packet: baud divisor, frame format, DTR/RTS control bits, TX status, pin state, and pending RX byte count. `struct oti6858_private` stores a spinlock, latest status packet, read/write in-use flags, delayed setup and write work, pending line setup, transient state, setup completion flag, and the associated port.

Important functions include `oti6858_open()`, `oti6858_close()`, `oti6858_set_termios()`, `oti6858_tiocmget()`, `oti6858_tiocmset()`, `oti6858_read_int_callback()`, `oti6858_read_bulk_callback()`, `oti6858_write()`, `send_data()`, `setup_line()`, and port probe/remove. Vendor control requests are `OTI6858_REQ_GET_STATUS`, `OTI6858_REQ_SET_LINE`, and `OTI6858_REQ_CHECK_TXBUFF`.

## Control Flow

Port probe allocates private state, initializes delayed work, stores the port pointer, and sets a drain delay. Open clears endpoint halts, reads the current control packet or synthesizes default 38400 8N1 DTR/RTS values, saves status and pending setup, submits the interrupt URB, and applies current tty termios. `oti6858_set_termios()` translates data bits, stop bits, parity, and baud rate into the pending setup fields. The actual device update is performed later by `setup_line()`, which reads current status, patches divisor/control/frame fields when they differ from pending setup, sends `SET_LINE`, marks setup done, and restarts interrupt monitoring.

The interrupt callback is the driver scheduler. A valid control packet may trigger delayed setup when observed settings differ from pending settings and no RX data is waiting. It updates modem-status counters on pin changes, submits the bulk read URB when `rx_bytes_avail` is nonzero, or schedules delayed write work when the write FIFO has data and no write URB is active. `send_data()` checks the device transmit buffer with a control request before pulling bytes from `port->write_fifo` and submitting the bulk-out URB. Bulk read pushes received data into the tty flip buffer and returns to interrupt polling; bulk write clears the in-use flag and resumes interrupt polling.

## State and Persistence Behavior

State is entirely runtime and per port. The write FIFO is owned by the USB serial port. The private object tracks last device status, pending serial settings, transient setup retries, and in-flight URB flags. Delayed work is canceled and URBs are killed on close, while port remove frees the private state. The driver does not persist settings across disconnects, but it initializes from the device's current status packet when possible.

## Dependencies and Integration Points

The driver integrates with the USB serial and TTY cores, kfifo buffering, tty flip buffers, modem-control ioctls, delta modem-status waits, and USB control/bulk/interrupt URBs. It includes `oti6858.h` for the USB IDs. The design is locally similar to `pl2303`, but does not share helper code.

## Risks and Test Signals

The file itself warns that the protocol is reverse-engineered. Risks include incorrect active-high or active-low assumptions for modem-control bits, incomplete error reporting for parity/framing/overflow, retry loops from repeated setup failure, races around in-use flags touched by work and callbacks, and lost wakeups if interrupt URB resubmission is skipped in a transient state. The `send_data()` path also returns early on allocation failure without clearing `write_urb_in_use`, which is a risk signal for stalled writes.

Useful tests include open/close with URB cancellation, reading default or live status packets, applying baud/parity/data/stop changes and observing `SET_LINE`, toggling DTR and RTS through `TIOCMSET`, checking modem-status deltas and `TIOCMIWAIT`, receive availability causing one bulk read, TX-buffer-denied paths resubmitting the interrupt URB, write completion after bulk-out errors, and disconnect during delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/oti6858.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/oti6858.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/oti6858.h

## Purpose

`oti6858.h` is the local USB ID header for the Ours Technology Inc. OTi-6858 USB-to-serial driver. It gives `oti6858.c` a small, named contract for the device's vendor and product identifiers.

## Important APIs, Types, and Functions

The header defines the include guard `__LINUX_USB_SERIAL_OTI6858_H`, `OTI6858_VENDOR_ID` as `0x0ea0`, and `OTI6858_PRODUCT_ID` as `0x6858`. It declares no functions, structures, or inline helpers.

## Control Flow

There is no runtime control flow. The constants are consumed by `oti6858.c` when building its `usb_device_id` match table.

## State and Persistence Behavior

The header contains only compile-time constants. It has no runtime state, memory ownership, persistence, locking, or teardown behavior.

## Dependencies and Integration Points

Its only integration point is the USB device ID table in `oti6858.c`. Keeping the IDs in a separate header is a local convention, not a shared subsystem API.

## Risks and Test Signals

Risk is limited to ID correctness. Wrong constants prevent probe or bind the driver to the wrong hardware. Test signals are compile coverage of the include guard and successful USB modalias matching for vendor `0x0ea0`, product `0x6858`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/oti6858.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/pl2303.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/pl2303.c

## Purpose

`pl2303.c` is the USB serial driver for Prolific PL2303 adapters and many branded or cloned devices using compatible chips. It binds a broad USB ID table, detects the chip generation at attach time, initializes vendor registers, maps tty termios into Prolific line-coding control requests, manages DTR/RTS and break, and translates interrupt UART status into TTY modem and error state.

## Important APIs, Types, and Functions

The driver registers `pl2303_device` through `module_usb_serial_driver()`. The USB serial callbacks cover probe, endpoint counting, attach/release, port probe/remove, open/close, termios changes, DTR/RTS, break control, carrier detection, modem ioctls, interrupt status, and bulk read processing. `enum pl2303_type` distinguishes H, HX, TA, TB, HXD, and HXN/G chips. `struct pl2303_type_data` records per-type max baud, quirks, divisor support, and flow-control behavior. `struct pl2303_serial_private` stores type and quirks per serial device, while `struct pl2303_private` stores per-port line-control, line-status, and last line settings.

Important helpers include `pl2303_detect_type()`, `pl2303_startup()`, `pl2303_vendor_read()`, `pl2303_vendor_write()`, `pl2303_update_reg()`, `pl2303_set_termios()`, `pl2303_encode_baud_rate()`, `pl2303_set_control_lines()`, `pl2303_update_line_status()`, and `pl2303_process_read_urb()`. Quirks cover unusual UART status byte index, legacy initialization, interrupt endpoint discovery on another interface, and HXD clones that stall `GET_LINE` after break.

## Control Flow

Early probe stores ID-table quirks temporarily in serial data. `pl2303_calc_num_ports()` applies the endpoint hack when needed and requires an interrupt-in endpoint before accepting the interface. Attach calls `pl2303_detect_type()`, allocates serial private state, merges type and ID quirks, detects HXD break/get-line clones, and for non-HXN chips sends the vendor initialization sequence.

Open clears halts on legacy chips or resets pipes on newer chips, applies termios, submits the interrupt URB, and opens the generic bulk data path. Termios changes read or reuse the current seven-byte line setting, encode baud rate directly or through type-specific divisors, set data bits, stop bits, parity, and cached line settings, update DTR/RTS when entering or leaving B0, and configures hardware or software flow-control registers. Close shuts down generic data, kills the interrupt URB, and clears break.

Interrupt URBs carry UART state. `pl2303_update_line_status()` updates modem-control counters, handles break, wakes `delta_msr_wait`, and reports DCD changes to the tty core. Bulk read processing applies transient error flags to received bytes, emits overrun as a separate flip character, supports sysrq handling, and pushes data to the tty layer.

## State and Persistence Behavior

The driver has no persistent storage. Per-device state holds detected chip type and quirks for the USB serial lifetime. Per-port state holds the output modem-control bits, latest UART status byte, and cached line settings to avoid redundant `SET_LINE` requests that can drop bytes on some PL2303 chips. Hardware registers retain settings until device reset or disconnect, but driver state is rebuilt on attach and port probe.

## Dependencies and Integration Points

The driver depends on the USB core, USB serial core, TTY core, tty flip buffers, unaligned little-endian helpers, modem-control ioctls, and USB control transfers. `pl2303.h` supplies the large set of vendor and product IDs. It intentionally handles many rebranded adapters, phones, GPS cables, POS displays, dive computer interfaces, and RS232/RS485 adapters that share PL2303 behavior.

## Risks and Test Signals

Risk concentrates in chip-type detection, clone handling, and line-coding math. A wrong type can choose unsupported vendor requests, a bad divisor can silently select an unintended baud rate, and redundant `SET_LINE` requests may lose bytes on affected devices. Flow-control register differences between legacy, HXN, and other chips are another compatibility risk. Interrupt status length and index quirks affect modem counters and data error tagging.

Useful tests include attach across H, HX, TA, TB, HXD, and HXN descriptors; endpoint-hack devices with interrupt endpoints on interface 0; unknown descriptor rejection; common and custom baud rates with direct and divisor encodings; CS5 with 1.5 stop bits; parity including mark and space; B0 DTR/RTS behavior; hardware and XON/XOFF flow-control selection; break on/off including clone fallback; interrupt modem-status deltas; carrier hangup on DCD changes; and read URB parity, frame, break, and overrun propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/pl2303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/pl2303.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/pl2303.h

## Purpose

`pl2303.h` centralizes the vendor and product ID constants used by the PL2303 USB serial driver. It documents the many branded devices, cables, phones, displays, and adapters that should bind to `pl2303.c`.

## Important APIs, Types, and Functions

The header defines USB IDs for Prolific PL2303 variants and compatible or rebranded devices from ATEN, IODATA, ELCOM, ITEGNO, RATOC, Tripp Lite, RadioShack, Sitecom, Alcatel, Siemens, Nokia CA-42 clones, Sagem, Leadtek, Speed Dragon, Belkin, Alcor, Corega, HP, Cressi, Zeagle, Sony, Sanwa, ADLINK, SMART, Allied Telesis, Macrosilicon, and others. It declares no functions or structures.

## Control Flow

There is no executable control flow. `pl2303.c` includes the header and uses the constants in its `id_table[]` entries.

## State and Persistence Behavior

The file contains compile-time constants only. It has no runtime state, locking, allocation, or persistence behavior.

## Dependencies and Integration Points

The integration point is USB modalias matching through the `pl2303.c` ID table. Changes here must be reflected in `pl2303.c` entries to have runtime effect. The header is local to this driver rather than a public kernel interface.

## Risks and Test Signals

Incorrect IDs can cause missed binding or accidental binding of unrelated devices. Because many constants describe clones or branded cables, regression risk is mainly compatibility coverage. Test signals include successful module autoload for listed IDs, compile coverage for all constants referenced by `pl2303.c`, and manual checks that newly added IDs have the correct quirk flags in the source file when needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/pl2303.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/qcaux.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/qcaux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/qcserial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/qcserial.c

## Purpose

`qcserial.c` is a Qualcomm WWAN USB serial driver for Gobi QDL/modem devices and selected Sierra Wireless and Huawei layouts. It binds vendor-specific serial functions such as DM/DIAG, AT modem, and NMEA GPS ports while avoiding QMI, NCM, and other network interfaces that belong to network drivers. For actual serial I/O it uses the shared `usb-wwan` implementation.

## Important APIs, Types, and Functions

The driver registers `qcdevice` with the USB serial core. Its ID table assigns layout metadata through `driver_info`: `QCSERIAL_G1K` for Gobi 1000, `QCSERIAL_G2K` for default Gobi 2000+ layout, `QCSERIAL_SWI` for Sierra Wireless, and `QCSERIAL_HWI` for Huawei. `handle_quectel_ec20()` handles the nonstandard five-interface Quectel EC20 layout. `qcprobe()` performs class checks, interface-count and interface-number policy, alternate-setting selection, and whether `usb-wwan` should send setup control. `qc_attach()` allocates `struct usb_wwan_intf_private`, transfers the send-setup flag into `use_send_setup`, and initializes the suspend lock. `qc_release()` frees that private state.

## Control Flow

Probe first rejects non vendor-specific interfaces. For single-interface devices it recognizes QDL download mode, choosing alternate setting 1 on older devices when needed and requiring bulk-in plus bulk-out endpoints. For composite devices it defaults to altsetting 0, then filters by layout. Gobi 1K accepts DM/DIAG on interface 0 with altsetting 1 and modem on interface 2, rejecting serial-dead or QMI interfaces. Gobi 2K+ rejects interface 0 QMI/net and accepts DM/DIAG, modem, and NMEA interfaces. The Quectel EC20 special case accepts interfaces 0 through 3 and rejects NDIS on interface 4. Sierra Wireless accepts interfaces 0, 2, and 3, enabling send-setup for NMEA and modem ports. Huawei rejects known QMI and NCM protocol values and treats remaining vendor-specific functions as serial.

After a successful probe, attach builds the `usb-wwan` private state. Open, close, writes, modem-control ioctls, per-port setup, and suspend/resume are delegated to `usb-wwan`.

## State and Persistence Behavior

State is per matched USB serial interface. During probe, `usb_set_serial_data()` temporarily stores a boolean send-setup decision; attach replaces it with allocated `struct usb_wwan_intf_private`. Release clears serial data and frees the private object. No state survives disconnect or module unload.

## Dependencies and Integration Points

The driver depends on USB, USB serial, TTY, slab allocation, and `usb-wwan`. It integrates with other WWAN drivers by not binding QMI/net, NCM-like, and NDIS interfaces. User space sees the accepted functions as ttyUSB ports for QDL firmware download, diagnostic tools, AT commands, or GPS NMEA control depending on the device layout.

## Risks and Test Signals

The highest risk is layout policy drift. New firmware can change interface counts, numbers, protocols, or altsettings, causing the driver either to reject a valid serial function or claim a network function. Huawei's default-serial rule depends on the exclusion list staying current. Single-interface QDL detection depends on endpoint order and altsetting count. Send-setup must be applied only to interfaces that need it.

Useful tests include QDL one-interface devices with one and two altsettings, Gobi 1K and 2K composite layouts, Quectel EC20 five-interface layout, Sierra Wireless modem and GPS ports with DTR/RTS setup, Huawei protocol filtering against QMI and NCM functions, coexistence with `qmi_wwan` or NCM drivers, attach/release allocation failure paths, and suspend/resume through `usb-wwan`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/qcserial.c -->
