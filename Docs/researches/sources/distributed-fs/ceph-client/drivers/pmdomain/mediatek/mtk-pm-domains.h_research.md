# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-pm-domains.h

Purpose: shared data contract and register/macro definitions for the generic MediaTek SCPSYS PM-domain driver and SoC tables.

Important APIs and types: capability flags include `ACTIVE_WAKEUP`, `FWAIT_SRAM`, `SRAM_ISO`, `KEEP_DEFAULT_OFF`, `DOMAIN_SUPPLY`, `ALWAYS_ON`, `EXT_BUCK_ISO`, `HAS_INFRA_NAO`, `STRICT_BUS_PROTECTION`, `SRAM_PDN_INVERTED`, `MODEM_PWRSEQ`, `SKIP_RESET_B`, and `INFRA_PWR_CTL`. It defines common SPM offsets/status masks, bus-protection flags and blocks, helper macros such as `BUS_PROT_WR`, `BUS_PROT_UPDATE`, `BUS_PROT_WR_IGN`, and `BUS_PROT_INFRA_UPDATE_TOPAXI`, RTFF types, MTCMOS controller types, `struct scpsys_domain_data`, `struct scpsys_hwv_domain_data`, and `struct scpsys_soc_data`.

Control flow: SoC headers instantiate the structs/macros; `mtk-pm-domains.c` interprets them to decide direct vs hardware-voter callbacks, power sequencing, SRAM handling, bus-protection polling, supplies, and special RTFF/modem/infra behavior.

State and persistence behavior: no runtime state in the header. It defines the shape of static tables and bit meanings that control hardware state transitions.

Dependencies and integration points: depends on kernel bit macros and constants included by C files. It is the ABI between per-SoC table headers and the generic driver, so field order/semantics must remain synchronized with all table initializers.

Risks: adding a capability flag without updating `MTK_SCPD_CAPS()` consumers has no effect. `SPM_MAX_BUS_PROT_DATA` limits per-domain protection steps; larger sequences require increasing the constant and checking stack/static table size. Direct and HWV data share caps through a macro that switches on whether `data` or `hwv_data` is populated.

Test signals: all SoC table headers should compile with designated initializers; new flags should have targeted power-on/off tests. Static analysis can catch out-of-range bus-protection arrays and missing controller-type fields.
