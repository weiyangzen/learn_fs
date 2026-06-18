## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3670.c

### Purpose
`clk-hi3670.c` describes the HiSilicon Hi3670 clock topology and binds it to device-tree CRG, PCTRL, PMU, SCTRL, IOMCU, MEDIA1, and MEDIA2 clock-controller nodes. It is mostly declarative: fixed sources, fixed factors, gates, separated gates, muxes, and dividers are registered through the shared Hisilicon clock helpers.

### Important APIs, Types, And Functions
The file consumes `struct hisi_fixed_rate_clock`, `struct hisi_fixed_factor_clock`, `struct hisi_gate_clock`, `struct hisi_mux_clock`, and `struct hisi_divider_clock` from `clk.h`. The init functions `hi3670_clk_crgctrl_init()`, `hi3670_clk_pctrl_init()`, `hi3670_clk_pmuctrl_init()`, `hi3670_clk_sctrl_init()`, `hi3670_clk_iomcu_init()`, `hi3670_clk_media1_init()`, and `hi3670_clk_media2_init()` allocate onecell providers and register each table. `hi3670_clk_probe()` dispatches the matching init function from `of_device_get_match_data()`.

### Control Flow
At `core_initcall`, a platform driver is registered. Probe matches the compatible string, calls the corresponding init routine, maps the controller registers via `hisi_clk_init()`, and registers the clocks in dependency order: fixed sources first, then gates, muxes, factors, and dividers. Each controller has an independent onecell provider.

### State, Persistence, And Dependencies
Runtime state lives in common clock framework objects and MMIO registers. Parent names and clock IDs must align with `dt-bindings/clock/hi3670-clock.h` and device-tree consumers. Register writes persist only in hardware clock-control registers.

### Integration Points
The driver integrates with OF platform probing, `of_clk_src_onecell_get`, and the shared Hisilicon helpers in `clk.c`, `clkgate-separated.c`, and `clkdivider-hi6220.c`-style register helpers. Consumers request clocks by the Hi3670 binding IDs.

### Risks
The large table surface is sensitive to ID, parent-name, offset, bit, and `CLK_*_HIWORD_MASK` mistakes. Missing unregister/error unwinding means partial registration failures are logged but not deeply recovered. Many mux parent arrays intentionally include `clk_invalid`; consumers must avoid selecting invalid parents.

### Test Signals
Boot on Hi3670 DT should show the `hi3670-clk` provider for every compatible. Useful checks include `/sys/kernel/debug/clk/clk_summary`, enabling MMC/UFS/PCIe/display/media/IOMCU clocks, rate changes on mux/divider clocks, and no missing-provider errors in device probe logs.
