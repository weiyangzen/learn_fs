# Research Group subset-b-005533

This grouped report covers USB serial core and subdriver files under `sources/distributed-fs/ceph-client/drivers/usb/serial/`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/quatech2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/quatech2.c

## Purpose
`quatech2.c` is the USB serial subdriver for second-generation Quatech USB-to-serial adapters with 1, 2, 4, or 8 logical UART ports. The notable hardware model is that all logical ports share a single bulk-in endpoint and a single bulk-out endpoint, so the driver multiplexes transmit payloads with a Quatech control header and demultiplexes receive payloads by parsing in-band control escape records.

## Important APIs, Types, and Functions
The module registers one `usb_serial_driver` named `quatech-serial` with callbacks for open, close, write, write-room, line control, break, modem status, termios, attach, release, disconnect, and per-port probe/remove. `struct qt2_serial_private` holds shared device state, including the shared read URB, read buffer, and the currently selected receive port. `struct qt2_port_private` stores per-port UART number, write URB/buffer, URB busy flag, and cached line/modem status. Important helpers include `qt2_calc_num_ports()`, `qt2_set_port_config()`, `qt2_control_msg()`, `qt2_getregister()`, `qt2_setregister()`, and `update_mctrl()`.

## Control Flow, State, and Persistence
Probe-time port count is derived from product IDs. `qt2_attach()` powers the unit, allocates shared serial-private data, allocates a 512-byte shared read buffer, fills one shared bulk read URB against port 0 endpoints, and immediately submits it. Each port probe allocates its own write URB and 512-byte write buffer but targets the shared bulk-out endpoint. Open switches the selected logical port to RS232 mode, sends `QT_OPEN_CLOSE_CHANNEL`, snapshots initial LSR/MSR bytes, configures default 9600 8N, and applies caller termios. Write serializes one active write URB per port and prepends `ESC ESC <device_port> <le16 length>` before the payload. Read completion parses `ESC ESC` records for line status, modem status, transmit-hold, port switch, flush, and escaped control bytes, changing `current_port` and pushing tty flip buffers at port boundaries.

State lives only in kernel memory: shared URB/buffer data, per-port shadow LSR/MSR, write busy flags, and current demux port. It is reset on disconnect/module removal and not persisted externally. Line changes update `port->icount` and `delta_msr_wait` for generic TIOCM wait integration.

## Dependencies and Integration Points
The file depends on the USB serial core, TTY flip buffer API, USB control/bulk URB APIs, `serial_reg.h` UART bit definitions, and the generic USB serial helpers for `tiocmiwait` and `get_icount`. Integration is through `module_usb_serial_driver()`, `usb_set_serial_data()`, `usb_set_serial_port_data()`, and core callbacks in `struct usb_serial_driver`.

## Risks and Test Signals
Primary risks are malformed in-band control messages corrupting demultiplexing, shared endpoint concurrency bugs, short control responses during open/status reads, and write starvation because each port owns only one write URB. Suspend/resume is not implemented here, so behavior relies on core disconnect/close handling. Useful tests include binding each supported product ID, verifying calculated port counts, opening multiple ports concurrently, injecting data that includes escaped control bytes, changing termios and modem lines, checking break control, and disconnecting while read/write URBs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/quatech2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/safe_serial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/safe_serial.c

## Purpose
`safe_serial.c` implements the Lineo Safe Encapsulated Serial protocol. It adds optional end-to-end integrity over USB serial packets by appending a two-byte trailer containing valid payload length and a 10-bit CRC, with an optional padded mode that expands writes to the endpoint packet size.

## Important APIs, Types, and Functions
The file registers a one-port `safe_serial` USB serial driver. Module parameters `safe` and `padded` control encapsulation and packet padding. `fcs_compute10()` computes the 10-bit CRC using a static lookup table. `safe_process_read_urb()` validates and strips trailers before pushing data to the tty layer. `safe_prepare_write_buffer()` pulls bytes from the port write FIFO, optionally pads, writes the trailer, computes the CRC, and returns the packet length. `safe_startup()` validates device/interface class/subclass/protocol before allowing bind.

## Control Flow, State, and Persistence
On startup, the device must look like a CDC device with Lineo SafeSerial vendor interface class/subclass. The interface protocol selects normal CRC or CRC-padded mode; padded mode can also be configured by build/module parameter. Reads either pass through unchanged when `safe` is false or require at least a two-byte trailer, validate the CRC over the full frame, derive the actual data length from the high six bits of the penultimate byte, and reject inconsistent frames. Writes reserve trailer space, drain the generic write FIFO, optionally fill the remaining packet with ASCII zero bytes, set length bits, compute CRC, and OR the CRC into the trailer.

