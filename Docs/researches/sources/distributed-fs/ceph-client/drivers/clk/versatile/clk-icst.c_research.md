<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.c

## Purpose

`clk-icst.c` wraps ARM ICST307/ICST525 VCO clock generators in the Linux common clock framework. It supports normal Versatile-style registers and several Integrator/AP and Integrator/CP board-specific crippled encodings.

## Important APIs, Types, And Functions

`struct clk_icst` stores CCF hardware, regmap, VCO/lock offsets, cloned `icst_params`, cached rate, and `enum icst_control_type`. `vco_get()` decodes register fields for standard ICST, Integrator AP CM/SYS/PCI, and Integrator CP core/mem variants. `vco_set()` unlocks with `0xA05F`, updates masked VCO bits, and relocks. CCF ops recalc, round/determine, and set rates. Exported helpers are `icst_clk_setup()` and `icst_clk_register()`.

## Control Flow

For DT syscon clocks, `of_syscon_icst_setup()` gets the parent syscon regmap, reads `reg` or `vco-offset` plus `lock-offset`, selects parameter/control type by compatible string, registers the clock, and adds an OF provider. Legacy callers can pass MMIO base directly through `icst_clk_register()`.

## State And Persistence Behavior

Hardware VCO settings persist in syscon registers. The driver clones mutable parameter tables because parent-rate changes can update `params->ref`. It caches the last computed rate but always decodes hardware in recalc.

## Dependencies And Integration Points

It depends on `icst.c` math helpers, regmap MMIO/syscon, CCF, DT early clock declarations, and `clk-icst.h`. It is used by Integrator, Versatile, RealView-style board clocks and IM-PD1.

## Risks And Test Signals

Board-specific encodings are easy to break, especially AP PCI's 25/33 MHz bit and hardwired R/S values. A likely bug is the AP SYS max clamp assigning 5 MHz when the comment says 50 MHz. Test rate set/recalc for every compatible, lock-register writes, parent-rate changes, and DT syscon child probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.c -->
