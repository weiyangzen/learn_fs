# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apmixedsys.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apmixedsys.c

### Purpose
`clk-mt8365-apmixedsys.c` registers MT8365 APMIXED PLLs and two USB/universal gates. It provides root PLLs for CPU, system, multimedia, audio, DSP, APU, storage, and USB clock trees.

### Important APIs, Types, And Functions
The file defines `PLL_B`, `PLL`, PLL divider tables for ARM/MFG/DSP, the `plls` array, and `clk_mt8365_apmixed_probe()`. Probe uses `devm_platform_ioremap_resource()`, `mtk_devm_alloc_clk_data()`, `devm_clk_hw_register_gate()` for `univ_en` and `usb20_en`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`. It is registered with `builtin_platform_driver()`.

### Control Flow, State, And Persistence
As a built-in platform driver, it is available early. Probe maps registers, allocates clock data for all APMIXED IDs, registers two gates, registers PLLs, and adds the provider. Failure after PLL registration unregisters PLLs. Hardware PLL/gate registers persist clock state; devm handles mapped resources and gate objects.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include MT8365 clock bindings, topckgen factors expecting `univ_en`/`usb20_en`, CPUfreq/audio/DSP/APU consumers, and OF. Risks include early boot ordering, no custom remove path, PLL divider table accuracy, and USB parent naming. Test signals include boot provider availability, USB clock operation, PLL rate changes, topckgen parent resolution, and forced provider registration failure.
