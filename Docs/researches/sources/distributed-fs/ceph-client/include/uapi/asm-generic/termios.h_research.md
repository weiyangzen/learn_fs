# sources/distributed-fs/ceph-client/include/uapi/asm-generic/termios.h

## Purpose
Provides generic higher-level terminal ABI definitions, legacy `termio`, window size, and modem-control bits.

## Important APIs, Types, And Functions
Exports `struct winsize`, `NCC`, `struct termio`, modem line bits `TIOCM_LE`, `TIOCM_DTR`, `TIOCM_RTS`, `TIOCM_CTS`, `TIOCM_CAR`, `TIOCM_RNG`, `TIOCM_DSR`, aliases `TIOCM_CD`/`TIOCM_RI`, and output/loop bits.

## Control Flow
No runtime logic. It includes architecture `termbits.h` and `ioctls.h`.

## State, Persistence, And Dependencies
Window size and terminal settings persist per tty and are exchanged via ioctls. Dependencies are `<asm/termbits.h>` and `<asm/ioctls.h>`.

## Integration Points
Used by terminal ioctls, `SIGWINCH` generation, serial modem-control operations, libc termios compatibility, shells, terminal emulators, and pty stacks.

## Risks
Legacy `termio` uses 16-bit flags and only `NCC == 8`, so compat handling must not confuse it with `termios`. Modem bit values are fixed for existing serial tooling.

## Test Signals
`TIOCGWINSZ`/`TIOCSWINSZ`, `SIGWINCH` delivery, `TCGETA`/`TCSETA` legacy termio tests, modem status ioctl tests, and architecture header compatibility builds.
