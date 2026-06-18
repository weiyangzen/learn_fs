<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1636.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1636.c

Purpose: Auxiliary probe for VIA VT1636 LVDS transmitters on an I2C bus.

Important APIs/types/functions: `via_aux_vt1636_probe()` reads four bytes at address `0x40` and matches `{0x06, 0x11, 0x45, 0x33}`. On match it logs and adds a stateless `via_aux_drv` named `VT1636 LVDS Transmitter`.

Control flow and state: Stateless read-only detection. Active VT1636 programming is implemented separately in `vt1636.c`; this file only records presence on the aux bus.

Dependencies and integration points: Invoked from `via_aux_probe()` before VT1632/VT1631/TV encoder probes. Risks are split probe/programming paths with different address conventions (`via_aux` uses 7-bit `0x40`, legacy VT1636 code uses its target address constant), no preferred-mode callback, and no cleanup needs. Test signals are I2C detection and consistency with `viafb_lvds_identify_vt1636()` on ports `0x31`/`0x2C`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1636.c -->
