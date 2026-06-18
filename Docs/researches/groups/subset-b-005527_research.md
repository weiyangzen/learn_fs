# Research: subset-b-005527 USB serial driver files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/digi_acceleport.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/digi_acceleport.c

## Purpose

This file implements the Linux USB serial driver for Digi AccelePort USB-2 and USB-4 adapters. It registers separate `usb_serial_driver` instances for the two-port and four-port products, maps Digi's command protocol onto tty operations, and uses an extra USB serial port as an out-of-band command channel.

## Important APIs, Types, And Functions

The main private types are `struct digi_serial` and `struct digi_port`. `digi_serial` records the out-of-band port, its index, and a one-shot startup flag. `digi_port` stores per-port locks, the small write coalescing buffer, modem-signal cache, transmit-idle state, throttle state, wait queues, and the owning `usb_serial_port`.

Important callbacks are wired through `digi_acceleport_2_device` and `digi_acceleport_4_device`: `digi_open`, `digi_close`, `digi_write`, `digi_write_bulk_callback`, `digi_read_bulk_callback`, `digi_set_termios`, `digi_break_ctl`, `digi_tiocmget`, `digi_tiocmset`, `digi_rx_throttle`, and `digi_rx_unthrottle`. Command helpers include `digi_write_oob_command`, `digi_write_inb_command`, `digi_set_modem_signals`, and `digi_transmit_idle`.

## Control Flow

Module registration uses `module_usb_serial_driver()` with the combined VID/PID table. Attach allocates `struct digi_serial`, identifies the hidden OOB port as `num_ports`, initializes that port, and stores serial-private data. Normal data ports are initialized through `digi_port_probe`.

Opening a port calls `digi_startup_device()` to submit read URBs for all data ports plus the OOB endpoint exactly once. It then enables automatic modem-signal reporting, flushes TX/RX FIFOs through OOB commands, and pushes current termios settings. Writes frame tty bytes as `DIGI_CMD_SEND_DATA` with a length byte; single-byte writes can be buffered while a URB is outstanding. In-band commands share the same write URB and are ordered after any buffered data.

Read URBs dispatch by port number. Data ports expect `[opcode][len][status][payload...]`, translate Digi error bits into tty flags, and respect throttle by deferring URB resubmission. The OOB callback consumes four-byte command responses, updates modem signal state, wakes close/flush/transmit-idle waiters, and notifies tty wakeups on CTS changes.

## State And Persistence

The driver has no persistent storage. Runtime state lives in USB serial private structures, URBs, wait queues, tty flip buffers, cached modem flags, and device-side UART state. `ds_device_started` prevents duplicate read-URB submission. Close waits for transmit idle, sends OOB shutdown commands, kills outstanding writes, and clears `dp_write_urb_in_use`.

## Dependencies And Integration Points

The file depends on the USB serial core, tty core, URB APIs, wait queues, spinlocks, and Digi's adapter protocol constants. Integration points include tty modem-control ioctls, termios baud/parity/flow-control settings, generic USB disconnect handling, and kernel error counters via tty flags.

## Risks

The OOB port indexing is protocol-specific; off-by-one mistakes can treat a data port as the command endpoint. Several paths sleep or wait while coordinating with spinlocks through `cond_wait_interruptible_timeout_irqrestore`, so missed wakeups or early returns can leave locks or in-use flags inconsistent. Packet validation is strict for length but unknown opcodes are mostly logged, so protocol drift may silently drop events. Close has fixed sleeps and a FIXME noting transmit-idle belongs in wait-until-sent logic. The write buffer is intentionally tiny, so throughput behavior depends on timely write callbacks.

## Test Signals

Useful validation includes build coverage for both USB IDs, probing USB-2 and USB-4 devices, tty open/close under disconnect, baud and parity changes, CRTSCTS and XON/XOFF behavior, `TIOCMGET`/`TIOCMSET`, break signaling, throttle/unthrottle with continued RX, close-time drain, and malformed/short USB packet logging without crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/digi_acceleport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/empeg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/empeg.c

