# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-simple-gates.c

## Purpose
This legacy provider registers arrays of simple gate clocks from DT `clock-indices`/`clock-output-names` properties.

## Important APIs, Types, And Functions
Important functions are `sunxi_simple_gates_setup()`, `sunxi_simple_gates_init()`, protected variants for A10/A10s/A13/A20 AHB and A10 DRAM gates, and many `CLK_OF_DECLARE` compatible bindings.

## Control Flow
Early init maps the gate register block, reads the parent, allocates a onecell array sized by the largest index, registers one `clk_register_gate()` per listed index, optionally enables protected critical gates, and adds an OF provider.

## State And Persistence
State is gate bits in one or more 32-bit registers and the registered onecell provider. Protected gates are enabled during setup and left on.

## Dependencies And Integration Points
It depends on CCF, OF property parsing, OF address mapping, and shared spinlock. It integrates with many legacy bus-gate DT nodes across sun4i/sun5i/sun6i/sun7i/sun8i/sun9i.

## Risks
The code trusts DT property consistency. A bad largest index can undersize the array; wrong protected indices can disable SDRAM/DRAM outputs. Error cleanup releases the mapped resource only on early allocation failure.

## Test Signals
Test with legacy board boot, clock lookups for all gate IDs, protected SDRAM/DRAM clocks staying enabled, and peripheral gate enable/disable behavior.
