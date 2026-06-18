# Research: subset-b-005530

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan.c

## Purpose
This is the main Keyspan USB-to-serial converter driver for many post-renumeration Keyspan adapters plus a pre-renumeration firmware loader. It binds one-, two-, and four-port Keyspan products, downloads EZ-USB FX1 firmware for unconfigured devices, maps product IDs to device-specific endpoint layouts and message formats, and exposes serial ports through the Linux `usb_serial_driver` and TTY interfaces.

## Important APIs, Types, and Functions
The central device descriptor is `struct keyspan_device_details`, which records product ID, message format (`msg_usa26`, `msg_usa28`, `msg_usa49`, `msg_usa90`, `msg_usa67`), port count, endpoint maps, baud clock, and baud-rate callback. Per-device state lives in `struct keyspan_serial_private` with global status/control/data URBs and buffers. Per-port state lives in `struct keyspan_port_private` with input/output URB pairs, control URBs, baud and termios cache, modem input/output state, flip indexes, transmit start timestamps, and pending control resend state.

The public USB serial hooks are `keyspan_open`, `keyspan_close`, `keyspan_write`, `keyspan_write_room`, `keyspan_set_termios`, `keyspan_break_ctl`, `keyspan_tiocmget`, `keyspan_tiocmset`, `keyspan_dtr_rts`, `keyspan_startup`, `keyspan_disconnect`, `keyspan_release`, `keyspan_port_probe`, and `keyspan_port_remove`. `keyspan_fake_startup` selects and downloads firmware using `ezusb_fx1_ihex_firmware_download`. `keyspan_setup_urb` and `keyspan_setup_urbs` build URBs from endpoint descriptors and the `keyspan_callbacks` dispatch table.

## Control Flow
Module registration publishes four serial drivers: `keyspan_no_firm`, `keyspan_1`, `keyspan_2`, and `keyspan_4`. Pre-renumeration devices enter `keyspan_fake_startup`, pick a firmware filename from the product ID, download it, and deliberately return a nonzero attach result so the temporary device is not bound while it renumerates. Real devices enter `keyspan_startup`, match a `keyspan_device_details`, allocate global buffers/URBs, submit status URBs, and optionally submit the USA49WG aggregate data URB.

Each port is initialized by `keyspan_port_probe`, which allocates per-port buffers, constructs data/control URBs according to the selected endpoint map, and stores private state. `keyspan_open` resets modem defaults, submits all input URBs, derives the initial baud and flow-control settings from termios, then calls `keyspan_send_setup(..., 1)` to enable RX/TX and reset data toggles. `keyspan_close` drops RTS/DTR, sends a close setup message, delays for legacy transfer behavior, and kills per-port URBs.

Writes are split into protocol-sized packets: USA90 can use 64 bytes with no prefix; the others reserve byte 0 for the request-ack flag and send up to 63 payload bytes. For devices with endpoint flipping, `out_flip` alternates between URBs. If an output URB remains busy for more than ten seconds, it is unlinked before retry.

Inbound control flow is protocol-specific. USA26/49/67 parse a leading status byte and mark parity/framing/overrun errors with TTY flip flags. USA28 can flip between two input URBs and treat input as raw data. USA90 switches between by-hand error/status framing at lower baud rates and DMA/raw framing above 57600. USA49WG receives aggregate messages containing a port number and payload length, demultiplexing the single global IN endpoint to individual TTY ports. Status callbacks update cached CTS/DSR/DCD/RI values and hang up the TTY on DCD drops where implemented.

## State and Persistence
All runtime state is in kernel memory and attached to `usb_serial` or `usb_serial_port`; there is no persistent storage beyond required firmware blobs. State includes cached termios/baud fields, cached modem state, input/output endpoint flip indexes, `resend_cont` control-message retry intent, and the allocated URB/buffer graph. Open/close mutates port enablement, RX/TX flags, DTR/RTS, and break state through device-specific setup messages. Disconnect and release kill/free URBs and buffers.

## Dependencies and Integration Points
The file depends on the Linux USB serial core, TTY flip-buffer APIs, URB submission/killing, `usb_control`/bulk/interrupt pipe helpers, `linux/usb/ezusb.h`, and the five local Keyspan message headers. It integrates with firmware loading through `MODULE_FIRMWARE` names under `keyspan/`, and with TTY modem-control semantics via `TIOCM_*`, `CRTSCTS`, `CSTOPB`, `PARENB`, `PARODD`, and `CSIZE`.

## Risks
The driver relies on detailed per-product endpoint and message metadata; a wrong product mapping can silently route data or setup packets to the wrong endpoint. Several comments note missing locking around write-room and global control URB state, while the resend paths rely on `resend_cont` and busy URB status rather than a stronger serialized control queue. Some receive paths do not resubmit on nonzero URB status, so only expected teardown errors should reach those paths. Break handling is incomplete for some receive-side error reports. Legacy busy handling uses delays and status polling around URBs, which is sensitive to callback context and disconnect races.