Persistent state is limited to module-level booleans and generic USB serial port FIFO state. There is no device-private allocation beyond generic core resources.

## Dependencies and Integration Points
The driver is tightly coupled to the USB serial generic write/read path through `process_read_urb` and `prepare_write_buffer`. It uses the TTY flip-buffer API and kfifo access under `port->lock`. Device matching uses custom USB device ID fields that require both device and interface class/subclass matches.

## Risks and Test Signals
CRC and length trailer handling are the core risk: short packets, inconsistent lengths, or wrong CRCs must be dropped without leaking corrupt data. The `padded` global is mutated by startup, so multiple devices with different protocol requirements could interact through shared module state. Test signals include loopback with safe on/off, padded and unpadded packets, malformed CRCs, short frames, max-packet writes, and binding only to the expected SafeSerial protocol values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/safe_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/sierra.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/sierra.c

## Purpose
`sierra.c` is a Sierra Wireless modem USB serial subdriver. It handles many legacy AirPrime/Sierra/HP/AT&T device IDs, ignores Direct IP non-serial interfaces, selects alternate settings for some composite devices, manages modem control signaling, and implements high-throughput multi-URB read/write paths with suspend/resume queuing.

## Important APIs, Types, and Functions
`struct sierra_intf_private` tracks suspend state, open-port count, and write URBs in flight. `struct sierra_port_private` tracks per-port anchors, outstanding write URB count, input URBs, modem signal state, and memory profile. Important functions include `sierra_probe()`, `sierra_calc_num_ports()`, `sierra_send_setup()`, `sierra_open()`, `sierra_close()`, `sierra_write()`, `sierra_indat_callback()`, `sierra_instat_callback()`, `sierra_suspend()`, and `sierra_resume()`. Module parameter `nmea` enables a vendor request to start NMEA streaming.

## Control Flow, State, and Persistence
Probe may switch alternate setting 1 on two-altsetting interfaces and rejects interfaces listed in `direct_ip_interface_ignore`. Port count comes from endpoint count except dummy interface `0x99`, which returns zero. Attach allocates interface-private state, sets device power D0, and optionally enables NMEA. Port probe chooses low- or high-memory URB counts based on interface/port lists. Open allocates input URBs, submits read and optional interrupt URBs, enables remote wakeup when the first port opens, and releases the autopm reference acquired by the core. Write allocates a new buffer and URB per request, enforces an outstanding URB limit, anchors active or delayed URBs depending on suspend state, sets `URB_ZERO_PACKET`, and uses async runtime PM references until completion. Close drains delayed writes, stops RX, kills active writes, frees read URBs, and balances runtime PM state.

Runtime state is in anchors, signal booleans, counters, and suspend flags; nothing persists across disconnect. Interrupt-in notifications update CTS/DCD/DSR/RI, and DCD drop triggers a tty hangup.

## Dependencies and Integration Points
The driver integrates with USB serial core callbacks and directly uses USB runtime PM, USB anchors, TTY flip buffers, and generic USB serial module registration. It does not use `usb_wwan.c`; it carries a similar private implementation. Power and NMEA control are Sierra vendor-specific control messages.

## Risks and Test Signals
Risks include URB accounting imbalance across submit failures, delayed URB handling during suspend/resume, overcounted `chars_in_buffer()`, alternate-setting assumptions, and shared global `nmea` behavior. Test signals should cover Direct IP ignore lists, high-memory interfaces, writes during autosuspend, resume delayed-write replay, DCD hangup, multi-port concurrent open/close, and runtime PM reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/sierra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/spcp8x5.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/spcp8x5.c

## Purpose
`spcp8x5.c` supports SPCP8x5 USB-to-serial adapters and compatible Philips/Intermatic devices. It mostly relies on generic USB serial bulk data handling but provides vendor control messages for line settings, modem control/status, work mode, and carrier reporting.

## Important APIs, Types, and Functions
`struct spcp8x5_private` stores device quirks, a spinlock, and cached DTR/RTS line-control bits. `spcp8x5_probe()` stores the matching USB ID for quirk lookup. `spcp8x5_port_probe()` allocates private data and sets a drain delay. `spcp8x5_set_ctrl_line()`, `spcp8x5_get_msr()`, and `spcp8x5_set_work_mode()` issue vendor control transfers. `spcp8x5_set_termios()` maps termios to device-specific baud/format bytes. `spcp8x5_tiocmget()`, `spcp8x5_tiocmset()`, `spcp8x5_dtr_rts()`, and `spcp8x5_carrier_raised()` expose modem control semantics.

