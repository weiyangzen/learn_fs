# sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Makefile

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Makefile

### Purpose
Build rule for Book3S VAS API support.

### Important APIs, Types, And Functions
Builds `vas-api.o` when `CONFIG_PPC_VAS` is enabled.

### Control Flow
No runtime flow. The build system includes the object according to Kconfig.

### State, Persistence, And Dependencies
State is build artifact selection. Depends on the Kconfig symbol and source file name.

### Integration Points
Connects the `PPC_VAS` option to the userspace VAS API implementation.

### Risks
Missing object inclusion disables the `/dev/crypto/nx-gzip` style API even when configured.

### Test Signals
Build with `CONFIG_PPC_VAS=y` and verify `vas-api.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Makefile -->
