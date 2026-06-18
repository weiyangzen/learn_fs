# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-ar100.c

Registers the Allwinner A31 AR100 clock through the shared Sunxi factors framework. AR100 is a divide-only clock with parent muxing and two factors: preshift `p` and divider `m`.

`sun6i_get_ar100_factors()` clamps requests above the parent, computes a total divisor, chooses `p` so the remaining `m + 1` divider fits in five bits, clamps maximum divisor to 32, and returns the achieved rate. `sun6i_ar100_config` maps `m` to bits 12:8 and `p` to bits 5:4. `sun6i_ar100_data` adds a mux at bit 16 with two-bit mask. Probe maps the resource, calls `sunxi_factors_register()`, and stores the resulting clock in platform data.

State is contained in the AR100 clock register and protected by a static spinlock shared for this clock. There is no dynamic teardown because this is a built-in clock driver. It depends on `clk-factors.h`, platform resources, OF compatible `allwinner,sun6i-a31-ar100-clk`, and the Sunxi factors registration helper. Consumers are firmware/PRCM-side AR100 users.

Divider selection must respect the hardware field widths and divide-only semantics. Very low requested rates collapse to the maximum divisor. Test signals include `clk_round_rate()`/`clk_set_rate()` for boundary rates, parent mux selection, and boot-time probe on A31 DTs.
