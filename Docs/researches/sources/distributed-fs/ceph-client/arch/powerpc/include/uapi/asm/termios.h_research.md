<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termios.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termios.h

Purpose: Defines legacy PowerPC terminal helper structures layered on termbits/ioctls.

Important APIs/types/functions: `struct sgttyb`, `struct tchars`, `struct ltchars`, `struct winsize`, `NCC`, `struct termio`, and legacy `_V*` control-character indexes.

Control flow: Legacy tty ioctls and compatibility code copy these structures for old terminal APIs, while modern code uses `struct termios` from termbits.

State and persistence: Represents per-tty line discipline, window size, and legacy character settings.

Dependencies and integration points: Depends on PowerPC ioctls and termbits. Integrated with tty compatibility handlers and libc.

Risks: Legacy structure layout remains ABI for old programs.

Test signals: TTY legacy ioctl tests, window-size ioctls, pty tests, and libc structure checks.

Source read size: 77 lines, 1712 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/termios.h -->
