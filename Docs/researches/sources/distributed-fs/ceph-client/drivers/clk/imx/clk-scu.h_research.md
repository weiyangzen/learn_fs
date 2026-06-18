# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-scu.h

## Purpose
Declares the SCU clock integration API used by i.MX8 SCFW clock drivers and LPCG helpers.

## Important APIs, Types, And Functions
Defines GPR clock flags `IMX_SCU_GPR_CLK_GATE`, `IMX_SCU_GPR_CLK_DIV`, and `IMX_SCU_GPR_CLK_MUX`; `struct imx_clk_scu_rsrc_table`; extern declarations for `imx_scu_clks`, LPCG PM ops, and SoC resource tables; and prototypes for SCU module init/exit, SCU provider init, phandle lookup, SCU clock allocation, direct SCU clock registration, unregister, LPCG registration, and GPR clock registration.

Inline helpers wrap the generic constructors: `imx_clk_scu()`, `imx_clk_scu2()`, `imx_clk_lpcg_scu_dev()`, `imx_clk_lpcg_scu()`, `imx_clk_gate_gpr_scu()`, `imx_clk_divider_gpr_scu()`, and `imx_clk_mux_gpr_scu()`.

## Control Flow
No executable control flow beyond inline wrappers that pass standard flag/parent/count arguments into implementation functions.

## State And Persistence Behavior
The header declares shared state but does not allocate it. Runtime state is implemented in `clk-scu.c` and `clk-lpcg-scu.c`.

## Dependencies And Integration Points
Depends on SCU firmware types from `linux/firmware/imx/sci.h` and OF declarations. It is included by SCU platform clock files, LPCG drivers, and resource-table files.

## Risks
Inline wrappers encode important flag combinations. Passing a stack parent pointer is safe only because registration consumes names immediately as expected by the clock framework. Changing return semantics or wrappers affects all SCU-based clock declarations.

## Test Signals
Compile all SCU clock users, verify wrappers create gate/divider/mux behavior, and run two-cell phandle lookup tests on i.MX8QXP/QM/DXL platforms.
