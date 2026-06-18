<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/Makefile

### Purpose
`mti-malta/Makefile` selects the Malta platform support objects and adds the libfdt include path for the DT shim.

### Important APIs, Types, And Functions
It builds `malta-dtshim.o`, `malta-init.o`, `malta-int.o`, `malta-memory.o`, `malta-platform.o`, `malta-setup.o`, and `malta-time.o`. `CFLAGS_malta-dtshim.o` adds `scripts/dtc/libfdt`.

### Control Flow
When the Malta platform directory is selected by Kbuild, all listed objects are linked into the kernel.

### State, Persistence, And Dependencies
The build output is platform object code. Dependencies include libfdt headers for `malta-dtshim.c` and the surrounding MIPS platform Kbuild.

### Integration Points
This Makefile ties together Malta boot, memory, interrupt, platform device, setup, and time initialization.

### Risks
Missing any listed object breaks a required platform hook. The relative libfdt include path must remain valid if the tree layout changes.

### Test Signals
Build `MIPS_MALTA` configurations with device tree shim enabled and verify all platform hooks link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/Makefile -->
