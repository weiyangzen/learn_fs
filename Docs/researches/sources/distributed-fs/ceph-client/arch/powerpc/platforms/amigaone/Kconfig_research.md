# sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Kconfig

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Kconfig

### Purpose
Kconfig option for Eyetech AmigaOne platform support.

### Important APIs, Types, And Functions
Defines `AMIGAONE`, its dependencies, help text, and selected platform features needed for the Articia S based board.

### Control Flow
No runtime flow. The symbol controls whether `amigaone/setup.o` is built.

### State, Persistence, And Dependencies
State is build configuration only. Dependencies are PowerPC platform and PCI/interrupt feature selections.

### Integration Points
Feeds the platform Makefile and enables the AmigaOne machine descriptor.

### Risks
Incorrect dependencies may expose unsupported builds or omit required PCI/interrupt support.

### Test Signals
Enable `CONFIG_AMIGAONE`, verify config dependencies and successful build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Kconfig -->
