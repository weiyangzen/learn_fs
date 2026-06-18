# sources/distributed-fs/ceph-client/drivers/clk/analogbits/wrpll-cln28hpc.c

Purpose: this is a reusable math/configuration library for the Analog Bits CLN28HPC wide-range PLL. It calculates PLL register fields and output rates but does not own hardware registers.

Important exported APIs: `wrpll_configure_for_rate()` fills `struct wrpll_cfg` for a target output rate and parent reference rate. `wrpll_calc_output_rate()` calculates output from an existing config. `wrpll_calc_max_lock_us()` returns the maximum lock delay. Private helpers compute filter range, feedback divisor, Q divider, and parent-rate-dependent R divider limits.

Control flow/state: callers pass a mutable `wrpll_cfg`; the function caches `parent_rate`, `max_r`, and `init_r` in that struct. It validates reference frequency ranges, handles parent-rate bypass, chooses `divq`, scans valid R values for the best `divf`, computes filter `range`, and clears reset/bypass flags as needed. The code exports GPL symbols for integration by platform-specific PLL drivers.

Dependencies and risks: depends on constants from the public WRPLL header and Linux math helpers. External feedback calculation is explicitly unsupported in `wrpll_calc_output_rate()`. The algorithm assumes initialized feedback flags and caller-side serialization. Test signals are unit tests over datasheet bounds, parent rates near min/max, bypass behavior, exact and inexact rates, and comparing computed fields to hardware manuals.
