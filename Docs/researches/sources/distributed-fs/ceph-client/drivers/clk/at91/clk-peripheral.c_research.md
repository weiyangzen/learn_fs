# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-peripheral.c

Purpose: providers for AT91 peripheral clocks: legacy PCER/PCDR gates and SAM9x5 PCR-based gates with optional divisors and parent-rate propagation.

Important APIs and data: `at91_clk_register_peripheral()` creates a legacy gate for IDs 2-31. `at91_clk_register_sam9x5_peripheral()` creates `struct clk_sam9x5_peripheral` with PCR layout, range, divider, `auto_div`, flags, and optional `chg_pid`. It also defines global `pmc_pcr_lock`.

Control flow: legacy enable/disable writes PCER/PCDR or PCER1/PCDR1 based on ID. PCR enable writes PID then PCR divider/cmd/enable under the lock; disable clears enable. Recalc reads active divider or computes an automatic shift that keeps the peripheral below range max. Determine-rate searches power-of-two shifts and optionally requests a changeable parent rate; set-rate stores the selected shift.

State and persistence: PCR divider state is cached in memory until enable. Save/restore records enable state and replays PCR setup if it was active. Legacy gates have no explicit PM callbacks.

Dependencies and integration: used by nearly every SoC setup file and DT compat. PCR users require a correct `clk_pcr_layout`, regmap, and lock; critical flags are passed for DDR-related peripherals.

Risks: legacy registration rejects IDs over 31 while PCR supports larger IDs; range zero disables rate management; auto-div depends on parent rate at registration/recalc. Test signals include peripheral enable bits, PCR divider fields, rate constraints for SAMA5D2/SAM9X60 high-speed peripherals, and DDR-critical clocks surviving unused-clock cleanup.
