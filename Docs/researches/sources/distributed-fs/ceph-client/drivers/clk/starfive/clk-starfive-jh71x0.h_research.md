# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.h

## Purpose
This header defines the shared JH71x0 clock register format, declarative table macros, and common private structures used by StarFive clock domain drivers.

## Important APIs, Types, And Functions
It defines register masks for enable, invert, mux, integer divider, and fractional divider fields. `struct jh71x0_clk_data` is the compact table entry used by SoC files. Macros such as `JH71X0_GATE`, `JH71X0__DIV`, `JH71X0_GDIV`, `JH71X0_FDIV`, `JH71X0__MUX`, `JH71X0_GMUX`, `JH71X0_MDIV`, `JH71X0__GMD`, and `JH71X0__INV` encode clock capabilities into `max`. `struct jh71x0_clk_priv` stores shared runtime state.

## Control Flow
The header itself has no flow. Its macro output drives `starfive_jh71x0_clk_ops()` in the implementation file and parent resolution loops in each SoC/domain driver.

## State And Persistence
No state is stored by the header, but it defines the state layout used by all domain drivers: MMIO base, RMW lock, optional original CPU-root clock, PLL notifier, fallback PLL hardware, and one `jh71x0_clk` per register.

## Dependencies And Integration Points
It integrates all StarFive JH71x0 clock drivers with the Linux common clock framework. The flexible array uses `__counted_by(num_reg)`.

## Risks
The encoded `max` field has dual meaning: capability bits and maximum divider. Mistakes in macros or table values can select incorrect ops or divider limits. Parent arrays are fixed at four entries, so hardware with more parents would need structural changes.

## Test Signals
Build-time coverage should compile all macro users. Runtime tests should check that each macro family maps to expected operations and that max divider limits are enforced.
