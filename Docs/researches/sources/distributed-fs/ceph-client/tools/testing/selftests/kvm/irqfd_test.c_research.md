# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/irqfd_test.c

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/irqfd_test.c

Purpose: executable KVM selftest for IRQFD assignment semantics and races. It verifies that KVM rejects assigning one eventfd to multiple GSIs/VMs while allowing deassign operations for valid fds, then stress-tests assignment/deassignment while another thread races close/recreate.

Important APIs/types/functions: globals `vm1`, `vm2`, `__eventfd`, `done`; constants `GSI_BASE_PRIMARY` and `GSI_BASE_SECONDARY`; `juggle_eventfd_secondary`, `secondary_irqfd_juggler`, `juggle_eventfd_primary`, and `main`.

Control flow and state: `main` requires a default irqchip, creates two full VMs with one unused vCPU each, assigns an eventfd to one GSI, asserts duplicate assignment returns `EBUSY`, deassigns valid fds, then starts a secondary thread. The primary loop creates 10,000 eventfds, attempts conflicting assignments on both VMs, deassigns, and closes the fd. The secondary thread repeatedly attempts assign/deassign on the current fd and accepts `EBUSY` or `EBADF` because the primary may close/recreate concurrently.

Dependencies and integration: depends on pthreads, eventfd helpers, IRQFD wrappers, VM creation, default irqchip support, and `READ_ONCE`/`WRITE_ONCE` style concurrency macros from included utility headers.

Risks: intentionally racy close/recreate behavior can expose timing-dependent failures. The test assumes KVM's asymmetric IRQFD ABI: assignment requires unique eventfd, deassignment keys on eventfd plus GSI and may succeed for never-assigned GSIs if fd is valid.

Test signals: pass means duplicate IRQFD assignment returns `EBUSY`, deassignment remains permissive for valid fds, and concurrent close/reassign does not crash or corrupt KVM state. Failures include unexpected success, wrong errno, or thread-race assertion failure.
