# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-mmc.c

Registers Allwinner A80 MMC configuration clocks and a matching reset controller. The hardware exposes one 32-bit word per MMC channel, with a gate bit and reset bit in each word.

`struct sun9i_mmc_clk_data` owns the mapped base, parent clock, upstream reset, onecell clock data, reset controller, and spinlock. Reset ops assert/deassert bit 18 for each ID while temporarily enabling the parent clock. `sun9i_a80_mmc_config_clk_probe()` maps the resource, derives channel count from resource size divided by four, gets and deasserts the parent reset, registers one gate clock per word at bit 16, publishes an OF onecell provider, then registers reset-controller ops.

Per-channel gate and reset bits persist in MMIO. The parent reset is deasserted during probe and reasserted only on probe error. The reset controller and clock provider persist for the built-in driver's lifetime. It depends on platform resources, reset framework, CCF gates, `devm_clk_get()`, and OF reset-controller registration. MMC host drivers consume both the clock outputs and reset IDs.

Error cleanup unregisters `count` entries even if only a prefix was successfully registered, so sparse failure handling should be tested. Reset ops ignore `clk_prepare_enable()` failures. Test signals include MMC probe/reset behavior, gate bit toggling per channel, reset pulse timing, and provider/reset-controller registration in DT.
