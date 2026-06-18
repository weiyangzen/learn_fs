# sources/distributed-fs/ceph-client/drivers/message/fusion/Kconfig Research

## Purpose
This Kconfig file defines the Fusion Message Passing Technology driver menu and child driver symbols for SPI, Fibre Channel, SAS, ioctl control, Fibre Channel LAN, scatter-gather sizing, and logging.

## Important APIs, Types, And Functions
The parent `FUSION` bool depends on `PCI && HAS_IOPORT`. Child symbols include `FUSION_SPI`, `FUSION_FC`, `FUSION_SAS`, `FUSION_MAX_SGE`, `FUSION_CTL`, `FUSION_LAN`, and `FUSION_LOGGING`. Dependencies/selects connect the storage transports to SCSI transport attributes (`SCSI_SPI_ATTRS`, `SCSI_FC_ATTRS`, `SCSI_SAS_ATTRS`), networking (`NET_FC`), and control device support.

## Control Flow
Kconfig controls visibility and compilation. If `FUSION=n`, all child options are skipped. If enabled, individual transport modules can be built independently while sharing common base/scsi helper objects via the Makefile.

## State And Persistence
Configuration state is persisted in `.config`. `FUSION_MAX_SGE` sets a compile-time/default maximum scatter-gather limit between 16 and 128. `FUSION_LOGGING` compiles in debug logging support controlled later through sysfs.

## Dependencies And Integration Points
The file integrates Fusion MPT drivers with PCI, SCSI transport classes, Fibre Channel networking, misc-device ioctl control, and the build rules in `fusion/Makefile`.

## Risks
Transport symbols cause repeated inclusion of common objects (`mptbase.o`, `mptscsih.o`) through separate module lists; build rules must continue to avoid duplicate built-in conflicts. `FUSION_MAX_SGE` below hardware/workload expectations can reduce I/O segmentation capability. `FUSION_CTL` exposes powerful firmware/control ioctls and should be enabled deliberately.

## Test Signals
Run Kconfig dependency tests for each child, build SPI/FC/SAS combinations, verify `FUSION_MAX_SGE` bounds, confirm logging sysfs exists only with `FUSION_LOGGING`, and smoke-test module names described in help text.