## Purpose

This file is a minimal USB serial driver for the Empeg Mark I/II car player. It binds one VID/PID pair, exposes a single tty port, resets the device configuration during attach, and applies the raw 115200 8N1 tty setup expected by the player.

## Important APIs, Types, And Functions

The driver defines `empeg_device`, a `struct usb_serial_driver` with one port, a 256-byte bulk-out buffer, generic USB serial throttle/unthrottle callbacks, `empeg_startup` as `.attach`, and `empeg_init_termios` as `.init_termios`. `id_table` matches `EMPEG_VENDOR_ID` and `EMPEG_PRODUCT_ID`.

`empeg_startup()` verifies the active USB configuration is configuration 1 and calls `usb_reset_configuration()`. `empeg_init_termios()` clears canonical processing, echo, signals, output post-processing, input translations, parity, and existing baud bits, sets `CS8`, and encodes 115200 baud.

## Control Flow

The module registers through `module_usb_serial_driver()`. When a matching device is attached, the USB serial core invokes `empeg_startup()`. If the device is not on configuration 1, attach fails with `-ENODEV`; otherwise the active configuration is reset and the core continues with generic serial-port setup. Port I/O is handled by the USB serial generic implementation because this file does not supply custom open, close, read, write, or termios-change callbacks beyond initial termios.

## State And Persistence

The driver owns no private data and no persistent state. Device state is limited to USB configuration reset effects and the tty termios initialized for each tty instance. Runtime buffers, URBs, throttling state, and tty lifetime are all owned by the USB serial core.

## Dependencies And Integration Points

The file depends on the USB serial core, tty termios helpers, module USB ID matching, and generic USB serial throttle/unthrottle handling. It integrates with user space only as a single ttyUSB-style serial device configured for raw 115200 communication.

## Risks

The attach path assumes configuration value 1; devices with a different but compatible descriptor layout would be rejected. Resetting the configuration during attach can disrupt endpoints or interface state if a composite device variation appeared. The driver does not implement runtime termios enforcement after initialization, so later user changes may be accepted by the tty layer even though comments say the player only supports 115200. There is no custom recovery for short reads, stalls, or device-specific framing.

## Test Signals

Signals include successful probe for `084f:0001`, attach failure when forced to a non-1 configuration, creation of exactly one tty port, initial termios showing 115200 8N1 raw mode, generic read/write data transfer, and clean disconnect/unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/empeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ezusb_convert.pl -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ezusb_convert.pl

## Purpose

This Perl helper converts Intel HEX firmware input from stdin into a C header containing a sorted `static const struct ezusb_hex_record` array. The generated output is meant for EZ-USB firmware-loading users such as USB serial drivers.

## Important APIs, Types, And Functions

The script is straight-line Perl. It requires one argument, `$basename`, used to name the output array as `${basename}_firmware`. It reads lines matching Intel HEX syntax, extracts byte count, address, record type, payload, and optional DOS carriage return, stores records as `[$addr, \@bytes]`, sorts by address, and prints C initializer rows ending with `{ 0xffff, 0, {0x00} }`.

## Control Flow

On startup the script dies if no basename is provided. For each stdin line, it parses `:<len><addr><type><data><cr>`, dies on malformed input, stops at record type `01`, converts the declared number of data bytes from hexadecimal to binary bytes, and appends the record. After sorting by address, it emits a comment header, the array declaration, one initializer per record, and a sentinel.

## State And Persistence

There is no persistent state. In-memory state consists of `@records` and `@sorted_records`. The script writes generated C to stdout only; callers decide whether to redirect it into a header.

## Dependencies And Integration Points

The script depends on Perl core functions such as regex matching, `hex`, `pack`, `unpack`, `sort`, and `printf`. The generated C depends on `struct ezusb_hex_record` being defined by the including firmware loader. It is integrated into build or maintenance workflows by shell redirection rather than a kernel runtime path.

## Risks

