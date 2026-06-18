# Group Research: group_1360_open_iscsi_sources_virtualization_open_iscsi_usr_login_c_sources_vi_a098f115c193

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/open-iscsi`. All files listed for this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/login.c -->
# File Research: sources/virtualization/open-iscsi/usr/login.c

Purpose: Implements the iSCSI login negotiation engine used by userspace initiator paths. It builds Login Request PDUs, parses Login Response PDUs, negotiates security and operational text keys, handles target redirection, and drives the request/response loop until full-feature phase or failure.

Key entry points:
- `iscsi_add_text()` appends NUL-terminated `key=value` text entries to an iSCSI PDU data segment and updates the 24-bit data length field.
- `resolve_address()` wraps `getaddrinfo()` for target address resolution into `sockaddr_storage`.
- `iscsi_update_address()` parses `TargetAddress` values, including optional portal-group tag and bracketed IPv6 address, then updates the connection socket address and session TPGT.
- `iscsi_login_begin()`, `iscsi_login_req()`, and `iscsi_login_rsp()` expose a split login state machine for callers that manage polling externally.
- `iscsi_login()` is the synchronous login loop: make request, send PDU, poll the connection, receive/process response, and repeat until `ISCSI_FULL_FEATURE_PHASE`.

Implementation notes:
- Text-key parsing is exact-prefix based via `iscsi_find_key_value()`, which returns the value span within the received text data. `iscsi_process_login_response()` ensures a trailing NUL by requiring a receive buffer larger than the PDU data length.
- Security-stage keys are split between initiator-visible keys (`TargetAlias`, `TargetAddress`, `TargetPortalGroupTag`) and authentication-library keys selected through `acl_get_next_key_type()` and consumed with `acl_recv_key_value()`.
- Operational negotiation recognizes standard iSCSI keys such as `InitialR2T`, `ImmediateData`, burst lengths, digests, marker settings, ordering, `MaxConnections`, `ErrorRecoveryLevel`, and RDMA-specific keys. Unsupported or unacceptable values map to login-status failures rather than silent downgrade.
- Discovery sessions mark normal-session-only keys as irrelevant and later answer with `key=Irrelevant` using `session->irrelevant_keys_bitmap`.
- Digest negotiation supports strict `None`, strict `CRC32C`, and ordered preference lists (`None,CRC32C` or `CRC32C,None`) when constructing outbound login text.
- RDMA transports use `InitiatorRecvDataSegmentLength`, `TargetRecvDataSegmentLength`, and `RDMAExtensions`; non-RDMA and discovery use `MaxRecvDataSegmentLength`.
- Authentication setup initializes ACL buffers, username/password, CHAP algorithm list, IPsec flag, and bidirectional-auth policy from `iscsi_session_t`.
- Response validation checks active iSCSI version, current-stage consistency, transit-bit stage advancement, login opcode, and old draft-8 opcode mismatch.

Dependencies and interactions:
- Uses `initiator.h` session/connection state, `transport.h` transport properties, `log.h`, and `iscsi_timer.h`.
- Calls lower I/O functions `iscsi_io_send_pdu()` and `iscsi_io_recv_pdu()` through the connection.
- Uses authentication functions from the ACL/auth layer (`acl_init`, `acl_send_*`, `acl_recv_*`, `acl_finish`, CHAP helpers).
- Updates session command/status sequence numbers (`cmdsn`, `exp_cmdsn`, `max_cmdsn`, `tsih`) from accepted login responses.

Filesystem/storage relevance:
- This file is the userspace control-plane gateway that turns an iSCSI node record and transport connection into an authenticated, negotiated storage session. Storage parameters negotiated here determine later SCSI command limits, data segment sizes, digest enforcement, and error-recovery behavior.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/login.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/meson.build -->
# File Research: sources/virtualization/open-iscsi/usr/meson.build

Purpose: Defines Meson source groupings for the open-iscsi userspace programs under `usr`.

Key definitions:
- Enters `fwparam_ibft` with `subdir('fwparam_ibft')`.
- `iscsi_lib_srcs` is the common library-like source set shared by user tools. It includes login, sysfs, session info, transport, netlink IPC, iface, IDBM, flashnode, and utility code.
- `initiator_srcs` adds daemon initiator pieces such as `initiator.c`, `scsi.c`, event polling, management IPC, and kernel error tables.
- `discovery_srcs` contains discovery support.
- `iscsid_srcs`, `iscsiadm_srcs`, and `iscsistart_srcs` add program-specific main/control files.
- `iscsi_usr_arr` maps executable names (`iscsid`, `iscsiadm`, `iscsistart`) to the file arrays built from those source groups.

Implementation notes:
- `session_mgmt.c` and `mntcheck.c` are compiled into both `iscsid` and `iscsiadm`.
- `mgmt_ipc.c` is daemon-side and only part of the `iscsid` source set through `initiator_srcs`.
- `netlink.c`, `transport.c`, `uip_mgmt_ipc.c`, `session_info.c`, and `login.c` are common across the three programs through `iscsi_lib_srcs`.

Dependencies and interactions:
- This file does not declare link libraries or targets directly in the viewed content; it prepares source arrays consumed by surrounding Meson build files.

Filesystem/storage relevance:
- The build layout shows which storage-control features are shared by administration, daemon, and early-start tools, and which are daemon-only control-plane pieces.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/mgmt_ipc.c -->
# File Research: sources/virtualization/open-iscsi/usr/mgmt_ipc.c

Purpose: Implements the local management IPC server used by `iscsiadm` and related clients to send requests to `iscsid`.

Key entry points:
- `mgmt_ipc_listen()` obtains a systemd-passed socket when available or creates/listens on an abstract Unix-domain socket.
- `mgmt_ipc_systemd()` validates `LISTEN_PID` and `LISTEN_FDS` and returns fd 3 when exactly one socket is passed.
- `mgmt_ipc_close()` exits the event loop and closes the listening fd.
- `mgmt_ipc_handle()` and `mgmt_ipc_handle_legacy()` accept a client, authorize it, read a request, dispatch a handler, and send a response.
- `mgmt_ipc_write_rsp()` serializes `iscsiadm_rsp_t`, closes the per-request fd, frees any payload, and conditionally frees the task object.

Command handling:
- Session operations dispatch to `session_login_task()`, `session_logout_task()`, and `iscsi_sync_session()`.
- `MGMT_IPC_SESSION_STATS` finds a session by SID and calls `ipc->get_stats()`.
- `MGMT_IPC_SEND_TARGETS` calls `iscsi_host_send_targets()`.
- `MGMT_IPC_SESSION_INFO` returns daemon-side session and connection state.
- Config commands return initiator name, initiator alias, or config filename from `dconfig`.
- Immediate stop exits the event loop.
- Connection add/remove currently return generic error.
- Notify add/delete node/portal commands parse string-vector payloads but route to placeholder handlers that return success.

Implementation notes:
- Authorization defaults to Linux `SO_PEERCRED` UID check requiring UID 0. Legacy mode also resolves the peer username and requires `"root"`.
- Request payloads are bounded to `EXTMSG_MAX` (64 KiB) and allocated with one extra byte for possible NUL termination.
- Extended notification payloads encode repeated strings as a 32-bit length followed by raw bytes; `mgmt_ipc_parse_strings()` rewrites separators in place and returns an argv-style array.
- The dispatch table `mgmt_ipc_functions[]` maps command enum values to handler functions and rejects unknown or out-of-range commands.
- `queue_task_t->allocated` distinguishes standalone IPC tasks from tasks embedded in larger recovery structures.

Dependencies and interactions:
- Depends on daemon/session modules (`iscsid.h`, `initiator.h` through task handlers), IDBM/config, event loop control, transport, sysdeps, kernel IPC vtable, and error-code helpers.
- Writes responses with `ISCSI_ERR_*`/`ISCSI_SUCCESS` semantics expected by `iscsid_req` clients.

Filesystem/storage relevance:
- This file is the daemon command ingress for login/logout, target discovery, statistics, and session status. It connects administrative storage operations to the running userspace iSCSI session manager.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/mgmt_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/mgmt_ipc.h -->
# File Research: sources/virtualization/open-iscsi/usr/mgmt_ipc.h

Purpose: Declares the daemon/admin IPC command protocol, request/response wire structures, and management IPC server functions.

Key definitions:
- `ISCSIADM_NAMESPACE` names the abstract Unix socket namespace environment key.
- `iscsiadm_cmd_e` enumerates management commands, including session login/logout/sync/stats/info, connection add/remove, config reads, send-targets discovery, immediate stop, and discovery notifications.
- `iscsiadm_req_t` carries a command, optional payload length, and command-specific union fields for session record/SID, connection SID/CID, send-targets host/address, and host parameter setting.
- `iscsiadm_rsp_t` carries the command, an `ISCSI_ERR` result, and result unions for stats, config string, or session/connection state.
- `MGMT_IPC_GETSTATS_BUF_MAX` sizes the stats response buffer for base and custom iSCSI stats.
- `mgmt_ipc_fn_t` is the handler signature for a queue task.

Declared APIs:
- `mgmt_ipc_write_rsp()`
- `mgmt_ipc_listen()`
- `mgmt_ipc_systemd()`
- `mgmt_ipc_close()`
- `mgmt_ipc_handle()`
- `mgmt_ipc_handle_legacy()`

Dependencies and interactions:
- Includes `types.h`, `iscsi_if.h`, and `config.h` for protocol, kernel-interface, and size definitions.
- Embeds `node_rec_t` in session requests, making this IPC ABI carry full login records.

Filesystem/storage relevance:
- The header is the local control ABI between admin tooling and the iSCSI daemon for operations that create, tear down, inspect, or discover storage sessions.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/mgmt_ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/mntcheck.c -->
# File Research: sources/virtualization/open-iscsi/usr/mntcheck.c

Purpose: Checks whether block devices attached to an iSCSI session are currently in use by mounted filesystems, swap, partitions, or stacked block-device holders.

Key entry point:
- `session_in_use(int sid)` initializes libmount tables, resolves the iSCSI host number for the SID, iterates session devices, counts users, cleans up libmount state, and returns the count.

Implementation notes:
- `libmount_init()` creates mount and swap tables, attaches a cache, parses current mtab and swaps, and returns `-ENOMEM` on allocation failure.
- `blockdev_check_mnts()` reads `DEVNAME` from a sysfs `uevent`, builds `/dev/<name>`, and searches both mount and swap tables for that source.
- `blockdev_get_partitions()` scans child sysfs directories and recurses into those whose `uevent` `DEVTYPE` is `partition`.
- `blockdev_get_holders()` scans a device's `holders` directory, resolves holder symlinks with `realpath()`, and recurses into stacked devices such as dm/md layers.
- `count_device_users()` combines direct mount/swap checks, partition checks, and holder checks.
- `device_in_use()` maps a host/target/lun to a block device name using `iscsi_sysfs_get_blockdev_from_lun()` and checks `/sys/class/block/<dev>`.

Dependencies and interactions:
- Uses libmount for mounted filesystem and swap lookups.
- Uses iSCSI sysfs helpers for SID-to-host and LUN-to-block-device traversal.
- Reads generic sysfs `uevent` fields via `sysfs_get_uevent_devtype()` and `sysfs_get_uevent_devname()`.

Filesystem/storage relevance:
- This file protects session logout or shutdown flows from disconnecting iSCSI-backed block devices still in use by filesystems, swap, partitions, or upper-layer block mappings.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/mntcheck.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/netlink.c -->
# File Research: sources/virtualization/open-iscsi/usr/netlink.c

Purpose: Implements the open-iscsi userspace kernel IPC backend over `NETLINK_ISCSI`, exposing it as the global `struct iscsi_ipc *ipc`.

Key entry points:
- `ctldev_open()` allocates fixed transmit/receive buffers, opens a `NETLINK_ISCSI` socket, binds to the current pid and multicast group 1, and initializes the kernel destination address.
- `ctldev_close()` closes the control socket and frees buffers.
- `ctldev_handle()` reads and dispatches asynchronous kernel events.
- `ipc_register_ev_callback()` installs callbacks used to allocate, schedule, and free event contexts.
- `iscsi_nla_alloc()` allocates a netlink attribute with open-iscsi length macros.

Synchronous kernel commands:
- Session lifecycle: `kcreate_session()`, `kdestroy_session()`, `kunbind_session()`.
- Connection lifecycle: `kcreate_conn()`, `kdestroy_conn()`, `kbind_conn()`, `kstart_conn()`, `kstop_conn()`.
- Discovery and transport endpoints: `ksendtargets()`, `ktransport_ep_connect()`, `ktransport_ep_poll()`, `ktransport_ep_disconnect()`.
- Parameter paths: `kset_param()`, `kset_host_param()`, `kset_net_config()`.
- Stats and host data: `kget_stats()`, `kget_host_stats()`.
- CHAP table operations: `kget_chap()`, `kset_chap()`, `kdelete_chap()`.
- Flashnode operations: `kset_flashnode_params()`, `knew_flashnode()`, `kdel_flashnode()`, `klogin_flashnode()`, `klogout_flashnode()`, `klogout_flashnode_sid()`.
- Ping: `kexec_ping()` and `ksend_ping()`.

PDU streaming:
- `ksend_pdu_begin()` starts an in-memory `ISCSI_UEVENT_SEND_PDU` aggregate containing event header, iSCSI header, and data.
- `kwritev()` appends payload fragments to the aggregate for send-PDU operations, otherwise emits a netlink message immediately.
- `ksend_pdu_end()` sends the accumulated PDU and clears transmit state.
- `krecv_pdu_begin()` obtains an async receive context, points `recvbuf` at the PDU payload after the kernel event, and supports `-EAGAIN` for unrelated events.
- `kread()` copies from the current receive buffer.
- `krecv_pdu_end()` releases the event context and clears receive state.

Implementation notes:
- `__kipc_call()` serializes synchronous commands. It sends the request, peeks at incoming events, handles `ISCSI_KEVENT_IF_ERROR`, queues unrelated async events through `ctldev_handle()`, and only returns when the expected event type is available.
- Netlink send retries on `-ENOMEM` after sleeping, reflecting comments that kernel allocation can fail while the userspace path can wait.
- Fixed buffers are sized by `NLM_BUF_DEFAULT_MAX`, `PDU_SENDBUF_DEFAULT_MAX`, and `NLM_SETPARAM_DEFAULT_MAX`; oversized sends are treated as fatal bugs.
- `ctldev_handle()` recognizes create/destroy session, receive PDU, connection error, connection login state, unbind session, host link events, and ping completion. Unknown events are dropped after logging.
- Async connection events are matched by SID/CID to the in-memory session table and scheduled as `EV_CONN_RECV_PDU`, `EV_CONN_ERROR`, `EV_CONN_LOGIN`, or `EV_CONN_STOP`.
- `kexec_ping()` opens its own control device, sends a ping with a random pid, polls for up to 30 seconds, and matches completion by pid.

Dependencies and interactions:
- Depends on kernel ABI definitions from `iscsi_if.h`, transport/session state from `initiator.h` and `transport.h`, sysfs lookup via `iscsi_sysfs.h`, and timer helpers.
- Supplies the full `nl_ipc` vtable consumed by daemon/login/session code through the global `ipc`.
- Requires callback integration from the event loop/initiator layer to allocate and schedule receive contexts.

Filesystem/storage relevance:
- This is the userspace-to-kernel bridge that creates iSCSI kernel sessions/connections, pushes negotiated parameters, sends/receives iSCSI PDUs, receives connection failure events, and retrieves statistics for network block storage sessions.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/scsi.c -->
# File Research: sources/virtualization/open-iscsi/usr/scsi.c

Purpose: Provides SCSI sense-data normalization copied from Linux kernel SCSI error handling.

Key entry point:
- `scsi_normalize_sense(const uint8_t *sense_buffer, int sb_len, struct scsi_sense_hdr *sshdr)` extracts common fields from fixed-format and descriptor-format sense buffers.

Implementation notes:
- Rejects null or zero-length input, zeroes the output header, stores `response_code = sense_buffer[0] & 0x7f`, and validates it with `scsi_sense_valid()`.
- Descriptor-format responses (`response_code >= 0x72`) read `sense_key`, `asc`, `ascq`, and optional `additional_length` from bytes 1, 2, 3, and 7.
- Fixed-format responses read `sense_key` from byte 2 and, if the additional sense length covers them, read `asc` and `ascq` from bytes 12 and 13.
- The function returns 1 for valid normalized data and 0 when the sense buffer is absent or invalid.

Dependencies and interactions:
- Includes `scsi.h` for `struct scsi_sense_hdr` and `scsi_sense_valid()`.

Filesystem/storage relevance:
- Normalized sense keys and ASC/ASCQ values are the compact error details needed by storage tools when SCSI commands against iSCSI LUNs return CHECK CONDITION.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/scsi.h -->
# File Research: sources/virtualization/open-iscsi/usr/scsi.h

Purpose: Declares the SCSI sense header abstraction and normalization API.

Key definitions:
- `struct scsi_sense_hdr` stores response code, sense key, ASC, ASCQ, three intermediate bytes, and descriptor-format additional length.
- `scsi_sense_valid()` returns true when the response code has the SCSI sense response class bits (`0x70`) set.
- `scsi_normalize_sense()` is declared for converting raw sense bytes into `struct scsi_sense_hdr`.

Implementation notes:
- The structure intentionally supports response codes `0x70`, `0x71`, `0x72`, and `0x73`, allowing both fixed and descriptor sense formats to be represented in one shape.

Dependencies and interactions:
- Includes `stdint.h` for fixed-width byte fields.

Filesystem/storage relevance:
- Defines the minimal SCSI error-information structure used by initiator-side storage diagnostics and error handling.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/scsi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_info.c -->
# File Research: sources/virtualization/open-iscsi/usr/session_info.c

Purpose: Builds and prints active iSCSI session information for admin tooling, combining libopeniscsiusr session objects, sysfs attributes, daemon IPC state, interface records, negotiated parameters, timeouts, CHAP settings, and attached SCSI devices.

Key entry points:
- `session_info_create_list()` copies a `session_info` object into a sorted/grouped linked list, optionally filtered by a match callback.
- `session_info_free_list()` frees a list built by `session_info_create_list()`.
- `session_info_print()` prints session arrays at info levels 0 through 3.
- `session_info_print_tree()` prints grouped target/portal/session details according to bit flags.

Implementation notes:
- Flat output (`session_info_print_flat()`) prints transport, SID, persistent portal, TPGT, target name, and node type (`flash` or `non-flash`).
- Node type is inferred through `iscsi_sysfs_session_user_created()`: sessions without a user-created pid are treated as flash.
- `print_iscsi_state()` sends `MGMT_IPC_SESSION_INFO` to `iscsid` for daemon connection/internal state and reads kernel session state from sysfs.
- `print_iscsi_params()` reads negotiated session and connection config from sysfs and prints valid operational values only.
- `print_scsi_state()` maps SID to host number, optionally prints host state, and iterates attached devices.
- `print_scsi_device_info()` prints each host/target/lun, block-device name, and device state when available.
- Tree output groups consecutive sessions by target name and current portal, prints current and persistent portals, then conditionally prints interface, state, timeouts, CHAP, negotiated parameters, and SCSI devices.
- Passwords are masked unless `do_show` is set.
- Info level behavior: level 0/default prints flat lines; level 1 includes state and iface; level 2 adds iSCSI params, timeouts, and auth; level 3 adds kernel/tool version and SCSI/host devices.

Dependencies and interactions:
- Uses `libopeniscsiusr` getters for session fields.
- Uses open-iscsi sysfs helpers for transport, state, negotiated params, host numbers, LUN iteration, device state, and kernel version.
- Uses management IPC through `iscsid_exec_req()` and `MGMT_IPC_SESSION_INFO`.
- Uses `iface_print()` for interface details.

Filesystem/storage relevance:
- This is the user-visible inspection layer for active iSCSI-backed storage sessions, including portal identity, negotiated block-transfer parameters, authentication settings, and attached SCSI/block devices.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_info.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_info.h -->
# File Research: sources/virtualization/open-iscsi/usr/session_info.h

Purpose: Declares data structures and print/list APIs for active iSCSI session reporting.

Key definitions:
- `struct session_timeout` stores abort, LUN reset, recovery, and target reset timeouts.
- `struct session_CHAP` stores outgoing and incoming CHAP username/password strings.
- `struct session_info` stores local iface/SID/request-timeout fields plus remote target name, TPGT, current portal, and persistent portal details.
- `session_match_info_fn_t` is the callback type for filtering `session_info` entries.
- `struct session_link_info` passes list, match callback, and callback data into sysfs session iteration.
- `SESSION_INFO_*` flags select interface, negotiated parameters, state, SCSI devices, host devices, timeouts, and auth output.

Declared APIs:
- `session_info_create_list()`
- `session_info_free_list()`
- `session_info_print()`
- `session_info_print_tree()`

Dependencies and interactions:
- Includes libopeniscsiusr session declarations, generic `sysfs.h`, iSCSI protocol/config size definitions, and project list types.

Filesystem/storage relevance:
- Provides the structured representation used to correlate iSCSI sessions with portals, interfaces, authentication, timeouts, and attached storage devices.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_info.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_mgmt.c -->
# File Research: sources/virtualization/open-iscsi/usr/session_mgmt.c

Purpose: Implements admin-side helpers for requesting iSCSI session login/logout operations from `iscsid`, including batching, async request tracking, multi-session creation, and active-session checks.

Key entry points:
- `iscsi_login_portal()` logs into one portal record, honoring `session.nr_sessions` and `session.multiple`.
- `iscsi_login_portal_nowait()` sends login requests and closes async request fds without waiting for final results.
- `iscsi_login_portals()` logs into every record on a list and frees the list afterward.
- `iscsi_login_portals_safe()` performs the same batching without clearing the caller's list.
- `iscsi_logout_portal()` sends a logout request for a specific `session_info`.
- `iscsi_logout_portals()` discovers active sessions, applies a caller-provided logout filter/function, and optionally waits for all logouts.
- `iscsi_check_for_running_session()` checks sysfs for an existing session matching a node record.

Implementation notes:
- Async requests are tracked in `struct iscsid_async_req`, which stores a list node, caller data pointer, and socket fd.
- `__iscsi_login_portal()` sends either sync or async `MGMT_IPC_SESSION_LOGIN` requests by node record and logs immediate failures.
- `iscsi_login_portal()` counts existing matching sessions through `iscsi_sysfs_for_each_session()` and only creates missing sessions up to `rec->session.nr_sessions`.
- For multi-session records, it sets `rec->session.multiple` before issuing repeated login requests.
- `__iscsi_login_portals()` batches logins, waits with `iscsid_login_reqs_wait()` when requested, otherwise closes pending fds.
- Logout batching first builds a `session_info` list from sysfs, then applies the caller's logout function to each entry and waits/closes async requests according to the `wait` flag.
- Logging helpers report target, iface, portal, SID, and detailed iSCSI error text through `iscsi_err_print_msg()`.

Dependencies and interactions:
- Uses management IPC helpers from `iscsid_req.h` with `MGMT_IPC_SESSION_LOGIN` and `MGMT_IPC_SESSION_LOGOUT`.
- Uses sysfs session iteration and match callbacks from `iscsi_sysfs.h`.
- Uses `session_info_create_list()` and `session_info_free_list()` for logout target discovery.
- Uses IDBM node records and project list primitives.

Filesystem/storage relevance:
- This file is the admin orchestration layer that turns configured iSCSI node records into active kernel sessions and tears down active storage sessions selected from sysfs.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_mgmt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_mgmt.h -->
# File Research: sources/virtualization/open-iscsi/usr/session_mgmt.h

Purpose: Declares session login/logout management helpers used by open-iscsi admin and daemon code.

Key declarations:
- Portal login helpers: `iscsi_login_portal()`, `iscsi_login_portal_nowait()`, `iscsi_login_portals()`, and `iscsi_login_portals_safe()`.
- Portal logout helpers: `iscsi_logout_portal()` and `iscsi_logout_portals()`.
- Session existence helper: `iscsi_check_for_running_session()`.

Implementation notes:
- Uses forward declarations for `struct node_rec`, `struct list_head`, and `struct session_info`, keeping the header lightweight.
- Batch login/logout APIs take callback function pointers so callers can supply filtering or alternate per-record behavior.

Dependencies and interactions:
- Implemented by `session_mgmt.c`; callers must include concrete node/list/session definitions where they build records or callbacks.

Filesystem/storage relevance:
- Exposes the high-level API for creating or removing iSCSI storage sessions from lists of configured portals or active session records.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/session_mgmt.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/sysfs.c -->
# File Research: sources/virtualization/open-iscsi/usr/sysfs.c

Purpose: Provides generic sysfs path resolution, device caching, attribute reads/writes, typed conversion helpers, and `uevent` field extraction. The code is derived from udev sysfs utilities.

Key entry points:
- `sysfs_init()` sets global `sysfs_path` from `SYSFS_PATH` or defaults to `/sys`, then initializes the device cache.
- `sysfs_cleanup()` frees cached `sysfs_device` entries.
- `sysfs_device_get()` resolves supported sysfs device paths, follows symlinks, populates subsystem/driver/kernel names, and caches devices.
- `sysfs_device_get_parent()` and `sysfs_device_get_parent_with_subsystem()` traverse device parents.
- `sysfs_attr_get_value()` reads an attribute or symlink target value from a device path.
- `sysfs_lookup_devpath_by_subsys_id()` maps subsystem/id pairs to sysfs devpaths across `/subsystem`, `/bus`, `/class`, `/module`, `/firmware`, and driver layouts.
- `sysfs_get_value()` composes lookup plus attribute read and filters `<NULL>`/`(null)` values.
- Typed readers: `sysfs_get_uint()`, `sysfs_get_int()`, `sysfs_get_str()`, `sysfs_get_uint64()`, `sysfs_get_uint8()`, and `sysfs_get_uint16()`.
- `sysfs_set_param()` writes a sysfs attribute after path lookup and permission validation.
- `sysfs_get_uevent_field()`, `sysfs_get_uevent_devtype()`, and `sysfs_get_uevent_devname()` read fields from a device `uevent` file.

Implementation notes:
- Device cache entries store devpath, subsystem, driver, kernel name, kernel numeric suffix, and parent pointer.
- `sysfs_resolve_link()` resolves relative symlink targets containing `../` segments into absolute sysfs devpaths relative to `sysfs_path`.
- `sysfs_device_set_values()` also translates `!` in kernel names to `/`, matching sysfs naming behavior.
- `sysfs_attr_get_value()` treats symlink attributes as the final path component of the symlink target, skips directories and unreadable files, reads up to `NAME_SIZE`, and strips trailing newlines.
- Integer readers initialize outputs to `-1`; `sysfs_get_int()` treats `"off"` specially for `iscsi_session` attributes.
- `sysfs_set_param()` requires user-write permission and writes the caller-provided buffer size exactly.
- `sysfs_get_uevent_field()` reads `/uevent` line by line, tokenizes on `=`, and duplicates the requested value.

Dependencies and interactions:
- Uses project list primitives, `strlcpy`/`strlcat` from `sysdeps.h`, and logging.
- Serves higher-level open-iscsi sysfs helpers and mount/session code that need typed reads from kernel sysfs.

Filesystem/storage relevance:
- iSCSI session discovery, mounted-device checks, transport detection, and status reporting all rely on sysfs. This file is the generic sysfs access substrate under those storage-control paths.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/sysfs.h -->
# File Research: sources/virtualization/open-iscsi/usr/sysfs.h

Purpose: Declares the generic sysfs utility API and cached device representation used by open-iscsi.

Key definitions:
- `PATH_SIZE` is 512 and `NAME_SIZE` is 256 for sysfs path/name buffers.
- `struct sysfs_device` stores list linkage, cached parent pointer, devpath, subsystem, kernel name, kernel numeric suffix, and driver name.
- `sysfs_path` is the global base path, normally `/sys`.

Declared APIs:
- Initialization/cleanup: `sysfs_init()`, `sysfs_cleanup()`.
- Device helpers: `sysfs_device_set_values()`, `sysfs_device_get()`, `sysfs_device_get_parent()`, `sysfs_device_get_parent_with_subsystem()`.
- Path/value helpers: `sysfs_attr_get_value()`, `sysfs_resolve_link()`, `sysfs_lookup_devpath_by_subsys_id()`, `sysfs_get_value()`.
- Typed readers/writer: `sysfs_get_uint()`, `sysfs_get_int()`, `sysfs_get_str()`, `sysfs_get_uint64()`, `sysfs_get_uint8()`, `sysfs_get_uint16()`, `sysfs_set_param()`.
- Uevent helpers: `sysfs_get_uevent_field()`, `sysfs_get_uevent_devtype()`, and `sysfs_get_uevent_devname()`.

Dependencies and interactions:
- Includes `stdint.h`, project `list.h`, and project string helpers.

Filesystem/storage relevance:
- Exposes reusable sysfs primitives that the iSCSI userspace tools use to map sessions, hosts, SCSI devices, and block devices into kernel-visible storage state.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/transport.c -->
# File Research: sources/virtualization/open-iscsi/usr/transport.c

Purpose: Defines built-in iSCSI transport templates, probes/loads kernel transport modules, and attaches runtime transport records to matching templates.

Key entry points:
- `transport_probe_for_offload()` enumerates network interfaces, identifies Ethernet devices, maps netdevs to iSCSI transport names, and attempts to load matching kernel modules.
- `transport_load_kmod()` loads a transport module with libkmod, including special module-name mappings for `tcp` -> `iscsi_tcp` and `iser` -> `ib_iser`.
- `set_transport_template()` matches an `iscsi_transport` name to a static template and stores the template pointer.

Transport templates:
- `iscsi_tcp`: software TCP path using userspace TCP endpoint functions.
- `iscsi_iser`: RDMA/iSER path using kernel transport endpoint functions and `iser_create_conn()`.
- `cxgb3i` and `cxgb4i`: Chelsio offload transports with bind-required endpoint handling and cxgbi connection creation.
- `bnx2i`: Broadcom offload transport requiring host IP setup, boot info, uIP net config, and uIP ping.
- `be2iscsi`: offload transport with VLAN sync and custom connection creation.
- `qla4xxx` and `ocs`: bind-required kernel endpoint transports.
- `qedi`: offload transport requiring host IP, boot info, no netdev, uIP net config, and uIP ping.

Implementation notes:
- `transport_probe_for_offload()` uses `if_nameindex()`, an AF_INET datagram socket, and `SIOCGIFHWADDR` to restrict probing to Ethernet-like interfaces.
- Module insertion uses `kmod_module_probe_insert_module()` with `KMOD_PROBE_APPLY_BLACKLIST`.
- Missing or unknown templates are logged as likely requiring updated userspace tooling.

Dependencies and interactions:
- Uses endpoint functions from TCP I/O, netlink kernel transport (`ktransport_ep_*`), and offload-specific modules (`cxgbi`, `be2iscsi`, `iser`, `uip_mgmt_ipc`).
- Uses network utility `net_get_transport_name_from_netdev()` and error constants from `iscsi_err.h`.

Filesystem/storage relevance:
- Transport selection decides whether iSCSI storage sessions use software TCP, RDMA, or hardware offload paths, and controls how network endpoints and host IP configuration are established.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/transport.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/transport.h -->
# File Research: sources/virtualization/open-iscsi/usr/transport.h

Purpose: Declares iSCSI transport metadata, behavior hooks, and module-loading/template matching APIs.

Key definitions:
- `enum set_host_ip_opts` describes whether a transport does not support, requires, or optionally uses host IP configuration.
- `struct iscsi_transport_template` names a transport and declares feature flags (`rdma`, `set_host_ip`, `use_boot_info`, `bind_ep_required`, `no_netdev`, `sync_vlan_settings`) plus hooks for endpoint connect/poll/disconnect, connection creation, network config, and ping.
- `struct iscsi_transport` represents a runtime data-path provider with list linkage, kernel handle, capabilities, name, session list, and selected template.

Declared APIs:
- `set_transport_template()`
- `transport_load_kmod()`
- `transport_probe_for_offload()`

Dependencies and interactions:
- Includes project `types.h` and `config.h`.
- Forward-declares `struct iscsi_transport` and `struct iscsi_conn`; hook signatures also refer to `struct iface_rec` and `struct iscsi_session`.

Filesystem/storage relevance:
- Defines the abstraction boundary between iSCSI session management and the actual network/storage transport implementation.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/transport.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/types.h -->
# File Research: sources/virtualization/open-iscsi/usr/types.h

Purpose: Provides common fixed-width and system type includes plus sparse-style big-endian typedef aliases for userspace code.

Key definitions:
- Includes networking/system integer headers: `netinet/in.h`, `stdint.h`, `sys/types.h`, and `limits.h`.
- Defines `__be16` as `uint16_t` and `__be32` as `uint32_t`.

Implementation notes:
- Comments explain that the `__be` names mirror kernel sparse typechecking conventions even though this userspace header maps them directly to integer types.

Dependencies and interactions:
- Included by IPC, transport, and other protocol-facing headers that share kernel-style type names.

Filesystem/storage relevance:
- Supplies protocol type aliases used around iSCSI and kernel-interface structures.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.c -->
# File Research: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.c

Purpose: Sends management broadcasts from `iscsid`/admin code to the uIP helper for offload transports that need userspace IP configuration or ping handling.

Key entry points:
- `uip_broadcast_params()` sends an `ISCSID_UIP_IPC_GET_IFACE` broadcast containing an `iface_rec`.
- `uip_broadcast_ping_req()` sends an `ISCSID_UIP_IPC_PING` broadcast containing interface data, destination address, and ping payload length, and waits for status.

Implementation notes:
- Both functions populate `struct iscsid_uip_broadcast`, set command and payload length, copy the relevant interface record, and call `uip_broadcast()`.
- `uip_broadcast_params()` uses `O_NONBLOCK` and does not request a status pointer.
- `uip_broadcast_ping_req()` accepts IPv4 and IPv6 destination addresses, rejects unknown address families with `ISCSI_ERR_INVAL`, stores `datalen`, and passes `status` through to `uip_broadcast()`.

Dependencies and interactions:
- Uses `uip_mgmt_ipc.h` protocol structures, `iscsid_req.h` for `uip_broadcast()`, logging, and iSCSI error constants.
- Referenced by transport templates such as `bnx2i` and `qedi` for `.set_net_config` and `.exec_ping`.

Filesystem/storage relevance:
- Supports hardware/offload iSCSI transports whose network setup is delegated to a uIP companion process before or during storage session establishment.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.h -->
# File Research: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.h

Purpose: Defines the local broadcast protocol used between open-iscsi userspace and the uIP helper process.

Key definitions:
- `ISCSID_UIP_NAMESPACE` names the abstract namespace used for uIP IPC.
- `iscsid_uip_cmd_e` enumerates uIP commands: unknown, get iface, and ping.
- `iscsid_uip_broadcast_header_t` carries command and payload length.
- `iscsid_uip_broadcast_t` carries either an interface record or a ping record with interface, destination address, data length, and status pointer.
- `iscsid_uip_mgmt_ipc_err_e` enumerates uIP IPC result states including OK, generic error, not found, no memory, device up, and device initializing.
- `iscsid_uip_rsp_t` carries command, uIP IPC error, and iSCSI ping status code.

Declared APIs:
- `uip_broadcast_params()`
- `uip_broadcast_ping_req()`

Dependencies and interactions:
- Includes generic types, kernel iSCSI interface definitions, config, management IPC declarations, initiator state, and transport types.

Filesystem/storage relevance:
- Defines the protocol shape for offload-network setup and ping checks that gate access to iSCSI storage sessions on supported hardware transports.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/version.h -->
# File Research: sources/virtualization/open-iscsi/usr/version.h

Purpose: Centralizes the userspace iSCSI tools version string requirement and the sysfs path for the kernel iSCSI transport class version.

Key definitions:
- Requires `ISCSI_VERSION_STR` to be defined by the build system; otherwise compilation fails with `#error Must set ISCSI_VERSION_STR`.
- Defines `ISCSI_VERSION_FILE` as `/sys/module/scsi_transport_iscsi/version`.

Implementation notes:
- Comments note that the tools version may differ from kernel version because kernel-side patches can be merged independently.

Dependencies and interactions:
- Used by session reporting code to print userspace version alongside the kernel iSCSI transport class version.

Filesystem/storage relevance:
- Provides version identity for iSCSI tooling and points to the kernel transport-class version exposed through sysfs.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/version.h -->