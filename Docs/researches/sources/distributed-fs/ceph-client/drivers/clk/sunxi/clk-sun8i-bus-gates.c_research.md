# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-bus-gates.c

Registers Sun8i H3/A83T bus gate clocks whose parent depends on the clock index range. It maps DT `clock-indices` into sparse onecell outputs and chooses AHB1, AHB2, APB1, or APB2 parents.

`sun8i_h3_bus_gates_init()` maps the gate register block, resolves the four named parents from `clock-names`, allocates a `clk_onecell_data` sized to the largest listed index, iterates each `clock-indices` value, reads the corresponding output name, selects the parent by index ranges/special cases, computes register word and bit, and registers each gate with a shared spinlock. Two `CLK_OF_DECLARE()` entries bind H3 and A83T compatibles to the same setup.

Gate state persists in the bus gate registers. Provider arrays are sparse and indexed by DT clock IDs. There is no teardown for early OF registration. It depends on DT properties `clock-names`, `clock-indices`, and `clock-output-names`; CCF gate helpers; and OF onecell lookup. Downstream bus/peripheral clocks rely on the index-to-parent routing policy.

Several early returns after mapping do not release the mapping, which is tolerable during boot but risky for error hygiene. Wrong index ranges silently assign the wrong bus parent. Test signals include each gate's parent name, enable bit toggling in the correct 32-bit bank, and peripheral probes across AHB/APB domains.
