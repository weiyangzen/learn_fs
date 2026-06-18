# sources/distributed-fs/ceph-client/include/net/netlink.h

Purpose: Provides the core in-kernel netlink message and attribute construction, parsing, validation, iteration, typed access, nesting, multicast/unicast, and policy-dump interfaces.

Important APIs/types/functions: It defines `nla_policy`, range validation structs, `nl_info`, validation modes, and many policy macros (`NLA_POLICY_*`). Message helpers cover size/alignment, data/payload/attr access, `nlmsg_ok/next`, strict/deprecated parsing and validation, find/report/seq, construction (`nlmsg_put`, `nlmsg_append`, `nlmsg_new`, `nlmsg_new_large`, `nlmsg_end/cancel/free/consume`), multicast/unicast, dump consistency, and message iteration. Attribute helpers cover size/alignment, `nla_type/data/len/ok/next`, strict/deprecated nested parsing/validation, typed put/get for integer/endian/string/flag/msecs/IP/bitfield attributes, memdup, nesting start/end/cancel, 64-bit alignment, iteration macros, range extraction, and policy dumping.

Control flow: Kernel families build replies by allocating skbs, placing netlink headers, appending attributes, ending or canceling on error, and sending unicast/multicast. Receive paths validate messages with a selected strictness level, parse attributes into type-indexed arrays, and use typed getters. Dump paths track sequence consistency and can expose policies to userspace.

State and persistence: Mostly stateless inline helpers; mutable state is in skbs, netlink callbacks, extack reporting, and optional policy dump state allocated by implementation functions.

Dependencies/integration: Used by rtnetlink, generic netlink, nfnetlink/nftables, NetLabel, XFRM, and many networking subsystems. Depends on skbuff, netlink sockets, jiffies, extended ACK, alignment rules, and uapi netlink flags.

Risks/test signals: High-risk areas are strict vs deprecated validation compatibility, `strict_start_type`, nested `NLA_F_NESTED` enforcement, 64-bit alignment padding, U16 nested length overflow, variable-sized signed/unsigned attributes, and malformed/trailing data. Test attribute fuzzing, policy round trips, old userspace compatibility, extack messages, dump interruption flagging, multicast error normalization, and architectures without efficient unaligned access.
