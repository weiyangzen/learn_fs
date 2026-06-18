# sources/distributed-fs/ceph-client/include/linux/clk/clk-conf.h

Purpose: This header exposes the Devicetree clock-default application helper used to apply assigned-clock parents and rates from firmware nodes.

Important APIs/types/functions: The only API is `of_clk_set_defaults(struct device_node *node, bool clk_supplier)`, with a stub returning `0` when either OF or Common Clock Framework support is disabled.

Control flow: Clock providers or consumers call the helper during probe or early initialization. The real implementation reads clock default properties from the node and applies parent/rate assignments, while the stub is a no-op.

State and persistence behavior: The header stores no state. The real helper mutates clock framework state and hardware rates/parents based on DT configuration.

Dependencies and integration points: It includes `<linux/types.h>`, forward-declares `struct device_node`, and integrates with OF clock parsing, CCF rate/parent operations, and platform driver probe ordering.

Risks: Calling with the wrong `clk_supplier` role can apply defaults at the wrong time. Disabled configs returning success can hide absent default processing. DT defaults can conflict with consumer rate constraints or exclusive-rate users.

Test signals: DT boot tests with `assigned-clocks`, `assigned-clock-parents`, and `assigned-clock-rates`, probe-order tests for suppliers and consumers, and clock tree inspection after probe validate behavior.
