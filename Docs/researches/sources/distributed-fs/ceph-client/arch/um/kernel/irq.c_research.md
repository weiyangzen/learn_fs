# sources/distributed-fs/ceph-client/arch/um/kernel/irq.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/irq.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/irq.c

### Purpose
This file is UMLs fd/signal-backed interrupt controller. It maps host epoll/SIGIO readiness to Linux IRQs, supports read/write events, dynamic IRQ allocation, suspend/resume wake state, and optional time-travel IRQ delivery.

### Important APIs, Types, And Functions
Important types are `irq_reg` and `irq_entry`. Key APIs are `um_request_irq()`, `um_request_irq_tt()`, `um_free_irq()`, `free_irq_by_fd()`, `deactivate_fd()`, `deactivate_all_fds()`, `do_IRQ()`, `init_IRQ()`, SIGIO/SIGCHLD handlers, PM helpers, and arch interrupt display.

### Control Flow
Registration makes fds async, creates or updates an epoll entry under `irq_lock`, stores read/write event registrations, optionally attaches time-travel handlers, and calls `request_irq()`. SIGIO processing polls triggered entries, invokes time-travel handlers or `do_IRQ()`, coalesces reentry through active/pending flags, and frees deferred IRQs.

### State, Persistence, And Dependencies
State includes the active fd list, allocated IRQ bitmap, per-fd registrations, suspended/wakeup flags, pending time-travel events, and per-CPU IRQ stats. Dependencies include host epoll wrappers, SIGIO management, Linux IRQ core, time-travel APIs, and UML signal register handling.

### Integration Points And Risks
Risks include lockless epoll assumptions, fd reuse races, dynamic IRQ range interactions with MSI, pending-event handling during suspend, and cleanup ordering when handlers unregister themselves. Integration is used by xterm, virtio, VFIO, network, and other fd-backed drivers.

### Test Signals
Test read/write fd IRQs, duplicate registrations, handler reentry, dynamic IRQ exhaustion, free-by-fd, suspend/resume wake, external time-travel handlers, SIGCHLD, and `/proc/interrupts` counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/irq.c -->
