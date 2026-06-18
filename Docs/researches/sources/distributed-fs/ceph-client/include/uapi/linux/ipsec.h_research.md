# sources/distributed-fs/ceph-client/include/uapi/linux/ipsec.h

## Purpose
`ipsec.h` exports common IPsec/XFRM selector constants, direction identifiers, policy modes, and limits.

## Important APIs, Types, and Functions
It defines wildcard values `IPSEC_PORT_ANY`, `IPSEC_ULPROTO_ANY`, and `IPSEC_PROTO_ANY`. Enums identify security protocol IDs, policy directions, policy types/actions, and policy modes. `IPSEC_MANUAL_REQID_MAX` limits manual request IDs, and `IPSEC_REPLAYWSIZE` defines a default replay window size.

## Control Flow
Userspace policy managers use these values when configuring xfrm state/policies via PF_KEY or netlink. The kernel then applies policy lookup and transform processing during packet input/output/forwarding.

## State and Persistence
No local state exists. Policies and SAs persist in the kernel xfrm database until deleted, expired, or namespace teardown.

## Dependencies and Integration Points
The header includes `<linux/pfkeyv2.h>`. It integrates with PF_KEY, xfrm netlink, IPsec policy engines, and packet transform paths.

## Risks and Test Signals
Tests should validate wildcard selector behavior, direction/action/mode mapping, manual reqid limits, replay-window defaults, and compatibility with PF_KEY constants. Misnumbered enum values would break userspace policy tools.