The parser accepts `\w` rather than strict hex characters, so non-hex word characters may reach `hex`/`pack` behavior instead of being rejected early. It ignores the Intel HEX checksum byte rather than validating it, and it does not support extended linear or segment address records, so firmware above the base 16-bit address model would be mishandled. The comment says the source is `${basename}.s`, while usage describes `.hex`, which can confuse provenance. Duplicate or overlapping addresses are sorted but not coalesced or rejected.

## Test Signals

Good tests include conversion of a small HEX file with multiple out-of-order data records, EOF handling, malformed-line failure, no-basename failure, checksum-corrupted input showing the current lack of validation, and compiling a generated header in a file that defines `struct ezusb_hex_record`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ezusb_convert.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/f81232.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/f81232.c

## Purpose

This file supports Fintek F81232 one-port USB serial adapters and the F81532A/F81534A/F81535/F81536 family exposed through a compatibility path. It implements register access over USB control endpoint 0, UART termios programming, modem-status tracking, interrupt-in handling, RX packet decoding, suspend/resume, and a separate control USB driver that enables all F81534A-family serial ports.

## Important APIs, Types, And Functions

`struct f81232_private` stores the per-port mutex, cached MCR/MSR/LCR, selected baud base, two work items, and the port pointer. Register helpers are `f81232_get_register`, `f81232_set_register`, and `f81232_set_mask_register`. Serial callbacks include `f81232_open`, `f81534a_open`, `f81232_close`, `f81232_set_termios`, `f81232_break_ctl`, `f81232_tiocmget`, `f81232_tiocmset`, `f81232_dtr_rts`, `f81232_tx_empty`, `f81232_process_read_urb`, `f81534a_process_read_urb`, `f81232_read_int_callback`, `f81232_suspend`, and `f81232_resume`.

The F81534A control path uses `f81534a_ctrl_probe`, `f81534a_ctrl_disconnect`, and `f81534a_ctrl_resume` to write `F81534A_CTRL_CMD_ENABLE_PORT`.

## Control Flow

`f81232_init()` first registers the control-interface `usb_driver`, then registers two USB serial drivers. Port probe allocates private state and initializes work. F81534A port probe additionally programs the GPIO mode register for default RS232 mode.

Open enables FIFOs and modem-status interrupts, applies termios, submits the interrupt URB, then starts generic bulk I/O. F81534A open first programs larger FIFO/trigger settings. Interrupt URBs decode IIR-style status; modem-status changes schedule `interrupt_work`, while LSR changes are read from bulk-in data or cleared later. F81232 bulk-in packets are pairs of `[LSR][DATA]`; F81534A packets are `[LEN][DATA...][LSR]`. Termios chooses one of four baud bases, writes clock selection, toggles DLAB to program divisor registers, then writes LCR parity, stop, word length, and break state.

## State And Persistence

Per-port shadow state persists while the USB serial port exists. `modem_control`, `modem_status`, and `shadow_lcr` cache register values under `priv->lock`; `baud_base` is exposed through `get_serial`. Work items serialize deferred MSR and LSR register reads. The device registers retain UART configuration until reset, close, suspend, disconnect, or later termios updates.

## Dependencies And Integration Points

The file depends on Linux USB serial, tty, serial register definitions, interrupt URBs, workqueues, and USB control-message helpers. It integrates with generic `tiocmiwait`, DCD change handling, break/sysrq handling, tty flip buffers, and PM suspend/resume. The control-interface driver is a non-serial USB driver needed to create/enable all ports on the multi-port family.

## Risks

The shared register model relies on correct USB control responses; retries are limited to the lower-level USB helpers. Baud programming has several staged register writes, and failures can leave DLAB or clock state partially changed. `f81232_open()` does not disable the port if interrupt-URB submission fails after `f81232_port_enable()`. The F81534A control driver's dummy read is required for fast load/unload stability, so removing it can make port enumeration incomplete. RX decoders silently drop malformed packets, which protects tty input but can hide device framing regressions.

## Test Signals

