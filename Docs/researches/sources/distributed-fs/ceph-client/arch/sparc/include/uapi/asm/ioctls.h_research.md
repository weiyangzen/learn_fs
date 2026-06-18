<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctls.h

Purpose: SPARC tty, pty, serial, and file ioctl number ABI.

Important APIs and control flow: defines termio/termios commands under `'T'`, BSD/SunOS-style `TIOC*` commands under `'t'`, file ioctls under `'f'`, Linux serial ioctls, packet-mode constants, and aliases such as `TIOCINQ`. Commands marked with double underscores preserve SunOS numeric space without declaring Linux support.

State, dependencies, and risks: state is tty/serial line discipline, pty lock/packet state, modem control, window size, and file descriptor flags. Dependencies include `asm/ioctl.h`, `termbits.h`, serial structures, and tty core dispatch. Risks are legacy numeric compatibility, struct-size mismatches, and accidental exposure of unsupported SunOS commands. Test signals are tty ioctl ABI tests, pty packet-mode tests, serial modem-line operations, and 32-bit compat ioctl handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctls.h -->
