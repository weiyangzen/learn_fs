# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-apb0.c

Provides the Allwinner A23 APB0 divider clock for both early OF clock declaration and platform-device probing. Unlike A31, the A23 APB0 clock is a standard two-bit divider.

`sun8i_a23_apb0_register()` reads the first parent and optional output name, registers `clk_register_divider()` over bits 1:0, and adds a simple OF provider. `sun8i_a23_apb0_setup()` maps early resources with `of_io_request_and_map()` for `CLK_OF_DECLARE_DRIVER()`, while `sun8i_a23_apb0_clk_probe()` uses devm platform mapping and reuses the same registration helper.

The hardware divider field persists in the PRCM register. The early setup path manually releases mappings on error; the platform path uses devm mapping but still registers a non-devm CCF divider. It integrates with OF early clock init, platform-device fallback, `of_clk_add_provider()`, and compatible `allwinner,sun8i-a23-apb0-clk`.

The dual init path can duplicate provider registration if DT/platform population is wrong. The early path intentionally suppresses the common `-EINVAL` mapping error for MFD-instantiated nodes. Test signals include successful APB0 clock resolution in both early and MFD paths and correct divider readback for all two-bit values.
