# sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctls.h

Purpose: Defines generic terminal, pty, serial, and file ioctl command numbers.

Important APIs/types/functions: Exports `TCGETS/TCSETS*`, `TCGETS2/TCSETS2*`, `TIOC*` pty/session/window/serial controls, `FIONREAD/FIONBIO/FIOCLEX/FIONCLEX/FIOASYNC/FIOQSIZE`, packet-mode flags `TIOCPKT_*`, and `TIOCSER_TEMT`.

Control flow: Includes `linux/ioctl.h` and uses `_IOR/_IOW/_IOWR` for typed commands. Guards allow architectures to predefine conflicting values like `TIOCSRS485` or `FIOQSIZE`.

State/persistence: No runtime state; constants are ioctl ABI.

Dependencies/integration: Used by tty, pty, serial, and libc terminal APIs.

Risks: Numeric conflicts are permanent ABI issues. Type arguments in typed ioctl macros must match UAPI structs.

Test signals: Headers compile checks and tty/pty/serial ioctl ABI tests.
