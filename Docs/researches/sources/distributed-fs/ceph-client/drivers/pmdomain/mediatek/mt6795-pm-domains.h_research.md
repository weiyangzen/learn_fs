# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6795-pm-domains.h

Purpose: MT6795 domain description for the generic SCPSYS driver.

Important data: domains are `vdec`, `venc`, `isp`, `mm`, `mjc`, `audio`, `mfg_async`, `mfg_2d`, and `mfg`. It declares a bus-protection block list containing infra access. `mm` and `mfg` include bus-protection configuration; the rest are mostly direct SPM control plus SRAM masks.

Control flow: the table is referenced by `mt6795_scpsys_data`; probe in `mtk-pm-domains.c` selects it for `mediatek,mt6795-power-controller`. The generic direct-control path handles regulators/clocks from DT, SPM on/off bits, SRAM enable/disable, and bus-protection set/clear.

State and persistence behavior: static SoC data only. Runtime state is SPM status and bus-protect register state.

Dependencies and integration points: depends on `dt-bindings/power/mt6795-power.h`, shared SPM constants, and an infra regmap/access-controller entry. Display, video, image, audio, and GPU consumers bind by DT power-domain ID.

Risks: MediaTek GPU hierarchy is split across async/2D/mfg islands; missing subdomain modeling in DT can allow consumers to power a child while a required parent is off. Bus protection on `mm` and `mfg` is the main integration risk.

Test signals: verify every table ID can be instantiated from DT, multimedia and GPU domains power-cycle without bus-protect timeouts, and no default-off warning appears unexpectedly.
