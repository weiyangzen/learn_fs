<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_fc.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_fc.h

## Purpose
This header defines the Fibre Channel SCSI transport class: FC host, remote-port, virtual-port, target attributes, FC statistics/events, sysfs visibility flags, BSG helpers, and ready/error behavior for FC transports.

## Important APIs, Types, And Functions
Important enums/constants cover FC port types/states, vport states, classes of service, speeds, target-ID binding, port roles, event codes, and vport error returns. Structures include `fc_vport_identifiers`, `struct fc_vport`, `fc_rport_identifiers`, `fc_fpin_stats`, `fc_encryption_info`, `struct fc_rport`, `fc_starget_attrs`, `fc_host_statistics`, `fc_host_attrs`, and `fc_function_template`. APIs attach/release transport, remove hosts, add/delete/role-change remote ports, post events/vendor events/FPINs, create/terminate vports, block rports/EH, and handle timeouts/retry decisions.

## Control Flow
LLDDs attach a transport with an `fc_function_template`, set host attributes, add remote ports as topology is discovered, and optionally create NPIV vports. `fc_remote_port_chkready()` gates I/O based on rport state, role, dev-loss, and fast-fail flags. Work items manage dev-loss, scans, fast-fail, target deletion, rport deletion, and vport deletion. Event APIs publish async FC state to netlink/sysfs consumers.

## State And Persistence
Host attributes store fixed/dynamic FC identity, speeds, FC4s, fabric name, discovered rports/vports, counters, workqueues, BSG queue, and FPIN stats. Rports and vports store transport-managed state, flags, delayed work, devices, and driver-private data. State is runtime/sysfs visible, not durable.

## Dependencies And Integration Points
It depends on scheduler, BSG, unaligned access, SCSI netlink, SCSI host, and SCSI status. It integrates with FC HBAs, libfc/FCoE, SCSI targets, vport NPIV management, BSG vendor commands, and SCSI EH.

## Risks
Rport state transitions drive data loss vs retry behavior; dev-loss and fast-fail timers must be coordinated. Sysfs visibility flags must match implemented callbacks. WWN conversion uses unaligned big-endian helpers. Vport state updates assume external locking.

## Test Signals
Exercise rport add/delete/role changes, `fc_remote_port_chkready()` matrix, dev-loss/fast-fail timers, vport create/delete/disable, host/rport sysfs attributes, FC event posting, FPIN receive stats, BSG host/rport mapping, and EH timeout retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_fc.h -->
