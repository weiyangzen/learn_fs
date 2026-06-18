<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1621.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1621.c

Purpose: Auxiliary probe for VIA VT1621(M) TV encoders.

Important APIs/types/functions: `via_aux_vt1621_probe()` reads register `0x1B` from address `0x20` and matches value `0x02`. On success it logs and adds a stateless `via_aux_drv` named `VT1621(M) TV Encoder`.

Control flow and state: Single-address, single-register identity check with no private data and no callbacks.

Dependencies and integration points: Called from `via_aux_probe()` after newer LVDS/DVI probes. Risks are weak ID validation, no mode enumeration or TV-standard control, and no configuration path after discovery. Test signals are I2C probe success/failure at `0x20` and absence of false positives with other VT162x devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1621.c -->
