# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Makefile

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Makefile

### Purpose
Build rules for 86xx platform support.

### Important APIs, Types, And Functions
Always builds common 86xx objects such as `pic.o` and `common.o` when the directory is selected. Adds `mpc86xx_smp.o` for SMP and board objects based on Kconfig symbols, including MPC8641 HPCN, GE boards, and MVME7100.

### Control Flow
No runtime flow. The kernel build system expands `obj-*` variables according to configuration.

### State, Persistence, And Dependencies
State is build artifact selection. Dependencies are Kconfig symbols and source file names.

### Integration Points
Connects 86xx Kconfig selections to compiled machine descriptors and shared helpers.

### Risks
Missing object entries cause selected boards to compile without machine support. Stale object names break builds.

### Test Signals
Build all 86xx board configs and SMP/non-SMP variants; verify expected objects appear in the link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Makefile -->
