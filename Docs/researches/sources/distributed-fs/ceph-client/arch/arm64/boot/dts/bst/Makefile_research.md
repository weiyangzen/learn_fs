<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bst/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bst/Makefile

### Purpose
This Makefile adds the BST C1200 CDCU ADAS board DTB.

### Important APIs, Types, And Functions
The exported Kbuild target is `dtb-$(CONFIG_ARCH_BST) += bstc1200-cdcu1.0-adas_4c2g.dtb`.

### Control Flow
The DTB is compiled only when `CONFIG_ARCH_BST` is enabled.

### State, Persistence, And Dependencies
State is the generated DTB. The target depends on the matching DTS, DTC, and BST architecture Kconfig.

### Integration Points
The DTB describes the BST automotive/ADAS board for Linux boot and platform-driver matching.

### Risks
The filename includes punctuation and memory-size metadata, making accidental renames or shell/glob handling mistakes more likely than for simpler names.

### Test Signals
Build with `CONFIG_ARCH_BST=y` and run DTC/schema checks on the target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bst/Makefile -->
