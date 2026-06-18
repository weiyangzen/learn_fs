# sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Makefile

Purpose: Build glue for IXP4xx platform support.

Important APIs/types/functions: Adds `ixp4xx-of.o` to `obj-y`.

Control flow: No runtime flow; Kbuild includes the DT machine descriptor when the directory is selected.

State and persistence: No state beyond build outputs.

Dependencies and integration points: Depends on the Kconfig selecting this machine directory and `ixp4xx-of.c` providing the machine descriptor.

Risks: If this file omits future platform objects, configured support silently lacks required init code.

Test signals: Compile an IXP4xx kernel and confirm `ixp4xx-of.o` is linked.
