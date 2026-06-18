# sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Makefile

Purpose: Build glue for TI Keystone platform support.

Important APIs/types/functions: Links `keystone.o` into the machine directory.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on `ARCH_KEYSTONE` selecting the directory and `keystone.c` providing the DT machine descriptor.

Risks: Future Keystone platform hooks require adding objects here.

Test signals: Compile `ARCH_KEYSTONE=y` and verify `keystone.o` is linked.
