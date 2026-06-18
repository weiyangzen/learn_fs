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
