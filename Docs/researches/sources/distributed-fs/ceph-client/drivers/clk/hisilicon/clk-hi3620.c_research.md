# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3620.c

Purpose: provides early OF clock initialization for Hi3620 system clocks and a separate MMC CIU clock provider with timing-programming behavior.

Important APIs/types/functions: top-level descriptor arrays define fixed rates, fixed factors, muxes, dividers, and separated gates for timers, UARTs, SPI, PWM, SD/MMC, display, video, GPIO, USB, and buses. `hi3620_clk_init()` registers the main provider via `CLK_OF_DECLARE`. MMC-specific types are `hisi_mmc_clock` and `clk_mmc`; ops include `mmc_clk_recalc_rate()`, `mmc_clk_determine_rate()`, `mmc_clk_set_timing()`, `mmc_clk_prepare()`, and `mmc_clk_set_rate()`.

Control flow: early clock init maps the clock controller through `hisi_clk_init()` and registers descriptor arrays. MMC init maps a pctrl node, allocates onecell data sized to the number of MMC descriptors, registers each MMC CIU clock, and adds an OF provider. MMC prepare sets a safe default timing; set-rate disables the clock, writes sample/drive/divider delay fields, then re-enables it under a spinlock.

State and persistence: MMIO registers hold mux/divider/gate and MMC timing state. Allocated `clk_mmc` objects persist for the life of the boot.

Dependencies and integration points: depends on shared Hisilicon helpers, OF early init, DT binding IDs, and pctrl-compatible MMC clock node.

Risks: `mmc_clk_determine_rate()` sets a rate but returns `-EINVAL`, which is unusual and may prevent normal rate negotiation. MMC provider allocates `clk_data->clks` with length equal to descriptor count while indexing by binding IDs, which is only safe if IDs are dense from zero. Missing cleanup on partial init is typical early-boot code but leaks on failure.

Test signals: boot Hi3620 DT, validate timer/UART/MMC/display clock IDs, run MMC at 13/25/50/100/180 MHz, confirm timing fields, and watch for determine-rate failures in MMC consumers.
