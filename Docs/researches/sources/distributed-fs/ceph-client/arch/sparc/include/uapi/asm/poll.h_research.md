<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/poll.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/poll.h

Purpose: SPARC poll event constants layered on generic poll definitions.

Important APIs and control flow: defines SPARC values/aliases for `POLLWRNORM`, `POLLWRBAND`, `POLLMSG`, `POLLREMOVE`, and `POLLRDHUP`, then includes `asm-generic/poll.h`.

State, dependencies, and risks: state is event masks exchanged by poll/select/epoll paths. Dependencies include generic poll constants. Risks are ABI changes breaking userspace event decoding. Test signals are poll/epoll tests for write band, hangup, and removal events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/poll.h -->
