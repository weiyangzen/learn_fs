<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/axiado/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/axiado/Makefile

### Purpose
This Makefile adds the Axiado AX3000 evaluation-kit DTB to the arm64 DT build.

### Important APIs, Types, And Functions
The only build API is `dtb-$(CONFIG_ARCH_AXIADO) += ax3000-evk.dtb`.

### Control Flow
Kbuild includes `ax3000-evk.dtb` only when `CONFIG_ARCH_AXIADO` is enabled.

### State, Persistence, And Dependencies
State is the generated DTB artifact. The Makefile depends on `ax3000-evk.dts`, DTC, and Axiado Kconfig support.

### Integration Points
The DTB describes the AX3000 EVK for boot firmware and Linux platform drivers.

### Risks
The small file has low internal risk; the main failure mode is a missing or renamed DTS target.

### Test Signals
Build with `CONFIG_ARCH_AXIADO=y`, run DT schema checks, and boot-test the EVK DTB if hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/axiado/Makefile -->
