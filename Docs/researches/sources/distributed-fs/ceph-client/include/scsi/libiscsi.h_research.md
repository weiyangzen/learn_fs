<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/libiscsi.h

## Purpose
This header defines the generic kernel iSCSI initiator library used by software and offload transports. It models hosts, sessions, connections, tasks, command-private data, management pools, error handling, PDU completion, and SCSI mid-layer integration.

## Important APIs, Types, And Functions
Core types are `struct iscsi_task`, `struct iscsi_conn`, `struct iscsi_session`, `struct iscsi_host`, `struct iscsi_pool`, and `struct iscsi_cmd`. Constants bound command counts, ITT encoding, connection flags, address storage, management-command pools, and task states. Inline helpers expose unsolicited data progress, next-header storage, task completion checks, command-private lookup, and iSCSI padding calculations.

Exported APIs include SCSI host template callbacks (`iscsi_queuecommand()`, abort/session/device/target reset handlers, timed-out handling), host allocation/add/remove/free, session setup/teardown/removal/free, parameter get/set, connection setup/bind/start/stop/unbind/failure, transmit/receive work queueing, PDU send/complete, ITT lookup/verification, task refcounting/requeue/completion, and pool/string helpers.

## Control Flow
A driver allocates an iSCSI host, creates a session with a command pool, then creates and binds one or more connections. SCSI commands enter through `iscsi_queuecommand()`, are represented by `iscsi_task`, and move through pending/running/completed or abort/recovery states. Connection transmit work drains management, command, and requeue lists under the forward lock. Receive completion updates CmdSN windows, verifies ITTs, completes SCSI tasks, or triggers recovery/failure.

## State And Persistence
State is volatile and split across host, session, connection, and task objects. The session has strict forward/back lock hierarchy for CmdSN windows, pools, queues, and state. Connection fields persist negotiated operational parameters, TCP/offload attributes, counters, and stats for the lifetime of the connection. User-visible persistent strings are stored as allocated pointers but are not durable storage.

## Dependencies And Integration Points
The header depends on SCSI command, iSCSI protocol/if, and iSCSI transport-class headers. It bridges SCSI mid-layer queueing and EH to the iSCSI control plane, sysfs transport classes, userspace parameter configuration, and transport-specific data through `dd_data`.

## Risks
Lock ordering is explicitly constrained; violating forward/back/eh mutex order can deadlock error recovery. ITT age/index handling must prevent stale-task completion. Queue-depth and pool sizes must remain power-of-two-compatible with masks. Recovery paths must not complete or requeue tasks after refcount teardown.

## Test Signals
Exercise login/session setup, command queuing and completion, R2T/unsolicited data tracking, PDU padding, ITT stale detection, abort/session/device reset EH, connection suspend/resume/failure, parameter round trips, stats counters, pool exhaustion, and command recovery timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi.h -->
