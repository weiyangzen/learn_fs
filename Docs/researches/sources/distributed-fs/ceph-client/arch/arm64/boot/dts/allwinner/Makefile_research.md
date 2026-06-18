## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/allwinner/Makefile

### Purpose
Lists Allwinner/Sunxi ARM64 DTB targets for A64, H5, H6, H313/H616/H618/H700, A100/A133, and newer sun55i boards.

### Important APIs, Types, And Functions
All entries are `dtb-$(CONFIG_ARCH_SUNXI) += ...` for boards such as Pine64, PinePhone, Banana Pi, Orange Pi, Libretech, Tanix, Anbernic, Cubie, Avaota, and X96 variants.

### Control Flow
When `ARCH_SUNXI` is enabled, Kbuild builds the entire listed board set from matching DTS files.

### State, Persistence, And Dependencies
State is the DTB target list. Depends on board DTS sources and shared Allwinner include files.

### Integration Points
Feeds `make dtbs` and boot packaging for a broad set of Allwinner ARM64 boards.

### Risks
Large board lists are prone to stale target names and missed additions. One config gate means all listed boards build together, so a single bad DTS can fail Sunxi DTB coverage.

### Test Signals
Run `make ARCH=arm64 dtbs` with `ARCH_SUNXI`, watch `dtc` warnings, and boot-test representative boards from each SoC family.
