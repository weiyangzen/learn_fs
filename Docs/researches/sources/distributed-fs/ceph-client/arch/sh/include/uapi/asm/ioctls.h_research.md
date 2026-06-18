<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ioctls.h

Purpose: defines SH terminal and file ioctl command numbers.

Important APIs/types/functions: `FIOCLEX`, `TCGETS`, `TCSETS*`, `TIOCGWINSZ`, `TIOC*`, `FIONREAD`, and socket/group tty ioctls.

Control flow: drivers and libc use fixed numbers for ioctl dispatch across the syscall boundary.

State and persistence: no kernel state here, but each number selects stateful tty/socket behavior in drivers.

Dependencies/integration: integrates with generic termios, tty, serial, and libc ABI.

Risks: renumbering any ioctl breaks existing binaries and device tools.

Test signals: run headers ABI checks and tty ioctl smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ioctls.h -->