## Test Signals
Useful tests include firmware-load/renumeration checks for every pre-product ID, smoke opens for one-, two-, and four-port adapters, baud setting across supported rates, DTR/RTS and `TIOCMGET`/`TIOCMSET`, close/open cycling, high-rate USA90 DMA receive, USA49WG aggregate receive demultiplexing, endpoint-flip write throughput, DCD hangup behavior, and disconnect while status/control/data URBs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_pda.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_pda.c

## Purpose
This driver supports the USB Keyspan PDA serial converter and compatible Xircom/Entrega devices. It handles both fake pre-firmware devices and the real one-port serial adapter after firmware renumeration. The real device uses one bulk-out endpoint for TX and one interrupt-in endpoint for both RX data and status notifications.

## Important APIs, Types, and Functions
`struct keyspan_pda_private` stores estimated device TX room, unthrottle work, and the associated serial/port pointers. The main callbacks are `keyspan_pda_open`, `keyspan_pda_close`, `keyspan_pda_write`, `keyspan_pda_write_start`, `keyspan_pda_write_bulk_callback`, `keyspan_pda_rx_interrupt`, throttle/unthrottle handlers, `keyspan_pda_set_termios`, break control, modem-control helpers, and `keyspan_pda_fake_startup`.

Vendor requests include request 0 for baud selection, 3 for modem pins, 4 for break, 6 for querying write room, and 7 for requesting a TX unthrottle interrupt. Firmware names are `keyspan_pda/keyspan_pda.fw` and `keyspan_pda/xircom_pgs.fw`.

## Control Flow
The combined device table binds fake IDs and the post-firmware Keyspan PDA ID. Fake devices enter `keyspan_pda_fake_startup`, assert FX1 reset, select firmware by vendor, download it, and return nonzero so the device renumerates. Real devices use `keyspan_pda_port_probe` to allocate private state and initialize unthrottle work.

Open queries device write room with vendor request 6, stores it under `port->lock`, and submits the interrupt-in URB. RX interrupts are message-framed: type 0 carries data after the first byte; type 1 carries status. A status subcode of 2 signals TX unthrottle, restores estimated room to at least `KEYSPAN_TX_THRESHOLD`, starts more queued writes, and wakes the serial core.

Write data is first copied into the port FIFO. `keyspan_pda_write_start` checks whether the single write URB is free, the FIFO is nonempty, and estimated device room is nonzero. It drains up to the smaller of device room and bulk endpoint size into the URB, decrements `tx_room`, submits the URB, and schedules `unthrottle_work` when it exactly fills the remaining room. The work item asks the device to notify when room exceeds the threshold and then re-queries room to avoid missing an already-empty buffer.

## State and Persistence
State is per-port and volatile: `tx_room`, FIFO contents, the write URB free bit, and pending unthrottle work. Termios persistence is minimal because the hardware path only applies baud; unsupported framing/parity settings are copied back from the old termios state. Close kills the interrupt and write URBs, cancels unthrottle work synchronously, and resets the FIFO.

## Dependencies and Integration Points
The file depends on USB serial FIFO/write-URB helpers, TTY flip buffers, workqueues, spinlocks, and EZ-USB firmware loading. It integrates with TTY modem control through `TIOCM_*` bit mapping to a one-byte device pin field, with baud control through discrete index values, and with software flow control by killing/resubmitting the interrupt receive URB.

## Risks
TX room is an estimate maintained by the host and corrected by vendor queries/interrupts; a missed unthrottle signal or failed room query can stall writes. `keyspan_pda_write` returns the negative result of `keyspan_pda_write_start` after bytes may already have entered the FIFO, so callers must tolerate normal serial-core buffering semantics. The device largely ignores non-baud termios changes. RX throttle kills the only interrupt URB, so status notifications are also suppressed while throttled.

## Test Signals
Exercise firmware renumeration for Keyspan, Xircom, and Entrega fake IDs; open/close with interrupt URB submission; RX data and status type parsing; TX FIFO draining and unthrottle threshold behavior; failed room-query handling; baud fallback to 9600; break request behavior; DTR/RTS and modem input bit translation; and disconnect/close while work and write URB are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_pda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa26msg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa26msg.h

## Purpose
This header defines the Keyspan USA26/USA28X-style async message protocol consumed by `keyspan.c`. It is a wire-format contract for host-to-device port control messages, device-to-host status messages, and RX/TX data framing. It has no executable code but directly determines how setup messages and receive parsers interpret bytes.

## Important APIs, Types, and Constants
`struct keyspan_usa26_portControlMessage` contains requested configuration fields (`setClocking`, baud bytes, external/rx clocking, `setLcr`, LCR bits, flow-control flags, RTS/DTR-compatible outputs, prescaler) and action fields (`_txOn`, `_txOff`, `txFlush`, `txBreak`, `rxOn`, `rxOff`, `rxFlush`, `rxForward`, `returnStatus`, `resetDataToggle`). `struct keyspan_usa26_portStatusMessage` reports port number, CTS-like and DCD-like pins, DSR, RI, TX state, RX enablement, and control-response status.

LCR constants encode data bits, stop bits, and parity. RX error bits (`RXERROR_OVERRUN`, `RXERROR_PARITY`, `RXERROR_FRAMING`, `RXERROR_BREAK`) are shared with `keyspan.c` receive callbacks. Global control/status/debug message structs exist for status-toggle management but are lightly used by the current driver.

