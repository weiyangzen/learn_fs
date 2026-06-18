<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/route.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/route.h

Purpose: preserves the legacy IPv4 route ioctl ABI used by `SIOCADDRT` and `SIOCDELRT`, predating rtnetlink.

Important APIs, types, and functions: `struct rtentry` carries destination, gateway, netmask, flags, metric, optional device pointer, MTU/MSS, window, and initial RTT. Route flags include `RTF_UP`, `RTF_GATEWAY`, `RTF_HOST`, `RTF_DYNAMIC`, `RTF_MODIFIED`, `RTF_MTU`, `RTF_WINDOW`, `RTF_IRTT`, and `RTF_REJECT`; `rt_mss` aliases `rt_mtu` for userspace compatibility.

Control flow: legacy route tools fill `struct rtentry` and issue socket ioctls. The kernel copies the structure, resolves the optional device name from `rt_dev`, decodes flags and socket addresses, then adds or deletes an IPv4 route through compatibility glue.

State and persistence behavior: the header stores no state. Routes created through this ABI become kernel FIB state like routes created through rtnetlink, but the ioctl representation is a lossy legacy interface.

Dependencies and integration points: includes `linux/if.h` for `struct sockaddr` use and `linux/compiler.h` for `__user`. It integrates with IPv4 route ioctl handling and old net-tools-style programs.

Risks and edge cases: pointer-sized fields make the ABI architecture-sensitive. `rt_metric` has historical “+1” semantics, `rt_dev` is a userspace pointer, and flags overlap conceptually with newer rtnetlink route attributes. IPv6 uses route flag values above 64k, so flag expansion must avoid collisions.

Test signals: exercise add/delete of host, network, gateway, reject, MTU, window, and IRTT routes through ioctl on 32- and 64-bit builds; compare resulting FIB entries to rtnetlink dumps; validate bad `rt_dev` pointers and malformed sockaddr families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/route.h -->
