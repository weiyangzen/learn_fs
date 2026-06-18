# sources/distributed-fs/ceph-client/drivers/clk/clk-en7523.c


### Purpose
`clk-en7523.c` provides clock and reset-controller support for Airoha/EcoNet EN7523, EN7581, and EN751221 SCU blocks. It exposes fixed-rate clocks computed from SCU strap/divider registers plus a PCIe reference clock gate and SoC-specific reset mappings.

### Important APIs, Types, And Functions
Clock descriptions use `struct en_clk_desc`, PCIe gates use `struct en_clk_gate`, reset state uses `struct en_rst_data`, and variant behavior is described by `struct en_clk_soc_data`. Important functions are `en7523_get_base_rate()`, `en7523_get_div()`, `en7523_register_clocks()`, `en7581_register_clocks()`, `en751221_register_clocks()`, `en7523_register_pcie_clk()`, PCIe prepare/enable callbacks, reset assert/deassert/status/xlate helpers, and `en7523_clk_probe()`.

### Control Flow, State, And Persistence
Probe selects variant match data, allocates onecell clock data, runs the variant `hw_init()`, then adds an OF provider. EN7523 maps two MMIO resources; EN7581 and EN751221 also lookup syscon regmaps. Base clocks are registered as fixed-rate clocks by reading base selectors and divider fields. PCIe clock registration may first disable/unprepare hardware, then later prepare/enable toggles refclk, PERST, and reset bits with documented delays. Reset registration maps DT reset IDs through per-SoC tables into bank/bit offsets and writes SCU reset registers.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform MMIO resources, syscon regmaps, reset-controller framework, DT clock/reset bindings for all variants, and early `arch_initcall()` registration. Risks include fixed-rate snapshots not tracking later SCU changes, direct PCIe reset sequencing in clock callbacks, sparse reset maps returning raw mapped IDs without sentinel validation, no provider cleanup path, and table/register drift across variants. This snapshot contains duplicated statements in a few helper/table areas, making compile tests important. Test signals include OF provider resolution, correct rates from straps/dividers, PCIe refclk/perst sequencing, reset assert/deassert/status for all banks, syscon lookup failure handling, EN751221 hardware-ID-dependent SPI rate, and boot ordering before PCIe consumers.
