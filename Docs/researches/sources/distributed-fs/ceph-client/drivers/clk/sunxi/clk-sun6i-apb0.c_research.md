# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0.c

Provides the Allwinner A31 APB0 divider clock. APB0 has a two-bit divider field whose first two encodings both mean divide-by-2, so it cannot use a plain power-of-two divider.

`sun6i_a31_apb0_divs` maps register values 0 and 1 to divisor 2, value 2 to 4, and value 3 to 8. `sun6i_a31_apb0_clk_probe()` maps the register, obtains the first parent name, reads an optional output name, registers a divider-table clock with `clk_register_divider_table()`, and adds a simple OF provider.

Persistent state is the two-bit divider field in the mapped APB0 register. Allocations and mappings are devm-managed, while the registered CCF clock persists for the built-in platform driver's lifetime. The driver uses platform-device probing, OF clock parent naming, CCF divider-table helpers, and compatible `allwinner,sun6i-a31-apb0-clk`. APB0 gate drivers and low-power peripherals consume this clock as their parent.

The DT node must have a parent and valid resource. The non-linear divider table is the important correctness contract. Test signals include reading the rounded APB0 rate for each encoding, peripheral bus stability after rate changes, and absence of `-EINVAL`/`PTR_ERR` probe failures.
