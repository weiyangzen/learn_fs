# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-mx-sdhc-clkc.c

## Purpose

`meson-mx-sdhc-clkc.c` registers the clock controller embedded in the older Amlogic Meson MX SDHC block. It exposes a mux, divider, and four gate clocks derived from `MESON_SDHC_CLKC` so the SDHC host driver can use normal Linux clock APIs for module, TX, RX, and SD clocks.

## Important APIs, Types, And Functions

- `struct meson_mx_sdhc_clkc` stores clock framework objects: source mux, divider, and four gates.
- `meson_mx_sdhc_src_sel_parents` names four firmware clock inputs: `clkin0` through `clkin3`.
- `meson_mx_sdhc_div_table` lists hardware divider encodings, including non-linear divisors from 6 through 4096.
- `meson_mx_sdhc_clk_hw_register()` builds a named `clk_init_data` using `<dev_name>#<suffix>` and registers one clock hardware object with `devm_clk_hw_register()`.
- `meson_mx_sdhc_gate_clk_hw_register()` registers a gate whose parent is another `clk_hw` and stores an acquired `struct clk *` into a provided `clk_bulk_data` slot.
- `meson_mx_sdhc_register_clkc()` is the exported local API used by `meson-mx-sdhc-mmc.c`; it allocates state, registers mux/divider/gates against the SDHC MMIO base, and fills the four bulk clock slots.

## Control Flow And State

Registration is linear: allocate `clkc_data`, bind the mux to bits 17:16 of `MESON_SDHC_CLKC`, bind the divider to bits 11:0 with the divider table and mux parent, then register gate clocks on bits 15, 14, 13, and 12. The gate registration stores clocks in bulk indices 0 through 3, which the host driver later bulk-enables/disables. State is devm-managed and persists for the device lifetime.

## Dependencies And Integration Points

The file depends on the Linux clock framework, platform device/device helpers, and `meson-mx-sdhc.h` register definitions. Its sole external integration is `meson_mx_sdhc_register_clkc()`, which expects a mapped SDHC base address and a `clk_bulk_data` array sized by the caller.

## Risks And Edge Cases

- Clock names are limited to 32 bytes in a stack buffer; extremely long `dev_name()` values may be truncated.
- Bulk clock index meanings are positional and must match the host driver's expectations. The host uses `bulk_clks[1]` as `sd_clk`.
- The divider table is sparse and hardware-specific; unsupported rates depend on clock framework rounding.
- All clocks use `CLK_SET_RATE_PARENT`, so rate changes can propagate to parent clocks.

## Test Signals

Validation should confirm all five clock hardware nodes register, `clk_bulk_prepare_enable()` works for the four gates, the divider rounds expected SD rates, parent firmware clock names resolve from DT, gate bits toggle the expected `MESON_SDHC_CLKC` bits, and probe defers cleanly if parent clocks are missing.
