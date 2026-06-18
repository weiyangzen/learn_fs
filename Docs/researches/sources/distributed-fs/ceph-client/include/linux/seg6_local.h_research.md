# sources/distributed-fs/ceph-client/include/linux/seg6_local.h

Purpose: `seg6_local.h` wraps UAPI definitions for SRv6 local actions.

Important APIs/types/functions: It includes `<uapi/linux/seg6_local.h>` and provides no local functions or structs.

Control flow: No local flow exists. SRv6 local action implementations use the included constants to parse route attributes and execute endpoint behaviors.

State and persistence behavior: Endpoint behavior configuration lives in routing/lwtunnel state, not in this header.

Dependencies and integration points: It integrates with IPv6 routing, local SRv6 endpoint actions, netlink, and lwtunnel infrastructure.

Risks: Local action IDs and attribute semantics are UAPI. Implementation code must enforce action-specific validation and privilege checks.

Test signals: Configure each supported local action, verify packet processing, reject malformed netlink attributes, and dump routes back to userspace.
