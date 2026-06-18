<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/Makefile

### Purpose
This Makefile registers Samsung Exynos ARM64 DTBs and recurses into Axis ARTPEC and Google GS101 subdirectories.

### Important APIs, Types, And Functions
It declares `subdir-y += axis` and `subdir-y += google`, then adds 19 `dtb-$(CONFIG_ARCH_EXYNOS)` targets covering Exynos2200, 5433, 7, 7870, 7885, 850, 8895, 9810, 990, ExynosAuto v9, and ExynosAuto v920 boards.

### Control Flow
Kbuild always descends into `axis` and `google`; this file's own Exynos DTBs build when `CONFIG_ARCH_EXYNOS` is enabled.

### State, Persistence, And Dependencies
State is generated DTB output. Dependencies include DTS sources, Exynos pinctrl headers, child Makefiles, DTC, and Exynos Kconfig.

### Integration Points
The DTBs drive boot-time hardware discovery for Samsung phones, boards, and automotive platforms. Child directories add Axis ARTPEC and Google Tensor/GS101 board support.

### Risks
Subdirectory recursion is important even though child targets have their own Kconfig gates. Exynos board naming often encodes product SKUs; wrong target names can produce valid DTBs for the wrong device variant.

### Test Signals
Build with `CONFIG_ARCH_EXYNOS=y` and `CONFIG_ARCH_ARTPEC=y`, run dt-schema validation, and boot-test representative mobile, board, auto, Axis, and GS101 DTBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/Makefile -->
