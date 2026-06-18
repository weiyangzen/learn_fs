<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vhost/Kconfig

## Purpose
This Kconfig file defines vhost core, ring, IOTLB, and frontend/backend accelerator options for virtio net, SCSI, vsock, and vDPA. It also defines optional cross-endian and fork-owner controls.

## Important APIs, types, and functions
Core symbols are `VHOST_IOTLB`, `VHOST_RING`, `VHOST_TASK`, and `VHOST`. User-visible symbols under `VHOST_MENU` include `VHOST_NET`, `VHOST_SCSI`, `VHOST_VSOCK`, `VHOST_VDPA`, `VHOST_CROSS_ENDIAN_LEGACY`, and `VHOST_ENABLE_FORK_OWNER_CONTROL`.

## Control flow
Driver options select the hidden core symbols they need. `VHOST_NET`, `VHOST_SCSI`, `VHOST_VSOCK`, and `VHOST_VDPA` select `VHOST`; `VHOST_RING` selects `VHOST_IOTLB`; `VHOST` selects both `VHOST_IOTLB` and `VHOST_TASK`. Dependency expressions ensure required subsystems such as `EVENTFD`, `TARGET_CORE`, `VSOCKETS`, `VDPA`, TUN/TAP, and IRQ bypass are present.

## State and persistence behavior
There is no runtime state. The persistent output is the configured kernel/module feature set and default enablement of fork-owner control.

## Dependencies and integration points
The file integrates with the vhost Makefile and with networking, target core, vsock, vDPA, eventfd, and virtio subsystems. The fork-owner option changes availability of vhost worker mode ioctls and a module parameter in the core.

## Risks and test signals
Risks include dependency drift causing build breaks or exposing ioctls unexpectedly. Test signals include config combinations for each vhost driver as built-in and module, absence of EVENTFD, cross-endian ioctl availability only when enabled, and fork-owner ioctl/module-parameter presence when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Kconfig -->