## Control Flow
`keyspan_usa26_send_setup` fills `keyspan_usa26_portControlMessage` when ports open, close, change termios, change break state, or update modem outputs. The driver sets `setClocking` and `setPrescaler` only when baud changes, always programs LCR and flow-control intent, and uses the action flags to enable/disable TX/RX depending on reset mode. `usa26_indat_callback` implements this header's RX framing: byte 0 is a status byte when bit 7 is clear, or alternating status/data pairs when bit 7 is set.

## State and Persistence
The header declares only packed-by-convention message layouts. Persistence is external: `keyspan.c` caches baud, cflag, flow-control mode, modem lines, and break state, then serializes them into these fields for each control transfer.

## Dependencies and Integration Points
It depends on Linux integer type `u8` from the including C file and is included only by `keyspan.c`. Field names deliberately encode historical USA17/USA26 dual meanings, so the integration point is both the Linux driver and the firmware running on Keyspan adapters.

## Risks
The structs are wire layouts without explicit `__packed`; because all fields are `u8`, padding risk is low, but reordering or changing field types would break firmware compatibility. Constants such as `MAX_DATA_LEN` and RX error names are duplicated across message headers, so accidental include-order or macro reuse changes can affect shared parser code. Break RX error reporting is defined here but only partially surfaced by the driver.

## Test Signals
Validate serialized setup size and field offsets, baud/prescaler programming for USA26-format products, correct LCR mapping for CS5-CS8/parity/stop bits, RX status/data and alternating error/data packet parsing, modem status update behavior, and open/close reset-data-toggle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa26msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa28msg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa28msg.h

## Purpose
This header documents and defines the USA28/USA18/USA19 message format used by older Keyspan adapters. It supplies control and status structures for `keyspan.c` and documents how parity-aware data packets differ from the USA26-family framing.

## Important APIs, Types, and Constants
`struct keyspan_usa28_portControlMessage` carries baud selection (`setBaudRate`, `baudLo`, `baudHi`), always-sent parity/flow/modem-output fields, forwarding and break timing parameters, and action flags for TX/RX enable, flush, break, force-XOFF, status return, and data-toggle reset. `struct keyspan_usa28_portStatusMessage` reports port number, CTS/DSR/DCD/RI, TX-off/XOFF state, `dataLost`, RX enablement, break state, invalid RS-232 input, and control response.

`TX_OFF` and `TX_XOFF` document transmit state bits. `RX_PARITY_BIT` and `TX_PARITY_BIT` describe parity byte encoding for data streams, though the current driver mostly treats USA28 input as raw bytes and does not fully implement parity handling.

## Control Flow
`keyspan_usa28_send_setup` builds this control message on open, close, break, modem, and termios changes. It computes baud divisor bytes through the product's baud callback, sets RTS/DTR, sets CTS flow-control intent, uses fixed forwarding and break thresholds, and toggles the RX/TX action fields based on open or close mode. `usa28_instat_callback` consumes `keyspan_usa28_portStatusMessage` reports and updates modem-line cache and DCD hangup behavior.

## State and Persistence
The header is stateless. The driver keeps runtime settings in `keyspan_port_private` and serializes them into this structure for every setup message. Status reports update volatile cached modem state only.

## Dependencies and Integration Points
The sole direct integration is `keyspan.c`. The comments are also part of the integration contract with Keyspan firmware, describing the USB OUT request-ack prefix and parity/data alternation rules.

## Risks
The driver's current receive path does not fully implement the parity-data framing described here; parity mode may be less complete than the protocol allows. As with other Keyspan headers, macro names overlap with other included message headers, so maintainers must treat the include set as one coupled protocol namespace. Invalid packet sizes in status callbacks are dropped after debug logging.

## Test Signals
Test USA28 open/close setup serialization, baud divisor fallback, RTS/DTR and CTS-flow fields, status length validation, DCD transition hangup, data receive with normal and parity modes if hardware/firmware supports it, and control response behavior after reset-data-toggle requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa28msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa49msg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa49msg.h

## Purpose
This header defines the USA49W four-port Keyspan global-control/global-status protocol. Unlike the per-port control endpoints used by some smaller adapters, USA49 messages put a port selector in the payload and send control over a global endpoint or, for USA49WG, endpoint zero.

## Important APIs, Types, and Constants
`struct keyspan_usa49_portControlMessage` begins with `portNumber` and includes clocking, baud divisor/prescaler, LCR, flow control, XON/XOFF characters, RTS/DTR setters, forwarding, loopback, TX/RX action flags, reset-data-toggle, and explicit `enablePort`/`disablePort`. `struct keyspan_usa49_globalControlMessage` controls global status behavior and remote wakeup. `struct keyspan_usa49_portStatusMessage` reports per-port modem pins, TX state, RX enabled state, control response, TX ACK, and RS-232 validity. Global status and debug structs identify non-port messages with `portNumber` values `0x80` and `0x81`.

