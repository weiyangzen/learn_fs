# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Makefile

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Makefile

### Purpose
Build rules for MPC8xx platform support.

### Important APIs, Types, And Functions
The Makefile selects shared objects such as setup, PIC, CPM1, machine check, and optional microcode patching, plus board setup objects based on Kconfig symbols.

### Control Flow
No runtime flow. Kernel build configuration expands `obj-*` entries to choose compiled files.

### State, Persistence, And Dependencies
State is build artifact selection. Dependencies are Kconfig symbols and source/object file names.

### Integration Points
Connects 8xx Kconfig board selections to machine descriptors and shared CPM/PIC support.

### Risks
Missing or wrong object entries produce link failures or selected boards without runtime support.

### Test Signals
Build all 8xx board configurations and optional feature combinations; verify expected objects in the link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Makefile -->
