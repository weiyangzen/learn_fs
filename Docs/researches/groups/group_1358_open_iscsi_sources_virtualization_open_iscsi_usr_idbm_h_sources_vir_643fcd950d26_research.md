# Group Research: group_1358_open_iscsi_sources_virtualization_open_iscsi_usr_idbm_h_sources_vir_643fcd950d26

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/idbm.h -->
# File Research: sources/virtualization/open-iscsi/usr/idbm.h

This header defines the public interface for open-iscsi's initiator database manager, which persists and retrieves discovery, node, iface, host CHAP, and flashnode records below `ISCSI_DB_ROOT`.

Key contents:
- Database path constants for nodes, iSNS, static, firmware, and SendTargets records: `NODE_CONFIG_DIR`, `ISNS_CONFIG_DIR`, `STATIC_CONFIG_DIR`, `FW_CONFIG_DIR`, `ST_CONFIG_DIR`.
- Record value typing constants used by `recinfo_t`: integer, string, sized integer, and integer-list variants.
- `recinfo_t`, the generic descriptor for a configurable key: name, value string, backing data pointer/length, visibility, accepted options, and mutability.
- `idbm_t`, the in-memory database manager state, holding config file callback, node/discovery defaults, and `recinfo_t` arrays.
- `struct user_param`, a list item for user-supplied name/value updates.
- Iteration callback types and walkers for portals, nodes, node records, SendTargets discovery records, and iSNS discovery records.
- CRUD/default/read/update/print APIs for node records, discovery records, iface records, host CHAP records, and flashnode records.
- Lower-level helpers exported for `iface.c`, including config serialization/parsing, record metadata construction, DB locking, parameter verification, and parameter update.

Important dependencies:
- Includes `initiator.h`, `config.h`, `list.h`, and `flashnode.h`.
- The header exposes `node_rec_t`, `discovery_rec_t`, `struct iface_rec`, `struct iscsi_chap_rec`, and `struct flashnode_rec` interactions, so it is a central bridge between persisted config and runtime initiator/session structures.

Filesystem/storage relevance:
- This is the control-plane persistence layer for iSCSI storage targets. It does not issue I/O itself, but it defines the records that determine which remote block devices are discovered, logged into, scanned, and exposed to the host.

Notable implementation constraints:
- Fixed maxima are used for keys, key names, values, and option lists (`MAX_KEYS`, `NAME_MAXVAL`, `VALUE_MAXVAL`, `OPTS_MAXVAL`).
- DB locking policy is exposed with retry timing constants and lock/unlock functions.
- There is a duplicated declaration of `idbm_node_setup_defaults`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/idbm.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/idbm_fields.h -->
# File Research: sources/virtualization/open-iscsi/usr/idbm_fields.h

This header is the string schema for open-iscsi database records. It defines the exact key names used in persisted configuration files and in `recinfo_t` mappings.

Key field groups:
- Record framing: `ISCSI_BEGIN_REC`, `ISCSI_END_REC`.
- Node identity/startup/discovery fields: `node.name`, `node.tpgt`, startup, discovery address/port/type, boot LUN.
- Session fields: command sequencing, retry counts, queue depth, CHAP credentials, timeouts, iSCSI negotiation parameters, autoscan, and reopen settings.
- Connection fields: per-connection portal address/port, TCP window/TOS/congestion options, login/logout/auth/noop timeouts, digests, markers, and data segment lengths.
- Iface fields: binding identity, initiator name, ISID, IPv4/IPv6 address configuration, VLAN, TCP/network tuning, DHCP options, IPv6 neighbor/router behavior, and iSCSI offload/session knobs.
- Discovery fields: SendTargets and iSNS startup, type, address/port, auth, timeouts, discovery daemon controls, and receive segment length.
- Host CHAP fields: table index, auth method, usernames, passwords, and password lengths.
- Flashnode session and connection fields: firmware-backed discovery/session/portal flags, CHAP indexes and credentials, target metadata, boot target flag, per-connection digest/TCP/IP/VLAN-style parameters, statsn fields, and redirect/local addresses.

Important dependencies:
- Includes `version.h` for versioned begin-record markers.

