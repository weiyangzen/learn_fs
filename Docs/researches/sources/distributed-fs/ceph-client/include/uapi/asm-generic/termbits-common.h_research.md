# sources/distributed-fs/ceph-client/include/uapi/asm-generic/termbits-common.h

## Purpose
Provides generic terminal flag and speed constants shared by terminal ABI headers.

## Important APIs, Types, And Functions
Exports `cc_t`, `speed_t`, input flags such as `IGNBRK`, `ICRNL`, and `IXANY`, output flags such as `OPOST` and `OCRNL`, base baud constants `B0` through `B38400`, aliases `EXTA`/`EXTB`, control flags `ADDRB`, `CMSPAR`, `CRTSCTS`, `IBSHIFT`, `tcflow` actions, and `tcflush` selectors.

## Control Flow
No runtime flow. The header only defines constants.

## State, Persistence, And Dependencies
Terminal drivers persist these values in termios state associated with tty devices. No includes are required.

## Integration Points
Included by `termbits.h`, consumed by `termios.h`, tty line disciplines, libc terminal APIs, shells, serial tools, and pseudo-terminal implementations.

## Risks
Flag values are ABI and must stay compatible with legacy ioctl encodings. Baud and input-speed bit placement is shared with `CBAUD`/`CIBAUD` logic in `termbits.h`.

## Test Signals
`tcgetattr`/`tcsetattr` round trips, serial baud programming tests, flow-control tests, `tcflush`/`tcflow` behavior, and compile comparison against libc-exported termios constants.
