<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/blaize/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/blaize/Makefile

### Purpose
This Makefile adds the Blaize BLZP1600 CB2 DTB to arm64 DT builds.

### Important APIs, Types, And Functions
The only exported build target is `dtb-$(CONFIG_ARCH_BLAIZE) += blaize-blzp1600-cb2.dtb`.

### Control Flow
Kbuild queues the DTB when the Blaize architecture option is enabled.

### State, Persistence, And Dependencies
Generated DTB output is the only state. The target depends on the same-named DTS file, DTC, and `CONFIG_ARCH_BLAIZE`.

### Integration Points
The DTB integrates platform hardware description with Linux driver probing on the BLZP1600 CB2 board.

### Risks
As with other one-target platform Makefiles, stale filenames and missing Kconfig coverage are the primary risks.

### Test Signals
Build with `CONFIG_ARCH_BLAIZE=y` and run DT schema validation for the board DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/blaize/Makefile -->
