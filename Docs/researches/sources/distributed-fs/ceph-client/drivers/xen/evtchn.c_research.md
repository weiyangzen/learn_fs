# sources/distributed-fs/ceph-client/drivers/xen/evtchn.c

Purpose: implements the `/dev/xen/evtchn` misc device, allowing userspace to bind, receive, acknowledge, notify, restrict, and unbind Xen event channels through read/write/ioctl/poll/fasync.

Important APIs/functions: file operations are `evtchn_open`, `evtchn_release`, `evtchn_read`, `evtchn_write`, `evtchn_ioctl`, `evtchn_poll`, and `evtchn_fasync`. Internal helpers manage `struct per_user_data`, `struct user_evtchn`, red-black tree lookup, the notification ring, and late-EOI IRQ binding through `evtchn_bind_to_user` and `evtchn_unbind_from_user`.

Control flow: open allocates per-file state and a process-tagged IRQ name. IOCTL bind commands create VIRQ, interdomain, unbound, or static ports, add them to the per-file tree, resize the ring if needed, bind a late-EOI IRQ handler, and make the event channel refcounted. The interrupt handler disables the logical event until userspace acknowledges it, writes the port into the ring, wakes poll/read waiters, and sends SIGIO. Reads copy whole port entries from the ring, including wraparound. Writes re-enable listed ports by calling `xen_irq_lateeoi`. Unbind and release disable IRQs, drop handler bindings, and remove tree nodes.

State and persistence: per-open state includes bound event-channel tree, ring buffer, producer/consumer indices, overflow flag, wait queue, async queue, and optional restricted domid. Bound channels persist until explicit unbind or file release. Ring overflow is sticky until `IOCTL_EVTCHN_RESET`.

Dependencies and integration: depends on Xen event-channel hypercalls, exported event binding APIs from `events_base.c`, Linux misc devices, poll/fasync, rbtrees, wait queues, and userspace ABI structs in `<xen/evtchn.h>`.

Risks: ring overflow blocks reads with `-EFBIG` until reset; bind/unbind races are serialized by `bind_mutex` but interrupt delivery can overlap teardown via the `unbinding` flag; domain restriction must be applied before untrusted bind operations; static ports are not closed by this driver; userspace must write back ports to complete late EOI and re-enable delivery.

Test signals: bind VIRQ and interdomain channels from userspace, test poll/read/write acknowledgment, overflow and reset, fasync SIGIO, restricted domid enforcement, static binding, close cleanup, and concurrent unbind while events arrive.
