# sources/distributed-fs/ceph-client/drivers/usb/serial/whiteheat.h

## Purpose

`whiteheat.h` defines the host-to-firmware command protocol, payload layouts, event formats, and firmware reply structures used by the Connect Tech WhiteHEAT usb-serial driver.

## Important APIs, Types, and Functions

The header enumerates command IDs such as `WHITEHEAT_OPEN`, `WHITEHEAT_CLOSE`, `WHITEHEAT_SETUP_PORT`, modem-signal commands, `WHITEHEAT_GET_HW_INFO`, `WHITEHEAT_EVENT`, and command-complete/failure replies. Request payloads include `struct whiteheat_simple`, `struct whiteheat_port_settings`, `struct whiteheat_set_rdb`, `struct whiteheat_dump`, `struct whiteheat_purge`, `struct whiteheat_echo`, and `struct whiteheat_test`. Reply/event payloads include `struct whiteheat_status_info`, `struct whiteheat_dr_info`, `struct whiteheat_hw_info`, `struct whiteheat_event_info`, and `struct whiteheat_test_info`.

## Control Flow

The header has no executable flow. It establishes the byte-level ABI consumed by `whiteheat.c`: command helpers fill these packed structures, the command port sends command ID plus payload, and the read callback interprets the first response byte against the reply constants.

## State and Persistence Behavior

No state is stored in the header. Its structures describe transient USB command and response packets. The protocol includes firmware-visible state such as port settings, UART modem control, purge requests, hardware/EEPROM information, and unsolicited events, but persistence is owned by the WhiteHEAT firmware or hardware.

## Dependencies and Integration Points

The definitions depend on kernel integer types and little-endian annotations. The host driver maps tty settings to parity, software flow, hardware flow, break, DTR, and RTS constants from this file, while firmware must interpret the same numeric command and layout contract.

## Risks and Test Signals

Risks are protocol drift between host and firmware, packed-layout or endian mistakes, and fields whose comments expose firmware-specific constraints such as dump address ranges and 8051 side effects. Test signals are compile coverage from `whiteheat.c`, packet-size checks for command endpoint buffers, successful hardware-info parsing, and termios/modem operations matching expected command payloads on USB traces.
