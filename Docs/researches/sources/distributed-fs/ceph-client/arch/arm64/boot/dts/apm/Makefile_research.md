<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apm/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apm/Makefile

### Purpose
This Makefile registers AppliedMicro X-Gene ARM64 board DTBs for the kernel build.

### Important APIs, Types, And Functions
It exports two Kbuild targets via `dtb-$(CONFIG_ARCH_XGENE)`: `apm-mustang.dtb` and `apm-merlin.dtb`. There are no functions, types, or stateful APIs.

### Control Flow
When `CONFIG_ARCH_XGENE` is enabled, arm64 DT Kbuild compiles both listed DTS files into DTBs during `make dtbs`.

### State, Persistence, And Dependencies
Generated DTBs are build artifacts. The file depends on matching DTS sources, the top-level arm64 DT build, and Kconfig selecting `CONFIG_ARCH_XGENE`.

### Integration Points
The outputs describe X-Gene platforms used by boot firmware and the Linux kernel at boot. They indirectly affect storage/network/filesystem behavior by describing platform buses, interrupts, and devices.

### Risks
The file is small; the main risk is stale target names or disabled coverage for older X-Gene boards.

### Test Signals
Run an arm64 `dtbs` build with `CONFIG_ARCH_XGENE=y` and boot-test the Mustang/Merlin DTBs if hardware or emulation is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apm/Makefile -->
