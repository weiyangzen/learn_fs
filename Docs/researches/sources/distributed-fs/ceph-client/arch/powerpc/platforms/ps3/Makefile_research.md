## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/Makefile

### Purpose
The PS3 `Makefile` selects platform object files for PS3 builds.

### Important APIs, Types, And Functions
It always builds `setup.o`, `mm.o`, `time.o`, `hvcall.o`, `htab.o`, `interrupt.o`, `exports.o`, `os-area.o`, `system-bus.o`, and `device-init.o`. It conditionally builds `gelic_udbg.o`, `smp.o`, and `spu.o`.

### Control Flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` assignments to include PS3 platform code and optional early debug, SMP, and SPU support.

### State, Persistence, And Dependencies
The file carries build graph state only. It depends on config symbols defined in PS3 Kconfig and broader PowerPC config.

### Integration Points
It ties PS3 architecture sources into the kernel image or modules selected by the architecture build.

### Risks
Missing an always-needed object breaks platform boot. Optional object guards must match declarations in `platform.h`.

### Test Signals
PS3 builds with early GELIC debug, SMP on/off, and SPU on/off validate object selection.
