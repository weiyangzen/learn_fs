<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Makefile

### Purpose
Defines SA1100 machine object compilation.

### Important APIs, Types, And Functions
Common objects include core generic, clock, GPIO/IRQ/PM support as selected. Board objects are conditionally added for Assabet, Collie, H3600/H3xxx, and related machines.

### Control Flow
No runtime flow; Kbuild compiles objects based on Kconfig symbols.

### State, Persistence, And Dependencies
State is the build graph.

### Integration Points
Maps SA1100 Kconfig board selections to source files.

### Risks
Missing common objects can break board link. Extra objects can register unwanted machine descriptors.

### Test Signals
Per-board kernel builds validate object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Makefile -->
