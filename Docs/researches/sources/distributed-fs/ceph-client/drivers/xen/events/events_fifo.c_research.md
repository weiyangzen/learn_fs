# sources/distributed-fs/ceph-client/drivers/xen/events/events_fifo.c

Purpose: implements the FIFO-based Xen event-channel ABI behind the generic event layer. It manages per-vCPU control blocks, the global event array, priority queues, pending/masked bits, and FIFO event consumption.

Important APIs/functions: provides `xen_evtchn_fifo_init` and the `evtchn_ops_fifo` callbacks: `max_channels`, `nr_channels`, `setup`, `bind_to_cpu`, `clear_pending`, `set_pending`, `is_pending`, `mask`, `unmask`, `handle_events`, `resume`, `percpu_init`, and `percpu_deinit`. Core state is `cpu_control_block`, `cpu_queue`, `event_array`, and `event_array_pages`.

Control flow: initialization allocates a control block for the boot CPU, initializes it through `EVTCHNOP_init_control`, and installs FIFO ops. Port setup expands the event array one Xen page at a time with `EVTCHNOP_expand_array`, initializing all event words as masked before exposing them. Upcall handling atomically takes the control block ready word, consumes the highest ready priority queues through linked event words, clears linked state, and calls `handle_irq_for_port` for pending unmasked ports. Unmasking clears the masked bit only when safe; if the port is pending it uses `EVTCHNOP_unmask` so Xen can requeue delivery.

State and persistence: per-CPU queue heads cache partially consumed FIFO links, control blocks persist while CPUs are online, and event array pages are retained across resume but `event_array_pages` is reset so the hypervisor array is rebuilt lazily. Offline CPU teardown drains events with a NULL loop controller, logging dropped pending ports.

Dependencies and integration: depends on `events_internal.h`, Xen FIFO event-channel definitions, sync bitops, hypercalls, vCPU numbering, and the generic `handle_irq_for_port` callback in `events_base.c`.

Risks: event words need correct alignment handling on 64-bit systems; unmasking must run with interrupts disabled; array expansion failures after the first page leave limited channel capacity; events drained during CPU deinit can be dropped; stale control blocks after resume must be reinitialized before use.

Test signals: verify FIFO ABI selection at boot, event delivery under multiple priorities, suspend/resume, CPU online/offline, array expansion beyond the first page, and fallback to 2-level events when FIFO init fails.
