<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctls.h

Source read size: 101 lines, 3752 bytes.

Purpose: declares PA-RISC tty, pty, serial, and file ioctl request numbers. Important APIs: `TCGETS`, `TCSETS*`, `TCGETA`, `TIOCGWINSZ`, `TIOCSWINSZ`, `FIONREAD`, `FIONBIO`, `TIOC*` serial/pty commands, packet-mode bits, and `TIOCSER_TEMT`. Control flow: userspace issues these constants through `ioctl`; tty/serial subsystems interpret them using PA-RISC ioctl encoding. State and persistence: tty settings, pty locks, packet state, and serial settings persist in device state; constants are ABI. Dependencies and integration points: `termbits.h`, tty core, serial drivers, pty, and libc termios. Risks: numeric overlaps or structure-size mismatches break terminal control; several legacy constants are raw numeric values rather than generic macro expansions. Test signals: POSIX terminal tests, pty open/lock tests, serial ioctl tests, `stty` behavior, and compat ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctls.h -->