Filesystem/storage relevance:
- This is the canonical on-disk/user-visible naming layer for iSCSI target, session, interface, and firmware flashnode configuration. Tools that create or mutate remote block-storage sessions depend on these exact strings.

Notable details:
- The iSNS address and port macros are defined as `discovery.sendtargets.address` and `discovery.sendtargets.port`, which may be intentional compatibility behavior or a schema typo. It is worth checking corresponding parser/serializer code before changing it.
- Many fields map to kernel IPC attributes later built in `iface.c` and `initiator_common.c`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/idbm_fields.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/iface.c -->
# File Research: sources/virtualization/open-iscsi/usr/iface.c

This implementation manages iSCSI iface records: default interfaces, persisted iface config files, matching/binding logic, boot-context conversion, iface printing, iface enumeration, and translation of iface records into kernel netlink parameter buffers.

Major responsibilities:
- Defines built-in default ifaces:
  - `default` using `tcp`.
  - `iser` using `iser`.
- Reads, writes, updates, deletes, and enumerates iface config files under `IFACE_CONFIG_DIR`.
- Protects config file reads/writes with `idbm_lock()` and `idbm_unlock()`.
- Prevents modification/deletion/persistence of special default iface records.
- Creates default offload iface records by scanning SCSI hosts, transport names, hardware addresses, and kernel-exported iface records.
- Copies sparse iface records with `iface_copy()`, only overwriting destination fields that are present/nonzero in the source.
- Validates iface records based on name, transport, and binding by hardware address/netdev/ip/transport.
- Matches iface patterns by iface name and, except for `default`, by transport name.
- Prints iface records in tree or flat forms and links non-default ifaces into lists.
- Builds iface records from boot firmware contexts, including initiator name, MAC, address, VLAN, subnet, gateway, transport, and generated iface name.
- Counts and serializes iface network parameters into `struct iovec` arrays for kernel IPC/netlink setup.

Key control flow:
- `iface_conf_read()` first handles built-in defaults, then reads persisted config under DB lock. If a requested iface is missing, it attempts offload host binding setup once and retries.
- `iface_setup_host_bindings()` creates the iface directory if needed, probes offload transports, scans hosts, and writes generated iface files for offload adapters.
- `iface_for_each_iface()` yields default ifaces unless skipped, then opens `IFACE_CONFIG_DIR`, reads each persisted iface, validates it, and invokes the caller callback.
- `iface_get_param_count()` and `iface_build_net_config()` share filtering by primary hardware address and can operate on one iface or all matching ifaces.
- IPv4 handling supports DHCP or static address/subnet/gateway plus DHCP DNS/SLP/vendor/client-id controls, TOS, ARP, fragmentation, forwarding, TTL, and common TCP/iSCSI parameters.
- IPv6 handling supports address autoconfig, link-local autoconfig, router autoconfig, explicit IPv6/link-local/router addresses, neighbor discovery controls, MLD, flow label, traffic class, hop limit, and common TCP/iSCSI parameters.
- Common parameter serialization covers iface enable, VLAN enable/tag, MTU, port, delayed ACK, Nagle, window scaling, TCP timestamps, redirect, task management timeout, digests, immediate data, initial R2T, ordering, ERL, burst lengths, R2T count, and CHAP/discovery flags.

Important dependencies:
- Uses IDBM metadata/parsing/printing functions from `idbm.h`.
- Uses sysfs and host helpers for offload discovery.
- Uses net helpers for transport lookup and netdev activation.
- Uses `iscsi_netlink.h` allocation/alignment helpers and kernel `iscsi_if.h` net parameter IDs.
- Uses `libopeniscsiusr` accessor APIs for printing `struct iscsi_iface`.

Filesystem/storage relevance:
- This file is the binding layer between configured iSCSI targets and network interfaces. Correct iface binding determines which NIC/offload path carries storage traffic and how firmware/uIP/kernel networking is configured before login.

