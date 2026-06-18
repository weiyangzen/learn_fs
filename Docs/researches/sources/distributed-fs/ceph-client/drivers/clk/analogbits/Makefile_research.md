# sources/distributed-fs/ceph-client/drivers/clk/analogbits/Makefile

Purpose: this Makefile maps the hidden Analog Bits WRPLL Kconfig symbol to its implementation object.

Important build rule: `obj-$(CONFIG_CLK_ANALOGBITS_WRPLL_CLN28HPC) += wrpll-cln28hpc.o`.

Control flow/state: no runtime state; the file only participates in kernel object selection.

Dependencies and risks: the object must remain synchronized with the public header `<linux/clk/analogbits-wrpll-cln28hpc.h>` and any drivers selecting the Kconfig symbol. Test signals are allmodconfig builds and link coverage for consumers of `wrpll_configure_for_rate()`, `wrpll_calc_output_rate()`, and `wrpll_calc_max_lock_us()`.
