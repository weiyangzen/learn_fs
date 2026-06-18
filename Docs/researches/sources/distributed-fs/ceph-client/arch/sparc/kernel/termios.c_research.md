# sources/distributed-fs/ceph-client/arch/sparc/kernel/termios.c

Purpose: converts between SPARC user `termio`/`termios`/`termios2` ABI layouts and kernel `ktermios`.

Important APIs/types/functions: `kernel_termios_to_user_termio()`, `user_termios_to_kernel_termios()`, `kernel_termios_to_user_termios()`, `user_termios_to_kernel_termios_1()`, and `kernel_termios_to_user_termios_1()` use `_VMIN` and `_VTIME` compatibility indexes plus canonical `VEOF`/`VEOL`, `VMIN`, and `VTIME`.

Control flow: conversion copies flags, line discipline, control-character arrays, and for `termios2` input/output speeds. The special SPARC/SysV compatibility rule maps character slots 4 and 5 as `VEOF`/`VEOL` when `ICANON` is set, otherwise as `VMIN`/`VTIME`.

State and persistence: no owned state. It reads/writes user termios buffers and kernel terminal settings; terminal driver state is maintained elsewhere.

Dependencies and integration points: used by generic tty ioctl conversion hooks through `linux/termios_internal.h` and SPARC UAPI layouts.

Risks: control-character index remapping is ABI-sensitive and differs by canonical mode. Partial user-copy failures return accumulated nonzero errors. `NCC` versus `NCCS` sizes must match target ABI structures.

Test signals: tty ioctl round trips for `TCGETS`, `TCSETS`, `TCGETS2`, old `termio`, canonical and noncanonical mode VMIN/VTIME behavior, speed fields in `termios2`, and user-copy fault paths.