## Control Flow, State, and Persistence
Open clears endpoint halts, sends a device-init control request, restores cached control lines, applies termios, and then delegates to `usb_serial_generic_open()`. Termios changes are skipped if hardware settings did not change. Baud rates are mapped to fixed encoded values, unsupported rates fall back by programming the code currently held in the zero-initialized buffer path, and `CRTSCTS` enables U2C working mode. B0 transitions reassert DTR/RTS after coming back from hangup. Quirked SPCP825 devices avoid UART status and work-mode requests.

The only persistent runtime state is per-port cached line control and quirk flags. Actual payload movement is handled by generic USB serial URBs and FIFOs.

## Dependencies and Integration Points
The driver depends on USB serial core, generic open/close/read/write behavior, TTY termios helpers, and vendor USB control transfers. It registers one one-port driver with callbacks for termios, carrier, modem-control, probe, and port-private lifecycle.

## Risks and Test Signals
Main risks are unsupported baud handling, device-specific quirk coverage, lockless interactions between carrier/modem control and termios paths, and control transfer failures that generic data paths may not surface. Test signals include all supported baud/format combinations, B0 hangup/reassert behavior, `TIOCMGET/TIOCMSET`, devices with `NO_UART_STATUS` and `NO_WORK_MODE` quirks, endpoint halt recovery, and hardware-flow-control enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/spcp8x5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ssu100.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ssu100.c

## Purpose
`ssu100.c` supports the single-port Quatech SSU-100 USB-to-serial adapter. It initializes the device into RS232 mode, programs UART format and flow control with Quatech control requests, tracks line/modem status, and parses status prefixes embedded in received bulk data.

## Important APIs, Types, and Functions
`struct ssu100_port_private` stores shadow LSR/MSR under a spinlock. Helpers wrap Quatech control transfers: `ssu100_control_msg()`, `ssu100_getdevice()`, `ssu100_setdevice()`, `ssu100_getregister()`, `ssu100_setregister()`, and `update_mctrl()`. Lifecycle and TTY functions include `ssu100_attach()`, `ssu100_open()`, `ssu100_set_termios()`, `ssu100_dtr_rts()`, `ssu100_tiocmget()`, `ssu100_tiocmset()`, and `ssu100_process_read_urb()`.

## Control Flow, State, and Persistence
Attach calls `ssu100_initdevice()`, which reads device configuration, clears full-power flags, sets prebuffer trigger level, disables ATF, selects clock and RS232 mode, and writes configuration back. Open sends `QT_OPEN_CLOSE_CHANNEL` to retrieve initial LSR/MSR, configures default UART divisor, applies termios, and starts generic reads. Termios maps parity, data bits, divisor from a 460800 base, hardware flow (`SERIAL_CRTSCTS`), and software flow XON/XOFF into control requests. Read processing recognizes a four-byte `0x1b 0x1b type status` prefix for LSR/MSR updates, then forwards remaining data with the appropriate tty flag.

Runtime state is limited to per-port shadow status and generic USB serial resources. Modem status deltas update `port->icount` and wake `delta_msr_wait`; line status errors update break/parity/frame/overrun counters and flags.

## Dependencies and Integration Points
The file uses USB serial generic open/data paths plus custom `process_read_urb`, TTY flip helpers, UART register constants, and generic `tiocmiwait/get_icount`. It registers a one-port driver for Quatech vendor/product `0x061d:0xc020`.

## Risks and Test Signals
Risks include short status-prefixed packets, LSR flag propagation across a full received packet, divisor rounding edge cases, control transfer failures during attach/open, and behavior when modem lines are changed while flow control is enabled. Test signals include attach init sequence, status-only packets, mixed status+data packets, break/parity/frame/overrun reporting, termios and flow-control changes, B0/DTR/RTS behavior, and disconnect during generic read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ssu100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/symbolserial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/symbolserial.c

## Purpose
`symbolserial.c` is a USB serial subdriver for Symbol barcode scanners matching `0x05e0:0x0600`. It exposes scanner interrupt-in reports as tty data and implements throttle/unthrottle so the interrupt URB is not resubmitted while the line discipline cannot accept data.

## Important APIs, Types, and Functions
`struct symbol_private` stores `throttled` and `actually_throttled` flags under a spinlock. `symbol_open()` starts the interrupt read URB. `symbol_close()` kills it. `symbol_int_callback()` parses interrupt packets whose first byte is the payload length and pushes the remaining bytes to the tty layer. `symbol_throttle()` and `symbol_unthrottle()` coordinate deferred URB resubmission. `symbol_port_probe()` and `symbol_port_remove()` allocate per-port state.

