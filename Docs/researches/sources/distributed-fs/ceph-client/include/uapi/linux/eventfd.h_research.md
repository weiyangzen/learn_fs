# sources/distributed-fs/ceph-client/include/uapi/linux/eventfd.h

This small UAPI header defines flags for the `eventfd` and `eventfd2` syscalls. It is the public contract for creating a counter-backed file descriptor used for userspace/kernel notifications and lightweight wakeups.

Exports are `EFD_SEMAPHORE`, `EFD_CLOEXEC`, and `EFD_NONBLOCK`. `EFD_CLOEXEC` and `EFD_NONBLOCK` deliberately alias the generic `O_CLOEXEC` and `O_NONBLOCK` definitions from `linux/fcntl.h`, keeping file descriptor creation semantics aligned with other fd-producing syscalls.

Control flow is syscall driven: userspace calls `eventfd2(initval, flags)`, the kernel creates an anonymous fd with a 64-bit counter, writes add to the counter and wake waiters, reads either drain the counter or decrement by one in semaphore mode, and poll/epoll observe readability/writability. State is the in-kernel counter and wait queue tied to the fd; no state exists in the header and no persistent on-disk state is involved.

Dependencies are `linux/fcntl.h` and the eventfd implementation in the kernel core. Integration points include epoll, io_uring, AIO, KVM irqfds, VFIO, FPGA DFL interrupt eventfds, and many driver notification APIs.

Risks are flag-value ABI mismatches with `O_*` values, userspace assuming semaphore and counter modes behave identically, counter overflow blocking writes, and close-on-exec omissions leaking synchronization fds across exec. Test signals include eventfd syscall tests for blocking/nonblocking reads and writes, `EFD_SEMAPHORE` decrement behavior, `EFD_CLOEXEC` inheritance tests, and poll/epoll readiness checks.