Test signals include probing each supported VID/PID class, verifying the control interface enables all expected ports, open/close with interrupt URBs, baud fallback and exact divisor cases, parity/stop/word/break changes, DTR/RTS ioctls, DCD wakeups and `tiocmiwait`, F81232 pair-framed RX, F81534A length-framed RX, suspend/resume with open ports, and fast module reload loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/f81232.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/f81534.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/f81534.c

## Purpose

This file is the dedicated Fintek F81532/F81534 USB-to-serial bridge driver. These devices expose up to four UARTs over one bulk-in endpoint and one shared 512-byte bulk-out endpoint. The driver discovers board configuration from internal flash, maps physical UARTs to tty ports, configures RS232/RS485 GPIO state, multiplexes writes, demultiplexes RX/MSR/TX-empty blocks, and handles termios and modem-control operations per port.

## Important APIs, Types, And Functions

`struct f81534_serial_private` stores flash configuration bytes, physical-to-logical tty mapping, custom-setting index, opened-port count, and `urb_mutex` for shared read URBs. `struct f81534_port_private` stores MCR/LCR locks, LSR work, TX-empty bit, MSR spinlock, baud base, shadow registers, and physical port number.

Core helpers include `f81534_get_register`, `f81534_set_register`, `f81534_read_flash`, `f81534_calc_num_ports`, `f81534_prepare_write_buffer`, `f81534_submit_writer`, `f81534_set_port_config`, `f81534_process_read_urb`, `f81534_process_per_serial_block`, `f81534_set_port_output_pin`, and `f81534_update_mctrl`.

## Control Flow

Probe-time `calc_num_ports` validates endpoint packet sizes, allocates serial-private data, reads custom or default flash configuration, checks for hardware-disabled ports, assigns tty indexes, and aliases all logical bulk-out endpoints to endpoint 0. Port probe maps the logical port to a physical UART, enables UART interrupts except LSR interrupt, sets RS485 clock flags from configuration, and drives transceiver GPIO pins.

Open clears FIFOs, applies termios, reads initial MSR, and submits shared read URBs only when the first port opens. Writes enqueue bytes into the port kfifo, then submit one 512-byte frame if the hardware has reported TX empty. Each frame contains four fixed 128-byte port slots; only the active physical port slot carries outgoing bytes. Read URBs contain one or more 128-byte blocks tagged as receive data, TX empty, or MSR change. The receive path translates per-character LSR bytes into tty flags and schedules LSR clearing work on errors.

## State And Persistence

Flash configuration is read but not modified. Runtime state includes logical/physical mappings, opened-port count, per-port shadow MCR/LCR/MSR/clock values, TX-empty bits, work items, and the shared read URB lifecycle. Device UART configuration persists in hardware registers while powered. Close kills pending writes, resets the port kfifo, decrements the shared open count, and kills read URBs when the final port closes.

## Dependencies And Integration Points

The driver depends on USB serial core multiplexing hooks, tty kfifo buffering, tty flip buffers, UART register bit definitions, workqueues, mutexes/spinlocks, USB control transfers, and PM resume. It integrates with `calc_num_ports`, `prepare_write_buffer`-like custom writing through `.write`, modem ioctls, `get_serial`, DCD handling, sysrq/break handling, and shared endpoint management.

## Risks

Endpoint size assumptions are hard requirements; unexpected descriptors fail probe. Flash parsing supports a narrow configuration model and falls back to four ports if no ports are found, which is necessary for old chips but can mask corrupt configuration. All ports share one read stream and one write URB format, so physical-to-logical mapping errors route data to the wrong tty. TX progress depends on TX-empty tokens; missing tokens can stall queued data. LSR interrupts are deliberately disabled because overrun plus LSR interrupt can hang the device, so error clearing relies on bulk data and deferred work.

## Test Signals

Useful tests include endpoint-size validation, old and new configuration flash layouts, disabled-port detection, physical-to-tty mapping, RS232/RS485/inverted GPIO output states, concurrent opens, first-open/final-close read URB behavior, per-port writes under shared bulk-out framing, TX-empty-driven draining, MSR delta and DCD handling, LSR error injection, suspend/resume with queued data, and malformed block-size/token handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/f81534.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio.c

