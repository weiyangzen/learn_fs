<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rk808.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-rk808.c

### Purpose
`clk-rk808.c` exposes two 32.768 kHz clock outputs from Rockchip RK805/RK808/RK809/RK817/RK818 PMIC families. CLKOUT1 is fixed always-on behavior from the clock framework perspective; CLKOUT2 can be enabled and disabled through PMIC registers.

### Important APIs, Types, And Functions
`struct rk808_clkout` stores the parent PMIC regmap and two `clk_hw` objects. Common helpers include `rk808_clkout_recalc_rate()`, `of_clk_rk808_get()`, `rk808_clkout_probe()`, and variant dispatch through `rkpmic_get_ops()`. RK808-style and RK817-style CLKOUT2 ops use different register and bit definitions from the RK808 MFD header.

### Control Flow, State, And Persistence
Probe inherits the parent OF node, allocates state, obtains the parent regmap, registers `rk808-clkout1` and `rk808-clkout2` with optional `clock-output-names`, and publishes a two-entry OF provider. CLKOUT2 prepare/unprepare updates the relevant enable bit; `is_prepared` reads it back. Persistent state is the PMIC register bit and devm-managed clock objects.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the RK808 MFD platform device, parent regmap, PMIC variant ID, OF clock cells, and 32 kHz consumers such as RTC, WiFi, or Bluetooth. Risks include variant misclassification selecting the wrong register, CLKOUT1 lacking enable-state control, RK817 `is_prepared()` returning 0 instead of an error on failed reads, and invalid phandle indexes. Test signals include both output names, phandle index 0/1 behavior, CLKOUT2 bit toggling on each supported PMIC variant, consumer enable counts, and measured 32768 Hz output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rk808.c -->
