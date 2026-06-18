<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si514.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-si514.c

### Purpose
`clk-si514.c` drives the Silicon Labs Si514 programmable oscillator over I2C. It exposes one programmable output clock with enable control and frequency programming from 100 kHz to 250 MHz.

### Important APIs, Types, And Functions
`struct clk_si514` holds `clk_hw`, regmap, and I2C client. `struct clk_si514_muldiv` holds fractional multiplier, integer multiplier, low-speed divider bits, and high-speed divider. Important functions are `si514_get_muldiv()`, `si514_set_muldiv()`, `si514_calc_muldiv()`, `si514_calc_rate()`, `si514_recalc_rate()`, `si514_determine_rate()`, `si514_set_rate()`, `si514_enable_output()`, and `si514_probe()`.

### Control Flow, State, And Persistence
Probe sets the clock name from `clock-output-names` or node name, initializes an I2C regmap, registers the clock, and adds an OF provider. Rate calculation reads seven hardware registers, reconstructs the multiplier/divider tuple, and computes output from the fixed 31.98 MHz crystal. Setting a rate disables output, writes divider registers in an order that triggers the change last, starts calibration, waits 10-12 ms, and restores output if it was previously enabled. Persistent state is entirely in oscillator registers and regmap cache.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C, regmap with volatile/writeable callbacks, OF compatible `silabs,si514`, and CCF rate consumers. Risks include no parent clock modeling for the crystal, `determine_rate()` placing an errno in `req->rate`, output left disabled after failed programming, integer overflow risk in low-frequency calculations, and large-rate changes only despite hardware fine-adjust support. Test signals include recalc from known register images, min/max rate rejection, output-enable prepare/unprepare, calibration wait after set-rate, regmap access restrictions, and measured oscillator frequency after programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si514.c -->
