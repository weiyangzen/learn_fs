<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_ch7301.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_ch7301.c

Purpose: Auxiliary probe for Chrontel CH7301 DVI transmitters on VIA display I2C buses.

Important APIs/types/functions: `via_aux_ch7301_probe(struct via_aux_bus *bus)` probes addresses `0x75` and `0x76`; the local `probe()` reads register `0x4B` and accepts the device when the value is `0x17`, then logs and calls `via_aux_add()`.

Control flow and state: Probe is read-only and stateless. A successful match creates a `via_aux_drv` descriptor with name `CH7301 DVI Transmitter`; there are no callbacks or private data.

Dependencies and integration points: Uses `via_aux_read()` from `via_aux.h` and is invoked from `via_aux_probe()`. Risks are minimal ID validation from a single register, no configuration or power sequencing support, and no preferred-mode callback. Test signals are I2C scan results at both addresses and ensuring false positives do not occur on unrelated devices returning `0x17` at register `0x4B`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_ch7301.c -->
