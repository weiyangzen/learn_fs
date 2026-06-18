# sources/distributed-fs/ceph-client/arch/m68k/Kbuild

Purpose: top-level m68k Kbuild object directory selection.

The file always builds `kernel/` and `mm/`, then conditionally includes machine, bus, emulator, FPU, math-emulation, CPU-core, and virtual-machine subdirectories according to Kconfig symbols. Examples include `amiga/` for `CONFIG_AMIGA`, `atari/` for `CONFIG_ATARI`, `68000/` for `CONFIG_M68000`, and `coldfire/` for `CONFIG_COLDFIRE`.

Control flow is Kbuild evaluation rather than runtime code. Object directory inclusion determines which board support code can define machine hooks, interrupt controllers, platform devices, and startup objects.

State/persistence: no runtime state; the persistent effect is the build graph and the resulting linked kernel image.

Dependencies are the Kconfig symbols defined under `arch/m68k/Kconfig*` and subdirectory Makefiles. Integration is with the global kernel build system through `obj-y` and `obj-$(CONFIG_*)`.

Risks and test signals: missing or overly broad directory inclusion can cause unresolved symbols, duplicate platform code, or omitted boot support. Validate with `make ARCH=m68k` for representative classic, Sun3, 68000 non-MMU, and ColdFire configs, and inspect that selected objects match enabled machine symbols.