Notable implementation constraints and risks:
- Several string copies use fixed-size buffers and assume source data already fits the target struct fields.
- `iface_get_iptype()` uses heuristics rather than full address validation.
- IP-address binding is recognized but software TCP binding by IP is explicitly unsupported.
- Parameter counting must stay exactly in sync with parameter construction; otherwise callers may allocate the wrong iovec capacity.
- The code treats zero numeric values as absent for many fields, which can make it impossible to represent a meaningful explicit zero for some parameters.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/iface.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/iface.h -->
# File Research: sources/virtualization/open-iscsi/usr/iface.h

This header declares the iface management API and iface config directory for open-iscsi.

Key contents:
- `IFACE_CONFIG_DIR`, pointing to `ISCSI_DB_ROOT"/ifaces"`.
- Forward declarations for `struct iface_rec`, `struct list_head`, and `struct boot_context`.
- APIs for copying, matching, allocating, reading, defaulting, validating, writing, updating, deleting, enumerating, and linking iface records.
- Binding predicates for hardware address, netdev, and IP address.
- Printing helpers for tree and flat iface output.
- Boot-context helpers for deriving iface records from firmware boot metadata.
- Kernel net-config helpers:
  - `iface_get_param_count()`
  - `iface_build_net_config()`
  - `iface_get_iptype()`
- `iface_fmt` and `iface_str()` logging macros for consistent iface log formatting.

Important dependencies:
- Includes `libopeniscsiusr/libopeniscsiusr.h` for `struct iscsi_iface` and iface type definitions.
- Includes `<sys/uio.h>` for iovec-based netlink parameter construction.

Filesystem/storage relevance:
- This header exposes the interface binding layer used by session login and offload setup, which directly affects how iSCSI-backed block devices are reached.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/iface.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/initiator.c -->
# File Research: sources/virtualization/open-iscsi/usr/initiator.c

This is the main iSCSI initiator slow-path/session management implementation. It drives session creation, connection establishment, login negotiation, recovery/reopen, logout, async event handling, userspace NOP handling, session resync, and IPC event callback registration.

Major responsibilities:
- Allocates and manages per-connection event contexts from a fixed pool.
- Creates and destroys `iscsi_session_t` and leading connection state.
- Maps login response statuses and iSCSI status class/detail into retry, redirect, fatal, auth-failure, or success outcomes.
- Initializes connection timeouts, NOP settings, TCP options, negotiated parameters, and portal address resolution.
- Performs initial connection and login scheduling through the actor/event system.
- Handles login timeouts, transport errors, kernel-reported connection errors, redirects, and recovery stages.
- Starts full-feature phase after login by setting negotiated params, starting the kernel connection, scanning the host, and scheduling userspace NOPs when needed.
- Sends logout PDUs, handles logout timeout, unbinds sessions when supported, and shuts down/destroys kernel/user session state.
- Handles incoming NOP-In, logout responses, async events, and login responses.
- Supports login-offload transports by waiting for kernel connection-state notifications instead of doing all login negotiation in userspace.
- Supports session sync after daemon restart or external session creation by reconstructing userspace state from node record and sysfs session id.
- Registers `iscsi_ipc_ev_clbk` callbacks for async firmware/session creation/destruction and per-connection event scheduling.

Key state machines:
- Connection states are interpreted across `ISCSI_CONN_STATE_XPT_WAIT`, `IN_LOGIN`, `LOGGED_IN`, `IN_LOGOUT`, `LOGOUT_REQUESTED`, and `CLEANUP_WAIT`.
- Recovery stages use `R_STAGE_NO_CHANGE`, `SESSION_CLEANUP`, `SESSION_REOPEN`, `SESSION_REDIRECT`, and `SESSION_DESTOYED`.
- Login error handling distinguishes initial login retry timeout, fatal login errors, auth failures, redirected retries, recovery reconnects, and cleanup.
- Reopen paths honor `DefaultTime2Wait`, reopen counters/max, reconnect delay constants, and whether the reopen follows redirect or ordinary failure.

Important entry points:
- `session_login_task()` starts login for a node record and internally retries when host/offload readiness is not available yet.
- `session_logout_task()` logs out a running session, with safe-logout checks against mounted/in-use storage.
- `iscsi_sync_session()` reconstructs daemon state for an existing kernel session and starts recovery.
- `iscsi_host_send_targets()` asks offload-capable transports to perform SendTargets discovery.
- `free_initiator()` releases all sessions and transports.
- `iscsi_initiator_init()` registers IPC callbacks.

