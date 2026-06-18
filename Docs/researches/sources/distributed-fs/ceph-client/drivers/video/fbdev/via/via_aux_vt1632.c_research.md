<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1632.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1632.c

Purpose: Auxiliary probe for VIA VT1632 DVI transmitters.

Important APIs/types/functions: `via_aux_vt1632_probe()` scans addresses `0x08` through `0x0F`; local `probe()` matches the four-byte ID `{0x06, 0x11, 0x92, 0x31}` and adds a descriptor named `VT1632 DVI Transmitter`.

Control flow and state: Stateless scan loop, no private data or callbacks beyond detection.

Dependencies and integration points: Called from `via_aux_probe()`. TMDS output support elsewhere checks chip information and DVI sense, so this aux probe is primarily discovery/logging and possible future extension. Risks include scan overhead across eight addresses and no configuration state created from the detected transmitter. Test signals are detection on address-strapped VT1632 boards and lack of disruption to EDID/DDC reads on the same bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_vt1632.c -->
