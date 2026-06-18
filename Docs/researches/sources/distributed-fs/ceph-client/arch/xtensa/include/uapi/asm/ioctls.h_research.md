<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ioctls.h

Purpose: defines Xtensa UAPI ioctl numbers for file, terminal, pty, modem, serial, and termios operations. Important constants include `FIOCLEX`, `FIONBIO`, `FIONREAD`, `TCGETS/TCSETS*`, `TCGETA/TCSETA*`, `TIOCSWINSZ/TIOCGWINSZ`, modem bits `TIOCM_*`, pty controls, RS485/ISO7816 controls, and serial diagnostics.

Control flow is ABI constant lookup by drivers and userspace. Persistent state affected at runtime is device/tty state managed by generic tty and serial subsystems. Dependencies include `asm/ioctl.h`, type sizes for `pid_t`, `loff_t`, and tty structs. Integration points are libc ioctl wrappers, terminal emulators, serial drivers, ptys, and strace decoding. Risks are ABI-number incompatibility, hardcoded legacy values with structure-size assumptions, and divergence from generic tty ioctl expectations. Test signals include tty/pty selftests, serial ioctl tests, termios tools, strace number decoding, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ioctls.h -->
