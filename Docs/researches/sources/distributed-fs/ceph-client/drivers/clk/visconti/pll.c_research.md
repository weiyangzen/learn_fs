<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.c

## Purpose

`pll.c` implements common Toshiba Visconti programmable PLL CCF operations.

## Important APIs, Types, And Functions

`struct visconti_pll` stores CCF hardware, base address, lock, flags, copied rate table, count, and provider context. Helpers read current PLL fields, match register data back to known rates, choose supported rates, program PLL parameters, enable/disable PLLs with bypass and delays, and register PLLs. Public APIs are `visconti_init_pll()` and `visconti_register_plls()`.

## Control Flow

Enable selects config, enters bypass, writes default rate-table parameters, toggles `PLL_PLLEN` with 1 us and 40 us delays, then exits bypass. Set-rate only accepts exact rates present in the copied table. Recalc reads hardware parameters and returns the matching known rate or table default.

## State And Persistence Behavior

PLL state persists in MMIO registers. The driver copies rate tables into heap memory per PLL and stores provider references permanently. There is no unregister path for early clocks.

## Dependencies And Integration Points

It depends on CCF, raw MMIO, bitfield helpers, spinlocks, and `pll.h`. TMPV770x PLL setup consumes it.

## Risks And Test Signals

Risks include `WARN()` but no hard error when rate-table allocation fails, no lock-status polling, default-rate fallback hiding unknown hardware state, and exact-only set-rate behavior. Test enable/disable sequences on hardware, recalc before/after boot firmware configuration, and invalid rate rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.c -->
