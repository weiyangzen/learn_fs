# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx95-blk-ctl.c

## Purpose
Implements block-control clock providers for i.MX95 and i.MX94 subsystem CSR blocks, including VPU, camera, LVDS/display, NETC mix, and HSIO. It registers gate, divider, and mux clocks from per-compatible data tables and restores selected CSR state across runtime/system suspend.

## Important APIs, Types, And Functions
`struct imx95_blk_ctl` stores device state, APB clock, base address, spinlock, saved register, and matched data. `struct imx95_blk_ctl_clk_dev_data` describes each clock's name, parents, register, bit field, type, and flags. `struct imx95_blk_ctl_dev_data` groups clock data and PM behavior. `imx95_bc_probe()` registers clocks with `clk_hw_register_mux()`, `clk_hw_register_divider()`, or `clk_hw_register_gate()`. PM handlers are `imx95_bc_runtime_suspend()`, `imx95_bc_runtime_resume()`, `imx95_bc_suspend()`, and `imx95_bc_resume()`.

## Control Flow
Probe allocates state, maps MMIO, gets and enables the APB clock, obtains match data, optionally enables runtime PM, allocates onecell data, iterates clock table entries, registers the provider, populates child devices, and for runtime-PM-enabled blocks autosuspends by disabling APB. If no match data is present, the node is treated as a parent container and only child devices are populated.

## State And Persistence Behavior
Clock bits live in subsystem CSR registers. Linux stores one saved register value at `clk_reg_offset` for PM restore. Runtime-enabled blocks disable the APB clock after probe and restore CSR clock state on resume.

## Dependencies And Integration Points
Depends on i.MX94/i.MX95 clock binding IDs, common clock framework, runtime PM, OF platform population, APB clock provider, and subsystem consumers such as VPU, camera, display, LVDS, NETC, and HSIO drivers.

## Risks
Only one register is saved per block, so tables must keep `clk_reg_offset` aligned with all relevant state. Probe currently returns early on missing match data after enabling APB, which is acceptable for populated containers but worth reviewing for power behavior. Gate polarity flags such as `CLK_GATE_SET_TO_DISABLE` must match hardware.

## Test Signals
Probe each compatible, verify clock provider cells, toggle VPU/camera/LVDS/display/NETC/HSIO consumers, check runtime suspend/resume register restore, and test system sleep with blocks both active and runtime-suspended.
