# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/serialio.h

## Purpose
Private definitions for the legacy serial transport used by direct UART Speakup synthesizers.

## Important APIs, Types, And Functions
Defines `struct old_serial_port`, serial timeout constants, allowed `ttyS` range, disable-timeout count, and `spk_serial_tx_busy()` over `UART_LSR`.

## Control Flow
No executable flow; the macros/constants shape `serialio.c` probe and wait behavior.

## State And Persistence Behavior
Stores no state directly. Macros read `speakup_info.port_tts`, which is maintained by the serial transport.

## Dependencies, Integration Points, Risks, And Test Signals
Includes Linux serial headers and `spk_priv.h`. Risks are stale 8250 assumptions and macros requiring a valid UART base. Test compile coverage across architectures and runtime timeout behavior through serial synth probes.