Important dependencies:
- Depends on `transport`, `ipc`, sysfs helpers, IDBM, management IPC, actor/event scheduling, SCSI sense parsing, kernel error translation, and config defaults.
- Calls shared setup functions from `initiator_common.c`.
- Calls socket/PDU helpers from `io.c`.

Filesystem/storage relevance:
- This is the daemon control path that turns persisted target records into active kernel iSCSI sessions, which then expose remote SCSI LUNs as local block devices. It also performs host scans and queue-depth setup after login.

Notable implementation constraints and risks:
- Only the leading connection is fully handled in several places; comments mark multi-connection login/logout as TODO.
- Recovery depends on actor scheduling and context-pool availability; leaks are logged if allocated contexts remain during teardown.
- Some shutdown paths call response-writing helpers through task pointers that may be NULL depending on error source; safety depends on downstream helper behavior.
- Fatal/auth login failures force the reopen counter to its max to stop retry loops.
- `R_STAGE_SESSION_DESTOYED` is misspelled in the enum and usage, but consistently named.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/initiator.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/initiator.h -->
# File Research: sources/virtualization/open-iscsi/usr/initiator.h

This header defines the core runtime data structures and public APIs for the open-iscsi daemon initiator.

Key contents:
- Default config paths:
  - `CONFIG_FILE`
  - `INITIATOR_NAME_FILE`
  - `PID_FILE`
  - DB lock files under `LOCK_DIR`
- Connection-aware logging macros: `conn_info`, `conn_warn`, `conn_error`, `conn_debug`.
- Recovery-stage enum `iscsi_session_r_stage_e`.
- Login result enums:
  - `conn_login_status_e`
  - `enum iscsi_login_status`
- Actor/event enum `iscsi_event_e`.
- `iscsi_login_context_t`, holding login PDU state, buffers, auth client, response status, timeout, and queue task.
- `iscsi_conn_t`, the daemon-side connection record:
  - ids and session pointer
  - login and receive contexts
  - logout queue task
  - receive/data buffer
  - connection state
  - timers
  - event context pool
  - login stage/status
  - socket or transport endpoint handle
  - TCP settings
  - login/logout/auth/noop timeouts
  - statsn and negotiated digest/data segment values
- `struct iscsi_ev_context`, actor plus connection/event payload.
- `queue_task_t`, management IPC request/response plus optional payload.
- `iscsi_session_t`, the daemon-side session record:
  - transport, session id, host number, iface/netdev
  - original node record
  - negotiated iSCSI parameters
  - target/initiator identifiers
  - CHAP/auth buffers
  - connection array
  - recovery/reopen state
  - error-handling timeouts
  - notification task pointer
- Login/session constants, digest constants, and irrelevant-key bit flags.
- Prototypes for login code, kernel transport endpoint helpers, TCP I/O helpers, session tasks, discovery, common setup, and session lookup.

Important dependencies:
- Includes protocol, kernel ABI, auth, management IPC, actor, list, config, and logging headers.
- Provides the common struct definitions consumed by `initiator.c`, `initiator_common.c`, and `io.c`.

Filesystem/storage relevance:
- These structures are the in-memory model of iSCSI sessions and connections. They bridge user-space configuration to kernel transport/session state and ultimately to visible SCSI/block devices.

Notable details:
- Connection data buffer is sized with `ISCSI_DEF_MAX_RECV_SEG_LEN`.
- Only `ISCSI_CONN_MAX` connections are embedded per session.
- `CONTEXT_POOL_MAX` is fixed at 32 per connection.
- The header documents that some transports have kernel-managed endpoints, while TCP uses a socket fd cast/stored through the transport endpoint handle path.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/initiator.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/initiator_common.c -->
# File Research: sources/virtualization/open-iscsi/usr/initiator_common.c

This file contains setup logic shared by normal and discovery sessions: session lookup, authentication setup, negotiated parameter validation/copying, portal resolution, host/session/kernel parameter publication, and iface network setup.

