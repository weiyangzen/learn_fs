<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/Makefile

### Purpose
This Makefile selects Amlogic/Meson ARM64 device-tree blobs for the kernel DT build. It contributes 108 DTB/DTBO references under `CONFIG_ARCH_MESON`, covering newer `amlogic-a4/a5/c3/s6/s7/t7` boards and established Meson A1, AXG, G12, GXBB/GXL/GXM, S4, and SM1 boards.

### Important APIs, Types, And Functions
The public surface is Kbuild data: repeated `dtb-$(CONFIG_ARCH_MESON) += ...` assignments plus four composite `*-dtbs := base.dtb overlay.dtbo` definitions. There are no C functions or runtime types. The build contract is the exact DTB target names and overlay composition variables.

### Control Flow
Kbuild includes this file while descending through `arch/arm64/boot/dts`. If `CONFIG_ARCH_MESON` is enabled, each listed target is queued for DTC compilation. For composite targets such as `meson-g12a-fbx8am-brcm`, Kbuild first builds the base DTB and overlay DTBO, then emits the named composite DTB.

### State, Persistence, And Dependencies
State is build-system state only: generated `.dtb` and `.dtbo` artifacts in the kernel build output. It depends on matching `.dts`/`.dtso` source files in the same directory, the top-level arm64 DT Makefiles, DTC, and Kconfig selection of `CONFIG_ARCH_MESON`.

### Integration Points
The generated blobs are consumed by boot firmware, bootloaders, and test infrastructure for Amlogic boards. Reset binding headers in this directory are included by DTS files that describe reset-controller cells for newer Amlogic SoCs.

### Risks
Target names must match source filenames exactly; stale entries break `make dtbs`. Composite overlay targets are sensitive to overlay symbol support and base/overlay compatibility. A broad `CONFIG_ARCH_MESON` target set means a single bad board DTS can break all Meson DT builds.

### Test Signals
Run `make ARCH=arm64 dtbs` with `CONFIG_ARCH_MESON=y`, and separately build the composite overlay targets. DTC warnings, missing-source errors, and boot smoke tests on representative Meson boards are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/Makefile -->
