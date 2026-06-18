# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8186-pm-domains.h

Purpose: MT8186 SCPSYS direct-control table covering GPU, USB, display, imaging, camera, video, connectivity, CSI, and ADSP islands.

Important data: domains are `mfg0`, `mfg1`, `mfg2`, `mfg3`, `ssusb`, `ssusb_p1`, `dis`, `img`, `img2`, `ipe`, `cam`, `cam_rawa`, `cam_rawb`, `venc`, `vdec`, `wpe`, `conn_on`, `csirx_top`, `adsp_ao`, `adsp_infra`, and `adsp_top`. Many media domains are `KEEP_DEFAULT_OFF`; USB domains are active-wakeup; `mfg0`/`mfg1` use domain supplies; `adsp_top` combines SRAM isolation and active wakeup.

Control flow: table is selected by `mediatek,mt8186-power-controller`; generic direct sequencing uses custom status offsets `0x16c`/`0x170`, ordered bus-protect config, and main/subsystem clocks from DT.

State and persistence behavior: static table only; runtime state sits in SPM status/control registers, bus-protect regmaps, and supplies for GPU roots.

Dependencies and integration points: requires MT8186 binding IDs, access-controller list matching `scpsys_bus_prot_blocks_mt8186`, regulator supplies for GPU domains, and DT subdomain nesting.

Risks: default-off media domains will not be initialized on unless consumers request them, exposing missing power-domain references quickly. `conn_on` active-wakeup/default-off combination needs suspend testing. Camera/raw and image pipelines rely on correct bus-protect order.

Test signals: validate USB wake, GPU power/regulator behavior, ADSP suspend/resume, and camera/video/display runtime PM with regmap debug for bus-protect ack bits.
