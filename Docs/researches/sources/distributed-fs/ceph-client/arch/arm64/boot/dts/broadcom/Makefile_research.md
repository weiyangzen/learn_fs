<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/Makefile

### Purpose
This parent Broadcom DT Makefile enables Raspberry Pi/Broadcom BCM283x/BCM271x DTBs and descends into Broadcom subfamilies.

### Important APIs, Types, And Functions
It sets global `DTC_FLAGS := -@` for overlay symbol generation, adds 11 `dtb-$(CONFIG_ARCH_BCM2835)` Raspberry Pi targets, and declares `subdir-y += bcmbca`, `northstar2`, and `stingray`.

### Control Flow
Kbuild applies the DTC symbol flag while building this directory, compiles BCM2835-family DTBs when configured, and always descends into the listed subdirectories so their own Kconfig-gated targets can participate.

### State, Persistence, And Dependencies
State is generated DTB output, including symbol metadata from `-@`. Dependencies include Raspberry Pi DTS files, subdirectory Makefiles, DTC overlay support, and Kconfig options for Broadcom platforms.

### Integration Points
The output feeds Raspberry Pi boot flows and Broadcom platform driver probing. Subdirectories integrate additional BCA, iProc Northstar2, and Stingray SoC families.

### Risks
The global `DTC_FLAGS := -@` affects all DTs in this directory; it is useful for overlays but can alter generated blob contents. Subdirectory recursion must be preserved or entire Broadcom families disappear from `make dtbs`.

### Test Signals
Build Broadcom DTBs with `CONFIG_ARCH_BCM2835`, `CONFIG_ARCH_BCMBCA`, and `CONFIG_ARCH_BCM_IPROC`; check that symbol-enabled blobs still pass DTC and dt-schema validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/Makefile -->
