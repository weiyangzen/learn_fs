<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bitmain/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bitmain/Makefile

### Purpose
This Makefile registers the Bitmain BM1880 Sophon Edge board DTB.

### Important APIs, Types, And Functions
Its single target is `dtb-$(CONFIG_ARCH_BITMAIN) += bm1880-sophon-edge.dtb`. It contains no runtime code.

### Control Flow
Kbuild compiles the Sophon Edge DTS into a DTB when `CONFIG_ARCH_BITMAIN` is set.

### State, Persistence, And Dependencies
The only persistent output is the generated build artifact. It depends on the DTS file, DTC, and Bitmain architecture Kconfig.

### Integration Points
The DTB feeds boot-time hardware discovery for the BM1880 platform and any drivers bound through its compatible strings.

### Risks
The SPDX line uses `GPL-2.0+`, so license scanners may distinguish it from the more common `GPL-2.0-only` spelling used elsewhere. Build risk is otherwise limited to target/source drift.

### Test Signals
Run the arm64 DTB build with `CONFIG_ARCH_BITMAIN=y` and check DTC/schema output for the board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bitmain/Makefile -->
