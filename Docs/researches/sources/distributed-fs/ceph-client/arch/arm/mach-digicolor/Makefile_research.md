# sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/Makefile

Purpose: maps `mach-digicolor` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-digicolor`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