Major responsibilities:
- `session_find_by_sid()` searches all transports and sessions for a given SID.
- `iscsi_setup_authentication()` copies CHAP credentials and configures one-way or bidirectional auth buffers.
- `iscsi_copy_operational_params()` validates and copies negotiated session/connection parameters from config into runtime session/connection state.
- `iscsi_setup_portal()` resolves target address/port into `sockaddr_storage`, stores failback address, and records numeric host string.
- `iscsi_host_set_params()` publishes netdev and hardware address host parameters through `ipc->set_host_param`.
- `iscsi_session_init_params()` builds a parameter mask based on transport capabilities, clearing unsupported MaxR2T, digest, and marker parameters.
- `iscsi_session_set_neg_params()` publishes negotiated full-feature iSCSI parameters through `ipc->set_param`.
- `iscsi_session_set_params()` publishes target/session/recovery/auth/NOP/iface/boot/discovery parameters through `ipc->set_param`.
- `iscsi_set_net_config()` invokes transport-specific network configuration setup, deriving host number and netdev when needed.
- `iscsi_host_set_net_params()` enforces/offers iface IP setup, brings up netdevs, applies transport net config, and publishes IP/netdev/hwaddress host parameters.

Important validation behavior:
- Data segment and burst lengths are aligned down to 32-bit boundaries and clamped to allowed min/max values.
- FirstBurstLength is forced to be no larger than MaxBurstLength.
- Discovery sessions cap receive segment length for text negotiation and disable header/data digests.
- NOP timeout parameters are skipped if sysfs says the session does not support kernel NOP handling.
- CHAP with `authmethod=None` is currently warned as deprecated but still allowed if passwords are configured.

Important dependencies:
- Uses transport capability flags and transport templates.
- Uses global `ipc`.
- Uses sysfs for session NOP support, host lookup, and host info.
- Uses iface and net helpers for binding and netdev setup.

Filesystem/storage relevance:
- This file establishes kernel-visible session parameters for remote storage connections. Incorrect parameter publication can affect login success, error recovery, queueing, and discovery of block devices.

Notable constraints:
- Return codes mix POSIX-style values and open-iscsi error codes depending on caller path.
- Unsupported kernel operations returning `-ENOSYS` are often tolerated for compatibility.
- Some TODOs remain around older kernel handling and initiator-name host fallback.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/initiator_common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/io.c -->
# File Research: sources/virtualization/open-iscsi/usr/io.c

This file implements low-level iSCSI connection I/O for TCP sockets and IPC-backed kernel I/O. It handles socket creation, binding, TCP options, connect/poll/disconnect, PDU send, and PDU receive.

Major responsibilities:
- Uses `SIGALRM` and a file-static `timedout` flag to bound blocking socket operations.
- Validates that an iface-bound netdev has an address of the expected family before binding.
- Binds software TCP sessions to a netdev using `SO_BINDTODEVICE` when the iface is bound by hardware address or netdev.
- Creates TCP sockets, sets `TCP_NODELAY`, optional receive/send window sizes, and optional TCP congestion control.
- Supports nonblocking connect and subsequent poll-based completion.
- Disconnects TCP sockets and uses abortive close with `SO_LINGER` when not in clean logout.
- Sends iSCSI PDUs by writing header/AHS and data plus 4-byte alignment padding through `writev()` or `ipc->writev()`.
- Receives iSCSI PDUs by reading fixed header, rejecting unsupported additional header segments, validating data length against caller buffer, reading data and padding, and logging login/text content.
- Wraps IPC PDU transactions with `send_pdu_begin/end` and `recv_pdu_begin/end`.

Important dependencies:
- Uses iface binding helpers from `iface.c`.
- Uses net helper `net_get_netdev_from_hwaddress()`.
- Uses global `ipc` and transport/session runtime state from `initiator.h`.
- Uses iSCSI protocol macros for opcodes, padding, and 24-bit data length conversion.

Filesystem/storage relevance:
- This is the userspace data/control PDU path for software iSCSI login, discovery, logout, NOP, text, and async handling. It does not carry SCSI read/write data once the kernel session is active, but it is essential for establishing and maintaining block-storage sessions.

