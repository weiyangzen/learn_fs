# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6893-pm-domains.h

Purpose: MT6893 direct-control SCPSYS data with extensive multimedia/GPU bus-protection sequences.

Important data: domain inventory is `conn`, `mfg0` through `mfg6`, `isp`, `isp2`, `ipe`, `vdec0`, `vdec1`, `venc0`, `venc1`, `mdp`, `disp`, `audio`, `adsp` (named `audio` in the table), `cam`, `cam_rawa`, `cam_rawb`, `cam_rawc`, and `dp_tx`. It defines many MT6893-specific top-axi protection masks and offsets for MCU, VDNR, and sub-infra paths. Several GPU/video/display domains are `MTK_SCPD_KEEP_DEFAULT_OFF`; `mfg0`/`mfg1` also require domain supplies.

Control flow: selected by `mediatek,mt6893-power-controller`. The generic driver executes ordered bus-protection entries in `bp_cfg` during power off and reverses them during power on. Domains share custom status offsets `0x16c` and `0x170`.

State and persistence behavior: static table; runtime state is controlled by SPM, regulator state for supplied domains, and multiple bus-protect regmaps.

Dependencies and integration points: requires MT6893 binding IDs, regulator supplies for GPU root domains, access-controller regmaps that match the table's bus-protection block order, and DT hierarchy for GPU/media dependencies.

Risks: the ADSP entry name duplicates `audio`, which can make genpd diagnostics ambiguous. Long multi-step bus-protect sequences are ordering-sensitive; wrong access-controller order or missing phandle causes probe/power failures. Default-off domains may remain off until consumers attach.

Test signals: boot should register all MT6893 domains with access-controller count matching SoC data. Exercise GPU, camera raw, display, MDP, video encoder/decoder, and DP power cycles while tracing bus-protect ack polling.
