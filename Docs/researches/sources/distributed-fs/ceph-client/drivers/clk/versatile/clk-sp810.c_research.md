<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-sp810.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-sp810.c

## Purpose

`clk-sp810.c` exposes the four ARM SP810 `TIMERCLKEN` muxes as CCF clocks. Each output selects between two parent clocks, typically REFCLK and TIMCLK.

## Important APIs, Types, And Functions

`struct clk_sp810` stores node, MMIO base, spinlock, and four `clk_sp810_timerclken` entries. `clk_sp810_timerclken_get_parent()` reads `SCCTRL`; `clk_sp810_timerclken_set_parent()` updates the per-channel select bit under lock. `clk_sp810_timerclken_of_get()` resolves one-cell DT clock specifiers.

## Control Flow

`CLK_OF_DECLARE()` runs setup for `arm,sp810`. It allocates state, reads two parent names, maps registers, registers four mux clocks named by instance/channel, optionally forces parent 1 for old DTs missing `assigned-clock-parents`, and adds an OF provider.

## State And Persistence Behavior

Parent selection persists in the SP810 `SCCTRL` register. Static `instance` only makes generated clock names unique. There is no teardown for the early provider.

## Dependencies And Integration Points

It depends on AMBA SP810 register definitions, OF address mapping, CCF mux semantics, and DT one-cell providers.

## Risks And Test Signals

Risks include missing parents, failed `of_iomap()` not being explicitly checked, legacy forced parent behavior changing timer rates, and only two valid parents. Test timer operation on Versatile Express, assigned-clock parent changes, and invalid clock cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-sp810.c -->