Notable constraints and risks:
- Header and data digest arguments are currently unused in these routines.
- Additional header segments are not supported on receive.
- The static `timedout` flag and process-wide `SIGALRM` approach are simple but fragile in a multi-operation/evented daemon.
- `iscsi_io_tcp_connect()` returns `-1` on bind failure without closing the just-created socket in that branch.
- PDU receive returns `-EIO` for timeout/failure and otherwise returns bytes read excluding padding.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/io.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_err.c -->
# File Research: sources/virtualization/open-iscsi/usr/iscsi_err.c

This small file defines open-iscsi's global error variable and maps open-iscsi error codes to human-readable messages.

Key contents:
- Global `enum iscsi_error_list iscsi_err`.
- Static `iscsi_err_msgs[]` table indexed by numeric error value.
- `iscsi_err_to_str(int err)` returns the message string or logs and returns NULL for invalid codes.
- `iscsi_err_print_msg(int err)` logs a formatted initiator error message or logs invalid-code input.

Important dependencies:
- Includes `iscsi_err.h` for error enum/max value.
- Includes `log.h` for `log_error()`.

Filesystem/storage relevance:
- Provides user/admin-facing diagnostics for iSCSI session, discovery, IPC, sysfs, auth, and target connection failures.

Notable constraints:
- The table must stay aligned with `enum iscsi_error_list` and `ISCSI_MAX_ERR_VAL`.
- Invalid errors are logged rather than mapped to a fallback string.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_err.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_ipc.h -->
# File Research: sources/virtualization/open-iscsi/usr/iscsi_ipc.h

This header defines the user/kernel IPC abstraction used by open-iscsi transports. It is the common interface for netlink/ioctl/control-device implementations to create sessions, manage connections, set parameters, send/receive PDUs, configure networking, and handle firmware/offload features.

Key contents:
- Value type enum: `ISCSI_INT`, `ISCSI_UINT`, `ISCSI_STRING`.
- `struct iscsi_ipc_ev_clbk`, callbacks from IPC layer into initiator/event code:
  - async session create/destroy notifications
  - event context allocation/release
  - event context scheduling
- `ipc_register_ev_callback()` declaration.
- IPC auth modes:
  - UID-only root check
  - legacy UID plus user database matching
- `struct iscsi_ipc`, a function-pointer table for:
  - control device open/close/handle/read/writev
  - SendTargets offload
  - session create/destroy/unbind
  - connection create/destroy/bind/start/stop/state
  - session/host parameter set/get
  - statistics retrieval
  - PDU send/receive transactions
  - net config
  - ping
  - CHAP get/set/delete
  - flashnode create/delete/login/logout/parameter setup
  - host stats

Important dependencies:
- Includes `iscsi_if.h`, the kernel ABI definitions.
- Uses `struct iovec`, `struct sockaddr`, and iSCSI param enums.

Filesystem/storage relevance:
- This is the ABI abstraction through which userspace creates kernel iSCSI sessions that expose remote SCSI LUNs as local block devices. It also carries offload/firmware management operations.

Notable constraints:
- The interface permits POSIX-style errors with `errno` set.
- Some operations are explicitly not implemented yet, such as `get_param`.
- Implementations must handle compatibility across kernels with differing operation support.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_net_util.c -->
# File Research: sources/virtualization/open-iscsi/usr/iscsi_net_util.c

This file provides network utility functions used by iSCSI iface and boot/offload setup. It maps NIC drivers to iSCSI transports, resolves MAC-to-netdev binding, identifies VLAN devices, validates IP versions, brings interfaces up, assigns firmware boot addresses, and installs host routes to target portals.

Major responsibilities:
- Maintains a driver-to-iSCSI-transport table:
  - `cxgb3` to `cxgb3i`
  - `cxgb4` to `cxgb4i`
  - `bnx2`/`bnx2x` to `bnx2i`
