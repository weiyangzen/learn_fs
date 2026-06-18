<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa2xx-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pxa2xx-cpufreq.c

## Purpose

Implements cpufreq for Intel/Marvell PXA25x and PXA27x SoCs using fixed frequency tables, the core clock, and optional VCC core voltage scaling.

## APIs, Types, And Functions

`struct pxa_freqs` stores kHz and regulator voltage bounds. Tables cover PXA255 run/turbo modes and PXA27x frequencies. `find_freq_tables()` selects the active table, `pxa_cpufreq_init_voltages()` discovers `vcc_core`, `pxa_set_target()` sequences voltage and `clk_set_rate()`, and `pxa_cpufreq_driver` exposes cpufreq callbacks.

## Control Flow

Module init gets the global `"core"` clock and registers the driver only for PXA25x/PXA27x. Policy init guesses or applies `pxa27x_maxfreq`, initializes voltage support, materializes cpufreq tables, invalidates PXA27x entries above max frequency, and selects the policy table. Targeting raises voltage before increasing frequency, sets the core clock rate, then lowers voltage after decreasing frequency.

## State And Persistence

Global state includes `pxa_cpufreq_data.clk_core`, optional `vcc_core`, module parameters, and generated tables. Hardware state persists in clock dividers/PLL state and regulator output. The driver does not release the clock in module exit.

## Dependencies And Integration Points

Depends on PXA CPU identification helpers, common clock API, optional regulator framework, cpufreq generic table verification, and module parameters for board-specific maximum frequency.

## Risks And Test Signals

The file warns that memory-bus changes require platform-specific timing notifiers, but the driver does not provide them. Downward voltage errors are ignored after a successful clock change. Test signals include generated table contents, rounded clock support, regulator availability logs, `clk_get_rate()` based `get`, and board stability for memory/flash timings at each frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa2xx-cpufreq.c -->
