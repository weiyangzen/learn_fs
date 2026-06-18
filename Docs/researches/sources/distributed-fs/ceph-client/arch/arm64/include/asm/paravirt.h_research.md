# sources/distributed-fs/ceph-client/arch/arm64/include/asm/paravirt.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/paravirt.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/paravirt.h

### Purpose
`paravirt.h` declares ARM64 paravirtualized time initialization.

### Important APIs, Types, And Functions
It exports `pv_time_init()` when paravirtual time is enabled and a no-op macro otherwise.

### Control Flow
Boot code calls `pv_time_init()` to initialize paravirtual clock support when configured.

### State, Persistence, And Dependencies
State lives in paravirtual clock data and hypervisor-provided time structures. It depends on `CONFIG_PARAVIRT` and platform/hypervisor support.

### Integration Points
Used by ARM64 timekeeping under virtualized environments, affecting scheduler timing and I/O latency accounting.

### Risks
Incorrect initialization can skew timekeeping in guests. The no-op path must keep bare-metal and unsupported configs clean.

### Test Signals
Boot under supported hypervisors with paravirt time; compare clock stability; build with paravirt disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/paravirt.h -->
