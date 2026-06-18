## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_clk_div.c

### Purpose

`mcde_clk_div.c` registers two internal MCDE clock-divider providers for FIFO A and FIFO B. These clocks let the display path request a DPI pixel clock through common-clock APIs while programming MCDE FIFO control registers.

### Important APIs, types, and functions

`struct mcde_clk_div` stores a `clk_hw`, MCDE pointer, register offset, and cached divider bits. `mcde_clk_div_ops` implements `.enable`, `.recalc_rate`, `.determine_rate`, and `.set_rate`. The exported entry point is `mcde_init_clock_divider()`, which registers `fifoa` and `fifob` clocks and stores them in `struct mcde`.

### Control flow

Rate determination scans possible dividers and optionally asks the parent to round its rate. `set_rate()` computes and caches CRX1 divider bits without touching hardware, which allows rate selection before the MCDE power domain is accessible. `enable()` locks `fifo_crx1_lock`, selects the LCD PLL parent, marks internal clocking, applies cached divider bits, and writes the FIFO A/B CR1 register. `recalc_rate()` returns a default divide-by-two when EPOD is off because registers cannot be read.

### State and persistence behavior

The divider caches desired register bits in `cr_div`. Hardware state is persisted in MCDE `CRA1`/`CRB1` clock-select, bypass, and divider fields while the EPOD power domain is enabled. The shared spinlock protects register read-modify-write with other display code.

### Dependencies

It depends on Linux common-clock provider APIs, regulator state checks, MMIO accessors, and MCDE register definitions from `mcde_display_regs.h`.

### Integration points

`mcde_display_init()` calls `mcde_init_clock_divider()`. DPI enable code uses `clk_round_rate()`, `clk_set_rate()`, and `clk_prepare_enable()` on `mcde->fifoa_clk`.

### Risks

Only the PLL72/LCD parent is implemented despite comments about other parents. Divider encoding is unusual: bypass for divide-by-one, zero field meaning divide-by-two. Reading registers while EPOD is disabled is avoided, so stale cached state must be trusted across power cycles.

### Test signals

Test with DPI panels: requested pixel clock close to mode clock, FIFO A clock enable/disable across modesets, suspend/resume after EPOD power loss, and lockdep coverage around concurrent CR1 updates.
