# File Research: sources/cow-pools/bcachefs-tools/include/linux/kernel.h

This is the central user-space Linux kernel compatibility header. It imports libc headers and many local compatibility headers, defines `BITS_PER_LONG`, kernel typedefs, GFP constants, fixed-width aliases, bit macros, config test macros (`IS_ENABLED`, `IS_BUILTIN`, etc.), integer limits, alignment helpers, `ARRAY_SIZE`, `container_of`, `struct_group`, IP macros, `panic()`, and sleep/relax stubs.

It declares and wraps kernel string conversion functions (`kstrtoul`, `kstrtol`, `kstrtoull`, `kstrtoll`, typed variants), printbuf output functions, hex lookup tables, `struct qstr`, flexible array helpers, sector/physical-address typedefs, comparator/swap callback typedefs, and `copy_to_user()` as memcpy.

Many headers depend on this file for types, macros, and kernel API surface. Because it is broad, changes here can affect nearly all bcachefs-tools kernel-shim code.
