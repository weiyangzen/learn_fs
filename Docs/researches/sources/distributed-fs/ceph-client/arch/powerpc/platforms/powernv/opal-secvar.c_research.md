## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-secvar.c

### Purpose
`opal-secvar.c` implements the `secvar_operations` backend for secure variables managed by OPAL firmware.

### Important APIs, Types, And Functions
Important functions are `opal_status_to_err()`, `opal_get_variable()`, `opal_get_next_variable()`, `opal_set_variable()`, `opal_secvar_format()`, `opal_secvar_max_size()`, `opal_secvar_probe()`, and `opal_secvar_init()`. The file defines `opal_secvar_ops`.

### Control Flow
Probe verifies OPAL supports get, get-next, and enqueue-update tokens, then registers operations with `set_secvar_ops()`. Get and get-next convert size arguments to big-endian before OPAL calls and convert them back on return. Set enqueues an update through firmware. Format and max-size are read from an available `ibm,secvar-backend` DT node.

### State, Persistence, And Dependencies
Linux keeps only the registered operations table. Secure variables and pending updates persist in firmware. Dependencies include OPAL secvar calls, secure boot/secvar core APIs, platform driver probing, device tree backend metadata, and OPAL error conventions.

### Integration Points
`opal.c` creates the `ibm,secvar-backend` platform device, and the generic secvar subsystem calls through this backend. It bridges secure boot variable storage to OPAL.

### Risks
`of_find_compatible_node()` may return NULL in `opal_secvar_format()` before `of_device_is_available(node)` is called, which relies on that helper tolerating NULL. OPAL status mapping collapses unknown returns to `-EINVAL`. Set requires non-NULL data, so deletion semantics must be represented by firmware-specific update payloads rather than NULL data.

### Test Signals
Test unsupported token combinations, endian size round trips, buffer-too-small `OPAL_PARTIAL`, empty variable iteration, unavailable backend node, missing `format` or `max-var-size`, firmware hardware/no-memory/resource errors, and `set_secvar_ops()` registration.
