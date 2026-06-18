<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcc.c

## Purpose

`clk-prcc.c` implements Ux500 PRCC peripheral (`pclk`) and kernel (`kclk`) clock gates backed by MMIO CLKRST registers. It gives `u8500_of_clk.c` reusable registration helpers for each PRCC bit.

## Important APIs, Types, And Functions

`struct clk_prcc` stores the CCF hardware object, remapped PRCC base, gate bit mask, and a software `is_enabled` flag. `clk_prcc_pclk_enable()` writes `PRCC_PCKEN` and polls `PRCC_PCKSR`; `clk_prcc_kclk_enable()` writes `PRCC_KCKEN` and polls `PRCC_KCKSR`. Disable paths write `PRCC_PCKDIS` or `PRCC_KCKDIS`. Public helpers are `clk_reg_prcc_pclk()` and `clk_reg_prcc_kclk()`.

## Control Flow

Registration validates the name, allocates `struct clk_prcc`, maps the physical base with `ioremap(SZ_4K)`, initializes a one-parent or no-parent `clk_init_data`, and calls `clk_register()`. CCF later invokes enable/disable/is_enabled callbacks.

## State And Persistence Behavior

Hardware enable state persists in PRCC registers. The driver also maintains `is_enabled`, initialized to 1, rather than reading status on `is_enabled()`. That makes software state stale if firmware or another driver changes the gate outside these callbacks.

## Dependencies And Integration Points

It depends on Linux CCF, raw MMIO access, `cpu_relax()` polling, and helper declarations from `clk.h`. `u8500_of_clk.c` maps PRCC base addresses from DT and stores returned clocks in two-cell provider arrays.

## Risks And Test Signals

The enable loops have no timeout, so wrong base addresses, bad bit masks, or powered-off PRCC blocks can hang. There is no unregister path and each clock maps a full page. Test by enabling each PRCC pclk/kclk, verifying status bits and `clk_summary`, and booting with invalid DT guarded in test kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcc.c -->
