# sources/distributed-fs/ceph-client/drivers/clk/clk-lmk04832.c

Purpose: SPI common-clock driver for the TI LMK04832 ultra-low-noise clock jitter cleaner. It models OSCin to VCO, SYSREF/SCLK, paired DCLKs, and 14 CLKOUT outputs as a clock tree.

Important APIs, types, and functions: `lmk04832_device_info` stores chip identity and VCO ranges. `struct lmk04832` owns regmap, input clock, reset GPIO, VCO/SCLK hw, DCLK/CLKOUT arrays, SYSREF/SYNC properties, and onecell provider data. `lmk04832_vco_ops`, `lmk04832_sclk_ops`, `lmk04832_dclk_ops`, and `lmk04832_clkout_ops` implement rate, prepare, mux, and enable behavior. `lmk04832_sclk_sync_sequence()` performs the deterministic SYSREF/DCLK synchronization flow.

Control flow: probe gets enabled `oscin`, optional reset GPIO, allocates clock arrays, reads TI-specific firmware properties and child CLKOUT format/sysref settings, initializes regmap, resets the chip, optionally configures 4-wire SPI readback, verifies product ID and mask revision, registers VCO, optionally sets its rate, registers SCLK, registers every paired DCLK and CLKOUT, and publishes a onecell provider. Rate changes on SCLK or DCLK program divider registers and rerun the sync sequence.

State and persistence: hardware state is entirely in LMK registers over SPI. The driver also keeps desired `clkout.format`, `sysref` source choice, SYSREF delay, pulse count, mux mode, and VCO target in memory from DT properties. Regmap has no cache, so reads/writes hit hardware.

Dependencies and integration points: depends on SPI, regmap, GPIO, parent `oscin` clock, OF child nodes, common clock framework, gcd/divider math, and TI LMK register semantics.

Risks and test signals: there are several correctness-sensitive details: VCO range validation, PLL2 divider limits, SYSREF divider range, DCLK divide-by-2/3 workaround, and the long sync register sequence. `lmk04832_clkout_is_enabled()` returns `enabled && !fmt`, which appears inverted relative to a nonzero active format and should be tested. Test signals include ID readback, provider registration for 14 outputs, exact rate acceptance/rejection, sync sequence failures, and suspend-free hardware reset behavior.
