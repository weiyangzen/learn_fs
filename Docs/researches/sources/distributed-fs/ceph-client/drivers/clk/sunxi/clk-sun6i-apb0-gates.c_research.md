# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0-gates.c

Registers APB0 gate clocks for Allwinner A31 and A23 style PRCM clock blocks. It exposes onecell clock outputs at sparse bit positions selected by SoC-specific masks.

`struct gates_data` stores a 32-bit bitmap of valid gate bits. The OF match table binds A31 to mask `0x7f` and A23 to `0x5d`. `sun6i_a31_apb0_gates_clk_probe()` validates OF data, maps the register, gets the single parent name, allocates `clk_onecell_data`, sizes the clock array to the last set bit, then iterates `for_each_set_bit()` to read each `clock-output-names` entry and call `clk_register_gate()`.

State lives in the APB0 gate register and in devm-managed provider allocations. Registered clocks are indexed by hardware bit number, leaving holes for unsupported bits. There is no explicit remove path for the built-in platform driver. It depends on platform-device probing, OF match data, `devm_platform_ioremap_resource()`, `clk_register_gate()`, and `of_clk_src_onecell_get`. Consumers rely on DT clock specifier indices matching gate bit positions.

The driver warns but continues if an individual gate registration fails, so consumers may later receive error pointers or NULL holes. Missing `clock-output-names` entries are not checked per gate. Test signals are provider registration success, correct `clk_num`, expected gate bits toggling in PRCM registers, and peripheral probe success for APB0 consumers.
