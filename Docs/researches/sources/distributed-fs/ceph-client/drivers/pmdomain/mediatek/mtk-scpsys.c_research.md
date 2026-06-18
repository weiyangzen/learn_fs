# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-scpsys.c

Purpose: legacy MediaTek SCPSYS generic PM-domain driver for older compatibles (`mt2701`, `mt2712`, `mt6797`, `mt7622`, `mt7623a`, `mt8173`).

Important APIs, types, and functions: `struct scp_domain_data` describes domain name, status mask, control offset, SRAM masks, bus-protect mask, clock IDs, and caps. `struct scp_domain`, `struct scp`, `struct scp_subdomain`, and `struct scp_soc_data` hold runtime/domain topology. `scpsys_power_on/off()` implement legacy SPM sequencing using MMIO `readl/writel`, clocks, regulators, SRAM polling, and `mtk_infracfg_*_bus_protection()`. `init_scp()` maps registers, gets infracfg and clocks/regulators, and builds genpd entries. `mtk_register_power_domains()` powers all domains on for sync, initializes genpd, and publishes onecell provider.

Control flow: platform probe selects legacy SoC data, initializes all table domains, registers providers, then adds static subdomain relationships from `scp_subdomain` arrays. Power-on enables regulator and clocks, sets PWR_ON/PWR_ON_2ND, waits for dual status, clears clock-disable/isolation, asserts reset, enables SRAM, and clears bus protection. Power-off sets bus protection, disables SRAM, asserts isolation/clock-disable/reset, clears power bits, waits off, disables clocks/regulator.

State and persistence behavior: no persisted state. Runtime state includes MMIO SPM registers, infracfg bus-protect bits, clock/regulator state, and genpd status. Domains are all powered on during registration to synchronize hardware and software.

Dependencies and integration points: depends on older DT compatibles, `infracfg` phandle, MediaTek infracfg bus-protect helpers, fixed clock-name enum (`mm`, `mfg`, `venc`, etc.), optional per-domain regulators named after domain names, and legacy power binding headers.

Risks: no remove path is registered because these domains are effectively permanent after provider registration. `scpsys_domain_is_on()` returns `-EINVAL` during transitional mismatched status, and polling treats positive/zero states carefully; changes can break transition detection. The table is duplicated conceptually with newer generic headers for MT8173-like SoCs, so fixes may need both paths.

Test signals: boot each legacy compatible, verify all domains register and subdomains attach, run display/GPU/video/network/USB workloads, and suspend/resume while watching for infracfg bus-protect or SRAM ack timeouts.
