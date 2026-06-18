# sources/distributed-fs/ceph-client/include/scsi/iscsi_if.h

Purpose: Defines the iSCSI kernel/userspace netlink ABI for session, connection, transport endpoint, discovery, host, interface, CHAP, flashnode, ping, path, and statistics operations.

Important APIs/types/functions: `enum iscsi_uevent_e` defines user-to-kernel commands and kernel-to-user events. `struct iscsi_uevent` is the aligned netlink message with input and response unions. Additional records include parameter info, interface parameter info, path updates, flashnode parameter info, stats, CHAP records, and offload host stats. Enums define target discovery, host events, parameter classes, network/interface/session/host/flashnode params, connection states, errors, discovery parents, port speed/state, and ping status. Capability and stop-connection flags describe transport behavior.

Control flow and state: Userspace sends `ISCSI_UEVENT_*` requests with object IDs, handles, lengths, and parameter identifiers; the kernel replies with return codes or events such as session create, PDU receive, connection error, path request, link-down, login state, host event, or ping completion. Variable payloads follow the fixed event for params, paths, stats, CHAP, or host events.

Dependencies and integration: Depends on `iscsi_proto.h`, IPv4/IPv6 address types, netlink multicast groups, and open-iscsi userspace. It is shared by software and offload iSCSI transports.

Risks and test signals: Risks include ABI size/alignment breakage, mismatched variable payload lengths, pointer-handle truncation, enum drift with userspace, secret exposure in CHAP records, and flashnode/offload feature incompatibilities. Tests should include netlink ABI size checks, create/bind/start/stop/destroy flows, param set/get, path update, CHAP CRUD, ping completion, stats dumps, and compatibility with existing open-iscsi tools.