## Control Flow
`keyspan_usa49_send_setup` fills the port-control message, sets `portNumber` from `port->port_number`, and sends it through `s_priv->glocont_urb`. For USA49WG it wraps the payload in a vendor control request on endpoint zero; for USA49W/USA49WLC it writes to the configured global control endpoint. `usa49_instat_callback` consumes `keyspan_usa49_portStatusMessage`; `usa49_glocont_callback` scans ports for pending `resend_cont` when a global control URB completes.

## State and Persistence
The header declares wire state only. Runtime enablement, modem line cache, baud cache, break state, and resend state live in `keyspan.c`. Status-suppression fields in the protocol imply firmware-side persistence until a later host control message, but the Linux driver does not expose a high-level persistent status policy.

## Dependencies and Integration Points
This header is included by `keyspan.c` and depends on `u8`. It is tightly coupled to the four-port endpoint maps in `keyspan_device_details`, especially the USA49WG special case with aggregate data input and endpoint-zero control.

## Risks
Global-control serialization means one URB is shared by all four ports; concurrent port reconfiguration can be delayed or coalesced through `resend_cont`. The protocol can suppress status messages, so incorrect use of global control could hide modem-line changes. The aggregate USA49WG path depends on the same status/error constants but parses data differently from ordinary USA49W devices.

## Test Signals
Test all four ports for independent open/close, DTR/RTS, baud, break, and receive paths; stress concurrent termios changes across ports; validate USA49WG endpoint-zero setup; verify global status reports by port number; exercise enable/disable status after close/open; and confirm TX ACK or busy resend behavior does not starve later ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa49msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa67msg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa67msg.h

## Purpose
This header defines the USA67 message format used for USA28XG-style two-port Keyspan devices running FX1 firmware. It resembles the USA26 protocol but adds an explicit port field to the control message and uses a global control endpoint for multi-port setup.

## Important APIs, Types, and Constants
`keyspan_usa67_portControlMessage` includes `port`, clocking/baud/prescaler fields, LCR, flow control, RTS/DTR-compatible outputs, forwarding and loopback fields, and TX/RX action flags. `keyspan_usa67_portStatusMessage` reports port number, CTS-like and DCD-like pins, TX state, TX ACK, RX enabled, and control response. Global control/status/debug typedefs support status-toggle messages. The LCR and RX error constants mirror the USA26-family definitions.

## Control Flow
`keyspan_usa67_send_setup` serializes this control structure to the device's global control URB. It sets `port` from the TTY port number, recomputes baud when needed, maps Linux termios to LCR bits, sets flow and XON/XOFF defaults, and uses open/close/intermediate reset modes to control TX/RX and data-toggle reset. `usa67_instat_callback` parses port status reports and updates cached CTS and DCD; `usa67_glocont_callback` scans all ports for pending setup resends after global control completion.

## State and Persistence
This file is a stateless protocol definition. Firmware may maintain port enablement, clocking, and status cadence based on messages, while Linux caches desired state in `keyspan_port_private` and resends when necessary.

## Dependencies and Integration Points
It is consumed by `keyspan.c` for products whose `keyspan_device_details.msg_format` is `msg_usa67`, currently USA28XG. It depends on the driver using the same endpoint mapping and message size expected by FX1 firmware.

## Risks
The status structure reports fewer modem lines than other formats, so DSR/RI are unavailable in `keyspan.c` for USA67 devices. Shared global control creates the same ordering risk as USA49: a busy control URB can defer setup from another port. RX error constants include break, but receive code does not fully surface break as a TTY break event.

## Test Signals
Validate two-port setup serialization, per-port `port` selection, baud/prescaler fallback, status report parsing, DCD hangup behavior, endpoint mapping for USA28XG, open/close reset-data-toggle, and concurrent setup resend across both ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa67msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa90msg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa90msg.h

## Purpose
This header defines the USA90 protocol used by the high-speed Keyspan USA19HS path. It supports explicit RX/TX modes, richer flow-control bitmaps, status counters, and a 64-byte raw data mode used by `keyspan.c` at higher baud rates.

## Important APIs, Types, and Constants
`struct keyspan_usa90_portControlMessage` contains setters and values for baud clocking, LCR, RX/TX mode, TX/RX flow control, XON/XOFF and immediate character transmission, RTS/DTR, forwarding thresholds, TX ACK policy, port enablement, flush/break/loopback state, RX flush/forward, XOFF cancellation, and status return. `struct keyspan_usa90_portStatusMessage` reports MSR-like state, CTS/DCD/DSR/RI, XOFF, break, overrun/parity/frame counters, port state, ACKs, and control response.

Constants define LCR bits, TX/RX flow-control masks, DMA/by-hand modes, RX error bits, port-state bits, and MSR bits. `RXMODE_DMA` and `TXMODE_DMA` are especially important because `keyspan_usa90_send_setup` selects DMA above 57600 baud and `usa90_indat_callback` changes receive parsing based on the cached baud.

