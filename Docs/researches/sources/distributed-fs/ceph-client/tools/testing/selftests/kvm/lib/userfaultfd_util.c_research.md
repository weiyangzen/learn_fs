<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/userfaultfd_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/userfaultfd_util.c

## Purpose
`userfaultfd_util.c` provides demand-paging infrastructure for KVM memory tests. It registers a host virtual range with userfaultfd, starts reader threads, dispatches page-fault events to a caller-provided handler, and tears the setup down cleanly.

## Important APIs, Types, and Functions
When `__NR_userfaultfd` is available, the file defines `uffd_setup_demand_paging()` and `uffd_stop_demand_paging()`. The worker `uffd_handler_thread_fn()` monitors both the userfaultfd and a stop pipe through epoll. It consumes `struct uffd_msg` records and invokes an `uffd_handler_t` with the mode, fd, and message.

## Control Flow
Setup allocates an `uffd_desc`, creates a nonblocking userfaultfd, negotiates `UFFD_API`, registers the range in missing or minor mode, verifies required ioctls (`UFFDIO_COPY` or `UFFDIO_CONTINUE`), creates one pipe per reader, and launches reader threads. Each reader waits for userfaultfd events or a pipe wakeup, optionally delays, handles page faults, counts handled pages, and exits when signaled. Stop writes to every pipe, joins readers, closes fds, and frees arrays.

## State and Persistence
State lives in `struct uffd_desc`, reader thread ids, pipe fds, and per-reader arguments. No state is persisted after `uffd_stop_demand_paging()`, but registered userfaultfd ranges affect live VM memory behavior while active.

## Dependencies and Integration Points
The file depends on Linux userfaultfd ioctls, epoll, pthreads, `kvm_util.h`, `test_util.h`, `memstress.h`, and `userfaultfd_util.h`. It integrates with demand paging and memory stress tests that resolve faults by copying or continuing pages.

## Risks and Test Signals
Risks include missing kernel userfaultfd support, unsupported minor/missing mode ioctls, lost wakeups, handler failures, incorrect nonblocking `EAGAIN` handling, and resource leaks on teardown. Test signals include `TEST_ASSERT()` checks around fd creation, registration, epoll events, handler return values, and debug output reporting handled page counts and rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/userfaultfd_util.c -->
