<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termios.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termios.h

Purpose: SPARC legacy terminal structure definitions layered on ioctl and termbits constants.

Important APIs and control flow: includes `ioctls.h` and `termbits.h`, conditionally exposes BSD `sgttyb`, `tchars`, and `ltchars` when requested or in-kernel, defines `winsize`, and provides legacy `struct termio` with `NCC=8`.

State, dependencies, and risks: state is terminal window size and legacy line settings exchanged with tty drivers. Dependencies include ioctl numbers, termbit layouts, and conditional BSD compatibility macros. Risks are source compatibility versus namespace pollution and legacy structure-size expectations. Test signals are `TCGETA`/`TCSETA`, `TIOCGWINSZ`/`TIOCSWINSZ`, and programs defining `__DEFINE_BSD_TERMIOS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/termios.h -->
