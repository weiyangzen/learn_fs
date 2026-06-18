<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.c

Purpose: I2C auxiliary-device bus infrastructure for display devices connected to VIA outputs. It probes EDID and known encoder/transmitter chips on a given `i2c_adapter`, stores discovered lightweight driver descriptors, and lets callers request a preferred display mode.

Important APIs/types/functions: `via_aux_probe()` allocates `struct via_aux_bus`, initializes its driver list, and calls all probe functions in fixed order: EDID, VT1636, VT1632, VT1631, VT1625, VT1622, VT1621, SiI164, and CH7301. `via_aux_free()` calls per-driver cleanup, unlinks list nodes, frees driver data and descriptors, then frees the bus. `via_aux_get_preferred_mode()` walks the driver list and returns the last non-NULL preferred mode reported by any driver implementing `get_preferred_mode`.

Control flow and state: A bus is created per probed I2C adapter from `viafbdev.c` (`i2c_26`, `i2c_31`, optional `i2c_2C`). Each probe may append a `via_aux_drv` to the bus list. EDID can carry allocated `fb_monspecs` state; most chip probes are stateless identity records. Preferred-mode lookup is list-order dependent and overwrites earlier modes with later ones if multiple drivers report a mode.

Dependencies and integration points: Depends on `via_aux.h`, Linux I2C/list/slab, and the concrete `via_aux_*_probe()` functions. It feeds `parse_mode()` in `viafbdev.c` when no explicit mode is supplied. Risks include no locking around the bus list, no reprobe on hotplug except EDID driver's always-present descriptor, and ambiguous preferred-mode precedence. Test signals are I2C adapter absence, EDID monitor preferred mode selection, multiple transmitter detection, and free-path leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux.c -->
