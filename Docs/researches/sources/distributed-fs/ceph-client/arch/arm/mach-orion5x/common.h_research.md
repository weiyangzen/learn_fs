<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.h

### Purpose
`common.h` declares shared Orion5x init APIs, MBUS target/attribute constants, PCI helpers, optional DT board hooks, and simple register bit helpers.

### Important APIs, Types, And Functions
It declares SoC init functions, peripheral init functions, PCI setup/scan/map functions, `orion5x_restart()`, `tag_fixup_mem32()`, and macros `orion5x_setbits()`/`orion5x_clrbits()`.

### Control Flow
There is no runtime flow. Conditional inline stubs make optional DT board hooks no-ops when the corresponding board config is disabled.

### State, Persistence, And Dependencies
The header has no state and depends on platform data forward declarations, reboot types, and PCI type declarations.

### Integration Points
All Orion5x board files include this as their shared interface to common SoC code.

### Risks
The register bit helpers are explicitly not preempt-safe; callers must provide locking where concurrent access is possible. MBUS constants are shared by board and common code and must match hardware decode attributes.

### Test Signals
Builds across DT and non-DT board options validate optional hook stubs and declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.h -->