## Purpose

This file is the main FTDI USB serial converter driver. It binds a very large VID/PID table, identifies FTDI chip families from descriptors, programs FTDI-specific baud/data/flow-control requests, parses status-prefixed bulk input, supports modem-control ioctls and legacy serial flags, exposes latency/event sysfs attributes, and optionally registers CBUS pins as GPIOs.

## Important APIs, Types, And Functions

`enum ftdi_chip_type` covers SIO, FT232 variants, FT2232/FT4232 variants, HP/HA devices, and FT-X. `struct ftdi_private` stores chip type, baud base, custom divisor flags, last data-control value, modem outputs, previous modem status, TX-empty status, channel index, forced settings, latency, max packet size, config lock, and optional GPIO state. `struct ftdi_quirk` supplies probe and port setup hooks for JTAG, USB-UIRT, HE-TIRA1, ST Micro Connect Lite, and 8U2232C cases.

Key functions include `ftdi_probe`, `ftdi_port_probe`, `ftdi_determine_type`, `ftdi_open`, `ftdi_set_termios`, `change_speed`, `get_ftdi_divisor`, `update_mctrl`, `ftdi_process_read_urb`, `ftdi_process_packet`, `ftdi_prepare_write_buffer`, `ftdi_get_modem_status`, `ftdi_tiocmget`, `ftdi_tiocmset`, `ftdi_break_ctl`, `ftdi_tx_empty`, `get_serial_info`, and `set_serial_info`. GPIO support is under `CONFIG_GPIOLIB`.

## Control Flow

Probe first runs optional quirk filtering, then stores quirk data. Port probe allocates private state, applies quirk port defaults, determines chip type and channel from `bcdDevice` and interface number, fixes endpoint packet size if needed, reads or defaults latency, writes latency, and initializes CBUS GPIOs when supported. Open resets the SIO channel, applies current termios, and enters generic USB serial open.

Termios changes program data bits, parity, stop bits, baud divisor, modem outputs, and flow control through vendor control messages. RX processing walks the URB in max-packet-size chunks; each packet starts with modem and line status bytes, followed by payload. Status changes update icount and DCD handling; line errors become tty flags; payload is pushed to the tty flip buffer. SIO writes reserve a length/status byte in each packet, while newer chips send raw bulk payload.

## State And Persistence

Private state persists for the lifetime of each USB serial port. Cached fields include latency, custom divisor, last DTR/RTS, last data format for break control, previous status for delta reporting, TX-empty state, and GPIO direction/value caches. Device EEPROM is read for CBUS configuration but not written. Hardware state changes through control requests and lasts until reset, reconfiguration, disconnect, or another driver/user action.

## Dependencies And Integration Points

The file depends on `ftdi_sio.h`, `ftdi_sio_ids.h`, USB serial core, tty termios, serial ioctls, USB vendor control transfers, sysfs device attributes, optional gpiolib, runtime PM for GPIO bitmode/pin reads, and generic USB serial throttling and wait/io-count helpers. It integrates with user space through tty devices, sysfs `latency_timer` and `event_char`, legacy `serial_struct` flags, and optional `ftdi-cbus` GPIO chips.

## Risks

The ID table is large and quirk-sensitive; an overly broad match can bind interfaces reserved for JTAG or vendor protocols. Chip detection relies on `bcdDevice` and special FT232B fallback behavior. Baud divisor math differs across SIO, AM/BM, FT-X, and high-speed chips, so regressions can affect only one family. Read packets may be processed more than once, so modem delta tracking must remain idempotent. `last_dtr_rts` has a FIXME about locking. CBUS GPIO cannot read initial output state from hardware and must avoid pins not configured as GPIO in EEPROM.

## Test Signals

