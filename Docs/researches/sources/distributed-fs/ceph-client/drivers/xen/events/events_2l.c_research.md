# sources/distributed-fs/ceph-client/drivers/xen/events/events_2l.c

## Purpose
`events_2l.c` implements Xen's classic two-level event-channel ABI for Linux IRQ delivery. It supplies the `evtchn_ops` backend that manages pending/mask bits, CPU binding masks, event scanning, unmask semantics, resume cleanup, and debug dumps.

## Important APIs, types, and functions
Important state includes per-CPU `cpu_evtchn_mask`, `current_word_idx`, and `current_bit_idx`. Operations are `evtchn_2l_max_channels`, `evtchn_2l_remove`, `evtchn_2l_bind_to_cpu`, `evtchn_2l_clear_pending`, `evtchn_2l_set_pending`, `evtchn_2l_is_pending`, `evtchn_2l_mask`, `evtchn_2l_unmask`, `evtchn_2l_handle_events`, `evtchn_2l_resume`, `evtchn_2l_percpu_deinit`, and initializer `xen_evtchn_2l_init`. `xen_debug_interrupt` dumps shared-info and per-CPU event-channel state.

## Control flow
Initialization assigns `evtchn_ops` to the two-level implementation. Binding sets the port bit in exactly one CPU mask. Mask/pending operations manipulate Xen shared-info bitmaps with sync bitops. Unmask either clears the local mask and locally resends a pending event by setting `evtchn_pending_sel`/`evtchn_upcall_pending`, or calls Xen `EVTCHNOP_unmask` when the port is non-local or HVM pending delivery requires hypervisor help. Event handling prioritizes the timer VIRQ, exchanges and clears the vCPU selector word, scans pending words/bits fairly from saved cursors, and dispatches each active port through `handle_irq_for_port`.

## State and persistence
State is per-CPU event mask and scan cursor state plus Xen shared-info pending/mask/select fields. Resume and CPU deinit clear local masks; shared hypervisor state is rebuilt by higher-level event code.

## Dependencies and integration points
It depends on Xen shared info, vCPU info, event-channel hypercalls, sync bitops, IRQ core `generic_handle_irq`, and internal event helpers from `events_internal.h`.

## Risks and test signals
Risks include bit-width mismatches between `xen_ulong_t` and `unsigned long`, lost event edges during unmask, fairness cursor arithmetic using word count constants, timer VIRQ priority interactions, HVM/PV delivery differences, CPU hotplug mask cleanup, and verbose debug interrupt locking. Test signals include high event-channel counts, CPU rebinding, pending-while-masked delivery, HVM and PV guests, timer VIRQ latency, suspend/resume, CPU offline/online, and debug interrupt output consistency.