## Control Flow, State, and Persistence
Open clears throttle flags and submits the interrupt URB. Each interrupt completion logs raw data, clamps the device-reported length to available bytes, inserts the payload after the one-byte length header, and pushes the flip buffer. The callback resubmits immediately unless throttled; if throttled, it marks `actually_throttled` so unthrottle knows to restart the URB. Close kills the interrupt URB. State is per-port and volatile.

## Dependencies and Integration Points
The driver requires one interrupt-in endpoint and one logical port. It integrates directly with USB serial core callbacks and TTY flip buffers, without generic bulk data paths. It uses `module_usb_serial_driver()` for module registration.

## Risks and Test Signals
Risks are malformed length headers, throttle races around interrupt completion, missing interrupt endpoint descriptors, and silent data drops if unthrottle submit fails. Test signals include short packets, oversized length byte clamping, repeated throttle/unthrottle cycles, unplug while throttled, and scanner report delivery through tty reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/symbolserial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ti_usb_3410_5052.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ti_usb_3410_5052.c

## Purpose
`ti_usb_3410_5052.c` supports TI TUSB3410 single-port and TUSB5052 dual-port USB serial adapters plus many rebranded devices. It handles bootloader versus active configurations, firmware download, one- and two-port driver variants, UART configuration, modem control/status, buffered writes, read throttling, and interrupt-driven status notifications.

## Important APIs, Types, and Functions
`struct ti_device` stores device-wide state: open/close mutex, open-port count, serial pointer, 3410-vs-5052 flag, and RS485-only mode. `struct ti_port` stores per-port UART base address, shadow modem control, modem status, read/write URB state, and locking. Firmware and control helpers include `ti_download_firmware()`, `ti_do_download()`, `ti_command_in_sync()`, `ti_command_out_sync()`, `ti_port_cmd_in()`, `ti_port_cmd_out()`, and `ti_write_byte()`. TTY callbacks include `ti_open()`, `ti_close()`, `ti_write()`, `ti_set_termios()`, `ti_tiocmget()`, `ti_tiocmset()`, `ti_break()`, `ti_throttle()`, `ti_unthrottle()`, `ti_tx_empty()`, and URB callbacks.

## Control Flow, State, and Persistence
Startup allocates `ti_device`, detects the device family, marks some Moxa devices as RS485-only, downloads firmware when the device has only boot endpoints, requests reset/re-enumeration by returning `-ENODEV`, switches from boot to active configuration when needed, and verifies endpoint counts. Port probe assigns UART base addresses and initial UART mode; 5052 ports get a one-character drain delay because the shift-register-empty bit is unavailable.

Open is serialized device-wide. The first open starts the shared interrupt-in URB with `ti_device` context. The port is configured, opened, started, purged, endpoint halts are cleared, configured/opened/started again, then the read URB is submitted with `ti_port` context. Writes enqueue into the core `write_fifo` under `tp_lock`; `ti_send()` drains the FIFO into the port write URB if not busy, submits it, updates tx counters, and wakes the tty when space is available. Bulk-in callbacks deliver data unless the port is closed and resubmit while read state is running. Interrupt callbacks decode port/function bits, handle hardware/data errors, and update modem status counters/wakeup. Termios builds `struct ti_uart_config`, handles parity/data/stop bits, hardware and software flow control, baud divisors, RS232/RS485 mode, and restores modem control because SET_CONFIG asserts DTR/RTS.

State is volatile in `ti_device`, `ti_port`, kfifo data, URB states, and line counters. Firmware is loaded through the kernel firmware API but not persisted by this driver.

## Dependencies and Integration Points
The driver depends on USB serial core endpoint allocation, firmware loading, TTY/kfifo APIs, USB control and bulk messages, interrupt URBs, and UART-like termios semantics. It exports no helper APIs; integration is via two `usb_serial_driver` entries and a combined USB ID table.

## Risks and Test Signals
High-risk areas are firmware selection/download and re-enumeration, double open/start sequencing, shared interrupt URB lifetime across multiple ports, FIFO/write-URB races, read-stop state transitions, unsupported CMSPAR handling, RS485-only mode, and control-transfer short reads. Test signals include boot-firmware devices, active-config devices, both 3410 and 5052 port counts, all advertised firmware fallback names, termios changes including B0, modem-status interrupts and TIOCM wait, throttle/unthrottle, tx-empty behavior, and disconnect during write FIFO drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ti_usb_3410_5052.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/upd78f0730.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/upd78f0730.c

