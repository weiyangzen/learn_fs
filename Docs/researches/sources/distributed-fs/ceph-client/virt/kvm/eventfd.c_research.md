<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/eventfd.c -->
# sources/distributed-fs/ceph-client/virt/kvm/eventfd.c

## Purpose

Implements KVM eventfd integration: irqfd maps eventfd signals to guest interrupts, resamplefd handles level-triggered deassert notifications, and ioeventfd maps guest MMIO/PIO writes to eventfd signals.

## Important APIs, Types, and Functions

Source size: 1052 lines, 26272 bytes. Functions/classes: __attribute__, irqfd_inject, if, irqfd_resampler_notify, irqfd_resampler_ack, irqfd_resampler_shutdown, if, irqfd_shutdown, if, irqfd_is_active, irqfd_deactivate, __attribute__, irqfd_wakeup, if, if, irqfd_update, kvm_irqfd_register, __attribute__, plus 36 more. Includes: linux/kvm_host.h, linux/kvm.h, linux/kvm_irqfd.h, linux/workqueue.h, linux/syscalls.h, linux/wait.h, linux/poll.h, linux/file.h, linux/list.h, linux/eventfd.h, linux/kernel.h, linux/srcu.h, linux/slab.h, linux/seqlock.h, linux/irqbypass.h, trace/events/kvm.h, kvm/iodev.h.

## Control Flow and Data Flow

irqfd assignment validates architecture state, grabs eventfd contexts, optionally attaches a resampler, registers a priority waitqueue callback through `vfs_poll`, injects pending events, and supports IRQ bypass. Wakeups read eventfd counts, try in-atomic IRQ injection using current routing, and defer to work if needed. Deassign/release deactivate entries and flush cleanup. ioeventfd assignment validates flags/lengths, checks collisions, registers an IO device, and signals eventfd from its write callback.

## State and Persistence Behavior

KVM holds `irqfds.items`, `resampler_list`, `ioeventfds`, seqcount-protected routing entries, eventfd refs, waitqueue entries, work items, and per-bus ioeventfd counts. SRCU, spinlocks, mutexes, and a cleanup workqueue serialize lifetime and routing updates.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Ordering is delicate around eventfd waitqueue registration, EPOLLHUP, SRCU routing updates, resampler list removal, and IRQ bypass. ioeventfd collision matching must avoid duplicate wildcard/datamatch registrations. Cleanup must flush deferred injection before freeing objects.

## Test Signals

KVM selftests should cover irqfd assign/deassign, eventfd close while active, pending event at registration, resamplefd ack, routing updates, IRQ bypass transitions, ioeventfd MMIO/PIO/datamatch/wildcard/fast-MMIO paths, and invalid flag/length cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/eventfd.c -->
