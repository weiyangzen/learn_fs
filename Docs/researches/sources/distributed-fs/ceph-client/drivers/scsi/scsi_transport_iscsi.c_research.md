# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_iscsi.c

## Purpose

`scsi_transport_iscsi.c` implements the Linux SCSI iSCSI transport class. It is the shared control plane between iSCSI low-level drivers, the SCSI midlayer, and userspace iSCSI management daemons. It publishes iSCSI transport, endpoint, interface, host, session, connection, and flashnode objects through the Linux device model; dispatches NETLINK_ISCSI userspace commands; emits asynchronous iSCSI events; coordinates session blocking and recovery; and provides BSG vendor passthrough for host-level iSCSI requests.

This file is not a PDU data-path implementation. Software and offload drivers provide a `struct iscsi_transport` callback table, and this class turns those callbacks into stable SCSI/sysfs/netlink APIs used by open-iscsi, firmware-offload tools, and the SCSI error handler.

## Important APIs, Types, and Functions

`struct iscsi_internal` wraps a `struct scsi_transport_template`, the registered `struct iscsi_transport`, the transport-class device, and transport containers for sessions and connections. Registered transports are tracked on `iscsi_transports` under `iscsi_transport_lock`; `iscsi_register_transport()` and `iscsi_unregister_transport()` are the public attach/release points.

Endpoint APIs are `iscsi_create_endpoint()`, `iscsi_destroy_endpoint()`, `iscsi_lookup_endpoint()`, and `iscsi_put_endpoint()`. Endpoints are numbered from an IDR beginning at 1 for userspace compatibility and expose a handle under `/sys/class/iscsi_endpoint`.

Interface and firmware flashnode APIs include `iscsi_create_iface()`, `iscsi_destroy_iface()`, `iscsi_create_flashnode_sess()`, `iscsi_create_flashnode_conn()`, `iscsi_find_flashnode_sess()`, `iscsi_find_flashnode_conn()`, `iscsi_destroy_flashnode_sess()`, and `iscsi_destroy_all_flashnode()`. Attribute visibility is delegated to `transport->attr_is_visible()`.

Session and connection lifecycle APIs include `iscsi_alloc_session()`, `iscsi_add_session()`, `iscsi_remove_session()`, `iscsi_free_session()`, `iscsi_force_destroy_session()`, `iscsi_alloc_conn()`, `iscsi_add_conn()`, `iscsi_remove_conn()`, `iscsi_get_conn()`, and `iscsi_put_conn()`. Recovery helpers include `iscsi_block_session()`, `iscsi_unblock_session()`, `iscsi_block_scsi_eh()`, `iscsi_session_chkready()`, and `iscsi_is_session_online()`.

Event APIs include `iscsi_recv_pdu()`, `iscsi_offload_mesg()`, `iscsi_conn_error_event()`, `iscsi_conn_login_event()`, `iscsi_post_host_event()`, `iscsi_ping_comp_event()`, and `iscsi_session_event()`. Debug hooks are exposed through exported tracepoints and `iscsi_dbg_trace()`.

## Control Flow

Module initialization registers the iSCSI transport, endpoint, and iface classes; the host, connection, and session transport classes; the flashnode bus; a NETLINK_ISCSI socket; and the `iscsi_conn_cleanup` workqueue. Exit unwinds those registrations and releases the netlink socket and cleanup workqueue.

Transport registration creates a device under `iscsi_transport`, exposes the transport handle and capabilities, registers host/connection/session attribute containers, sets the SCSI user scan hook, and appends the transport to the global list. Unregistration takes `rx_queue_mutex`, removes the transport from the list, unregisters all containers, removes the sysfs group, and unregisters the transport device so netlink dispatch cannot race a disappearing transport.

Userspace commands arrive in `iscsi_if_rx()`. The function serializes receive processing with `rx_queue_mutex`, validates netlink message sizes, calls `iscsi_if_recv_msg()`, and replies by unicast unless the command sent its own bulk response. `iscsi_if_recv_msg()` requires `CAP_SYS_ADMIN`, resolves the transport handle, pins the transport module, computes the trailing payload length, and dispatches create/destroy session, bind/start/stop connection, send PDU, endpoint connect/poll/disconnect, discovery, parameter, path, iface, ping, CHAP, flashnode, and host-stat operations.

Connection commands are split by state needs. Create, destroy, and stop are handled directly. Bind, start, and send PDU run under `conn->ep_mutex`; they first reject work if kernel cleanup has claimed the connection. A successful bind marks the connection `ISCSI_CONN_BOUND` and links the endpoint to the connection when endpoint callbacks exist. A successful start marks it `ISCSI_CONN_UP`.

