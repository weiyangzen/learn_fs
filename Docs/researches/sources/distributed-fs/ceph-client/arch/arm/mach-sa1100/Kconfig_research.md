<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Kconfig -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Kconfig

### Purpose
Defines configuration for Intel/StrongARM SA1100 machine family and supported boards.

### Important APIs, Types, And Functions
The menu enables `ARCH_SA1100` and board options such as Assabet, H3xxx/H3600, Collie, and related expansion-board or peripheral support. Selects pull in GPIO, clock, IRQ, MTD, PCMCIA, framebuffer, and PM dependencies as needed.

### Control Flow
No runtime flow; Kconfig choices decide which board files and common support build.

### State, Persistence, And Dependencies
State is kernel configuration. Dependencies span ARM SA1100 CPU support and board-specific device drivers.

### Integration Points
Controls the Makefile object list for SA1100 common and board code.

### Risks
Board options often encode old platform assumptions; missing selects surface as link errors or missing devices.

### Test Signals
Build coverage for individual board configs and multi-board configs validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/Kconfig -->
