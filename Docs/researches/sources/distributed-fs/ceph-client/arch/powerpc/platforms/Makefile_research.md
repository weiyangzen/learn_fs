# sources/distributed-fs/ceph-client/arch/powerpc/platforms/Makefile

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/Makefile

### Purpose
Top-level build dispatch for PowerPC platform directories and shared platform objects.

### Important APIs, Types, And Functions
Uses `obj-$(CONFIG_...)` entries to include platform directories: powermac, chrp, 44x, 512x, 52xx, 8xx, 82xx, 83xx, 85xx, 86xx, powernv, pseries, pasemi, cell, ps3, embedded6xx, amigaone, book3s, and microwatt. It also includes shared `fsl_uli1575.o` when selected.

### Control Flow
No runtime flow. The kernel build system chooses directories and objects according to configuration symbols.

### State, Persistence, And Dependencies
State is build artifact selection. Dependencies are Kconfig symbols and directory Makefiles.

### Integration Points
Connects top-level PowerPC architecture builds to all platform-specific code.

### Risks
Wrong dispatch entries can exclude entire platform families or include incompatible code.

### Test Signals
Build representative configs for every platform symbol and verify expected directory object traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Makefile -->
