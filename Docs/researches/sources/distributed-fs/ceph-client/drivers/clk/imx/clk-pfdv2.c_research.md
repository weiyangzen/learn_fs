# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pfdv2.c

## Purpose
Implements second-generation i.MX PFD clocks with explicit gate and valid bits, used by newer platforms such as i.MX8ULP.

## Important APIs, Types, And Functions
`struct clk_pfdv2` stores register, gate bit, valid bit, and fraction offset. Main operations are `clk_pfdv2_enable()`, `clk_pfdv2_disable()`, `clk_pfdv2_recalc_rate()`, `clk_pfdv2_determine_rate()`, `clk_pfdv2_set_rate()`, and `clk_pfdv2_is_enabled()`. `imx_clk_hw_pfdv2()` exports the factory and sets flags based on `enum imx_pfdv2_type`.

## Control Flow
Enable clears the gate bit under `pfd_lock` and polls the valid bit. Disable sets the gate bit. Recalc reads the fraction and returns zero for invalid fraction zero. Determine searches candidate parent rates 480 MHz, 528 MHz, and the current best parent, clamps fraction to 12..35, and picks the closest result. Set-rate disables hardware-enabled PFDs first because the hardware cannot change rate while enabled, then writes the fraction.

## State And Persistence Behavior
State is in hardware gate/valid/fraction fields. There is no explicit suspend state. A global spinlock serializes RMW operations across PFDv2 clocks.

## Dependencies And Integration Points
Used by CGC/PFD code in i.MX8ULP. Depends on `readl_poll_timeout()`, common clock framework, and i.MX clock type definitions.

## Risks
Set-rate may disable a PFD that was enabled by hardware but has no software consumer count; consumers relying on boot defaults must be checked. Parent-rate search has hard-coded common rates. Valid-bit timeout is only 1 ms.

## Test Signals
Assigned-clock changes on i.MX8ULP SPLL/PLL4 PFDs, valid-bit timeout injection, consumers sourced by PFDv2 outputs, and concurrent rate changes across multiple PFDs.
