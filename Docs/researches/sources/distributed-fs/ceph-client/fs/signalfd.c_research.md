<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/signalfd.c -->
## sources/distributed-fs/ceph-client/fs/signalfd.c

Purpose: implements `signalfd(2)` and `signalfd4(2)`, exposing pending signals selected by a mask as fixed-size `struct signalfd_siginfo` records readable from an anonymous inode file descriptor.

Important APIs and types: `struct signalfd_ctx` stores the inverted internal signal mask. Key functions are `do_signalfd4()`, `signalfd_read_iter()`, `signalfd_dequeue()`, `signalfd_poll()`, `signalfd_copyinfo()`, `signalfd_cleanup()`, and compat syscall wrappers.

Control flow: user syscalls copy a `sigset_t`, reject unexpected mask sizes or flags, remove uncatchable `SIGKILL`/`SIGSTOP`, invert the mask for kernel signal helpers, and either create a new anon inode or update an existing signalfd. Reads require at least one full `signalfd_siginfo`, repeatedly dequeue matching signals, translate `kernel_siginfo_t` by layout class, and copy records to the iterator. Blocking reads attach a wait entry to `current->sighand->signalfd_wqh` while holding `siglock` around dequeue checks.

State and persistence: per-fd state is only the signal mask in `signalfd_ctx`; pending signal queues remain task and thread-group state. Polling waits on the current task's `sighand` waitqueue rather than a persistent object-specific queue. `/proc` fdinfo renders the user-visible mask.

Dependencies and integration: uses anonymous inode files, signal dequeue/layout helpers, task sighand locking, wait queues, `iov_iter`, proc fdinfo, compat sigset conversion, and `O_CLOEXEC`/`O_NONBLOCK` flag ABI equivalence.

Risks: signalfd is tied to the current task at read/poll time, so behavior around shared file descriptors and task signal handlers is subtle. Mask inversion must stay consistent with signal core expectations. Copying siginfo requires updating when `siginfo_t` layouts evolve; the fixed 128-byte ABI is enforced by `BUILD_BUG_ON`.

Test signals: create and update signalfds, verify invalid flags and sizes, block vs nonblock reads, multiple records per read, signal mask exclusion of SIGKILL/SIGSTOP, `poll()` readiness, shared pending versus thread pending delivery, compat syscalls, fdinfo `sigmask`, and signal interruption returning restartable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/signalfd.c -->
