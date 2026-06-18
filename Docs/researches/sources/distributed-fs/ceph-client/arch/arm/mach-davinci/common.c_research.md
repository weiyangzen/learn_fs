# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/common.c

Purpose: centralizes Davinci SoC initialization from a `davinci_soc_info` descriptor.

Important APIs/types/functions: global exported `davinci_soc_info`; `davinci_init_id()` decodes JTAG ID; `davinci_common_init()` copies SoC info, maps IO, initializes pinmux, and stores SRAM metadata; `davinci_init_late()` runs late board/device quirks.

Control flow: SoC-specific init such as `da850_init()` calls `davinci_common_init()` with IO descriptors, ID table, pinmux base/table, and SRAM data. Common init maps IO, identifies CPU variant, initializes pinmux if enabled, and exposes shared data to other Davinci helpers.

State and persistence: `davinci_soc_info` is global and exported; mapped IO and pinmux state persist after init.

Dependencies and integration: integrates with ARM `iotable_init`, Davinci mux code, CPU type helpers, `pdata_quirks_init()`, and SoC-specific files.

Risks: incorrect ID tables or JTAG mapping can misidentify the SoC. Global state means only one SoC descriptor can be active and consumers assume it is initialized early.

Test signals: boot logs showing detected CPU, pinmux setup success, late pdata quirks, and legacy platform device registration.
