<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termios.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termios.h

### Purpose
`termios.h` provides legacy terminal ioctl structures and modem-line constants for MIPS userspace, layering on top of `termbits.h` and `ioctls.h`.

### Important APIs, Types, And Functions
It defines `struct sgttyb`, `struct tchars`, `struct ltchars`, `struct winsize`, `NCC`, `struct termio`, and modem status bits such as `TIOCM_DTR`, `TIOCM_RTS`, `TIOCM_CTS`, `TIOCM_CAR`, `TIOCM_RNG`, `TIOCM_DSR`, `TIOCM_OUT1`, `TIOCM_OUT2`, and `TIOCM_LOOP`.

### Control Flow
No executable logic exists. Includes establish dependencies before structures are declared.

### State, Persistence, And Dependencies
The header preserves old tty ioctl ABI layouts. Dependencies are Linux errno definitions, MIPS termbits, and MIPS ioctl numbers.

### Integration Points
TTY core ioctl compatibility, serial drivers, libc, old BSD/SysV terminal utilities, and terminal-size reporting use this ABI.

### Risks
`struct sgttyb` has an SGI-specific `int sg_flags`, not a short. `struct termio` uses `NCCS` for `c_cc` despite defining `NCC`, so assumptions from other architectures are risky.

### Test Signals
TTY ioctl tests should verify winsize round-trips, modem-line ioctls, old `termio` layout, and legacy `sgttyb` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/termios.h -->
