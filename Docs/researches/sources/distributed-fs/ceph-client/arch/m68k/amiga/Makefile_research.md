# sources/distributed-fs/ceph-client/arch/m68k/amiga/Makefile

Purpose: Amiga platform object list.

It always builds `config.o`, `amiints.o`, `cia.o`, `chipram.o`, `amisound.o`, and `platform.o` for `CONFIG_AMIGA` directory inclusion. It adds `pcmcia.o` only when `CONFIG_AMIGA_PCMCIA` is enabled.

Control flow is Kbuild-only: this determines which machine setup, interrupt, CIA, Chip RAM, beeper, platform-device, and optional PCMCIA support enters the kernel image.

State/persistence: no runtime state in the Makefile; the persistent effect is linked object selection.

Dependencies include top-level `arch/m68k/Kbuild` selecting `amiga/` and Kconfig symbols for Amiga PCMCIA. Integration is with board setup in `config.c` and device drivers that depend on exported Amiga helpers.

Risks and test signals: omitting `cia.o` or `chipram.o` breaks timer/interrupt or audio allocations, while including `pcmcia.o` without hardware config would add unnecessary Gayle support. Validate Amiga builds with and without `CONFIG_AMIGA_PCMCIA`.
