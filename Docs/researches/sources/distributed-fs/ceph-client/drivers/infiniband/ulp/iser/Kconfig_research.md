# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Kconfig

## Purpose
`iser/Kconfig` declares the kernel configuration option for the iSCSI Extensions for RDMA initiator transport over InfiniBand/RDMA.

## Important APIs, Types, And Functions
The file defines `config INFINIBAND_ISER` as a tristate option named "iSCSI Extensions for RDMA (iSER)". It depends on `SCSI`, `INET`, and `INFINIBAND_ADDR_TRANS`, and selects `SCSI_ISCSI_ATTRS`. The help text describes iSER as iSCSI over RDMA/InfiniBand and points to RFC 5046 and the InfiniBand Annex iSER specification.

## Control Flow And State
There is no runtime control flow or persistent state in this file. Its only state effect is build configuration: when enabled as built-in or module, it allows the Makefile to build the `ib_iser` object and ensures required SCSI iSCSI attribute support is selected.

## Dependencies And Integration Points
The dependencies express that iSER requires the SCSI midlayer, IP networking, and RDMA address translation. The selected `SCSI_ISCSI_ATTRS` integrates the driver with Linux iSCSI transport attributes. The Makefile in the same directory consumes `CONFIG_INFINIBAND_ISER`.

## Risks And Test Signals
Risks are configuration-level: missing dependencies prevent build selection, while incorrect `select` usage could omit iSCSI sysfs/session attributes. Test signals include Kconfig visibility under valid/invalid dependency combinations, built-in and module builds, and confirming `ib_iser.ko` is produced when `CONFIG_INFINIBAND_ISER=m`.
