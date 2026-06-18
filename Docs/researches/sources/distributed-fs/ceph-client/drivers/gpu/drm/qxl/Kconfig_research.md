# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/Kconfig

Purpose: This Kconfig entry exposes the QXL virtual GPU DRM driver as `DRM_QXL`, a tristate driver for SPICE/QXL virtualized desktop integration.

Important APIs, types, and functions: The configuration depends on `DRM`, `PCI`, and `HAS_IOPORT`, and selects DRM client selection, KMS helper, TTM, TTM helper, DRM exec, and CRC32 support. The help text warns that a matching X.org QXL userspace driver is expected for kernel modesetting.

Control flow: Build-time only: selecting `DRM_QXL=y/m` causes the qxl object list in the Makefile to build into `qxl.o` or the kernel image.

State and persistence: No runtime state. The selected symbols alter the available driver code and dependencies at kernel build time.

Dependencies and integration points: Integrates with PCI, DRM core, TTM memory management, KMS helpers, and CRC32 used by monitor config validation in `qxl_display.c`.

Risks: `HAS_IOPORT` is essential because QXL uses `outb()` I/O port commands. Removing selected helpers would cause link or runtime feature failures. The warning about userspace compatibility is meaningful: enabling KMS without compatible userspace may regress virtual desktop behavior.

Test signals: Build QXL as built-in and module; verify dependency closure selects TTM/CRC32/DRM_EXEC; boot under QEMU/SPICE with and without matching userspace.
