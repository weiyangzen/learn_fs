# sources/distributed-fs/ceph-client/include/linux/seg6.h

Purpose: `seg6.h` is a kernel wrapper for Segment Routing over IPv6 UAPI definitions.

Important APIs/types/functions: It includes `<uapi/linux/seg6.h>` and declares no additional kernel-only types or helpers in this snapshot.

Control flow: There is no executable control flow. Kernel code includes this wrapper to use shared SRv6 constants and structures.

State and persistence behavior: No state is owned by the header. SRv6 route, policy, and tunnel state live in networking subsystems that consume the UAPI definitions.

Dependencies and integration points: It integrates with IPv6 routing, lightweight tunnels, netlink configuration, and SRv6 headers.

Risks: The wrapper must stay aligned with UAPI definitions; adding kernel-only helpers here should avoid ABI confusion.

Test signals: Build users of SRv6 UAPI constants, route installation, packet encapsulation/decapsulation, and netlink dumps using the included definitions.
