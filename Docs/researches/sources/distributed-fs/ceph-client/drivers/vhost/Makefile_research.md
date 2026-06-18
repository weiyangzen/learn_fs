<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vhost/Makefile

## Purpose
This Makefile maps vhost Kconfig symbols to vhost object modules.

## Important APIs, types, and functions
It builds `vhost_net.o` from `net.o`, `vhost_scsi.o` from `scsi.o`, `vhost_vsock.o` from `vsock.o`, `vringh.o` for `VHOST_RING`, `vhost_vdpa.o` from `vdpa.o`, `vhost.o` for core, and `vhost_iotlb.o` from `iotlb.o`.

## Control flow
Kbuild includes each object according to the corresponding `CONFIG_VHOST_*` symbol. Hidden core symbols selected by Kconfig ensure shared dependencies such as vhost core and IOTLB support are available before dependent drivers link.

## State and persistence behavior
No runtime state exists. The file persists only build composition and module naming.

## Dependencies and integration points
It depends on the Kconfig symbols in the same directory and integrates vhost frontend accelerators with core and IOTLB support.

## Risks and test signals
Risk is limited to object naming and missing dependencies between hidden symbols. Test signals are clean builds for every vhost module as `m` and `y`, plus link coverage when multiple frontends select the same core object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/Makefile -->
