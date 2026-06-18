# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8183-pm-domains.h

Purpose: MT8183 power-domain table for the generic SCPSYS driver.

Important data: domains are `audio`, `conn`, `mfg_async`, `mfg`, `mfg_core0`, `mfg_core1`, `mfg_2d`, `disp`, `cam`, `isp`, `vdec`, `venc`, `vpu_top`, `vpu_core0`, and `vpu_core1`. GPU root domains use `MTK_SCPD_DOMAIN_SUPPLY`; VPU core domains use `MTK_SCPD_SRAM_ISO`. Display/camera/VPU entries contain multi-step bus-protection config.

Control flow: `mt8183_scpsys_data` provides direct-control domain data and infra/SMI bus-protection block order. The generic driver uses DT child hierarchy plus table indices to register genpds and subdomains.

State and persistence behavior: no local state. Runtime state is SPM status at offsets `0x0180`/`0x0184`, SRAM isolation bits, regulator state, and bus-protect acknowledgements.

Dependencies and integration points: uses MT8183 binding IDs, infra/SMI access-controller regmaps, optional domain supplies, and DT clock lists split into main and subsystem clocks.

Risks: MFG and VPU top/core hierarchy is sensitive to DT nesting. SRAM isolation ordering for VPU cores must match hardware or power-on can leave memory inaccessible. Bus-protection masks for display/camera/video are a common timeout source.

Test signals: run display, camera, video encode/decode, VPU/NPU, and GPU workloads across suspend/resume. Confirm OPP/regulator-backed GPU domains attach correctly.
