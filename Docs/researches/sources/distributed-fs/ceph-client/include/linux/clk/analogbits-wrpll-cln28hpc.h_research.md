# sources/distributed-fs/ceph-client/include/linux/clk/analogbits-wrpll-cln28hpc.h

Purpose: This header describes configuration helpers for Analog Bits WRPLL CLN28HPC PLLs, used by clock drivers that need to calculate PLL divisors and output rates.

Important APIs/types/functions: It defines `DIVQ_VALUES`, flag masks and shifts for bypass, reset, internal feedback, and external feedback, and `struct wrpll_cfg` with public PLL fields `divr`, `divq`, `range`, `flags`, and `divf`. Helper functions are `wrpll_configure_for_rate`, `wrpll_calc_max_lock_us`, and `wrpll_calc_output_rate`.

Control flow: Callers zero-initialize `struct wrpll_cfg`, set a feedback-mode flag, ask `wrpll_configure_for_rate` to search parameters for a target rate and parent rate, then program hardware with the resulting fields. Output-rate and lock-time helpers derive calculated behavior from an existing config.

State and persistence behavior: Public fields map to PLL signal values; private fields cache output rates across DIVQ values and remember parent-rate search bounds. No persistent state is stored by the header itself, but chosen divisor values become hardware state after driver programming.

Dependencies and integration points: It includes `<linux/types.h>` and is consumed by WRPLL-capable clock drivers, especially SoC PLL providers that bridge hardware-specific PLL math into CCF rate callbacks.

Risks: `divr` and `divf` are hardware values, not plain divisors, and `divq` is a power-of-two divider with `0` invalid. External feedback is documented as unsupported by this driver, so setting that flag without implementation support is risky. Stale cached parent-rate fields can be wrong if a config is reused without recalculation.

Test signals: Rate-rounding tests should verify target-rate search, output-rate reconstruction, lock-time bounds, invalid DIVQ handling, feedback-mode flags, and parent-rate changes. Hardware bring-up should confirm PLL lock and measured output frequencies.