## Control Flow
The driver uses `keyspan_usa90_send_setup` for USA19HS setup. On baud change it computes divisor bytes, sets RX/TX mode setters, and falls back to 9600 on invalid baud. Every setup message supplies the mode matching the cached baud, LCR when changed, flow-control fields, forwarding defaults, port enablement, break state, and RTS/DTR values. `usa90_instat_callback` updates modem-line cache from `keyspan_usa90_portStatusMessage` and treats the adapter as single-port.

## State and Persistence
The header stores no state itself. Runtime mode selection depends on `p_priv->baud`, so stale baud state would cause mismatched data parsing. Firmware-side counters for RX errors are reported in status messages, but the current driver primarily updates modem lines and does not expose all counters.

## Dependencies and Integration Points
It integrates only through `keyspan.c` and the USA19HS device metadata. The protocol is tied to the high-speed product's different endpoint layout with no input-ack endpoint and no endpoint flipping.

## Risks
Data parsing changes at the 57600 threshold; if the device and driver disagree about mode, RX bytes can be interpreted incorrectly. Several status fields and error counters are defined but underused, reducing observability for parity/framing/break diagnostics. The macro `USA_USA_MSR_RI` appears oddly named and must not be confused with generic MSR naming in other drivers.

## Test Signals
Test baud transitions around 57600, raw DMA receive versus by-hand status/data receive, invalid baud fallback, DTR/RTS and CTS flow-control fields, port enable/disable on open/close, break assertion, status-length tolerance, and disconnect during active out-control URB submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_usa90msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.c

## Purpose
This is the USB serial driver for KLSI KL5KUSB105-based adapters, specifically the PalmConnect USB serial adapter. It exposes one serial port through the generic USB serial data path but adds device-specific control requests for port settings, read enablement, modem-line polling, and KLSI packet framing.

## Important APIs, Types, and Functions
`struct klsi_105_port_settings` is the five-byte settings payload sent to the device. `struct klsi_105_private` caches that settings payload, cached modem line state, and a spinlock. Important functions include `klsi_105_chg_port_settings`, `klsi_105_get_line_state`, `klsi_105_open`, `klsi_105_close`, `klsi_105_set_termios`, `klsi_105_tiocmget`, `klsi_105_prepare_write_buffer`, and `klsi_105_process_read_urb`.

The `usb_serial_driver` uses generic throttle/unthrottle/open data machinery but overrides packet preparation and read processing to add/remove a little-endian length header.

## Control Flow
Probe allocates and initializes private settings to 9600 8-bit defaults. Open sends a known default settings packet, calls `usb_serial_generic_open` to start generic URB handling, sends `KL5KUSB105A_SIO_CONFIGURE_READ_ON`, polls line state, and caches it. On failure after generic open, it sends READ_OFF and closes generic URBs. Close sends READ_OFF and then calls `usb_serial_generic_close`.

Writes are framed by `klsi_105_prepare_write_buffer`: it drains FIFO bytes after a two-byte little-endian count and returns header plus payload length. Reads are inverse-framed by `klsi_105_process_read_urb`: empty packets are ignored; packets shorter than the header are rejected; declared length is clamped to actual payload size before being pushed to TTY.

Termios handling maps supported baud rates to KLSI constants, supports only 7 or 8 data bits, strips unsupported parity/stop/flow settings, encodes the accepted baud back into termios, and sends the updated five-byte settings payload. `klsi_105_tiocmget` polls modem line state on demand and returns cached DSR/CTS bits.

## State and Persistence
The only persistent state is volatile per-port state in `klsi_105_private`: current settings and last line state. Device read enablement is toggled on open/close. There is no firmware load or file-backed state.

## Dependencies and Integration Points
This file depends on `kl5kusb105.h` for vendor IDs, request codes, baud constants, data-bit constants, and line-state masks. It integrates with USB serial generic open/close/read/write paths, TTY termios, unaligned little-endian helpers, and the TTY flip buffer.

## Risks
The protocol is reverse engineered and comments explicitly note uncertain modem-line mapping and missing handshaking support. `B0` handling is not implemented. Unsupported termios settings are silently cleared or ignored, which can surprise applications expecting parity, stop bits, or hardware/software flow control. Length-framed reads are robust to overlong declarations but still depend on correct packet framing from device firmware.

## Test Signals
Test open error unwind, READ_ON/READ_OFF sequencing, write header encoding, malformed short and mismatched read packets, baud mapping and fallback, 7/8 data-bit changes, clearing of unsupported termios flags, `TIOCMGET` line polling, and close/disconnect during generic URB activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.h

## Purpose
This header defines the constants used by the KL5KUSB105 USB serial driver. It identifies the PalmConnect USB serial device, the KLSI vendor requests, supported baud/data-bit encodings, read-on/read-off configuration values, and provisional modem-line masks.

## Important APIs, Types, and Constants
`PALMCONNECT_VID` and `PALMCONNECT_PID` populate the driver's USB ID table. The anonymous enum maps supported baud rates to device-specific values. `kl5kusb105a_dtb_7` and `kl5kusb105a_dtb_8` encode data-bit choices. Request constants `KL5KUSB105A_SIO_SET_DATA`, `KL5KUSB105A_SIO_POLL`, and `KL5KUSB105A_SIO_CONFIGURE` are used for settings, line polling, and read configuration. `KL5KUSB105A_SIO_CONFIGURE_READ_ON` and `_READ_OFF` drive open/close read state. `KL5KUSB105A_DSR` and `KL5KUSB105A_CTS` map status bits to TTY modem lines.

