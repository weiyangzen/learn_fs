# sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.c

## Purpose

`mshv_eventfd.c` implements KVM-style `irqfd` and `ioeventfd` support for MSHV partitions. It lets userspace signal an eventfd to inject a guest interrupt and lets guest MMIO doorbells signal userspace eventfds.

## Important APIs, Types, and Functions

- IRQ ack notifier APIs register/unregister callbacks and notify matching GSIs.
- `mshv_set_unset_irqfd()` assigns or deassigns an eventfd/GSI binding.
- `mshv_irqfd_wakeup()` drains eventfd counters, updates routing, and asserts interrupts through a fast root-scheduler vector path or `hv_call_assert_virtual_interrupt()`.
- Resampler support groups irqfds by GSI and signals resample eventfds on EOI/ack.
- `mshv_set_unset_ioeventfd()` assigns/deassigns MMIO doorbell eventfds using `mshv_register_doorbell()`.
- `mshv_eventfd_init()` initializes partition lists/locks, and `mshv_eventfd_release()` tears down ioeventfds and irqfds.

## Control Flow

Assigning an irqfd resolves the eventfd, optionally resolves a resamplefd, joins or creates a resampler, installs a priority wait-queue callback through poll, checks duplicate eventfd use, snapshots routing under SRCU, links the irqfd, and handles already-pending events. On wakeup, EPOLLIN reads the counter and injects an interrupt; EPOLLHUP deactivates the binding and queues cleanup work. Deassign unlinks matching bindings and flushes the cleanup workqueue before returning.

Assigning an ioeventfd validates MMIO-only flags, length and overflow, checks collisions under the partition mutex, registers a Hyper-V doorbell port for address/value matching, and links the object into an RCU list. Doorbell ISR callbacks find the matching doorbell ID and signal the eventfd.

## State and Persistence Behavior

Per-partition hlist state stores active irqfds, resamplers, ack notifiers, and ioeventfds. `seqcount_spinlock_t` protects routing snapshots in irqfds. Cleanup is deferred through `irqfd_cleanup_wq`, but deassign/release flushes it to prevent late interrupts after teardown.

## Dependencies and Integration Points

The file depends on eventfd, poll, wait queues, workqueues, SRCU/RCU, APIC definitions on x86, MSHV IRQ routing, and SynIC doorbell APIs. It integrates with partition ioctls, `mshv_irq.c` routing updates, `mshv_synic.c` EOI and doorbell handling, and Hyper-V interrupt hypercalls.

## Risks and Edge Cases

Fast injection only supports x86_64 root scheduler, direct APIC destination mode, available VP register pages, and spare vector slots. A validation bug risk exists in `mshv_irqfd_assign()`: it checks resample/level-triggered before `mshv_irqfd_update()` fills `irqfd_lapic_irq`, so the level-triggered test may see zeroed routing data. Resampler shutdown must synchronize with SRCU readers. Duplicate detection forbids the same eventfd for another IRQ but not all possible semantic collisions. `ioeventfd_check_collision()` is annotated with `pt->mutex`, but the actual field is `pt_mutex`.

## Test Signals

Cover irqfd assign/deassign, duplicate fd rejection, pending event delivery after assign, EPOLLHUP cleanup, routing-table updates, resample signaling after EOI, fast-path fallback, ioeventfd collision rules, wildcard/datamatch behavior, doorbell unregister on release, and lockdep/RCU/SRCU teardown under concurrent signals.
