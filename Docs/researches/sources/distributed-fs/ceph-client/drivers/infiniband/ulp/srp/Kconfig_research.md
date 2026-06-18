# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/Kconfig

## Purpose
Declares the configuration option for the InfiniBand SCSI RDMA Protocol driver.

## Important APIs, Types, And Functions
Defines `config INFINIBAND_SRP` as a tristate named "InfiniBand SCSI RDMA Protocol". It depends on `SCSI` and `INFINIBAND_ADDR_TRANS`, selects `SCSI_SRP_ATTRS`, and includes help text describing SRP storage access over InfiniBand.

## Control Flow
During kernel configuration, this symbol becomes available only when the SCSI core and RDMA address translation support are enabled. Selecting it causes the adjacent Kbuild to compile `ib_srp.o`; selecting it also forces common SCSI SRP attributes.

## State And Persistence
The symbol value persists in the kernel `.config` and controls whether SRP support is absent, built-in, or a module. It has no direct runtime state.

## Dependencies And Integration Points
Integrates SCSI, RDMA address translation, and the kernel build system. The help text points to INCITS T10 as the SRP protocol authority.

## Risks
Dependency mistakes can expose an unbuildable option or hide valid configurations. The `select` assumes `SCSI_SRP_ATTRS` has no unmet dependencies that need user visibility.

## Test Signals
Exercise menuconfig/allmodconfig paths, dependency-disabled configurations, built-in and module builds, and verify `SCSI_SRP_ATTRS` is selected when SRP is enabled.