## Control Flow
`kl5kusb105.c` includes this header and uses the baud/data constants in `klsi_105_set_termios`, request constants in `klsi_105_chg_port_settings`, `klsi_105_get_line_state`, `klsi_105_open`, and `klsi_105_close`, and line masks when translating polled status to `TIOCM_DSR` and `TIOCM_CTS`.

## State and Persistence
This header has no runtime state. Its constants define values stored at runtime in `struct klsi_105_private.cfg` and sent to the device.

## Dependencies and Integration Points
The header is private to the KLSI driver and assumes Linux USB/TTY types are supplied by the C file. The values are reverse-engineered hardware protocol constants, so the primary integration point is the device firmware rather than another source module.

## Risks
The modem-line masks are explicitly uncertain and currently make DSR and CTS identical. Several possible modem-line names are left in a disabled block, showing incomplete hardware understanding. Incorrect constants can affect open/read enablement or termios behavior globally for the only supported product.

## Test Signals
Tests should confirm USB ID matching, each baud constant accepted by the device, READ_ON/READ_OFF behavior, 7-bit versus 8-bit settings, and real hardware modem-line polling for CTS/DSR to validate or correct the duplicated masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kl5kusb105.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.c

## Purpose
This driver supports KOBIL USB smart-card terminals, including Adapter B, Adapter K, USBTWIN, and KAAN SIM products. It exposes one serial-like port but uses interrupt endpoints and vendor control requests tailored to smart-card APDU transfer and reader control rather than a conventional UART.

## Important APIs, Types, and Functions
`struct kobil_private` contains a 300-byte APDU staging buffer, fill/send indexes, and product-specific device type. `kobil_ctrl_send` and `kobil_ctrl_recv` wrap vendor endpoint control requests. Main hooks include `kobil_open`, `kobil_close`, `kobil_write`, `kobil_write_room`, `kobil_read_int_callback`, `kobil_tiocmget`, `kobil_tiocmset`, `kobil_set_termios`, `kobil_ioctl`, and `kobil_init_termios`.

## Control Flow
Probe initializes private state and records the product ID. Open queries hardware and firmware versions, configures Adapter B/K line settings to 9600 even parity one stop bit, resets queues for those adapters, and starts interrupt-in reads for USBTWIN, Adapter B, and KAAN SIM. Close kills interrupt OUT and IN URBs.

Reads arrive through `kobil_read_int_callback`, which pushes any interrupt payload directly into the TTY flip buffer and resubmits the interrupt-in URB. Writes are APDU-aware: bytes are appended to the private buffer until a complete block is detected. TWIN, KAAN SIM, and Adapter K use `buf[1] + 3` as complete length; Adapter B uses `buf[2] + 4`. Once complete, Adapter B/K temporarily stop reading, send the APDU in chunks no larger than `interrupt_out_size` with sleeps between chunks, reset buffer indexes, and restart reading for Adapter B/K.

Modem and termios controls are product-dependent. USBTWIN and KAAN SIM reject ioctl/modem operations. Adapter B supports DTR and RTS via vendor status-line requests; Adapter K effectively supports RTS. `kobil_set_termios` supports 1200 or 9600 baud plus parity/stop selection through the header's bit masks and clears mark/space parity.

## State and Persistence
All state is per-port and volatile. APDU staging persists across partial writes until the driver detects a complete block, then resets. Device queues can be reset through open and `TCFLSH`. Termios changes are sent to the device but not cached in private state beyond the actual device configuration.

## Dependencies and Integration Points
This file depends on `kobil_sct.h` for vendor request and bitmask definitions, the USB serial interrupt endpoint model, TTY flip buffers, and Linux ioctl/termios APIs. It integrates with smart-card user-space through serial writes that are expected to form APDU-sized protocol messages.

## Risks
Write buffering has no explicit locking around `filled`/`cur_pos`, so concurrent write paths would rely on serial-core serialization. `write_room` always returns 8 and does not reflect the 300-byte staging buffer. APDU completion is inferred from early bytes; malformed user data can fill the staging buffer and return `-ENOMEM`. The sleeps between interrupt chunks are timing-sensitive. Product-specific support is uneven and some devices do not support ioctl calls.

## Test Signals
Test each product ID path, APDU length detection for Adapter B versus others, buffer overflow rejection, interrupt chunking and restart-read behavior, hardware/firmware version requests, queue reset on open/flush, unsupported ioctl behavior for USBTWIN/KAAN SIM, termios encoding, and interrupt read resubmission after normal packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.h

## Purpose
This header defines the KOBIL smart-card terminal vendor request numbers and bitfields used by `kobil_sct.c`. It maps baud/parity/stop settings, status-line operations, queue purge operations, status-line query bits, and hardware/firmware version selectors.

