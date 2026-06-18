<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_sii164.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_sii164.c

Purpose: Auxiliary probe for Silicon Image SiI 164 PanelLink transmitters.

Important APIs/types/functions: `via_aux_sii164_probe()` scans 7-bit I2C addresses `0x38` through `0x3F`. Local `probe()` reads four bytes at register `0x00` and matches the exact ID sequence `{0x01, 0x00, 0x06, 0x00}` before adding a stateless `via_aux_drv` descriptor.

Control flow and state: Read-only probe loop; successful detection persists only as a bus-list descriptor with the name `SiI 164 PanelLink Transmitter`.

Dependencies and integration points: Invoked by `via_aux_probe()` and depends on `via_aux_read()`. Risks are no programming support after detection, no preferred-mode callback, and scan cost/noise across eight addresses. Test signals are detection on boards with SiI164, non-detection on absent buses, and no collision with VT1631 address `0x38` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_sii164.c -->
