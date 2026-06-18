<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1622.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1622.c

Purpose: Auxiliary probe for VIA VT1622(M) digital TV encoders.

Important APIs/types/functions: `via_aux_vt1622_probe()` probes addresses `0x20` and `0x21`; local `probe()` reads register `0x1B` and matches value `0x03`, then adds a `VT1622(M) Digital TV Encoder` descriptor.

Control flow and state: Stateless read-only detection. No configuration, cleanup, or preferred-mode callback is installed.

Dependencies and integration points: Invoked by `via_aux_probe()` and uses `via_aux_read()`. Risks are single-register identity, overlap with other VT162x addresses, and discovery without usable TV encoder programming in this driver slice. Test signals are I2C detection on boards with either address strap and non-detection on VT1621/VT1625 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1622.c -->
