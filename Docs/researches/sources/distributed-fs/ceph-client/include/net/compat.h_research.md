# sources/distributed-fs/ceph-client/include/net/compat.h

Read `sources/distributed-fs/ceph-client/include/net/compat.h` completely for this pass (95 lines, 2535 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/compat.h_research.md`.

Purpose: declares 32-bit compatibility network ABI structures and conversion helpers used when a compat userspace process invokes socket, message, routing, or multicast APIs on a wider kernel.

Important APIs/types/functions: ABI structures include `struct compat_msghdr`, `struct compat_mmsghdr`, `struct compat_cmsghdr`, `struct compat_rtentry`, `struct compat_group_req`, `struct compat_group_source_req`, and `struct compat_group_filter`. Conversion/helper prototypes include `__get_compat_msghdr()`, `get_compat_msghdr()`, `put_cmsg_compat()`, and `cmsghdr_from_user_compat_to_kern()`.

Control flow: compat syscall paths copy user-provided 32-bit message headers and control messages into native kernel `msghdr`/iov structures, then native socket send/receive code proceeds. On receive, ancillary data can be emitted in compat `cmsghdr` form. Routing and multicast option handlers use packed compat structures so user ABI alignment matches 32-bit layout.

State and persistence: no persistent state is stored. The structures describe transient syscall buffers and conversion outputs. Pointers are represented as `compat_uptr_t` and must be translated through compat user access code.

Dependencies and integration points: depends on `linux/compat.h`, `struct sock`, `struct msghdr`, sockaddr storage, multicast group APIs, route ioctls, and ancillary data handling.

Risks: structure packing/alignment is ABI-critical. `compat_group_filter` uses a union to support historical one-element and flexible-array layouts. Incorrect pointer conversion or control-message length validation can cause user memory faults, truncation, or information leaks. Route metric comment notes binary compatibility quirks.

Test signals: 32-bit userspace socket sendmsg/recvmsg/recvmmsg tests on a 64-bit kernel, ancillary data round trips, malformed controllen/iovlen faults, route ioctl compatibility, multicast group source/filter option tests, and ABI layout checks against 32-bit headers.