Session creation calls the driver `create_session()` callback, records the userspace creator portid, and returns host and session IDs. `iscsi_add_session()` allocates a session ID, creates a per-session workqueue, assigns or allocates a target ID, registers the session device and transport attributes, inserts it on `sesslist`, and emits `ISCSI_KEVENT_CREATE_SESSION`. Removal deletes the session from lookup, cancels recovery/blocking work, marks the session free, unblocks SCSI to fail queued commands, flushes scans and unbinds, removes child connections, unregisters transport state, destroys the workqueue, and deletes the device.

Recovery flow is asynchronous. `iscsi_block_session()` queues work that marks the session failed, blocks targets, and optionally starts `recovery_work`. `iscsi_unblock_session()` cancels block/recovery work, marks the session logged in, unblocks the SCSI target, and flushes completion before returning. If recovery times out, `session_recovery_timedout()` moves failed sessions to free, unblocks targets as transport offline, and calls the driver timeout hook.

## State and Persistence Behavior

All persistence is volatile kernel state. Session IDs come from an atomic counter; SCSI target IDs may be assigned by the caller or allocated from `iscsi_sess_ida`; endpoint IDs are held in `iscsi_ep_idr`. Sessions and connections are also kept in global lookup lists protected by spinlocks. Session state includes `LOGGED_IN`, `FAILED`, and `FREE`; target binding state tracks unbound, allocated, scanned, and unbinding.

Device-model lifetime is central. Sessions hold a SCSI host reference until their release callback; connections hold a parent session device reference; iface release drops its parent host reference; endpoint release removes the IDR entry and frees memory. Flashnode release frees dynamically allocated string fields. Endpoint binding is protected by `conn->ep_mutex` so userspace endpoint disconnect and kernel cleanup do not free offload resources while attributes or callbacks are active.

The `recovery_tmo` sysfs attribute is transport-owned state. Userspace can override it unless the session is already failed/free; netlink parameter setting honors this override. During system shutdown, cleanup forces finite recovery timeouts to zero unless the user explicitly configured a non-timeout behavior.

## Dependencies and Integration Points

The file depends on the SCSI midlayer, transport class framework, Linux device model/sysfs, netlink, workqueues, IDR/IDA allocators, BSG, tracepoints, and UAPI structures from `iscsi_if.h` and `scsi_bsg_iscsi.h`. It integrates with userspace through NETLINK_ISCSI groups for iscsid and offload UIP, with SCSI EH through readiness/blocking helpers, and with driver callbacks for all transport-specific operations.

Drivers decide which attributes exist through `attr_is_visible()` and implement callbacks for endpoint connection, connection/session creation, start/stop/bind/send, parameter get/set, discovery, ping, CHAP, flashnode operations, host stats, BSG requests, and recovery timeout notification.

## Risks and Edge Cases

Connection cleanup is race-prone. Kernel error cleanup, userspace stop/disconnect, endpoint references, and connection state transitions are coordinated with `ISCSI_CLS_CONN_BIT_CLEANUP`, `ep_mutex`, and work flushing; missed ordering can leave resources leaked or callbacks run after endpoint teardown.

Netlink payload validation is uneven because many commands carry non-attribute trailing data. The file checks high-level lengths and string termination before parameter callbacks, but drivers still receive raw blobs for iface, path, CHAP, and flashnode operations.

The session and connection lookup helpers return pointers after dropping spinlocks without taking object references, relying on the serialized userspace/control-plane lifecycles around the lists. Destroy paths that remove from lookup before asynchronous teardown are particularly sensitive.

Attribute permission and visibility are callback-driven. Incorrect driver `attr_is_visible()` or getter behavior can expose unsupported or sensitive fields. Several credential fields are gated by `CAP_SYS_ADMIN` for reads, but the actual returned content is driver supplied.

Flashnode helpers assume a session has at most one flashnode connection child in lookup paths such as login/logout/set-param. Firmware implementations with unexpected child layouts would not be represented well.

## Test Signals

Useful signals include transport register/unregister with all sysfs containers present; endpoint create/lookup/destroy with ID reuse only after release; iface and flashnode visibility for IPv4, IPv6, CHAP, and firmware parameters; create/bind/start/send/stop/destroy connection netlink flows; endpoint disconnect races with `iscsi_conn_error_event()`; session block, unblock, recovery timeout, unbind, and target scan behavior; `iscsi_block_scsi_eh()` return values for failed versus free sessions; host and connection stats multicast responses; CHAP and flashnode netlink operations; BSG vendor command validation; and module unload after active transports have been unregistered.
