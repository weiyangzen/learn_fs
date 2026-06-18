# sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits.h

## Purpose
Defines generic `termios`, `termios2`, and `ktermios` layouts plus terminal control-character indexes and mode flags.

## Important APIs, Types, And Functions
Exports `tcflag_t`, `NCCS`, `struct termios`, `struct termios2`, `struct ktermios`, `VINTR` through `VEOL2`, input/output/control/local mode flags, high baud constants through `B4000000`, `BOTHER`, `CBAUD`, `CIBAUD`, and `TCSANOW`/`TCSADRAIN`/`TCSAFLUSH`.

## Control Flow
No runtime control flow. It imports common term bits and declares ABI layouts.

## State, Persistence, And Dependencies
These structures persist tty configuration in kernel tty state and are copied through terminal ioctls. It depends on `<asm-generic/termbits-common.h>`.

## Integration Points
Used by `termios.h`, `ioctls.h` commands such as `TCGETS`, `TCSETS`, `TCGETS2`, tty drivers, pty devices, libc, shells, terminal emulators, and serial configuration tools.

## Risks
`NCCS`, flag values, and speed encodings are fixed ABI. `termios2` custom speeds depend on `BOTHER` and explicit `c_ispeed`/`c_ospeed`. User/kernel `ktermios` exposure must stay layout-compatible here.

## Test Signals
Terminal ioctl ABI tests, custom baud `TCGETS2`/`TCSETS2`, pty canonical/raw mode tests, control character behavior, and comparison with architecture-specific headers.
