<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Kconfig -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Kconfig

### Purpose
`Kconfig` exposes Marvell Orion5x architecture and board support options.

### Important APIs, Types, And Functions
Key symbols are `ARCH_ORION5X`, `ARCH_ORION5X_DT`, and board options such as `MACH_KUROBOX_PRO`, `MACH_DNS323`, `MACH_TS209`, `MACH_TS409`, `MACH_D2NET_DT`, `MACH_NET2BIG`, `MACH_MSS2_DT`, and `MACH_RD88F5182_DT`.

### Control Flow
Configuration choices select shared platform dependencies such as Feroceon CPU support, GPIOLIB, MVEBU MBUS, PCI quirks, legacy Orion platform support, DT clock/IRQ/timer support, and optional I2C board-info.

### State, Persistence, And Dependencies
Kconfig has no runtime state; it controls build-time inclusion of platform and board files. Dependencies distinguish ATAGS boards from flattened device-tree boards.

### Integration Points
The Makefile and machine descriptors are gated by these symbols.

### Risks
Wrong dependencies can build board code without required subsystems or exclude needed legacy ATAGS paths. Mixed DT/ATAGS support requires consistent board selections.

### Test Signals
Defconfig and allmodconfig builds should cover both `ARCH_ORION5X_DT` and representative ATAGS board options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/Kconfig -->
