<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cavium/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cavium/Makefile

### Purpose
This Makefile registers the Cavium ThunderX 88xx DTB.

### Important APIs, Types, And Functions
It exports `dtb-$(CONFIG_ARCH_THUNDER) += thunder-88xx.dtb`.

### Control Flow
Kbuild compiles `thunder-88xx.dtb` when Thunder architecture support is configured.

### State, Persistence, And Dependencies
The only output is a generated DTB artifact. Dependencies are `thunder-88xx.dts`, DTC, and `CONFIG_ARCH_THUNDER`.

### Integration Points
The DTB supports ThunderX server-class ARM64 hardware and affects platform discovery for PCIe, network, storage, interrupt, and NUMA-adjacent resources.

### Risks
The target is single-board but server hardware has broad driver impact; stale DT data can surface as storage or network failures well above the DT layer.

### Test Signals
Build with `CONFIG_ARCH_THUNDER=y`, run DTC/schema checks, and boot-test with PCIe/network/storage enumeration where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cavium/Makefile -->
