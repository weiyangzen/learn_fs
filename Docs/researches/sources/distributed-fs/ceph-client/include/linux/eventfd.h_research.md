# sources/distributed-fs/ceph-client/include/linux/eventfd.h

Purpose: kernel API for eventfd counters used as lightweight notification objects.

Important APIs/types/functions: flag masks `EFD_SHARED_FCNTL_FLAGS`, `EFD_FLAGS_SET`, opaque `eventfd_ctx`, `eventfd_ctx_put()`, fd/file getters, `eventfd_signal_mask()`, `eventfd_ctx_remove_wait_queue()`, `eventfd_ctx_do_read()`, `eventfd_signal_allowed()`, and `eventfd_signal()`.

Control flow: subsystems obtain an eventfd context from fd/file, signal it with optional poll mask when an event occurs, optionally remove wait queues/read counters, and release references. Disabled config stubs return errors/no-op.

State/persistence: eventfd counter and wait queue live in `eventfd_ctx` and persist while referenced/open. No disk persistence.

Dependencies/integration: file descriptors, poll masks, wait queues, scheduler/task context constraints, KVM/aio/io_uring/user notification users.

Risks/test signals: risks are signaling from disallowed contexts, reference leaks, counter saturation semantics, missing wakeups, and config-off handling. Test fdget/fileget, signal/read behavior, semaphore mode, poll wakeups, wait queue removal, and users such as KVM irqfd.
