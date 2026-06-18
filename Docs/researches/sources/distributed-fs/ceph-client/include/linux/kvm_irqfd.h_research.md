# sources/distributed-fs/ceph-client/include/linux/kvm_irqfd.h

Purpose: declares KVM's in-kernel irqfd structures used to inject guest interrupts from eventfds and to emulate level-triggered interrupt resampling.

Important APIs and types: `struct kvm_kernel_irqfd` tracks the source eventfd, wait queue entry, cached routing entry protected by `seqcount_spinlock_t`, GSI, injection/shutdown work items, optional resampler, irq-bypass consumer/producer links, target vCPU, and private bypass data. `struct kvm_kernel_irqfd_resampler` groups irqfds sharing a GSI, owns an IRQ ack notifier, and links into the VM resampler list.

Control flow: eventfd readiness wakes the irqfd wait entry, schedules or fast-paths injection through the cached route, and may use irq bypass for direct device-to-vCPU notification. For resampled level IRQs, guest acknowledgment triggers the notifier, deasserts the interrupt source shared by the GSI, and signals the userspace resamplefd.

State and persistence: all state is VM-lifetime kernel state. Resampler lists are RCU-read and update-protected by `kvm->irqfds.resampler_lock`; irqfd route updates are protected by `kvm->irqfds.lock` and seqcount readers.

Dependencies and integration points: includes `kvm_host.h` and poll/eventfd infrastructure, and integrates with KVM IRQ routing, ack notifiers, workqueues, wait queues, and optional irq-bypass acceleration.

Risks and test signals: risks include stale cached routes, resampler lifetime races, shutdown work racing with eventfd wakeups, and incorrect sharing of level IRQ source IDs. Test irqfd attach/detach, route update during injection, level resample notification, irq-bypass add/remove, and VM destruction with active eventfds.