## Important APIs, Types, and Constants
`SUSBCRequest_SetBaudRateParityAndStopBits` combines `SUSBCR_SBR_*` baud bits, `SUSBCR_SPASB_*` parity bits, and stop-bit bits into one vendor request value. `SUSBCRequest_SetStatusLinesOrQueues` uses `SUSBCR_SSL_*` values for RTS/DTR and queue purge operations. `SUSBCRequest_GetStatusLineState` returns `SUSBCR_GSL_*` status bits including RXCHAR, TXEMPTY, CTS, DSR, RLSD, BREAK, ERR, and RING. `SUSBCRequest_Misc` and `SUSBCRequest_GetMisc` provide reset and version operations.

## Control Flow
`kobil_sct.c` uses these constants during open to set default Adapter B/K line settings and reset queues, during termios changes to encode baud/parity/stop selections, during modem control to set/clear RTS or DTR, during `TIOCMGET` to read DSR state, and during `TCFLSH` to reset all queues.

## State and Persistence
The header is stateless. The values sent with these requests affect transient reader hardware state such as line configuration, queues, and modem outputs.

## Dependencies and Integration Points
It is private to the KOBIL driver and encodes the contract with KOBIL firmware. User-visible integration is indirect through TTY termios, modem ioctls, and flush ioctls.

## Risks
The masks permit more baud rates than the C driver exposes; adding support must validate firmware behavior per product. DTR behavior is product-specific in the driver, and incorrect use of status-line bits could affect smart-card reader operation. Version field comments describe packed values but the driver reads raw bytes.

## Test Signals
Validate baud/parity/stop request values against hardware, RTS/DTR operations per product, queue purge behavior, status-line bit mapping, and hardware/firmware version retrieval for all supported KOBIL products.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/kobil_sct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.c

## Purpose
This driver supports Magic Control Technology USB-RS232 converters and compatible Sitecom, D-Link, and Belkin devices. It exposes one serial port, programs UART-like settings through vendor control requests, reads data through a second interrupt-in endpoint workaround, tracks modem status changes, and implements TTY modem, break, throttle, and termios operations.

## Important APIs, Types, and Functions
`struct mct_u232_private` stores the special read URB, spinlock, cached modem control state, last LCR/LSR/MSR, and RX throttle flags. Key functions include `mct_u232_calculate_baud_rate`, `mct_u232_set_baud_rate`, `mct_u232_set_line_ctrl`, `mct_u232_set_modem_ctrl`, `mct_u232_get_modem_stat`, `mct_u232_msr_to_icount`, `mct_u232_msr_to_state`, `mct_u232_open`, `mct_u232_close`, `mct_u232_read_int_callback`, `mct_u232_set_termios`, `mct_u232_break_ctl`, `mct_u232_tiocmget`, `mct_u232_tiocmset`, `mct_u232_throttle`, and `mct_u232_unthrottle`.

## Control Flow
Probe validates the expected second interrupt-in endpoint, stores that URB as the data-read URB, and points its context at the primary port. Open adjusts Sitecom bulk-out size, initializes DTR/RTS according to baud state, programs modem control and 8N1 line control, polls current modem status, submits the special read URB, and also submits the normal interrupt-in URB for status. Close kills both URBs and delegates to generic close.

Baud setting converts Linux speed to either a divisor (`115200 / baud`) or product-specific code for Sitecom/Belkin variants, sends `MCT_U232_SET_BAUD_RATE_REQUEST`, then sends two extra vendor requests mirroring the Windows driver: an unknown zero-byte request and a CTS gating request based on `CRTSCTS`. Termios updates baud, handles B0 by dropping or reasserting DTR/RTS, maps parity/data/stop to LCR bits, clears mark/space parity, sends line control, and caches state.

The read interrupt callback handles two kinds of URBs. When the transfer buffer length is greater than two, it treats the packet as bulk-like data and pushes it to TTY. Otherwise, it treats data[0] as MSR and data[1] as LSR, updates cached modem state and icount deltas, wakes modem-status waiters, and resubmits. LSR error handling is present only in disabled code.

## State and Persistence
Per-port volatile state includes control lines, last LCR/MSR/LSR, throttle state, and the selected special read URB. Device register state persists in hardware until changed or unplugged. No file-backed state exists.

## Dependencies and Integration Points
This file depends on `mct_u232.h`, Linux USB serial core, generic modem wait/count helpers, TTY termios, unaligned little-endian helpers, and spinlocks. It integrates with user-space through normal serial data, `TIOCMGET`/`TIOCMSET`, `TIOCMIWAIT`, `get_icount`, break control, and hardware-flow-control behavior.

## Risks
The hardware protocol is reverse engineered and includes unknown requests. The second endpoint workaround assumes `serial->port[1]->interrupt_in_urb` exists and remains valid for the primary port. LSR error reporting is not implemented, so parity/framing/break errors may be invisible. Throttle only drops RTS when CRTSCTS is enabled; non-RTS flow control is not implemented. Product-specific baud coding is subtle and could regress compatible devices.

