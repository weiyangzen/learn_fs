# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-pll.c

## Purpose
Implements the reusable Broadcom iProc PLL and PLL-derived channel clock provider. It programs PLL VCO parameters, reset and power sequencing, lock polling, optional ASIU top-level gating, optional software override, and leaf clock dividers, then exposes the PLL and its channels through the Linux common clock framework and a device-tree onecell provider.

## Important APIs, Types, And Functions
Core private types are `struct iproc_pll` for mapped status/control/power/ASIU bases and PLL metadata, and `struct iproc_clk` for a `clk_hw` tied to either the PLL root or one leaf channel. `iproc_pll_clk_setup` is the exported setup entry used by SoC files. PLL operations include `pll_calc_param`, `pll_set_rate`, `iproc_pll_recalc_rate`, `iproc_pll_determine_rate`, and `iproc_pll_set_rate`. Channel operations include `iproc_clk_enable`, `iproc_clk_disable`, `iproc_clk_recalc_rate`, `iproc_clk_determine_rate`, and `iproc_clk_set_rate`.

## Control Flow
Setup allocates the PLL, onecell data, and an array of iProc clocks, maps control plus optional power, ASIU, and split status resources, registers output 0 as the PLL root, then registers remaining outputs as channel clocks parented by the PLL. Rate changes either compute VCO parameters at runtime or select an exact table entry, enable power/ASIU paths, skip disruptive reset when only fractional NDIV changes, otherwise assert reset, program user mode, VCO band bits, NDIV, fractional NDIV, PDIV, release reset with Ki/Kp/Ka values, and poll lock.

## State And Persistence
Persistent runtime state is the registered `clk_hw` graph, mapped MMIO bases, optional VCO parameter table pointer, and hardware register contents for power, reset, NDIV, PDIV, channel enable/hold, and MDIV. The driver keeps little mutable software state after setup; hardware is the source for recalc and enable checks.

## Dependencies And Integration Points
Depends on iProc control descriptors from `clk-iproc.h`, SoC-specific data in files such as `clk-ns2.c`, `clk-nsp.c`, and `clk-sr.c`, common clock framework registration, DT `clock-output-names`, `of_iomap`, and onecell clock lookup. It integrates with consumers through normal `clk_ops`.

## Risks And Edge Cases
PLL lock timeout returns `-EIO`; bad target rates, parent rates, or VCO table misses return `-EINVAL`. `bit_mask(width)` assumes safe widths. Resource mapping cleanup is multi-stage and must match optional bases. `IPROC_CLK_AON` disables runtime power-down. Fractional-only fast path is valid only when the PLL is locked and integer NDIV/PDIV match the target.

## Test Signals
Useful tests include DT nodes with split and unified status/control mappings, fractional and integer-only PLLs, calculated VCO mode, exact table mode, lock failure injection, `MCLK_DIV_BY_2` leaf rates, disable requests on always-on clocks, and provider lookup of every `clock-output-names` index.
