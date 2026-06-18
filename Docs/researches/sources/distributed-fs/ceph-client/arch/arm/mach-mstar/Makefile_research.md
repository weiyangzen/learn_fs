# sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Makefile

Purpose: Build glue for MStar V7 platform.

Important APIs/types/functions: Links `mstarv7.o`.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Depends on MStar Kconfig.

Risks: Only one object is linked; future hooks require updates here.

Test signals: Compile with `ARCH_MSTARV7=y`.