- `net_get_transport_name_from_netdev()` uses `ETHTOOL_GDRVINFO` to find the NIC driver and maps it to an iSCSI offload transport. For bnx2/bnx2x, it requires the `iscsiuio` executable to exist.
- `net_get_netdev_from_hwaddress()` iterates interfaces, reads Ethernet hardware addresses with `SIOCGIFHWADDR`, and returns the first matching netdev.
- `find_vlan_dev()` scans interfaces and returns a VLAN device name matching a requested VLAN ID.
- `net_get_ip_version()` uses numeric `getaddrinfo()` to classify an IP string as IPv4 or IPv6.
- `net_setup_netdev_ipv4()` brings up physical/VLAN interfaces, sets IPv4 address and netmask when needed, and adds a host route to the target, using a gateway when target and local address are on different subnets.
- `net_setup_netdev_ipv6()` brings up physical/VLAN interfaces, sets IPv6 address/prefix when needed, and adds a host route through the gateway.
- `net_ifup_netdev()` brings an existing netdev up if not already up.

Important dependencies:
- Uses ioctl APIs: `SIOCETHTOOL`, `SIOCGIFHWADDR`, `SIOCGIFVLAN`, `SIOCSIFFLAGS`, `SIOCSIFADDR`, `SIOCSIFNETMASK`, and `SIOCADDRT`.
- Uses Linux networking headers for VLAN, Ethernet, IPv6 route, and socket ioctls.
- Uses `ethtool-copy.h`, `iscsi_net_util.h`, `sysdeps.h`, and logging helpers.

Filesystem/storage relevance:
- This is support code for firmware boot and offload iSCSI paths, ensuring the correct NIC/VLAN/address/route exists before login to remote storage.

Notable constraints and risks:
- VLAN handling only finds an existing VLAN device; it does not create one.
- MAC-to-netdev matching does not support bonds/aliases with duplicate hardware addresses.
- `find_vlan_dev()` appears to issue an initial `SIOCGIFHWADDR` without first assigning an interface name to `if_hwaddr`, so that path deserves careful verification.
- IPv6 setup requires a gateway string and always builds a gateway route.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_net_util.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_netlink.h -->
# File Research: sources/virtualization/open-iscsi/usr/iscsi_netlink.h

This header defines small netlink attribute helpers for open-iscsi.

Key contents:
- Includes Linux netlink definitions.
- Defines alignment/data/length macros:
  - `ISCSI_NLA_HDRLEN`
  - `ISCSI_NLA_DATA(nla)`
  - `ISCSI_NLA_LEN(len)`
  - `ISCSI_NLA_TOTAL_LEN(len)`
- Declares `iscsi_nla_alloc(uint16_t type, uint16_t len)`.

Important dependencies:
- Uses `struct nlattr` and `NLA_ALIGN()` from `<linux/netlink.h>`.
- Forward-declares `struct iovec`.

Filesystem/storage relevance:
- Supports construction of netlink payloads used to configure iSCSI kernel/session/iface parameters, particularly in `iface.c`.

Notable constraints:
- This header only declares allocation and macros; ownership/freeing behavior is determined by callers and the implementation of `iscsi_nla_alloc()`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_settings.h -->
# File Research: sources/virtualization/open-iscsi/usr/iscsi_settings.h

This header defines default initiator settings used by open-iscsi runtime and database setup.

Key defaults:
- Login/logout/noop/replacement timeouts.
- Error-handling timeouts for abort, LU reset, target reset, and host reset.
- Session reopen retry/logging defaults.
- Queue limits: `CMDS_MAX` and `QUEUE_DEPTH`.
- Xmit thread priority default.
- Default iface values:
  - iface name
  - netdev
  - IP address
  - hardware address
  - transport
  - unknown value marker
- Unknown portal group tag sentinel.
- TCP window size.
- Default iSCSI port `3260`.
- Initiator burst/data segment lengths.
- Initial login retry max.
- Initial autoscan enabled flag.

Important dependencies:
- None included directly; it is a pure constants header.

Filesystem/storage relevance:
- These defaults shape login behavior, error recovery, queue depth, TCP behavior, and target scanning for remote block storage sessions.

Notable constraints:
- The file notes that these defaults may differ from RFC values; protocol constants live elsewhere.
- Defaults are consumed across IDBM setup, iface setup, connection initialization, and session recovery.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/iscsi_settings.h -->