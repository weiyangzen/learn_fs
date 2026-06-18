# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8365-pm-domains.h

Purpose: MT8365 SCPSYS table for multimedia, connectivity, GPU, camera, video, APU, and DSP domains.

Important data: domains are `mm`, `venc`, `audio`, `conn`, `mfg`, `cam`, `vdec`, `apu`, and `dsp`. It defines MT8365-specific bus-protect helper macros for infra topaxi, SMI clamp, and way-enable cases. `mm` uses strict bus protection and `HAS_INFRA_NAO`; `conn` is active-wakeup plus keep-default-off; `audio` and `dsp` are active-wakeup.

Control flow: selected by `mediatek,mt8365-power-controller`; the generic driver honors strict bus-protection ordering by enabling subsystem clocks after protection release for affected domains.

State and persistence behavior: static table only. Runtime state is SPM status `0x0180/0x0184`, bus-protect registers, and SRAM ack bits.

Dependencies and integration points: requires MT8365 power binding IDs and access-controller regmaps for infra, infra-nao, and SMI where listed. Multimedia/APU/DSP consumers attach through genpd.

Risks: strict bus-protection behavior is easy to regress if generic ordering changes. `HAS_INFRA_NAO` affects expected clear acknowledgements, so the access-controller list must include the right block. Connectivity default-off plus wakeup should be validated in suspend.

Test signals: run display/MM, video, camera, APU, DSP, GPU, and connectivity wake tests. Check that strict bus protection avoids bus faults during MM power-on.
