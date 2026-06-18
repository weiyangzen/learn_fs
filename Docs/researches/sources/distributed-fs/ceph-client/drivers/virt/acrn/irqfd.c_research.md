# sources/distributed-fs/ceph-client/drivers/virt/acrn/irqfd.c

## Purpose
Provides ACRN irqfd support: userspace attaches an eventfd to a VM and each eventfd signal injects an MSI into the User VM.

## APIs, Types, and Functions
The core type is `struct hsm_irqfd`, carrying the VM, eventfd context, waitqueue entry, poll table, shutdown work, list node, and `struct acrn_msi_entry`. Public entry points are `acrn_irqfd_init()`, `acrn_irqfd_config()`, and `acrn_irqfd_deinit()`. Internal helpers are `acrn_irqfd_assign()`, `acrn_irqfd_deassign()`, `hsm_irqfd_wakeup()`, `hsm_irqfd_poll_func()`, `hsm_irqfd_shutdown()`, `hsm_irqfd_shutdown_work()`, and `acrn_irqfd_inject()`.

## Control Flow and State
VM creation initializes `vm->irqfds`, `vm->irqfds_lock`, and a per-VM irqfd workqueue. Assignment resolves the supplied fd, obtains an eventfd context, installs a custom waitqueue callback through `vfs_poll()`, rejects duplicate eventfd contexts, and injects immediately if the eventfd was already readable. On wakeup, `POLLIN` calls `acrn_msi_inject()` and `POLLHUP` schedules shutdown work. Deassignment looks up by eventfd and removes the waitqueue entry under `irqfds_lock`.

## Dependencies and Integration
The module depends on Linux `eventfd`, `poll`, `file` fd wrappers, VM-local mutexes/workqueue state, and the ACRN MSI injection helper implemented in `vm.c`.

## Risks and Test Signals
Important risks are eventfd lifetime races, shutdown work running after deinit, duplicate fd handling, and injection from waitqueue callback context. Notably `acrn_irqfd_deinit()` destroys `vm->irqfd_wq` before list shutdown; test coverage should check POLLHUP/deinit ordering, repeated assign/deassign, duplicate eventfd rejection, pending event injection at assignment, and invalid fd errors.
