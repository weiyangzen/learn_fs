## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/hisilicon/Makefile

### Purpose
This Kbuild fragment declares which HiSilicon ARM64 DTBs are built when `CONFIG_ARCH_HISI` is enabled. It is a device-tree build manifest rather than executable source.

### Important APIs, Types, And Functions
There are no functions or types. The important interface is seven `dtb-$(CONFIG_ARCH_HISI) += ...` entries: HiKey 960, HiKey 970, Poplar, HiKey, and Hip05/Hip06/Hip07 server boards. These lines are consumed by the kernel DTB build system.

### Control Flow
Kbuild evaluates the conditional `dtb-y` additions based on the active configuration. If `CONFIG_ARCH_HISI=y`, the listed `.dts` files are compiled into `.dtb` artifacts as part of `make dtbs` or architecture builds.

### State, Persistence, And Dependencies
The file has no runtime state. Its persistent output is the set of DTB artifacts included in build trees, packages, or install targets. It depends on the referenced DTS files existing and on Kbuild's `dtb-*` convention.

### Integration Points
Integration points include `arch/arm64/boot/dts/Makefile`, distro/kernel packaging, CI `dtbs` targets, bootloader DTB selection, and board DTS files under the same HiSilicon directory.

### Risks
Missing an entry prevents a valid board DTB from being built in standard workflows. Stale entries break `make dtbs`. Incorrect Kconfig guards can build DTBs under the wrong SoC family or omit them from distribution packages.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with `CONFIG_ARCH_HISI`, build logs showing all seven DTBs, and boot smoke tests on representative HiKey/Poplar/Hip boards. Source reading signal: 8 lines; 7 DTB references; no functions.
