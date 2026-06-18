# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ssp.c

Purpose: Provides the exported helper `mxs_ssp_set_clk_rate()` for programming the SSP block serial clock divider fields, used by MXS SPI/MMC-style SSP consumers.

Important APIs, types, and functions: `mxs_ssp_set_clk_rate(struct mxs_ssp *ssp, unsigned int rate)` reads the parent clock rate with `clk_get_rate(ssp->clk)`, searches even `clock_divide` values from 2 to 254, computes an 8-bit `clock_rate`, writes `HW_SSP_TIMING` fields, stores the actual SCK rate in `ssp->clk_rate`, and exports the symbol GPL-only.

Control flow: A consumer passes its SSP device context and requested bit clock. The helper picks the first divider pair where `clock_rate <= 255`; if none exists it logs an error and leaves the register unchanged. Otherwise it rewrites timing fields and logs the actual result at debug level.

State and persistence: Hardware timing register fields hold the active SSP clocking. The helper also updates `ssp->clk_rate` in the caller-owned structure.

Dependencies and integration points: Depends on `<linux/spi/mxs-spi.h>` register macros, `struct mxs_ssp`, and a valid prepared parent clock. It is not a CCF clock provider itself.

Risks: No locking is performed, so callers must serialize access against active transfers or other timing updates. A zero requested `rate` would divide by zero. The algorithm chooses the first valid divider pair, not necessarily the closest or least-jitter solution.

Test signals: SSP users should verify actual `ssp->clk_rate` is at or below the requested rate and the hardware timing fields match. Error-path tests should cover too-low requested rates and invalid zero-rate inputs at the caller boundary.