Signals include probe across representative chip families, quirk devices rejecting reserved interfaces, baud tests from low speeds through 3 Mbaud and high-speed 12 Mbaud paths, B0 DTR/RTS drop and restore, hardware and XON/XOFF flow control, parity/frame/break/overrun accounting, `TIOCMGET`/`TIOCMSET`/`TIOCSERGETLSR`, latency/event sysfs reads and writes, SIO packetized writes, modern bulk writes, CBUS GPIO discovery and direction/value operations, suspend/autopm during GPIO access, and malformed/status-only packet handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio.h

## Purpose

This header documents and defines the FTDI vendor protocol used by `ftdi_sio.c`. It contains request numbers, request types, channel identifiers, baud divisor constants, data-format bit fields, modem-control masks, flow-control modes, latency/event/bitmode/EEPROM requests, CBUS GPIO mux constants, and status-byte masks for bulk input.

## Important APIs, Types, And Functions

The header has no functions. Important definitions include `FTDI_SIO_RESET`, `FTDI_SIO_MODEM_CTRL`, `FTDI_SIO_SET_FLOW_CTRL`, `FTDI_SIO_SET_BAUD_RATE`, `FTDI_SIO_SET_DATA`, `FTDI_SIO_GET_MODEM_STATUS`, `FTDI_SIO_SET_LATENCY_TIMER`, `FTDI_SIO_SET_BITMODE`, `FTDI_SIO_READ_PINS`, `FTDI_SIO_READ_EEPROM`, `CHANNEL_A` through `CHANNEL_D`, and `enum ftdi_sio_baudrate`.

For data format it defines `FTDI_SIO_SET_DATA_PARITY_*`, `FTDI_SIO_SET_DATA_STOP_BITS_*`, and `FTDI_SIO_SET_BREAK`. For modem and flow control it defines `FTDI_SIO_SET_DTR_*`, `FTDI_SIO_SET_RTS_*`, `FTDI_SIO_DISABLE_FLOW_CTRL`, `FTDI_SIO_RTS_CTS_HS`, `FTDI_SIO_DTR_DSR_HS`, and `FTDI_SIO_XON_XOFF_HS`. Status masks include `FTDI_RS0_CTS`, `FTDI_RS0_DSR`, `FTDI_RS0_RI`, `FTDI_RS0_RLSD`, `FTDI_RS_OE`, `FTDI_RS_PE`, `FTDI_RS_FE`, `FTDI_RS_BI`, and `FTDI_RS_TEMT`.

## Control Flow

There is no executable control flow, but the constants define the protocol flow used by the C driver: reset or purge through request 0, set baud by encoding divisors into `wValue`/`wIndex`, set data characteristics through request 4, control DTR/RTS through mask/value bits, select flow-control protocol through high `wIndex` bits, read modem status through an IN control request, tune latency/event behavior through control requests, and parse the first two bytes of every bulk-in packet as modem and line status.

## State And Persistence

The header owns no state. It describes hardware state that the driver can set or observe: UART format, break state, DTR/RTS, flow control, latency timer, event character, bitbang mode, CBUS pin level, EEPROM words, modem inputs, line errors, and transmitter-empty status.

## Dependencies And Integration Points

`ftdi_sio.c` includes this header directly. The definitions align Linux tty/serial concepts with FTDI USB vendor commands and with EEPROM/CBUS behavior used by optional gpiolib integration. The file also documents legacy descriptor and endpoint data formats used by maintainers when validating packet parsing.

## Risks

Because this header is protocol authority, incorrect bit definitions propagate into every FTDI operation. The comments include historical notes and old-device caveats; implementation changes must preserve differences between SIO, AM/BM, and newer chips. The modem-control comment notes DTR and RTS cannot be set with one command, while the implementation composes both bits in one value, so behavior should be checked against real devices. Documentation-only descriptor examples can become stale relative to modern variants.

## Test Signals

Validation is indirect: build `ftdi_sio.c`, exercise every request family on hardware or USB emulation, compare baud divisor encodings against FTDI application notes, verify status-byte masks by injecting CTS/DSR/RI/DCD and line errors, test latency/event/EEPROM control messages, and confirm CBUS bitmode constants match EEPROM-configured GPIO pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ftdi_sio.h -->
