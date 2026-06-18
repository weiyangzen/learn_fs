# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Makefile

Purpose: Build glue for LPC32xx platform objects.

Important APIs/types/functions: Links `common.o`, `serial.o`, `pm.o`, `suspend.o`, and `phy3250.o`.

Control flow: No runtime flow; Kbuild composes the platform support files.

State and persistence: No runtime state.

Dependencies and integration points: Depends on `ARCH_LPC32XX` and the listed C/assembly files.

Risks: Omitting `suspend.o` or `pm.o` would compile but remove suspend functionality; object order is simple but early init ordering is in the code.

Test signals: Compile LPC32xx and verify linked symbols for suspend and machine descriptor.
