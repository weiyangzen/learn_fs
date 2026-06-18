<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signalfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/signalfd.h

Purpose: defines the signalfd userspace ABI for receiving signals as structured records through a file descriptor.

Important APIs, types, and functions: `struct signalfd_siginfo` contains signal number, errno, code, pid/uid, fd, timer, band, overrun/trap/status/int/ptr, utime/stime, sender address, address_lsb, syscall, call address, architecture, and padding. `SFD_CLOEXEC` and `SFD_NONBLOCK` alias descriptor flags from fcntl.

Control flow: userspace blocks signals in a mask, creates or updates a signalfd, then reads one or more `signalfd_siginfo` records instead of using traditional signal handlers. Kernel signal delivery packages pending signal metadata into the fixed record format.

State and persistence behavior: signalfd file descriptors reference a signal mask and task/signal state. Pending signals remain kernel task state until consumed. The record is a transient read output.

Dependencies and integration points: depends on Linux types and fcntl flags. It integrates with signal delivery, poll/epoll, pidfd/process supervision, seccomp `SIGSYS` metadata, and timer/async I/O signals.

Risks and edge cases: padding preserves fixed record size for future expansion. Consumers must handle partial reads only in multiples of the struct size. Architecture and syscall fields are meaningful only for some signal codes.

Test signals: signalfd reads for standard and realtime signals, timer signals with overrun, SIGCHLD status, SIGSYS/seccomp fields, nonblocking and close-on-exec flags, epoll readiness, and record-size ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signalfd.h -->
