# sources/distributed-fs/ceph-client/drivers/clk/ti/apll.c

## Purpose

`apll.c` implements TI OMAP APLL clock support for DRA7 APLL nodes and legacy OMAP2 APLL nodes. It provides CCF operations for enabling, disabling, checking lock/enable state, fixed-rate recalculation, autoidle control, and device-tree clock registration.

## Important APIs, Types, And Functions

DRA7 support uses `dra7_apll_enable()`, `dra7_apll_disable()`, `dra7_apll_is_enabled()`, and `apll_ck_ops`. It programs `APLL_FORCE_LOCK` or `APLL_AUTO_IDLE` through `dpll_data` control registers and polls idlest status up to `MAX_APLL_WAIT_TRIES`. `of_dra7_apll_setup()` parses parent clocks and register addresses, allocates `clk_hw_omap` and `dpll_data`, and defers registration via `ti_clk_retry_init()` if references are unavailable.

OMAP2 support uses `omap2_apll_is_enabled()`, `omap2_apll_recalc()`, `omap2_apll_enable()`, `omap2_apll_disable()`, and `omap2_apll_hwops` for autoidle. `of_omap2_apll_setup()` parses a single parent, `ti,clock-frequency`, enable bit, idlest shift, and three register addresses, then registers the clock provider.

## Control Flow

`CLK_OF_DECLARE()` hooks call setup functions early for compatible strings `ti,dra7-apll-clock` and `ti,omap2-apll-clock`. DRA7 registration obtains reference and bypass parent clocks, stores their hardware pointers in `dpll_data`, registers the OMAP hardware clock, adds an OF provider, and frees temporary init data. Runtime enable writes the force-lock state and polls idlest until locked. Disable moves to auto-idle. OMAP2 enable writes the locked state and polls idlest; disable writes stopped state; recalc returns the fixed configured frequency only when locked.

## State And Persistence Behavior

APLL state is held in PRCM/DPLL registers: control, autoidle, and idlest fields. Allocated `clk_hw_omap` and `dpll_data` persist as registered CCF objects after setup. OMAP2 autoidle count integration is via `clk_hw_omap_ops`, with actual allow/deny writes delegated to the helper functions in this file.

## Dependencies And Integration Points

The file depends on TI clock low-level ops (`ti_clk_ll_ops`), `clock.h`, OMAP clock registration helpers, DT register parsing, retry initialization, and CCF. It integrates with the OMAP autoidle framework through `allow_idle` and `deny_idle` operations.

## Risks And Edge Cases

Polling loops use a very large retry bound with 1 us delay, so hardware failure can stall boot for noticeable time. In `omap2_apll_set_autoidle()`, the computed value is written to `control_reg` rather than `autoidle_reg`; that is a risk signal because the function reads from `autoidle_reg`. DRA7 setup accepts at least one parent but later attempts to fetch parent index 1, so malformed DT with only one parent will defer/fail later. Retry and cleanup paths must avoid leaking allocated init data.

## Test Signals

Boot DRA7 and OMAP2 DTs containing APLL nodes and check provider registration. Enable and disable APLL consumers while tracing register values and idlest transitions. Verify OMAP2 fixed-rate reporting drops to zero when stopped and returns `ti,clock-frequency` when locked. Test autoidle all-enable/all-disable paths and malformed DT parent/register cases.
