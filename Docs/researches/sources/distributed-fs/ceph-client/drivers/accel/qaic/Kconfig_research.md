<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/Kconfig

### Purpose
`qaic/Kconfig` declares the build-time configuration option for the Qualcomm Cloud AI accelerator DRM accel driver.

### Important APIs, Types, And Functions
The single option is `CONFIG_DRM_ACCEL_QAIC`, a tristate named "Qualcomm Cloud AI accelerators". It depends on `DRM_ACCEL`, `PCI && HAS_IOMEM`, and `MHI_BUS`, and selects `CRC32` plus `WANT_DEV_COREDUMP`.

### Control Flow
No runtime flow exists. Kconfig controls whether the qaic driver is built-in, built as module `qaic`, or omitted.

### State, Persistence, And Dependencies
The configuration state persists in the kernel `.config`. Dependencies ensure the driver has DRM accel infrastructure, PCI/MMIO support, and MHI bus support. Selected symbols support control-message CRCs and device coredumps.

### Integration Points
The option drives `qaic/Makefile` through `obj-$(CONFIG_DRM_ACCEL_QAIC)`. It also controls availability of qaic PCI probing, MHI channel drivers, DRM ioctls, sysfs/debugfs, RAS, SSR, and Sahara firmware loading compiled into the module.

### Risks
Missing dependencies would produce build or probe failures. Selecting coredump and CRC is necessary for diagnostics and control paths. Users enabling the option without matching hardware get no functional device but loadable module code.

### Test Signals
Build with `y`, `m`, and `n`; verify module name `qaic`; confirm dependencies prevent invalid configs; boot a QAIC system and confirm PCI probe plus MHI channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/Kconfig -->
