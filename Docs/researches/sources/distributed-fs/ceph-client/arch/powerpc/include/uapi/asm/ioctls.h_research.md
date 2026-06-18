<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctls.h

Purpose: Defines PowerPC terminal, file, pseudo-terminal, serial, and console ioctl numbers.

Important APIs/types/functions: `FIOC*`, `TIOC*`, `TCGETS/TCSETS*`, modem bits `TIOCM_*`, packet mode bits `TIOCPKT_*`, serial ioctls, PTY helpers, and ISO7816 ioctls.

Control flow: TTY/VFS drivers decode these command numbers from userspace `ioctl()` calls and read/write the associated structures.

State and persistence: No state owned; constants address driver-maintained tty/file state.

Dependencies and integration points: Depends on PowerPC ioctl encoding, termios structure declarations, and generic tty/serial drivers.

Risks: Numbers are ABI-stable and include legacy BSD/System V compatibility. Incorrect structure direction/size breaks 32-bit and 64-bit userspace.

Test signals: TTY ioctl regression tests, pty tests, serial control-line tests, and ioctl-number comparison with libc expectations.

Source read size: 123 lines, 4359 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ioctls.h -->