## Purpose
`upd78f0730.c` supports Renesas uPD78F0730 USB-to-serial converter firmware used by several evaluation boards. It uses vendor control messages for all serial control operations while generic USB serial handles bulk data.

## Important APIs, Types, and Functions
`struct upd78f0730_port_private` stores the cached DTR/RTS/BREAK bitmask protected by a mutex. Packed command structures model device protocol requests: line control, DTR/RTS, XON/XOFF, open/close, and error-character configuration. Key functions are `upd78f0730_send_ctl()`, `upd78f0730_set_termios()`, `upd78f0730_open()`, `upd78f0730_close()`, `upd78f0730_tiocmget()`, `upd78f0730_tiocmset()`, `upd78f0730_break_ctl()`, and `upd78f0730_dtr_rts()`.

## Control Flow, State, and Persistence
Port probe allocates mutex-protected private state. Open sends an `OPEN_CLOSE` command with `PORT_OPEN`, applies termios, and delegates to `usb_serial_generic_open()`. Close calls generic close first and then sends `PORT_CLOSE`. Termios validates hardware changes, toggles DTR/RTS for B0 transitions, coerces unsupported baud/data/parity/flow modes back into supported settings, and sends a `LINE_CONTROL` command containing little-endian baud and parameter bits. TIOCM and break paths modify the cached signal bitmask and send a `SET_DTR_RTS` command.

State is only the cached signal bitmask and generic USB serial buffers. The driver deliberately reports only DTR/RTS via `tiocmget`; it does not read incoming modem status lines.

## Dependencies and Integration Points
The driver uses USB serial core for enumeration and data movement, TTY termios helpers for validation/coercion, and vendor control transfers with request `0x00`. It registers a single one-port subdriver for Renesas/NEC and compatible product IDs.

## Risks and Test Signals
Risks include `upd78f0730_dtr_rts()` accessing `port->port.tty`, unsupported flow-control settings being silently cleared after warning, and no handling of modem input status. Test signals include supported and unsupported baud rates, CS7/CS8 coercion, parity/CMSPAR handling, B0 line toggling, break set/clear, open/close command ordering, and failure handling for control-message submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/upd78f0730.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb-serial-simple.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/usb-serial-simple.c

## Purpose
`usb-serial-simple.c` groups many simple USB serial devices that need only static ID matching and generic USB serial behavior. It avoids one-file-per-ID boilerplate by generating `usb_serial_driver` instances with macros.

## Important APIs, Types, and Functions
The main abstractions are `DEVICE_N()` and `DEVICE()`, which generate a per-vendor USB ID table and a `usb_serial_driver` with `num_ports`. Device ID macros cover CareLink, Infineon Flashloader, Funsoft, Google vendor subclass serial, HP4x calculators, Kaufmann, libtransistor console, Motorola modems/TETRA, Nokia, NovAtel GPS, OWON, Siemens MPI, Suunto ANT, ViVOpay, and ZIO. `serial_drivers[]` aggregates all generated drivers; `id_table[]` aggregates all USB IDs for module registration.

## Control Flow, State, and Persistence
There is no custom runtime control flow in this file. At module load, `module_usb_serial_driver()` registers the generated subdrivers and combined ID table. On device bind, the USB serial core fills missing callbacks with generic operations, allocates endpoints and ports, and handles open/read/write/close. NovAtel GPS is the only generated entry with three ports; the rest use one port.

No file-specific private state exists. State is entirely managed by the USB serial core generic implementation and any TTY state held per port.

## Dependencies and Integration Points
This file depends on the USB serial core's default callback initialization in `usb-serial.c`. Its integration surface is the static set of ID tables and driver descriptors. Adding devices here changes module autoload matching and can claim interfaces before more specialized drivers if IDs overlap.

## Risks and Test Signals
Risks are incorrect IDs, wrong `num_ports`, matching overly broad interface descriptors, and conflicts with device-specific drivers that should perform vendor setup. Test signals include module autoload for each ID, endpoint availability with generic callbacks, multi-port NovAtel behavior, and verifying no specialized driver loses ownership because of a broad match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb-serial-simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb-serial.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/usb-serial.c

## Purpose
`usb-serial.c` is the USB serial core. It registers the ttyUSB major, manages dynamic minor allocation, discovers and binds USB serial subdrivers, allocates per-port devices and URBs, bridges TTY operations to subdriver callbacks, handles disconnect and PM, and provides registration APIs used by every USB serial module.

