# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_irq.c

Purpose: This file installs the QXL IRQ handler and dispatches host interrupt events to wait queues, release garbage collection, and monitor-config work.

Important APIs, types, and functions: `qxl_irq_init()` initializes wait queues, work item, atomic counters, requests the shared PCI IRQ, and enables `QXL_INTERRUPT_MASK`. `qxl_irq_handler()` handles display, cursor, I/O command, error, and client monitor config interrupts. `qxl_client_monitors_config_work_func()` calls into display monitor parsing.

Control flow: The IRQ handler atomically exchanges `ram_header->int_pending` with zero, returns `IRQ_NONE` if no bits were pending, increments counters, wakes display/cursor/I/O waiters, schedules release collection on display interrupts, schedules monitor config work on monitor interrupts, re-enables the interrupt mask, and notifies the host that IRQ state was updated.

State and persistence: Maintains atomic IRQ counters, `irq_received_error`, wait queues, and `client_monitors_config_work`. Host interrupt state lives in the shared RAM header and is cleared by the handler.

Dependencies and integration points: Depends on PCI IRQs, QXL RAM header, wait queues used by `qxl_cmd.c`, garbage collection, and monitor config reading in `qxl_display.c`. Initialized during `qxl_device_init()` before async memslot I/O commands.

Risks: `request_irq()` failure returns `1` rather than the exact negative error code. Error interrupts only warn and increment a counter; reset recovery is TODO. Correct ordering between clearing pending bits, re-enabling masks, and host notification is critical.

Test signals: Generate display/cursor/io interrupts under draw/cursor/update traffic; trigger SPICE monitor hotplug; inspect debugfs IRQ counters; test shared IRQ behavior; simulate request_irq failure if possible.
