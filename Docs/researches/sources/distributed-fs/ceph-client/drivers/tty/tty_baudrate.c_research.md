# Research: sources/distributed-fs/ceph-client/drivers/tty/tty_baudrate.c

## Purpose

`tty_baudrate.c` converts between termios baud-rate bit encodings and numeric `speed_t` rates, including `BOTHER` arbitrary speeds and independent input/output speeds. It also lets drivers encode actual selected speeds back into `ktermios` so user space can observe the real configured rate.

## Important APIs, Types, and Functions

`baud_table` maps termios baud indexes to numeric speeds, and `baud_bits` maps the same indexes back to `B*` constants. The table is architecture-sensitive for sparc. `tty_termios_baud_rate` returns output speed from `c_cflag`, `tty_termios_input_baud_rate` returns input speed from the `IBSHIFT` field or falls back to output speed for `B0`, `tty_termios_encode_baud_rate` rewrites `c_cflag`, `c_ispeed`, and `c_ospeed`, and `tty_encode_baud_rate` applies the same encoding to `tty->termios`.

## Control Flow

Decode helpers mask out `CBAUD`, handle `BOTHER` by returning `c_ospeed` or `c_ispeed`, handle extended baud values by removing `CBAUDEX` and adding the legacy offset, and return zero for indexes outside `baud_table`.

Encoding stores exact numeric speeds in `c_ispeed` and `c_ospeed`, clears old output and input baud bits, detects whether the user explicitly requested separate input speed, and scans the known baud table for rates within a tolerance of `rate / 50`. If output or input speed is close to a standard baud, it encodes the corresponding `B*` bits. If not, it uses `BOTHER`, preserving exact speeds in the numeric fields. `obaud == 0` also forces input speed to zero for hangup semantics.

## State and Persistence Behavior

This file has no independent runtime state beyond static lookup tables. It mutates caller-owned `struct ktermios` or `tty->termios` in place. Callers are expected to hold the termios lock when operating on live tty termios.

## Dependencies and Integration Points

The code depends on termios constants (`CBAUD`, `CBAUDEX`, `BOTHER`, `IBSHIFT`, and `B*` rates), tty core types, and export symbols. Drivers call these helpers from termios handlers when reporting actual hardware rates, and tty core code uses them to decode user-requested speeds.

## Risks and Edge Cases

The baud tables must remain aligned with architecture termbits definitions; a mismatch decodes or reports wrong rates. The tolerance behavior intentionally reports near-standard rates as standard `B*` values, which preserves compatibility but can hide small hardware rounding differences. Arbitrary speeds require correct `BOTHER` support in user space and architecture headers. Input-speed bits are omitted when input equals output and the user did not explicitly request a separate input speed.

## Test Signals

Tests should cover all standard baud constants, extended rates, sparc/non-sparc table variants, `BOTHER` exact speeds, `B0` hangup behavior, separate input/output rates, near-match tolerance, no-match fallback to `BOTHER`, and live `tty_encode_baud_rate` calls under termios locking.