## Important APIs, Types, and Functions
Global state includes `serial_minors` IDR, `table_lock`, and `usb_serial_driver_list`. Exported APIs include `usb_serial_port_get_by_minor()`, `usb_serial_claim_interface()`, `usb_serial_put()`, `usb_serial_port_softint()`, `usb_serial_suspend()`, `usb_serial_resume()`, `__usb_serial_register_drivers()`, and `usb_serial_deregister_drivers()`. Core functions cover tty install/open/close/write/ioctl/termios, endpoint discovery/setup, probe/disconnect, PM reset resume, driver registration, and fallback operation initialization.

## Control Flow, State, and Persistence
Initialization allocates a 512-minor tty driver on major 188, registers the USB serial bus, installs tty operations, registers the generic driver, and exposes ttyUSB devices dynamically. During probe, the core finds the matching serial subdriver under `table_lock`, creates `struct usb_serial`, calls subdriver probe, gathers endpoints from the primary and optional sibling interface, validates endpoint requirements, calculates port count, allocates `usb_serial_port` devices, allocates read/write/interrupt URBs and buffers, calls attach, reserves tty minors with IDR, and registers each `ttyUSBn` device. TTY install looks up by minor, takes a serial reference and module reference, sets initial termios, and stores `driver_data`. Open/close route through `tty_port_open()` with runtime PM around subdriver open/close. Writes, modem control, termios, throttling, and ioctls dispatch to `serial->type` callbacks with generic fallbacks if the subdriver did not provide them.

Disconnect marks the serial disconnected under `disc_mutex`, vhangs tty ports, poisons URBs, wakes waiters, removes device nodes, calls subdriver disconnect, releases sibling interfaces, and drops the serial reference. Suspend invokes subdriver suspend once across sibling interfaces and poisons URBs; resume unpoisons and invokes subdriver resume or generic resume. Lifetime is kref-based; `destroy_serial()` releases minors, calls subdriver release, drops interface/device references, and frees ports when their device refs reach zero.

State is in kernel memory only: IDR minor map, registered-driver list, krefs, port devices, tty state, URBs, FIFOs, and PM counters. There is no on-disk persistence.

## Dependencies and Integration Points
The file integrates Linux USB core, TTY core, device model, IDR, kfifo, module ownership, USB serial bus code, generic USB serial helpers, and optional console support. Subdrivers depend on `__usb_serial_register_drivers()` via the `module_usb_serial_driver()` macro and on generic callbacks installed by `usb_serial_operations_init()`.

## Risks and Test Signals
Risks include lifetime races among disconnect, tty cleanup, URB callbacks, and module unload; endpoint-to-port mapping mistakes; sibling-interface ownership; PM suspend counts across sibling interfaces; and dynamic-ID probe ordering. Test signals include binding/unbinding multiple subdrivers, minor exhaustion/unwind, hot unplug during open/write, module unload with active ttys, suspend/resume and reset-resume paths, missing endpoint rejection, generic fallback callback behavior, and `/proc` `usbserinfo` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb-serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb-wwan.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/usb-wwan.h

## Purpose
`usb-wwan.h` declares the shared helper API and private data structures used by USB wireless WAN modem subdrivers. It centralizes multi-URB buffering, modem control, and PM-related state for drivers that include `usb_wwan.c`.

## Important APIs, Types, and Functions
The header declares exported helpers for DTR/RTS, open/close, port probe/remove, write/write-room/chars-in-buffer, TIOCM get/set, and optional suspend/resume. Constants define four IN URBs, four OUT URBs, and 4096-byte input/output buffers. `struct usb_wwan_intf_private` tracks interface suspend state, feature flags `use_send_setup` and `use_zlp`, in-flight writes, open-port count, and an opaque private pointer. `struct usb_wwan_port_private` owns input/output URBs and buffers, an output busy bitset, delayed anchor, signal-state booleans, and tx start timestamps.

## Control Flow, State, and Persistence
The header itself has no execution path, but it defines the state contract that subdrivers must allocate and initialize before calling the helper functions. Interface-private flags control whether CDC `SET_CONTROL_LINE_STATE` requests are sent and whether outbound URBs use zero-length packets. Port-private state supports concurrent write URBs, delayed write queuing while suspended, and modem signal reporting.

All state is volatile per device/interface/port and is freed by the companion implementation during port remove or disconnect.

## Dependencies and Integration Points
It depends on USB serial core type definitions and PM types. Subdrivers must include this header, allocate `usb_wwan_intf_private` as serial data, and use the declared callbacks in their `usb_serial_driver` structures.

## Risks and Test Signals
Risks are contract mismatches: a subdriver can forget to initialize `susp_lock`, feature flags, or serial/port data before using helpers. The header exposes fields directly, so locking discipline is partly caller-dependent. Test signals include compile coverage for CONFIG_PM and non-PM builds, helper consumers allocating both private structures, and runtime tests for send-setup and zero-length-packet feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb-wwan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb_debug.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/usb_debug.c

