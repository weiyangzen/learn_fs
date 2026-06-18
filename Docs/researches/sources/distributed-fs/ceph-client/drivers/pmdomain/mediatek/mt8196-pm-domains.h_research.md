# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8196-pm-domains.h

Purpose: MT8196 SCPSYS data for both direct-control domains and hardware-voter power controllers.

Important data: direct domains include modem/connectivity, USB/DP PHY, PCIe MAC/PHY, audio, ADSP, MM dormant/shutdown/infra domains, video decoder/encoder groups, display dormant domains, MML shutdown domains, CSI RX, and DSI PHYs. It also declares `scpsys_hwv_domain_data_mt8196` and HFRP hardware-voter domain tables selected by `mediatek,mt8196-hwv-scp-power-controller` and `mediatek,mt8196-hwv-hfrp-power-controller`. Special caps include modem power sequencing, external buck isolation, RTFF generic/PCIe PHY types, always-on, keep-default-off, SRAM isolation, inverted SRAM PDN, and skip-reset behavior.

Control flow: direct entries use the generic direct MTCMOS path in `mtk-pm-domains.c`; HWV entries use the hardware-voter path with SET/CLR/DONE/EN/STA offsets and IRQ-safe genpd callbacks. RTFF type changes save/restore handling in power-on/off sequencing.

State and persistence behavior: static table only; runtime state is SPM status/control, RTFF save flags, external buck isolation bits, and HWV vote registers.

Dependencies and integration points: requires MT8196 binding IDs, access-controller phandles, secure monitor support for infra power control where caps require it, and DT compatibles selecting direct vs HWV controller data.

Risks: this is the most timing-sensitive table in the group. RTFF save/restore, modem sequence, HW voter command ack, and external buck isolation all have ordering constraints. Wrong compatible or ID can route a domain to the wrong control type. Some domains lack explicit status fields in the extraction region and rely on table defaults/macros, so changes need full-file review.

Test signals: verify all three MT8196 compatibles independently. Exercise modem, USB/DP, PCIe, ADSP, display dormant, MM infra, video, and CSI/DSI domains; include suspend/resume and secure-monitor failure paths.
