# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.c

Purpose: core ChromeOS EC device layer shared by bus transports. It allocates common `cros_ec_device` state, registers EC/PD child platform devices, handles MKBP event interrupts and notifiers, and centralizes suspend/resume host-sleep events.

Important APIs, types, and functions: exported functions are `cros_ec_device_alloc()`, `cros_ec_register()`, `cros_ec_unregister()`, `cros_ec_irq_thread()`, `cros_ec_suspend_prepare()`, `cros_ec_suspend_late()`, `cros_ec_suspend()`, `cros_ec_resume_early()`, `cros_ec_resume_complete()`, and `cros_ec_resume()`. Internal helpers include `cros_ec_handle_event()`, `cros_ec_sleep_event()`, `cros_ec_ready_event()`, and IRQ top half `cros_ec_irq_handler()`.

Control flow: bus drivers allocate an EC device, fill bus callbacks and metadata, then call `cros_ec_register()`. Registration attempts RWSIG continue, queries protocol/features, requests IRQ if present, creates a `cros-ec-dev` child for the EC and optionally PD passthrough, populates OF child devices, clears sleep event, registers an interface-ready notifier, marks the device registered, and drains pending MKBP events. IRQ top half timestamps the event and wakes the thread; the thread loops `cros_ec_get_next_event()` until no more events, triggering wakeups and notifier calls. Suspend/resume helpers send host sleep events, disable/enable IRQs, preserve wake IRQ state, and report events queued during suspend.

State and persistence: `cros_ec_device` owns command buffers, max request/response sizes, protocol feature flags from `cros_ec_query_all()`, event/panic notifier chains, lockdep class, registered/suspended/wake flags, last event time, last resume result, and suspend timeout. Firmware state changes through host sleep commands and feature queries.

Dependencies and integration points: depends on Chrome EC protocol helpers, platform devices, PM wakeup/suspend, OF population, IRQ threading, and child drivers under MFD/platform Chrome EC. Bus transports provide `cmd_xfer`, `pkt_xfer`, optional `cmd_readmem`, IRQ, and physical name.

Risks and edge cases: child platform devices are manually unregistered on failures; ordering matters. Sleep-event commands are allowed to fail on firmware without support. Event fanout relies on `ec_dev->event_data` being populated by protocol helpers before notifier call. The registered flag is protected by the EC mutex but not every reader may hold it. IRQ disable assumes valid IRQ when suspend helpers are used.

Test signals: protocol query success, child device creation, PD passthrough when `max_passthru` is set, MKBP interrupt fanout, interface-ready re-query, suspend/resume host-sleep events, wake IRQ behavior, and removal unregistering children/notifiers.