## Purpose
`usb_debug.c` supports USB debug cables and xHCI debug capability serial endpoints. It is a minimal one-port USB serial driver that emulates serial break with a fixed eight-byte marker sequence.

## Important APIs, Types, and Functions
Two `usb_serial_driver` instances are registered: `debug` for `0x0525:0x127a` with an 8-byte bulk-out size, and `xhci_dbc` for Linux foundation debug capability IDs. `USB_DEBUG_BRK` is the marker used to emulate break. `usb_debug_break_ctl()` writes the marker when break is asserted. `usb_debug_process_read_urb()` detects the marker and calls `usb_serial_handle_break()`, otherwise defers to generic read processing. `usb_debug_init_termios()` disables echo and newline echo.

## Control Flow, State, and Persistence
There is no private state. On break assertion, the driver sends the marker through `usb_serial_generic_write()`. Incoming packets that exactly match the marker and length are treated as break events rather than delivered as data. All other data is passed to the generic USB serial read path. Initial termios is adjusted at first tty install.

## Dependencies and Integration Points
The file relies on generic USB serial open/write/read behavior and only customizes break processing and termios. It integrates with the core through `process_read_urb`, `break_ctl`, and `init_termios`.

## Risks and Test Signals
Risks are marker collision with real data, partial marker delivery not being recognized as break, and endpoint max-packet assumptions for debug cable hardware. Test signals include break write success/failure, exact marker received as break, near-marker data delivered normally, echo disabled in initial termios, and both debug and xHCI DBC ID tables binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb_wwan.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/usb_wwan.c

## Purpose
`usb_wwan.c` implements shared GSM/mobile-broadband USB serial helper callbacks. It improves on simple generic serial behavior by maintaining multiple receive URBs, multiple transmit URBs, runtime PM references, optional CDC modem-control setup, optional zero-length packets, and suspend/resume delayed-write replay.

## Important APIs, Types, and Functions
Exported functions include `usb_wwan_dtr_rts()`, `usb_wwan_tiocmget()`, `usb_wwan_tiocmset()`, `usb_wwan_write()`, `usb_wwan_write_room()`, `usb_wwan_chars_in_buffer()`, `usb_wwan_open()`, `usb_wwan_close()`, `usb_wwan_port_probe()`, `usb_wwan_port_remove()`, and PM helpers. Internal helpers include `usb_wwan_send_setup()`, `usb_wwan_indat_callback()`, `usb_wwan_outdat_callback()`, `usb_wwan_setup_urb()`, `unbusy_queued_urb()`, `stop_urbs()`, and `usb_wwan_submit_delayed_urbs()`.

## Control Flow, State, and Persistence
Consumers allocate `usb_wwan_intf_private` as serial data and use `usb_wwan_port_probe()` to allocate four page-backed IN buffers/URBs and four 4096-byte OUT buffers/URBs per port. Open submits the optional interrupt URB and all IN URBs, enables remote wakeup on first open, and balances the core runtime PM reference. Write slices user data across free OUT URBs, marks busy bits, obtains async runtime PM, queues URBs on the delayed anchor if suspended, or submits immediately and increments `in_flight`. Completion wakes the tty, drops runtime PM, decrements `in_flight`, and clears the matching busy bit. Read completion pushes data to the tty and resubmits unless fatal shutdown errors occur.

Close disables remote wakeup on last close, drains delayed writes while clearing busy bits and PM refs, kills all IN/OUT and interrupt URBs, and gets a no-resume PM reference to rebalance open. Suspend refuses autosuspend if writes are in flight, marks suspended, and kills URBs. Resume resubmits interrupt/read URBs for initialized ports and replays delayed writes before clearing the suspended flag.

State is per interface and per port in the structures declared by `usb-wwan.h`; no state persists outside kernel memory.

## Dependencies and Integration Points
The implementation depends on USB serial core, CDC control-line request definitions, TTY flip buffers, USB anchors, runtime PM, jiffies, and exported symbols for subdriver reuse. Subdrivers control behavior through `use_send_setup` and `use_zlp` flags.

## Risks and Test Signals
Risks include documented insufficient locking around signal and busy state, URB busy bits left set after unusual unlink paths, PM reference imbalance, delayed-anchor replay errors, and writes that make no progress because all URBs are busy or stale for less than ten seconds. Test signals include concurrent multi-URB writes, autosuspend with in-flight writes returning `-EBUSY`, delayed write replay on resume, close while suspended, DTR/RTS setup control transfers, ZLP behavior, and hot unplug during read resubmission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/usb_wwan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/visor.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/visor.c

