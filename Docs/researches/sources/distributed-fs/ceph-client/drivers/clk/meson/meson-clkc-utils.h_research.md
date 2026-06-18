# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-clkc-utils.h

## Purpose
Defines the shared Meson clock-controller data structures, probe-helper prototypes, OF lookup callback, and macro helpers for common peripheral and composite clock declarations.

## Important APIs, Types, And Functions
`struct meson_clk_hw_data` contains the sparse `struct clk_hw **hws` array and its count. `struct meson_clkc_data` adds optional `init_regs`, `init_count`, and `hw_clks`. Public functions are `meson_clk_hw_get()`, `meson_clkc_syscon_probe()`, and `meson_clkc_mmio_probe()`. `MESON_PCLK` and `MESON_PCLK_RO` generate regmap-backed gate clocks with one parent. `MESON_COMP_SEL`, `MESON_COMP_DIV`, and `MESON_COMP_GATE` generate the mux, divider, and gate pieces of a common composite clock chain.

## Control Flow
The header itself has no runtime control flow. The macros expand at compile time into `struct clk_regmap` declarations wired to local parent arrays or previous macro-generated nodes. These declarations are later registered by the utility implementation.

## State And Persistence
Generated clocks persist state in regmap-backed hardware registers through offsets, shifts, masks, bit indexes, and flags supplied to macros. The structures are normally static data in SoC drivers and are not dynamically allocated by the macros.

## Dependencies And Integration Points
Includes OF-device and clock-provider headers and forward-declares `struct platform_device`. Macro users also need `clk-regmap.h` definitions in scope because generated objects use `struct clk_regmap_*_data` and regmap clock ops. The API is used across Meson clock driver files to reduce repeated gate/mux/divider declarations.

## Risks And Edge Cases
Macros create global symbols with names derived from arguments, so naming collisions are possible. `MESON_COMP_SEL` uses `ARRAY_SIZE(_pdata)`, which requires `_pdata` to be an actual array in scope, not a pointer. The generated composite pieces encode a fixed parent order: divider parent is `_prefix##_name##_sel`, gate parent is `_prefix##_name##_div`. Incorrect flags can propagate unwanted rate changes or prevent needed parent changes.

## Test Signals
Compile all macro users with sparse arrays and composite clocks enabled. Static review should verify parent arrays passed to `MESON_COMP_SEL` are arrays, gate bits match registers, and generated symbol names are referenced correctly from clock ID arrays. Runtime signals are successful clock registration and expected parent/divider/gate behavior through clk debugfs.
