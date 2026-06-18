<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.h

Purpose: Shared interface for simple I2C auxiliary display-device probes. It defines bus and driver descriptors, common add/read helpers, public bus lifecycle APIs, and declarations for all concrete probe functions.

Important APIs/types/functions: `struct via_aux_bus` stores an `i2c_adapter` and a list of `via_aux_drv`. `struct via_aux_drv` stores list linkage, target bus/address, display name, private data, cleanup callback, and preferred-mode callback. Inline helpers `via_aux_add()` duplicate and append a driver descriptor, and `via_aux_read()` performs a one-byte-register I2C read transaction. Public functions are `via_aux_probe()`, `via_aux_free()`, `via_aux_get_preferred_mode()`, and concrete probe declarations.

Control flow and state: No standalone runtime flow. The inline helpers are used by every auxiliary probe. State is dynamically allocated per bus and per found driver; optional private data belongs to the driver descriptor and is released by `via_aux_free()`.

Dependencies and integration points: Includes Linux list, I2C, and fb headers. It integrates with `via_i2c.c` adapters and mode selection in `viafbdev.c`. Risks include `via_aux_add()` shallow-copying `data` ownership, fixed 7-bit I2C addressing expectations, no synchronization, and no write/helper abstraction for configuration. Test signals are probe/fail allocation paths, I2C read error handling, and cleanup of EDID modedb private data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.h -->
