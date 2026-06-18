<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/poll.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/poll.h

Purpose: defines Xtensa-specific poll event aliases before including generic poll definitions. Important constants are `POLLWRNORM` as `POLLOUT`, `POLLWRBAND`, and `POLLREMOVE`.

Control flow is ABI event-bit interpretation in poll/select/epoll users. Persistent state is readiness bitmasks produced by file operations and consumed by userspace. Dependencies include `asm-generic/poll.h`. Integration points are libc poll APIs, epoll, drivers, and strace. Risks are event bit collision with generic definitions or userspace relying on architecture-specific values. Test signals include poll/epoll selftests, headers_install, and driver readiness behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/poll.h -->
