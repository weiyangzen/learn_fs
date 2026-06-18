# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8167-pm-domains.h

Purpose: MT8167 SCPSYS domain table for the generic MediaTek PM-domain driver.

Important data: defines `mm`, `vdec`, `isp`, `mfg_async`, `mfg_2d`, `mfg`, and `conn`. It adds MT8167-specific status bits for `mfg_2d` and `mfg_async`, a bus-protection block list for infra, and active-wakeup capabilities for `mm`, `vdec`, `isp`, and `conn`.

Control flow: `mt8167_scpsys_data` is selected by compatible string in `mtk-pm-domains.c`; direct-control sequencing drives SPM registers and optional bus-protect entries.

State and persistence behavior: no local state. SRAM and status masks define how runtime power state is observed and synchronized.

Dependencies and integration points: depends on MT8167 power binding IDs and infra bus-protect regmap. Consumers are multimedia, GPU, and connectivity blocks.

Risks: active-wakeup flags keep domains eligible during system wake paths; incorrect flags can affect suspend/resume. GPU split domains require correct parent/consumer topology in DT.

Test signals: suspend/resume with connectivity and multimedia wake sources, plus GPU/display/video power-cycle tests, should show no SPM timeout or infracfg bus-protection timeout.
