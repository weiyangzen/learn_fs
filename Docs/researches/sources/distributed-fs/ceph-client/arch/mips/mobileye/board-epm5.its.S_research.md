<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/board-epm5.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/mobileye/board-epm5.its.S

### Purpose
`board-epm5.its.S` adds an EyeQ5 EPM5 device-tree image and configuration fragment to a FIT image source.

### Important APIs, Types, And Functions
The DTS fragment defines an `images/fdt-mobileye-epm5` node that incbins `boot/dts/mobileye/eyeq5-epm5.dtb`, declares it as a MIPS flat DT with SHA1 hash, and a `configurations/conf-1` node that pairs `kernel` with that FDT.

### Control Flow
The assembler/preprocessor emits DTS/ITS text consumed by FIT image tooling. At boot, U-Boot can select `conf-1`, loading the kernel and associated EPM5 FDT.

### State, Persistence, And Dependencies
Persistent output is the FIT image containing the DTB blob. Dependencies include the built `eyeq5-epm5.dtb`, a `kernel` image node supplied by the base ITS, and U-Boot FIT support.

### Integration Points
This fragment works with `vmlinux.its.S` and the `FIT_IMAGE_FDT_EPM5` Kconfig option to package board-specific DT with the kernel.

### Risks
The incbin path must match the DTB build output. The configuration assumes the kernel image node is named `kernel`. A missing or stale DTB would fail FIT build or boot with wrong hardware description.

### Test Signals
Build EyeQ5 FIT images with EPM5 FDT enabled, inspect `dumpimage -l`, and boot via U-Boot selecting `conf-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/board-epm5.its.S -->
