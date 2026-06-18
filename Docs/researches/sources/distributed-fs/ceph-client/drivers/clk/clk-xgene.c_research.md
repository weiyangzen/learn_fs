# sources/distributed-fs/ceph-client/drivers/clk/clk-xgene.c

## Purpose
`clk-xgene.c` provides boot-time CCF support for AppliedMicro X-Gene SoC clocks. It covers SOC and PCP PLL clocks, PMD fractional scale clocks, and IP/device clocks with optional enable/reset CSR control and optional divider registers. All clocks are registered from device tree using `CLK_OF_DECLARE()`.

## Important APIs, Types, And Functions
PLL support centers on `struct xgene_clk_pll`, `xgene_clk_pll_is_enabled()`, `xgene_clk_pll_recalc_rate()`, `xgene_register_clk_pll()`, `xgene_pllclk_version()`, and `xgene_pllclk_init()`. PMD scaling uses `struct xgene_clk_pmd`, `xgene_clk_pmd_recalc_rate()`, `xgene_clk_pmd_determine_rate()`, `xgene_clk_pmd_set_rate()`, `xgene_register_clk_pmd()`, and `xgene_pmdclk_init()`. Device clocks use `struct xgene_dev_parameters`, `struct xgene_clk`, `xgene_clk_enable()`, `xgene_clk_disable()`, `xgene_clk_is_enabled()`, `xgene_clk_recalc_rate()`, `xgene_clk_set_rate()`, `xgene_clk_determine_rate()`, `xgene_register_clk()`, and `xgene_devclk_init()`.

Register field macros decode old and v2 PLL formats (`N_DIV_RD`, `SC_N_DIV_RD`, `SC_OUTDIV2`, `CLKR_RD`, `CLKOD_RD`, `CLKF_RD`, `REGSPEC_RESET_F1_MASK`). Device-tree compatibles bind SOC PLL, PCP PLL, v2 PLL variants, PMD clocks, and generic device clocks.

## Control Flow
PLL OF init maps the register resource, determines whether the compatible uses version 1 or version 2 layout, registers a read-only PLL clock with one parent, adds an OF clock provider, and registers a clkdev alias. PLL recalc reads hardware fields and computes PCP or SOC output frequency; version 2 uses a different feedback and output divider encoding.

PMD init skips disabled nodes, maps its CSR, sets an inverted 3-bit scale with denominator 8, registers a clock, and adds provider/clkdev entries. Its rate operations compute `parent_rate * scale / denom`; `determine_rate` rounds up scale, and `set_rate` writes the encoded scale field under the shared lock.

Device clock init maps up to two register resources, distinguishing `div-reg` from CSR registers by resource name, loads optional properties for enable/reset offsets and masks plus divider offset/width/shift, registers the CCF clock, and adds an OF provider. Enable first sets the clock-enable mask then clears CSR reset; disable asserts reset before clearing the enable mask. Rate operations divide by a register field when a divider resource is present, otherwise pass through the parent rate.

## State And Persistence
Persistent state is memory-mapped SoC register content for PLL status/configuration, PMD scale fields, device clock enable masks, CSR reset masks, and device dividers. In memory, each registered clock stores mapped register pointers and property-derived offsets/masks. There is no dynamic remove path; mappings and allocated clock structures persist for the system lifetime. A global `clk_lock` serializes register updates for PLL/PMD/device paths that pass it.

## Dependencies And Integration Points
The driver uses early OF clock declaration, `of_iomap()`, `of_address_to_resource()`, CCF registration, clkdev lookup registration, and relaxed MMIO accessors. It depends on DTS resource names and properties to distinguish CSR and divider resources and to provide parent clocks. Consumers obtain clocks through OF providers or clkdev names from `clock-output-names`.

## Risks
Several registration helpers return `NULL` instead of an `ERR_PTR` on `clk_register()` failure, while callers check only `IS_ERR()`, so failures may be treated as success and passed to provider registration. Device clock divider recalc divides by the raw field without guarding against zero. `xgene_clk_set_rate()` returns the achieved rate despite the CCF `.set_rate` contract expecting 0 or a negative errno. Divider calculation rounds down and masks without validating overflow against field width, which can silently program an unintended divisor. OF resource-name assumptions are fragile: anything not named `div-reg` is treated as CSR. MMIO mappings are generally not unmapped after successful boot-time registration, by design, but error cleanup must keep both mapped resources balanced.

## Test Signals
Tests should instantiate DT nodes for each compatible and verify `clk_summary` rates against known register snapshots for v1 SOC PLL, v1 PCP PLL, v2 SOC/PCP PLL, PMD inverted scaling, pass-through device clocks, and divided device clocks. Enable/disable tests should inspect CSR order: enable mask set before reset deassertion, reset assertion before enable clear. Negative tests should cover zero divider fields, missing or misnamed resources, disabled PMD/device nodes, divider field overflow, and simulated `clk_register()` failure so the NULL-versus-ERR_PTR path is caught.