## Test Signals
Test all USB IDs, endpoint validation failure, Sitecom 16-byte bulk-out quirk, baud mappings for regular and Sitecom/Belkin devices, B0 DTR/RTS behavior, CTS gating request with and without CRTSCTS, MSR-to-icount updates, `TIOCMIWAIT`, data URB versus status URB parsing, throttle/unthrottle RTS changes, and break LCR programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.h

## Purpose
This header defines the Magic Control Technology USB-RS232 protocol constants used by `mct_u232.c`: supported vendor/product IDs, vendor request numbers and sizes, LCR/MCR/MSR/LSR bit encodings, and a local forward declaration for baud-rate calculation.

## Important APIs, Types, and Constants
USB IDs cover original MCT, Sitecom, D-Link DU-H3SP, and Belkin F5U109 variants. Request constants define get/set modem status, baud rate, line control, modem control, the unknown post-baud request, and CTS gating. LCR constants map break, parity, data bits, and stop bits. MCR constants map DTR/RTS output encoding. MSR constants map current and delta modem-line bits. LSR constants map transmit and receive error/status bits.

## Control Flow
`mct_u232.c` uses these constants for every vendor control transfer, for termios-to-LCR encoding, for modem control and status translation, for `icount` delta increments, for break handling, and for the data/status indexes in interrupt packets.

## State and Persistence
The header is stateless. Its values are cached in `mct_u232_private.last_lcr`, `last_msr`, `last_lsr`, and `control_state`, and are sent to or read from device firmware/register emulation.

## Dependencies and Integration Points
It is a private header for the MCT driver and assumes Linux USB serial and `speed_t` declarations are present when included. The comments document reverse-engineered protocol behavior and serve as implementation guidance for compatible hardware variants.

## Risks
The header contains a duplicate `MCT_U232_LSR_OE` definition and a static function prototype in a header, which is safe only because it is included by the single C file defining the static function. Some request-size comments differ from observed Belkin/Sitecom behavior, so changing transfer sizes can regress devices that currently tolerate the generic four-byte path.

## Test Signals
Validate request IDs and payload sizes with hardware traces, regular versus code-based baud behavior, MCR bit mapping, MSR delta/current bit translation, LSR error bit availability, and compatibility across MCT, Sitecom, D-Link, and Belkin devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/mct_u232.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/metro-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/metro-usb.c

## Purpose
This driver supports Metrologic/Honeywell USB POS/scanner devices in bidirectional and unidirectional modes. It exposes a one-port USB serial interface using interrupt-in reads, optional interrupt-out mode commands for unidirectional devices, and simple modem-control state for RTS/DTR.

## Important APIs, Types, and Functions
`struct metrousb_private` stores a spinlock, throttle flag, and cached modem control state. Important functions include `metrousb_is_unidirectional_mode`, `metrousb_calc_num_ports`, `metrousb_send_unidirectional_cmd`, `metrousb_read_int_callback`, `metrousb_open`, `metrousb_cleanup`, `metrousb_set_modem_ctrl`, `metrousb_port_probe`, `metrousb_port_remove`, `metrousb_throttle`, `metrousb_unthrottle`, `metrousb_tiocmget`, and `metrousb_tiocmset`.

## Control Flow
Probe allocates private state. `calc_num_ports` enforces that unidirectional devices expose an interrupt-out endpoint because open/close commands are sent there. Open clears private state, clears halt on the interrupt-in pipe, fills the interrupt-in URB with the driver callback and interval 1, submits it, then sends `UNI_CMD_OPEN` if the product is unidirectional. Close kills the interrupt-in URB and sends `UNI_CMD_CLOSE`.

Read callbacks push any received interrupt payload to the TTY flip buffer, check whether the port has been throttled, and resubmit the interrupt URB only when not throttled. Throttle sets the flag and lets the current callback stop resubmission; unthrottle clears the flag and submits the URB again. `TIOCMSET` updates cached RTS/DTR state under the spinlock and sends a vendor control request intended to set modem control.

## State and Persistence
State is entirely per-port and volatile: current throttle flag and cached `TIOCM_*` control state. Device mode is derived from product ID each time. Unidirectional open/close state is maintained in device firmware after interrupt-out commands.

## Dependencies and Integration Points
The file depends on USB serial interrupt endpoint handling, TTY flip buffers, spinlocks, and vendor control/interrupt messages. It registers device IDs for `0x0c2e:0x0720`, `0x0c2e:0x0700`, and an MS7820 interface-class match. User-space integration is conventional serial reads plus modem-control ioctls.

## Risks
`metrousb_set_modem_ctrl` computes an `mcr` value but passes `control_state` as the USB request value rather than `mcr`; this may be intentional for firmware or a bug worth hardware verification. Throttle suppresses URB resubmission only after the current callback, so one already-submitted packet may still arrive. Unidirectional mode depends on interrupt-out command delivery and exact byte count. The driver has no custom termios handling and no explicit write path.

## Test Signals
Test bidirectional and unidirectional product IDs, missing interrupt-out rejection for unidirectional mode, open/close commands and byte counts, interrupt read resubmission, throttle/unthrottle stop and restart, modem `TIOCMGET`/`TIOCMSET` behavior on hardware, disconnect during open error unwind, and MS7820 interface-class matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/metro-usb.c -->
