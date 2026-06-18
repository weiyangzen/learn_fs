# sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-sai.c


### Purpose
`clk-fsl-sai.c` exposes Freescale/NXP SAI bit clock, and on i.MX8MQ also MCLK, as generic CCF composite clocks backed by SAI divider and gate registers.

### Important APIs, Types, And Functions
`struct fsl_sai_data` records the register offset and whether MCLK exists. `struct fsl_sai_clk` stores divider/gate subcomponents, registered clock HW pointers, and a shared spinlock. Important functions are `fsl_sai_of_clk_get()`, `fsl_sai_clk_register()`, and `fsl_sai_clk_probe()`. Variant data supports `fsl,vf610-sai-clock` and `fsl,imx8mq-sai-clock`.

### Control Flow, State, And Persistence
Probe allocates state, maps the SAI resource, optionally enables a `bus` clock with devm, initializes the spinlock, registers BCLK as a composite of divider and gate, conditionally registers MCLK, then installs a custom OF provider that returns BCLK for no args or arg 0 and MCLK for arg 1 when supported. Registration writes a direction bit to the divider/control register, builds a full OF-node-derived clock name, and registers a rate-gated composite using `clk_divider_ops` and `clk_gate_ops`. Persistent state is SAI gate/divider/direction register state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include SAI MMIO layout, optional bus clock, CCF composite/divider/gate helpers, OF clock specifier conventions, and variant-specific offset differences. Risks include writing `dir_bit` as a whole register value rather than read-modify-write, no validation of parent clock existence beyond parent-data index, shared register races if external SAI driver manipulates the same registers, and MCLK access on variants without MCLK. Test signals include BCLK-only VF610 behavior, BCLK/MCLK i.MX8MQ behavior, OF arg validation, divider rate changes under `CLK_SET_RATE_GATE`, gate enable/disable, optional bus-clock failure, and register direction programming.