## Purpose
`visor.c` supports Handspring Visor, Palm OS, Sony Clie, and related PDA USB serial devices. It binds a large legacy ID set, queries device connection information for some Palm OS versions, adjusts endpoint mappings for quirky devices, and delegates most data movement to generic USB serial.

## Important APIs, Types, and Functions
The file defines three `usb_serial_driver` instances: `visor`, `clie_5`, and `clie_3.5`. Important callbacks are `visor_probe()`, `palm_os_3_probe()`, `palm_os_4_probe()`, `visor_calc_num_ports()`, `clie_5_calc_num_ports()`, `clie_3_5_startup()`, `visor_open()`, `visor_close()`, and `visor_read_int_callback()`. It uses constants and structures from `visor.h` for vendor request codes and connection-info layouts.

## Control Flow, State, and Persistence
Probe rejects Samsung ACM devices that reuse a Palm ID and requires active configuration 1. Devices with `driver_info` call either the Palm OS 3 or Palm OS 4 probe helper. The OS 3 path requests `VISOR_GET_CONNECTION_INFORMATION`, validates and logs up to two logical ports, stores `num_ports` temporarily in serial data for `calc_num_ports()`, and sends a broken bytes-available request whose result is ignored. The OS 4 path requests extended connection info for debug logging. `visor_calc_num_ports()` retrieves stored port count and may swap bulk-in and interrupt-in endpoints for Handspring/Kyocera Treo-style devices. `clie_5_calc_num_ports()` maps both logical ports to the second bulk-out endpoint. `clie_3_5_startup()` performs GET_CONFIGURATION and GET_INTERFACE requests expected by older Sony devices.

Open verifies a read URB exists, starts generic bulk reading, and submits interrupt-in URB if present. Close calls generic close, kills interrupt-in, and sends `VISOR_CLOSE_NOTIFICATION`. Interrupt callbacks only debug-log and resubmit; data readiness is not otherwise interpreted.

Runtime state is minimal. Temporary serial data carries detected port count between probe and port-count calculation; all long-lived data is generic core state.

## Dependencies and Integration Points
The driver depends on USB serial core generic callbacks, TTY/USB APIs, CDC class constants for rejecting ACM conflicts, and `visor.h` protocol definitions. It integrates through three subdrivers sharing one combined USB ID table.

## Risks and Test Signals
Risks include legacy devices returning malformed connection-info lengths, endpoint swapping breaking assumptions for unusual Treo/Kyocera layouts, broad Samsung ID conflicts, and close-notification failures being ignored. Test signals include Palm OS 3 port-count query, Palm OS 4 extended-info query, Sony Clie 3.5 startup requests, Clie 5 endpoint remap, Treo endpoint swap, generic open/close with interrupt endpoint, and ACM Samsung rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/visor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/visor.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/visor.h

## Purpose
`visor.h` is the protocol and ID definition header for the Palm/Handspring/Sony Clie USB serial driver. It centralizes vendor/product IDs, vendor request codes, endpoint/function constants, and connection-info structure layouts consumed by `visor.c`.

## Important APIs, Types, and Functions
The header defines IDs for Handspring, Palm, GSPDA, Sony, Acer, Samsung, Tapwave, Garmin, Aceeca, Kyocera, and Fossil devices. It defines request codes `VISOR_REQUEST_BYTES_AVAILABLE`, `VISOR_CLOSE_NOTIFICATION`, `VISOR_GET_CONNECTION_INFORMATION`, and `PALM_GET_EXT_CONNECTION_INFORMATION`. `struct visor_connection_info` models the original Handspring/Palm OS 3 two-port response. `struct palm_ext_connection_info` models Palm OS 4 extended connection metadata with endpoint-number and function fields.

## Control Flow, State, and Persistence
The header has no executable flow or stored state. Its constants drive `visor.c` USB ID tables and control-message payload parsing. The structures are laid out with fixed-width little-endian fields matching device protocol responses.

## Dependencies and Integration Points
It is included only by `visor.c` in this subset and depends on kernel fixed-width integer and endian types being available through surrounding includes. Changes here directly alter which devices `visor.c` recognizes and how it interprets control response buffers.

## Risks and Test Signals
Risks include wrong product IDs causing incorrect binding, structure layout mismatches with device firmware, and stale comments around obscure Palm vendor requests. Test signals are compile coverage for `visor.c`, USB ID matching for each listed family, validating connection-info buffer sizes, and ensuring endpoint/function constants match the parser branches in `palm_os_3_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/visor.h -->
