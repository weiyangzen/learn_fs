# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_events.h

This header defines the internal KFD event object, event ID constants, timeout constants, event type constants, and the interrupt-signaling entry point.

`struct kfd_event` stores event ID, `event_age`, signaled and auto-reset state, event type, spinlock, wait queue, optional user signal address, memory or hardware exception payload, and RCU head. ID constants split low signal-event IDs from upper nonsignal IDs. `UNSIGNALED_EVENT_SLOT` is the all-ones marker written to signal slots. Event type constants mirror HSA/UAPI signal, HW exception, debug, and memory event types. `kfd_signal_event_interrupt` is declared for interrupt processing.

The header carries no runtime state, but it defines the concurrency contract used by `kfd_events.c`: event state and waiter lists are protected by `ev->lock`, process lookup/creation/destruction by `p->event_mutex` or RCU, and event memory by `kfree_rcu`. The low-ID signal-slot relationship is a stable behavior relied on by userspace and interrupt handlers.

Dependencies are Linux kernel ID/list/wait primitives, `kfd_priv.h`, and `uapi/linux/kfd_ioctl.h`. Risks are ABI-visible semantic changes to event IDs, slot markers, timeout constants, event payload layout, or event-age behavior. Test build coverage, ID boundary allocation, signal-page slot initialization, partial-ID interrupt signaling, event-age waits, and memory/HW exception data copying.
