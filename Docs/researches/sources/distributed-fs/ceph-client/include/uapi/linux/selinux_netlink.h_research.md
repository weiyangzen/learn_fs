<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/selinux_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/selinux_netlink.h

Purpose: defines SELinux netlink notification message types and payloads for policy state changes visible to userspace.

Important APIs, types, and functions: message constants include notifications for enforcing mode, policy load, setenforce denial, policy capability changes, and status. Payload structs carry enforcing mode, policy sequence numbers, deny_unknown, capability values, and status fields.

Control flow: SELinux kernel code multicasts events when policy is loaded or enforcement/capability state changes. Userspace policy daemons or monitors subscribe to the SELinux netlink channel and decode the fixed payload for each message type.

State and persistence behavior: SELinux enforcement mode, policy sequence, deny_unknown, and policy capability state live in the SELinux security server. Netlink messages are transient notifications.

Dependencies and integration points: integrates with SELinux policy loading, libselinux status monitoring, audit/security tooling, and netlink multicast delivery.

Risks and edge cases: userspace must tolerate missed messages and query current state when needed. Message struct layout must remain stable, and unknown future message types should be ignored safely.

Test signals: policy reload notifications, enforcing/permissive transitions, capability toggles, userspace monitor decoding, and netlink subscriber behavior across dropped messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/selinux_netlink.h -->
