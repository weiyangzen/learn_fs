# sources/distributed-fs/ceph-client/include/uapi/linux/termios.h

## Purpose
Provides the generic UAPI include wrapper for terminal I/O definitions, deferring architecture-specific layout and constants to `<asm/termios.h>`.

## Important APIs, Types, and Constants
This header defines no structs itself. It includes `<linux/types.h>` and `<asm/termios.h>`, which provide `termios`, `termios2`, `winsize`, modem control, and tty ioctl constants depending on architecture.

## Control Flow, State, and Persistence
No runtime logic. Terminal state is held by tty drivers and changed through termios ioctls; this file guarantees the include path for userspace.

## Dependencies and Integration Points
Depends directly on architecture UAPI. Integrates with libc, tty drivers, serial drivers, ptys, and command-line tools.

## Risks and Test Signals
Risks are architecture layout differences and include conflicts with libc termios. Test multi-arch header compilation, tty ioctl round trips, and libc/kernel header coexistence.
