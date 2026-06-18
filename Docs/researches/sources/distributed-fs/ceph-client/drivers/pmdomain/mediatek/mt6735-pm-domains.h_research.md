# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6735-pm-domains.h

Purpose: MT6735 SoC data table for the generic MediaTek SCPSYS PM-domain driver.

Important data: defines seven direct-control domains: `md1`, `conn`, `dis`, `mfg`, `isp`, `vde`, and `ven`. Each entry supplies status masks, control offsets, SRAM power-down and acknowledge masks where applicable, and status register offsets `SPM_PWR_STATUS`/`SPM_PWR_STATUS_2ND`.

Control flow: consumed by `mtk-pm-domains.c` through `mt6735_scpsys_data`. The generic driver indexes the table using DT child `reg` values from `dt-bindings/power/mt6735-power.h`, initializes matching `generic_pm_domain` instances, and applies the standard direct MTCMOS sequence.

State and persistence behavior: table only; no local state. The runtime state is represented by SPM status bits and SRAM ack fields.

Dependencies and integration points: depends on shared `mtk-pm-domains.h` constants and the MT6735 power binding. Bus protection is embedded in selected domain `bp_cfg` entries and uses the generic driver's legacy/new access-controller regmap lookup.

Risks: sparse or mismatched DT IDs can select an undefined or wrong domain. MD/connection/display/GPU bus protection masks are especially sensitive because failed ack polling blocks power transitions.

Test signals: boot with MT6735 power-controller DT should instantiate seven domains; power-cycle media, GPU, modem, and connectivity consumers while checking SPM status/ack transitions.
