<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/poll.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/poll.h

Purpose: exposes the architecture-specific poll/select event bit definitions to userspace by including `<asm/poll.h>`.

Important APIs and types: this wrapper defines no new structures or constants itself; it forwards `POLLIN`, `POLLOUT`, `POLLERR`, `POLLHUP`, and related architecture ABI definitions.

Control flow: userspace includes this header when compiling code that calls `poll()`, `ppoll()`, or consumes poll masks from device APIs. Runtime behavior is implemented in syscall and file-operation poll paths.

State and persistence: no state is owned here. Poll state is transient wait-queue readiness in kernel file descriptors.

Dependencies and integration points: depends entirely on arch UAPI `asm/poll.h` and integrates with libc headers, syscalls, device drivers, sockets, and event loops.

Risks and test signals: risk is wrapper/architecture mismatch or duplicate libc definitions. Test architecture header export, C userspace compilation, and poll mask compatibility across supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/poll.h -->
