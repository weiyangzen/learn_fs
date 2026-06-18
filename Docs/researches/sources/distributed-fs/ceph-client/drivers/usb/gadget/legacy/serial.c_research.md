# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/serial.c

Purpose: legacy `g_serial` composite gadget exposing one or more USB serial ports as CDC ACM, CDC OBEX, or vendor-specific generic serial functions.

Important APIs, types, and functions: module parameters `use_acm`, `use_obex`, `n_ports`, and dynamic `enable` choose function type, port count, and registration state. `serial_register_ports` adds the configuration and loops over ports, getting a function instance/function for `acm`, `obex`, or `gser`. `gs_bind` assigns strings, optional OTG descriptor, and registers the selected ports. `switch_gserial_enable`, `enable_set`, `gserial_init`, and `gserial_cleanup` implement runtime composite probe/unregister toggling.

Control flow: module init chooses descriptor class, product ID, configuration label/value, and string text based on `use_acm`/`use_obex`. If `enable` is true, it probes the composite driver. Bind creates string IDs and adds N serial functions to the one configuration. Runtime writes to the `enable` module parameter can register or unregister the composite driver after init.

State and persistence: static arrays `fi_serial` and `f_serial` hold per-port references up to `MAX_U_SERIAL_PORTS`. Module parameters persist only while the module is loaded. TTY buffering and port state live in the serial function implementation.

Dependencies and integration points: depends on libcomposite, `u_serial`, Linux TTY support, and the ACM/OBEX/generic serial USB function providers. It exposes host-visible serial ports and gadget-side TTY endpoints through lower layers.

Risks: `n_ports` must stay within the function framework limit; this file does not visibly clamp before indexing the static arrays, so validation is expected elsewhere or by parameter discipline. Runtime enable toggling can race conceptually with active host sessions, relying on composite unregister to quiesce. Function acquisition failures must unwind every previously added port.

Test signals: load with ACM, OBEX, and generic modes; vary `n_ports`; verify descriptors/product IDs; open gadget TTYs and host serial devices; toggle `enable` at runtime; disconnect during serial traffic; and unload while all ports are active.
