<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_genl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_genl.h

Purpose: defines generic-netlink command and attribute IDs for configuring SRv6 global behavior.

Important APIs, types, and functions: command enum values include `SEG6_CMD_SETHMAC`, `SEG6_CMD_DUMPHMAC`, `SEG6_CMD_SET_TUNSRC`, `SEG6_CMD_GET_TUNSRC`, and max constants. Attribute IDs include HMAC key ID, secret, algorithm, tunnel source address, and max constants.

Control flow: userspace sends generic-netlink SRv6 commands to set or dump HMAC keys and to set or query the tunnel source address. The kernel validates attributes, updates SRv6 per-netns state, and replies or dumps configured data.

State and persistence behavior: HMAC keys and tunnel source are kernel network-namespace runtime state. They are not persistent except through userspace reconfiguration.

Dependencies and integration points: integrates with SRv6 generic-netlink family, HMAC validation, tunnel encap code, and iproute2 `seg6` commands.

Risks and edge cases: secrets are sensitive netlink payloads; dumps must avoid unintended exposure according to permissions. Attribute length for IPv6 tunnel source and algorithm/key IDs must be validated.

Test signals: generic-netlink set/get/dump tests for HMAC and tunnel source, permission checks, malformed attributes, key replacement/removal, and packet HMAC validation after configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_genl.h -->
