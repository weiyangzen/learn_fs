# sources/distributed-fs/ceph-client/drivers/clk/analogbits/Kconfig

Purpose: this fragment declares the hidden tristate build symbol for the Analog Bits CLN28HPC wide-range PLL helper library.

Important symbol: `CLK_ANALOGBITS_WRPLL_CLN28HPC` has no prompt and no dependencies in this file, so it is selected by SoC/IP drivers that need the reusable PLL math library.

Control flow/state: Kconfig only controls whether `wrpll-cln28hpc.o` is built. The library itself exports GPL symbols for other drivers.

Dependencies and risks: because the symbol is hidden, missing `select CLK_ANALOGBITS_WRPLL_CLN28HPC` in a consumer will produce unresolved symbols or unavailable helper routines. Overly broad selection increases kernel size only modestly but exposes unused module code. Test signals are consumer driver builds and module/allmodconfig coverage.
