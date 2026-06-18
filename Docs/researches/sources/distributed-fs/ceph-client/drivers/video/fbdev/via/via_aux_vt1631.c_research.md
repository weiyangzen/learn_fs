<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1631.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1631.c

Purpose: Auxiliary probe for VIA VT1631 LVDS transmitters.

Important APIs/types/functions: `via_aux_vt1631_probe()` reads four ID bytes from address `0x38` and matches `{0x06, 0x11, 0x91, 0x31}` before adding a stateless `via_aux_drv` named `VT1631 LVDS Transmitter`.

Control flow and state: Single exact-ID read; successful detection is represented as a bus-list descriptor only.

Dependencies and integration points: Called by `via_aux_probe()`. Separate legacy LVDS detection in `lcd.c` also knows about VT1631 via target address and device ID. Risks include split responsibility between aux detection and active LCD setup, no preferred-mode/config callbacks, and address overlap with other DVI/LVDS transmitters. Test signals are I2C detection on VT1631 panels and ensuring `lcd.c` still configures the active LVDS chip state consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1631.c -->
