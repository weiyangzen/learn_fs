<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/Makefile

Purpose: Builds the SolidRun vDPA module and conditionally includes hardware monitoring support.

Important APIs/types/functions: Kbuild target `obj-$(CONFIG_SNET_VDPA) += snet_vdpa.o` links `snet_main.o` and `snet_ctrl.o`; `snet_hwmon.o` is included when `CONFIG_HWMON` is enabled.

Control flow: Kernel build produces one `snet_vdpa` module from main PCI/vDPA logic, DPU control protocol, and optional hwmon code.

State and persistence: No runtime state.

Dependencies and integration points: Controlled by `CONFIG_SNET_VDPA` and `CONFIG_HWMON`. `snet_main.c` provides fallback warning when hwmon support is requested by device config but not compiled.

Risks: Building without `CONFIG_HWMON` removes `psnet_create_hwmon()`, so the header's conditional declaration and main-file preprocessor block must remain aligned.

Test signals: Build with and without `CONFIG_HWMON` to confirm optional object selection and no unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/Makefile -->
