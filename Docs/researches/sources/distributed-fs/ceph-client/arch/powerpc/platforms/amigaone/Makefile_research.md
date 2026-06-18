# sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Makefile

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Makefile

### Purpose
Build rule for AmigaOne platform support.

### Important APIs, Types, And Functions
Always builds `setup.o` when the directory is selected by `CONFIG_AMIGAONE`.

### Control Flow
No runtime flow. Kernel build system compiles the machine file.

### State, Persistence, And Dependencies
State is build artifact selection. Depends on the Kconfig symbol and source file name.

### Integration Points
Connects AmigaOne Kconfig selection to the platform machine descriptor implementation.

### Risks
Missing or renamed object breaks AmigaOne builds.

### Test Signals
Build with `CONFIG_AMIGAONE=y` and verify `setup.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Makefile -->
