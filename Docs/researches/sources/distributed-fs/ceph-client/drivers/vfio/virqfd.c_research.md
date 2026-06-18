<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/virqfd.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/virqfd.c

## Purpose
This file implements VFIO generic virqfd support: a small eventfd polling bridge that invokes a handler and optional threaded callback when userspace signals an eventfd, and cleans itself up when the eventfd is closed.

## Important APIs, types, and functions
Exported APIs are `vfio_virqfd_init`, `vfio_virqfd_exit`, `vfio_virqfd_enable`, `vfio_virqfd_disable`, and `vfio_virqfd_flush_thread`. Important helpers include `virqfd_wakeup`, `virqfd_ptable_queue_proc`, `virqfd_shutdown`, and `virqfd_inject`. Global state is a single-thread cleanup workqueue and `virqfd_lock`.

## Control flow
Initialization creates `vfio-irqfd-cleanup`. Enabling allocates a `struct virqfd`, obtains the eventfd context from the supplied fd, installs the virqfd pointer under lock if no existing virqfd is active, registers a custom poll wait callback, and handles already-pending `EPOLLIN`. On `EPOLLIN`, it reads the eventfd counter, runs the handler, and schedules optional thread work. On `EPOLLHUP`, it clears the owner pointer under lock and queues shutdown. Disable clears the pointer, queues shutdown if active, and flushes the cleanup workqueue.

## State and persistence behavior
State is per enabled virqfd: eventfd context, wait queue entry, poll table, owner pointer, opaque/data callbacks, and work items. Cleanup removes the wait queue, flushes inject work, drops the eventfd context, and frees memory. No persistent storage exists.

## Dependencies and integration points
It depends on eventfd, file/poll APIs, workqueues, and VFIO internal `struct virqfd` from UAPI/private headers. Platform IRQ and PCI IRQ paths use it for mask/unmask or interrupt injection control.

## Risks and test signals
Risks include double shutdown races, eventfd HUP ordering, handler/thread callback lifetime, and cleanup workqueue flushing latency. Test signals include enable with invalid fd, duplicate enable returning `-EBUSY`, pending event delivery at registration, eventfd close cleanup, disable while inject work is pending, and module exit after all virqfds are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/virqfd.c -->
