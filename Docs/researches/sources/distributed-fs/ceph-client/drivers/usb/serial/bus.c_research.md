<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/bus.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/bus.c

Purpose: implements the `usb-serial` bus for matching assigned ports to converter drivers, invoking port probe/remove, registering tty devices, and exposing dynamic IDs. The complete 171-line source was read.

Important APIs/types/functions: `usb_serial_bus_type`, `usb_serial_device_match()`, `usb_serial_device_probe()`, `usb_serial_device_remove()`, `new_id_store()`, `new_id_show()`, `usb_serial_bus_register()`, `usb_serial_bus_deregister()`, and `free_dynids()`.

Control flow and state: matching compares the bus driver to `port->serial->type`; probe gets autopm, calls optional `port_probe`, registers `ttyUSB<minor>`, and logs attach; remove gets autopm when possible, unregisters tty, calls `port_remove`, and logs detach. State includes driver registration, dynamic IDs, and tty device nodes.

Dependencies and integration points: USB serial core, USB dynamic-ID helpers, TTY port registration, runtime PM, driver core, and `usb_dynids_lock`.

Risks and test signals: risks include PM races, cleanup after tty registration failure, dynid duplication between usbserial and usb_driver, and remove after autopm failure. Test register/deregister, dynamic `new_id`, probe rollback, suspend during probe/remove, disconnect, and multi-port minor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/bus.c -->
