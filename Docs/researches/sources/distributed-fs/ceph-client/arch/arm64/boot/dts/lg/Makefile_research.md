## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/lg/Makefile

### Purpose
This Kbuild fragment lists LG1K ARM64 board DTBs. It exists so standard ARM64 DTB builds include LG reference platform device trees when `CONFIG_ARCH_LG1K` is enabled.

### Important APIs, Types, And Functions
There are no functions or types. The build-facing API is two `dtb-$(CONFIG_ARCH_LG1K)` entries: `lg1312-ref.dtb` and `lg1313-ref.dtb`.

### Control Flow
Kbuild evaluates the two conditional additions during `make dtbs`. With `CONFIG_ARCH_LG1K` enabled, both referenced DTS files are compiled.

### State, Persistence, And Dependencies
The file has no runtime state. Its persistent effect is build output selection. It depends on Kbuild conventions, the `CONFIG_ARCH_LG1K` symbol, and the two referenced DTS files.

### Integration Points
Integration points include the parent ARM64 DTS Makefile, LG platform DTS files, CI build matrices, and any bootloader or image packaging workflow expecting LG reference DTBs.

### Risks
Because the file is tiny, the main risks are omission or stale target names. A missing line can silently remove board DTB coverage from generic ARM64 builds.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with `CONFIG_ARCH_LG1K`, verifying both DTBs exist, and `dtbs_check` on the generated outputs. Source reading signal: 3 lines; 2 DTB references; no functions.
