## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh_event.h

Purpose: declares the EEH event queue item and event handling entry points.

Important APIs/types/functions: `struct eeh_event` holds a list node and affected `struct eeh_pe *`; functions include `eeh_event_init()`, `eeh_send_failure_event()`, `__eeh_send_failure_event()`, `eeh_remove_event()`, `eeh_handle_normal_event()`, and `eeh_handle_special_event()`.

Control flow: EEH detection enqueues PE failure events, worker/recovery code handles normal PE events or special global events, and events can be removed forcibly for teardown.

State and persistence: event queue entries persist until processed or removed. PE pointers tie queued work to EEH recovery state.

Dependencies and integration: depends on EEH PE definitions and Linux lists. Used by EEH recovery threads and PCI error handling.

Risks and test signals: stale PE pointers during hotplug or duplicate events can race recovery. Test signals include EEH injection storms, forced removal while queued, normal and special event handling, and recovery thread initialization.
