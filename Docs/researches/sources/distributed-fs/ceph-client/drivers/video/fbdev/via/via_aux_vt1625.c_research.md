<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1625.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1625.c

Purpose: Auxiliary probe for VIA VT1625(M) HDTV encoders.

Important APIs/types/functions: `via_aux_vt1625_probe()` checks addresses `0x20` and `0x21`; local `probe()` reads register `0x1B`, accepts value `0x50`, logs the address, and adds a stateless aux driver descriptor.

Control flow and state: Stateless, read-only I2C identity probe. There is no cleanup or mode callback.

Dependencies and integration points: Called from `via_aux_probe()`. Risks include no HDTV mode programming, no output-state integration, and possible stale detection if a bus device aliases the same ID register. Test signals are probe coverage on both possible addresses and no false positives on VT1621/VT1622 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1625.c -->
