# sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.h

Purpose: defines the descriptor contract for DaVinci LPSC clocks, clkdev alias arrays, quirk flags, registration APIs, and device-specific PSC init data.

Important APIs/types/functions: flags are `LPSC_ALWAYS_ENABLED`, `LPSC_SET_RATE_PARENT`, `LPSC_FORCE`, and `LPSC_LOCAL_RESET`. `davinci_lpsc_clkdev_info` plus `LPSC_CLKDEV*()` macros describe legacy lookup aliases. `davinci_lpsc_clk_info` describes each module clock. `LPSC()` builds table entries. `davinci_psc_init_data` carries parent bulk clock requirements and a `psc_init()` callback.

Control flow: no executable flow; macros expand static descriptor tables consumed by `psc.c`.

State and persistence: none directly. Descriptor tables created with this header determine hardware state transitions and registered clock topology at runtime.

Dependencies and integration points: depends on common clock provider types and is shared by generic PSC code and DA850 descriptors. External init data symbols are referenced by the platform driver match tables.

Risks: macro-generated names are stringified, so C identifier changes alter ABI-visible clock names. Incorrect `md`/`pd` IDs or flags can affect unrelated modules or power domains. Local-reset support is opt-in by flag and must match hardware capability.

Test signals: compile coverage of descriptor tables, boot-time clock summary inspection, reset-controller phandle tests for local-reset entries, and legacy clkdev resolution for generated alias arrays.
