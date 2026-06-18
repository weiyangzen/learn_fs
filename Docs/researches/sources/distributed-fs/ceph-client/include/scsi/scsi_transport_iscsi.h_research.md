<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_iscsi.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_iscsi.h

## Purpose
This header defines the iSCSI transport class control plane for software and hardware/offload transports. It covers transport callback templates, class session/connection/host/endpoint/interface objects, flashnode configuration objects, events, BSG, and helper allocation/lifecycle APIs.

## Important APIs, Types, And Functions
`struct iscsi_transport` contains callbacks for session/connection creation/binding/start/stop/destruction, parameter get/set, PDU send/stats, task init/xmit/cleanup, PDU allocation/transmit/init, ITT parsing, recovery timeout, endpoint connect/poll/disconnect, discovery/path/interface operations, BSG, ping, CHAP, flashnode operations, host stats, and protection checks. State objects include `iscsi_cls_conn`, `iscsi_cls_session`, `iscsi_cls_host`, `iscsi_endpoint`, `iscsi_iface`, `iscsi_bus_flash_conn`, and `iscsi_bus_flash_session`.

## Control Flow
Transports register a template, allocate sessions under a host, add targets, allocate/bind/start connections, and report login/error/PDU/offload/host events to the class. Session work items block/unblock/scan/unbind/destroy targets and delayed work handles recovery timeout. Endpoint APIs model socket/offload connection handles. Flashnode APIs expose firmware-stored discovery/session configuration.

## State And Persistence
Class session/connection state is runtime device-model state with locks, work items, recovery timers, target IDs, creator PID, and private data. Flashnode session/connection structures model firmware-persistent configuration parameters, credentials indices, discovery parent data, and boot-target state, though actual persistence is owned by hardware/firmware.

## Dependencies And Integration Points
It depends on Linux device/list/mutex and `iscsi_if.h`, and integrates with SCSI hosts, iSCSI userspace management via netlink/events, BSG, firmware offload, CHAP management, endpoint lifetimes, and `libiscsi`.

## Risks
Connection `ep_mutex` and spinlock protect different startup/binding/cleanup state; misuse can race endpoint disconnect and workqueue cleanup. Many callbacks return `-ENODATA` for unsupported params, which userspace depends on. Flashnode credential strings/indices need careful lifetime and security handling. Recovery timeout overrides affect failover behavior.

## Test Signals
Validate transport register/unregister, session/connection lifecycle, bind/unbind races, block/unblock/scan work, endpoint lookup/refcounting, parameter get/set unsupported cases, login/error/PDU events, BSG requests, ping completion, CHAP CRUD, flashnode create/login/logout/destroy, and protection callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_iscsi.h -->
