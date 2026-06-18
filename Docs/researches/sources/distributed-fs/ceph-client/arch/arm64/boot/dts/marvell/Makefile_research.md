## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/marvell/Makefile

### Purpose
This Kbuild fragment enumerates Marvell/Mvebu ARM64 DTBs and descends into the `mmp` child directory. It is the build manifest for Armada 37xx, 7k/8k/80x0, CN913x, AC5/AC5X, Clearfog, EspressoBin, Turris MOX, and related boards.

### Important APIs, Types, And Functions
There are no functions or types. The important build interface is a set of `dtb-$(CONFIG_ARCH_MVEBU)` assignments containing 34 DTB targets, plus `subdir-y += mmp` to include Marvell MMP DTB targets from the child directory.

### Control Flow
Kbuild conditionally includes the listed DTBs when `CONFIG_ARCH_MVEBU` is active and always descends into `mmp` via `subdir-y`. Each `.dtb` target resolves to a same-directory DTS source or generated DTB dependency graph.

### State, Persistence, And Dependencies
There is no runtime state. Build artifacts persist as DTBs. Dependencies include the referenced DTS files, parent ARM64 Kbuild traversal, and the `CONFIG_ARCH_MVEBU` symbol.

### Integration Points
Integration points include parent ARM64 DTS builds, Marvell platform DTS/DTSI files, board image packaging, firmware/bootloader DTB selection, and CI coverage for network/storage-oriented Marvell boards.

### Risks
The broad board list is susceptible to stale filenames, missed board additions, and accidental removal from distro DTB packages. The `subdir-y` entry is also important: removing it would suppress child MMP DTBs even if their own Makefile is correct.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with `CONFIG_ARCH_MVEBU`, verifying all 34 listed DTBs plus child MMP outputs, `dtbs_check`, and boot tests for representative Armada 3720, 8040, CN913x, and AC5 boards. Source reading signal: 38 lines; 34 DTB references; one child subdir.
