# sources/distributed-fs/ceph-client/drivers/usb/misc/lvstest.c

Purpose: Link Layer Validation System test driver for SuperSpeed root hubs. It exposes sysfs triggers for USB 3 link validation actions such as U1/U2 timeouts, U3 entry/exit, hot/warm reset, compliance mode, and device descriptor fetch.

Important APIs and types: `struct lvs_rh`, `create_lvs_device()`, `destroy_lvs_device()`, sysfs store handlers, `lvs_rh_work()`, `lvs_rh_irq()`, probe, and disconnect. It integrates with root-hub class requests, HCD `enable_device/free_dev`, `usb_phy_notify_connect/disconnect`, and root-hub interrupt polling.

Control flow: probe only binds SuperSpeed root hubs with no parent, reads the SS hub descriptor, allocates an interrupt URB, and schedules work on root-hub interrupt activity. Work scans all ports, clears change bits, tracks which port has an LVS device, notifies the PHY, and resubmits the interrupt URB. Sysfs triggers send root-hub port feature requests; some create a temporary SuperSpeed `usb_device` so the HCD can issue device-scoped operations such as descriptor fetch or U3 transitions.

State and persistence: present flag, port number, cached hub descriptor/status, URB, and work item are volatile. Risks include lab-only operations that intentionally disrupt root hub ports, hand-built `usb_device` lifecycle, sysfs write-only ABI without payload semantics for most commands, and reliance on HCD optional hooks. Test signals include binding only to SS root hubs, port change detection, feature request traces, HCD enable/free invocation, sysfs error propagation, and disconnect flushing work after URB poison.
