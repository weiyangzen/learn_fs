# sources/distributed-fs/ceph-client/drivers/xen/events/events_internal.h

Purpose: defines the private ABI contract between the generic Xen event-channel core and concrete event-channel backends such as FIFO and the older 2-level implementation.

Important APIs/functions: declares `struct evtchn_ops`, the global `evtchn_ops`, `handle_irq_for_port`, `cpu_from_evtchn`, `xen_evtchn_2l_init`, and `xen_evtchn_fifo_init`. Inline wrappers expose max/nr channel queries, port setup/removal, CPU binding, pending bit operations, mask/unmask, event scanning, and resume.

Control flow: `events_base.c` calls the wrapper functions rather than direct backend functions. Backend initialization installs `evtchn_ops`; subsequent operations dispatch to the selected ABI. Optional callbacks such as `setup`, `remove`, `resume`, `percpu_init`, and `percpu_deinit` are guarded by NULL checks where appropriate.

State and persistence: the header owns no storage except the external `evtchn_ops` pointer. Its main persistence concern is that all event-channel operations depend on `evtchn_ops` having been initialized before callers use wrappers.

Dependencies and integration: included by `events_base.c`, `events_fifo.c`, and the 2-level backend. It depends on Xen event-channel port types and the private `evtchn_loop_ctrl` used to carry event-loop throttling state.

Risks: callbacks such as `bind_to_cpu`, `clear_pending`, `set_pending`, `is_pending`, `mask`, `unmask`, and `handle_events` are assumed non-NULL after backend selection; a partially initialized backend would crash. API changes here affect both event backends and the generic IRQ binding layer.

Test signals: compile both FIFO and 2-level backends, boot with FIFO enabled and disabled, and exercise CPU hotplug and resume paths that call the optional callbacks.
