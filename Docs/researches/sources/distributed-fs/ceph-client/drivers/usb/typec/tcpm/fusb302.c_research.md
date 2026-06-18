# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302.c

## Purpose

`fusb302.c` is the Fairchild/FCS FUSB302 Type-C port-controller driver for TCPM. It uses SMBus/I2C register access to implement the `tcpc_dev` callbacks for CC detection, DRP toggling, VBUS/VCONN control, PD RX/TX, and interrupt-driven state changes.

## Important APIs, Types, and Functions

`struct fusb302_chip` holds device/I2C/TCPM state, regulator, GPIO/IRQ/workqueue state, optional extcon, mutex-protected Type-C/PD state, current CC polarity/status, and debugfs log buffers. Key TCPM callbacks are `tcpm_init()`, `tcpm_get_vbus()`, `tcpm_get_current_limit()`, `tcpm_set_cc()`, `tcpm_get_cc()`, `tcpm_set_vconn()`, `tcpm_set_vbus()`, `tcpm_set_pd_rx()`, `tcpm_set_roles()`, `tcpm_start_toggling()`, and `tcpm_pd_transmit()`. Internal control paths include `fusb302_set_toggling()`, `fusb302_handle_togdone_snk()`, `fusb302_handle_togdone_src()`, `fusb302_pd_send_message()`, `fusb302_pd_read_message()`, and `fusb302_irq_work()`.

## Control Flow

Probe checks SMBus block support, allocates state, optionally looks up ACPI extcon, gets the VBUS regulator, creates a single-thread workqueue, initializes IRQ work and BC-level delayed work, creates debugfs, gets IRQ or GPIO interrupt, obtains connector fwnode or software defaults, allocates a DRM DP HPD bridge, registers with TCPM, requests the low-level IRQ, enables wake, and adds the bridge. TCPM calls initialize the chip via reset, auto-retry, interrupt masks, power mode, VBUS sampling, and device ID logging. The interrupt handler disables the level IRQ and schedules work; the worker reads interrupt/status snapshots, updates VBUS, handles TOGDONE CC resolution, schedules delayed sink current measurement, handles source detach comparator changes, maps PD collision/retry/hard-reset/TX/RX events into TCPM callbacks, then re-enables the IRQ.

## State and Persistence Behavior

The driver caches VBUS, VCONN, charge, PD RX, toggling mode, interrupt enable intentions, CC polarity/status, and sink PDO fallback data in memory. Hardware register state is volatile and reinitialized by TCPM init. Debugfs keeps a circular in-memory log only. Suspend marks IRQs as deferred, flushes current work before bus suspend, and resume schedules work if an IRQ arrived while suspended.

## Dependencies and Integration Points

It depends on I2C SMBus block operations, GPIO IRQ or client IRQ, regulator core, TCPM, USB PD helpers, Type-C class enums, optional extcon charger detection, workqueues, debugfs, software fwnodes, and DRM AUX HPD bridge. It is one of the main TCPM hardware adapters.

## Risks and Test Signals

Risks include complex interrupt ordering between TX success and GoodCRC, delayed BC-level measurement during PD activity, level-triggered IRQ re-enable on error paths, manual FIFO token framing, missing cleanup if HPD bridge add fails after IRQ request, and concurrency between TCPM callbacks and IRQ work. Test signals include TCPM registration, SW reset and register init, source/sink/DRP toggling outcomes, CC attach/detach and current-level changes, VBUS regulator transitions, PD send/receive/hard-reset/retry/collision IRQs, suspend/resume IRQ deferral, debugfs log operation, and software-node fallback connector properties.
