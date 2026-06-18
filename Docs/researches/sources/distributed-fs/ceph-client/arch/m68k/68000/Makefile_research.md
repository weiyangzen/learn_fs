<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/Makefile -->
## sources/distributed-fs/ceph-client/arch/m68k/68000/Makefile

### Purpose
This Makefile selects object files for m68k 68000-core based CPU/platform support.

### Important APIs, Types, And Functions
It always builds `entry.o`, `ints.o`, `timers.o`, `m68328.o`, and `head.o`; conditionally builds `romvec.o` for `CONFIG_ROM`, `dragen2.o` for `CONFIG_DRAGEN2`, and `ucsimm.o` for `CONFIG_UCSIMM` or `CONFIG_UCDIMM`.

### Control Flow
Kbuild evaluates configuration symbols and composes the directory object list. There is no runtime code in this file.

### State, Persistence, And Dependencies
No runtime state exists. Dependencies are Kbuild, m68k platform config symbols, and the listed source objects.

### Integration Points
This controls which 68000 startup, interrupt, timer, SoC, ROM vector, and board files are linked into m68k kernel builds.

### Risks
Wrong conditional object selection can omit board initialization or duplicate shared board code. Since `ucsimm.o` is used for both UCSIMM and UCDIMM, it must support both configs.

### Test Signals
Cross-build m68k 68000 configs for ROM, DRAGEN2, UCSIMM, and UCDIMM variants and check link coverage for entry/head/platform symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/68000/Makefile -->
