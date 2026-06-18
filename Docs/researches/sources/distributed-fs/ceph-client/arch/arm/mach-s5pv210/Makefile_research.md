<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Makefile

### Purpose
Lists S5PV210 machine objects built for the selected kernel configuration.

### Important APIs, Types, And Functions
`obj-y += s5pv210.o` builds the DT machine support. `obj-$(CONFIG_PM_SLEEP) += pm.o sleep.o` adds suspend/resume support when sleep PM is enabled.

### Control Flow
No runtime flow; Kbuild evaluates these object lists during compilation.

### State, Persistence, And Dependencies
State is build graph membership. Depends on Kconfig symbols.

### Integration Points
Ties `Kconfig` selections to compiled machine and PM code.

### Risks
PM declarations in `common.h` must match whether `pm.o` and `sleep.o` are built.

### Test Signals
Builds with and without `CONFIG_PM_SLEEP` validate object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/Makefile -->
